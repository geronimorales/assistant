# Active Context

## Current Focus
- Implementing MCP (Model Control Protocol) integration
- Setting up Ollama as the LLM provider
- Configuring vector store for document embeddings

## Recent Changes
- Created MCP configuration file with Ollama settings
- Set up vector store configuration for document embeddings
- Configured model parameters for Llama 3.2 8B

## Next Steps
1. Implement MCP client for Ollama integration
2. Set up vector store initialization
3. Create document embedding pipeline
4. Implement document search functionality

## Active Decisions
- Using Ollama as the LLM provider for local development
- Using Llama 3.2 8B as the default model
- Using Nomic's embedding model for document vectors
- Using HNSW for efficient vector search

## Learnings
- MCP provides a standardized way to interact with LLMs
- Ollama offers good local development experience
- Vector stores are essential for semantic search
- HNSW provides efficient approximate nearest neighbor search

## Important Patterns
1. Functional programming approach
2. Clean architecture with clear separation of concerns
3. Dependency injection for services
4. Repository pattern for data access

## Project Insights
1. Project is in early stages with basic structure
2. Need to implement core functionality
3. Focus on maintainable and scalable architecture
4. Emphasis on proper documentation and testing 