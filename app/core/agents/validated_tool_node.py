import json
from langgraph.prebuilt.tool_node import ToolNode
from langchain_core.messages import ToolMessage
from typing import Literal, Union, Sequence, Optional, Any, Optional, Callable, Union
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolCall
from langgraph.types import interrupt
from langchain_core.tools import BaseTool


INVALID_TOOL_NAME_ERROR_TEMPLATE = (
    "Error: {requested_tool} is not a valid tool, try one of [{available_tools}]."
)

TOOL_CALL_ERROR_TEMPLATE = "Error: {error}\n Please fix your mistakes."


def msg_content_output(output: Any) -> Union[str, list[dict]]:
    recognized_content_block_types = ("image", "image_url", "text", "json")
    if isinstance(output, str):
        return output
    elif isinstance(output, list) and all(
        [
            isinstance(x, dict) and x.get("type") in recognized_content_block_types
            for x in output
        ]
    ):
        return output
    # Technically a list of strings is also valid message content but it's not currently
    # well tested that all chat models support this. And for backwards compatibility
    # we want to make sure we don't break any existing ToolNode usage.
    else:
        try:
            return json.dumps(output, ensure_ascii=False)
        except Exception:
            return str(output)


class ValidatedToolNode(ToolNode):

    def __init__(
        self,
        tools: Sequence[Union[BaseTool, Callable]],
        *,
        name: str = "tools",
        tags: Optional[list[str]] = None,
        handle_tool_errors: Union[
            bool, str, Callable[..., str], tuple[type[Exception], ...]
        ] = True,
        messages_key: str = "messages",
        tools_metadata: Optional[dict] = None,
        user_data: Optional[dict] = None
    ) -> None:
        self._validated = {}
        self._tools_metadata = tools_metadata
        self._user_data = user_data
        super().__init__(
            tools,
            name=name,
            tags=tags,
            handle_tool_errors=handle_tool_errors,
            messages_key=messages_key,
        )

    def _validate_tool_call(self, call: ToolCall) -> Optional[ToolMessage]:

        if call["id"] in self._validated:
            return None

        self._validated[call["id"]] = True

        if (requested_tool := call["name"]) not in self.tools_by_name:
            content = INVALID_TOOL_NAME_ERROR_TEMPLATE.format(
                requested_tool=requested_tool,
                available_tools=", ".join(self.tools_by_name.keys()),
            )
            return ToolMessage(
                content, name=requested_tool, tool_call_id=call["id"], status="error"
            )

        error_messages = self._validate_call(call)

        if len(error_messages) > 0:
            return ToolMessage(
                content=f". ".join(error_messages) + ".",
                name=call["name"],
                tool_call_id=call["id"],
                status="error",
            )

        return None

    def _validate_call(self, tool_call: any) -> list:
        call_args = tool_call["args"]
        schema = self.tools_by_name[tool_call["name"]].args_schema

        required_args = schema["required"] if "required" in schema else []

        error_messages = []

        for arg_name in required_args:
            if (
                arg_name not in call_args
                or not call_args[arg_name]
                or str(call_args[arg_name]).strip() == ""
            ):
                error_messages.append(f"You need to specify a value for {arg_name}")

        return error_messages

    def _check_interrupt(self, call: ToolCall) -> Optional[ToolMessage]:
        tool_name = call["name"]
        tool_metadata = self._tools_metadata[tool_name]
        interrupt_data = tool_metadata.get("interrupt")

        call_args = call["args"]

        if interrupt_data and not interrupt(
            {"action": "ask_for_human_approval"} | interrupt_data | {"args": call_args}
        ):
            return ToolMessage(
                content=f"User has decided to cancel the action. Continue assisting, accounting for the user's input.",
                name=call["name"],
                tool_call_id=call["id"],
                status="error",
            )

        return None

    async def _arun_one(
        self,
        call: ToolCall,
        input_type: Literal["list", "dict", "tool_calls"],
        config: RunnableConfig,
    ) -> ToolMessage:

        if invalid_tool_message := self._validate_tool_call(call):
            return invalid_tool_message

        if interrupt_message := self._check_interrupt(call):
            return interrupt_message
        
        if self._user_data:
            call["args"]["user_data"] = self._user_data 

        return await super()._arun_one(call, input_type, config)

    def _run_one(
        self,
        call: ToolCall,
        input_type: Literal["list", "dict", "tool_calls"],
        config: RunnableConfig,
    ) -> ToolMessage:

        if invalid_tool_message := self._validate_tool_call(call):
            return invalid_tool_message

        if interrupt_message := self._check_interrupt(call):
            return interrupt_message

        return super()._run_one(call, input_type, config)
