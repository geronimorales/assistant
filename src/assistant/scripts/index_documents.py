import argparse
import json
from typing import Dict, Optional

import asyncio

from assistant.core.llamaindex.indexer import index_file_documents


def parse_metadata(metadata_str: Optional[str]) -> Optional[Dict]:
    """Parse metadata string into a dictionary."""
    if not metadata_str:
        return None
    try:
        return json.loads(metadata_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid metadata JSON format: {e}")


async def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Index documents with metadata")
    
    # Add required directory path argument
    parser.add_argument('directory', help='Directory path containing documents to index')
    
    # Parse known args first to get any custom metadata parameters
    args, remaining = parser.parse_known_args()
    
    # Create a new parser for the remaining arguments
    metadata_parser = argparse.ArgumentParser()
    
    # Add all remaining arguments as potential metadata
    for arg in remaining:
        if arg.startswith('--'):
            # Add the argument without the '--' prefix
            metadata_parser.add_argument(arg)
    
    # Parse the remaining arguments
    metadata_args = metadata_parser.parse_args(remaining)

    try:
        # Start with JSON metadata if provided
        metadata = {}
        
        # Add all other arguments as metadata
        for arg in vars(metadata_args):
            value = getattr(metadata_args, arg)
            if value is not None:
                metadata[arg] = value
        
        await index_file_documents(dir_path=args.directory, metadata=metadata)
        print("Successfully indexed documents")
        if metadata:
            print(f"With metadata: {metadata}")
    except Exception as e:
        print(f"Error indexing documents: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

def cli():
    asyncio.run(main())        


# if __name__ == "__main__":
#     asyncio.run(main())
