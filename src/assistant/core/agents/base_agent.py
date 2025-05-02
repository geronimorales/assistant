import os
import json

from psycopg import AsyncConnection
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt.tool_node import tools_condition
from langgraph.types import Command

from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from .state import State

from .validated_tool_node import ValidatedToolNode

from abc import ABC, abstractmethod

from langgraph.utils.runnable import RunnableCallable

from langchain_core.runnables import RunnableConfig

from typing import cast
from typing_extensions import Sequence
from langchain_core.messages import BaseMessage

from langgraph.errors import ErrorCode, create_error_message

from assistant.config.app import config as app_config

from langchain_mcp_adapters.client import MultiServerMCPClient

from assistant.core.agents import prompts


class BaseAgent(ABC):

    PROMPT_NAME = "v1"

    def __init__(self, thread_id: any, mcps: dict | None = None):
        """
        Initializes an BaseAgent instance.

        Args:
            thread_id: (any) an identifier used to keep track of a conversation.
            mcp_filename: (str) the filename of the MCP server.
            tools_metadata: (dict) this dict contains metadata for some tools.
        """
        self._thread_id = thread_id
        self._mcps = mcps

        self._tools_metadata = {}

        for name, config in mcps.items():
            self._tools_metadata.update(config["metadata"])

        self._mcps = mcps

        self._tools = None
        self._model_runnable = None
        self._graph = None

    @abstractmethod
    def _get_chat_model(self):
        pass

    def _get_prompt_template(self, prompt_name: str):
        system_prompt = self._load_system_prompt(prompt_name)

        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{messages}"),
            ]
        ).partial(tools=[tool_name for tool_name, _ in self._tools_metadata.items()])

    def _get_assistant_runnable(self):
        assistant_prompt = self._get_prompt_template(BaseAgent.PROMPT_NAME)
        llm = self._get_chat_model()
        return assistant_prompt | llm.bind_tools(self._tools)

    def _load_system_prompt(self, key: str) -> str:
        """
        Loads the system prompt from a prompts repository

        Args:
            key: (str) the key of the prompt to be loaded

        Returns:
            A string with the loaded prompt
        """
        return prompts.BTBOX_PROMPT

    def _direct_tool_output(self, state: State):
        messages = state.get("messages")

        if not messages or len(messages) == 0:
            raise Exception("No messages")

        tool_messages = []
        for i in range(len(messages) - 1, -1, -1):
            message = messages[i]

            # Stop if we encounter a non-ToolMessage
            if not isinstance(message, ToolMessage):
                break

            tool_messages.append(message)

        tool_messages.reverse()

        for tool_message in tool_messages:
            if tool_message.status == "success" and self._tools_metadata[
                tool_message.name
            ].get("return_direct"):
                tool_content = json.loads(tool_message.content)
                content = json.dumps(
                    {"tool_name": tool_message.name, "data": tool_content}
                )
                state = {**state, "messages": [AIMessage(content=content)]}

        # print("state", state)
        return state

    def _validate_chat_history(
        self,
        messages: Sequence[BaseMessage],
    ) -> None:
        """Validate that all tool calls in AIMessages have a corresponding ToolMessage."""
        all_tool_calls = [
            tool_call
            for message in messages
            if isinstance(message, AIMessage)
            for tool_call in message.tool_calls
        ]
        tool_call_ids_with_results = {
            message.tool_call_id
            for message in messages
            if isinstance(message, ToolMessage)
        }
        tool_calls_without_results = [
            tool_call
            for tool_call in all_tool_calls
            if tool_call["id"] not in tool_call_ids_with_results
        ]
        if not tool_calls_without_results:
            return

        print("all_tool_calls", all_tool_calls)
        print("tool_call_ids_with_results", tool_call_ids_with_results)
        print("tool_calls_without_results", tool_calls_without_results)

        error_message = create_error_message(
            message="Found AIMessages with tool_calls that do not have a corresponding ToolMessage. "
            f"Here are the first few of those tool calls: {tool_calls_without_results[:3]}.\n\n"
            "Every tool call (LLM requesting to call a tool) in the message history MUST have a corresponding ToolMessage "
            "(result of a tool invocation to return to the LLM) - this is required by most LLM providers.",
            error_code=ErrorCode.INVALID_CHAT_HISTORY,
        )
        raise ValueError(error_message)

    def _call_model(self, state: State, config: RunnableConfig) -> State:
        messages = state.get("messages")
        self._validate_chat_history(messages)
        response = cast(AIMessage, self._model_runnable.invoke(state, config))
        # add agent name to the AIMessage
        response.name = self.__class__.__name__

        return {"messages": response}

    async def _acall_model(self, state: State, config: RunnableConfig) -> State:
        messages = state.get("messages")
        self._validate_chat_history(messages)
        response = cast(AIMessage, await self._model_runnable.ainvoke(state, config))
        # add agent name to the AIMessage
        response.name = self.__class__.__name__
        return {"messages": response}

    async def _create_graph(self, checkpointer: AsyncPostgresSaver):
        """
        Set the graph builder, initializes the memory saver and returns a compiled StateGraph

        Returns:
            Compiled StateGraph
        """
        graph_builder = StateGraph(State)

        graph_builder.add_node(
            "assistant", RunnableCallable(self._call_model, self._acall_model)
        )
        graph_builder.add_node(
            "tools", ValidatedToolNode(self._tools, tools_metadata=self._tools_metadata)
        )
        graph_builder.add_node(
            "direct_tool_output", RunnableCallable(self._direct_tool_output)
        )

        graph_builder.add_edge(START, "assistant")

        graph_builder.add_conditional_edges(
            "assistant", tools_condition, ["tools", END]
        )

        graph_builder.add_edge("tools", "direct_tool_output")
        graph_builder.add_edge("direct_tool_output", "assistant")

        await checkpointer.setup()

        graph = graph_builder.compile(checkpointer=checkpointer)

        return graph

    async def _initialize(self):
        connection_kwargs = {"autocommit": True}
        connection_string = os.getenv("MEMORY_ASYNC_DATABASE_URL", None)
        if not connection_string:
            raise Exception(
                "No connection string set for agent memory. Please add MEMORY_ASYNC_DATABASE_URL to .env"
            )
        async with AsyncPostgresSaver.from_conn_string(
            connection_string
        ) as checkpointer:
            async with await AsyncConnection.connect(
                connection_string, **connection_kwargs
            ) as conn:
                checkpointer = AsyncPostgresSaver(conn)
                self._graph = await self._create_graph(checkpointer)

    async def _stream(self, config: dict, input: dict = None):

        async for event, meta in self._graph.astream(
            input, config=config, stream_mode="messages"
        ):
            event.pretty_print()
            if (
                hasattr(event, "tool_call_id")
                and hasattr(event, "status")
                and event.status != "error"
            ):
                tool_call = {
                    k: v
                    for k, v in event.__dict__.items()
                    if k in ["name", "tool_call_id", "status"]
                }
                metadata = self._tools_metadata[tool_call["name"]]
                description = metadata.get("message", tool_call["name"])
                tool_call["description"] = description
                yield json.dumps({"tool_call": tool_call})
            elif meta["langgraph_node"] == "assistant":
                yield event.content
            elif meta["langgraph_node"] == "direct_tool_output":
                yield event.content

    async def stream(self, user_input: str):
        """Stream the agent's response to user input"""

        async with MultiServerMCPClient(self._mcps) as client:
            self._tools = client.get_tools()
            self._model_runnable = self._get_assistant_runnable()

            connection_kwargs = {"autocommit": True}
            connection_string = app_config.get("llm.memory.async_database_url")
            if not connection_string:
                raise Exception(
                    "No connection string set for agent memory. Please add MEMORY_ASYNC_DATABASE_URL to .env"
                )
            async with AsyncPostgresSaver.from_conn_string(
                connection_string
            ) as checkpointer:
                async with await AsyncConnection.connect(
                    connection_string, **connection_kwargs
                ) as conn:
                    checkpointer = AsyncPostgresSaver(conn)
                    self._graph = await self._create_graph(checkpointer)

                    config = {"configurable": {"thread_id": self._thread_id}}

                    snapshot = await self._graph.aget_state(config)

                    # Check if previous interaction interrupted before tool calling
                    if snapshot.next and hasattr(
                        snapshot.values["messages"][-1], "tool_calls"
                    ):

                        for tool_call in snapshot.values["messages"][-1].tool_calls:
                            tool_name = tool_call["name"]
                            tool_metadata = self._tools_metadata[tool_name]

                            print("tool_metadata", tool_metadata)

                            if not tool_metadata["interrupt"]:
                                continue

                            resume = (
                                user_input.strip()
                                == tool_metadata["interrupt"]["continue"]
                            )

                            async for content in self._stream(
                                config, Command(resume=resume)
                            ):
                                yield content
                    else:
                        async for content in self._stream(
                            config, {"messages": ("user", user_input)}
                        ):
                            yield content

                    snapshot = await self._graph.aget_state(config)

                    # # Check if graph interrupted after processing user input.
                    if snapshot.next:
                        for task in snapshot.tasks:
                            yield json.dumps(task.interrupts[-1].value)
