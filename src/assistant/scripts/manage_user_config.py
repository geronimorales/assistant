#!/usr/bin/env python3
import argparse
import json
import sys
import asyncio
from typing import Optional, Dict, Any
from uuid import UUID

from src.assistant.repositories.user_config import UserConfigRepository
from src.assistant.schemas.user_config import UserConfigCreate, UserConfigUpdate


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Manage user configurations")
    parser.add_argument("--id", type=str, help="UUID of the user config to update")
    parser.add_argument("--description", type=str, help="Description of the user config")
    parser.add_argument("--config", type=str, help="JSON configuration string")
    parser.add_argument("--active", type=bool, default=True, help="Whether the config is active")
    
    return parser.parse_args()


def validate_config(config_str: str) -> Dict[str, Any]:
    """Validate and parse the JSON configuration string."""
    try:
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON configuration: {e}", file=sys.stderr)
        sys.exit(1)


async def main_async() -> None:
    """Async main entry point for the script."""
    args = parse_args()
    
    if args.config is None:
        print("Error: --config parameter is required", file=sys.stderr)
        sys.exit(1)
    
    config = validate_config(args.config)
    
    repository = UserConfigRepository()
    
    if args.id:
        try:
            config_id = UUID(args.id)
            if args.description:
                user_config = await repository.update_description(
                    config_id=config_id,
                    description=args.description
                )
            if args.config:
                user_config = await repository.update_config(
                    config_id=config_id,
                    config=config
                )
            if args.active is not None:
                user_config = await repository.toggle_active(
                    config_id=config_id,
                    active=args.active
                )
            
            if user_config:
                print(f"Updated user config: {user_config.id}")
            else:
                print(f"Error: User config with ID {args.id} not found", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid UUID format: {args.id}", file=sys.stderr)
            sys.exit(1)
    else:
        user_config = await repository.create_with_config(
            config=config,
            description=args.description,
            active=args.active if args.active is not None else True
        )
        print(f"Created user config: {user_config.id}")


def main() -> None:
    """Main entry point for the script."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main() 