import os
import json
from pathlib import Path
from typing import Any, Dict

def load_config() -> Dict[str, Any]:
    """Load MCP configuration from JSON file."""
    config_path = Path(os.path.join(os.getcwd(), "src/assistant/config/mcp/config.json"))
    if not config_path.exists():
        raise FileNotFoundError(f"MCP configuration file not found: {config_path}")
    
    with open(config_path) as f:
        return json.load(f) 