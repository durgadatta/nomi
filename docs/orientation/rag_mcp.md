# RAG MCP Context

> Status: basic scaffold.

Nomi now has a small local RAG surface under `tools/rag_mcp/`. It is meant to
make AI questions refer first to:

- this repository's code and active design docs;
- a local programming-books folder, currently named `Local_Programming_Books`
  as a generic placeholder.

The first version is deliberately dependency-light. It builds a lexical chunk
index from configured text files and exposes it through a minimal stdio MCP
server. Embeddings, vector stores, PDF extraction, and richer source adapters
can be added behind the same retrieval interface later.

## Configuration

Sources are tracked in:

```bash
config/rag_sources.json
```

The default index is generated at:

```bash
.nomi/rag_index.json
```

`.nomi/` is ignored by git because the index is derived from local files.

The placeholder books source points at:

```bash
Local_Programming_Books
```

Rename that path in `config/rag_sources.json` when the real folder is known, or
replace it with an absolute path outside the repo.

## Local Commands

Build the index:

```bash
python3 -m tools.rag_mcp.cli build
```

Search it directly:

```bash
python3 -m tools.rag_mcp.cli search "binding constraints"
```

After editable install, the equivalent commands are:

```bash
nomi-rag build
nomi-rag search "yield to block"
```

## MCP Server

Run the MCP stdio server:

```bash
python3 -m tools.rag_mcp.mcp_server
```

Example MCP client configuration:

```json
{
  "mcpServers": {
    "nomi-rag": {
      "command": "python3",
      "args": [
        "-m",
        "tools.rag_mcp.mcp_server",
        "--config",
        "config/rag_sources.json"
      ]
    }
  }
}
```

The server exposes:

- `rag_search`: search code/docs/books and return cited local snippets.
- `rag_sources`: list configured sources and whether their paths exist.
- `rag_rebuild`: rebuild the generated local index.

## Extension Points

Keep the retrieval contract centered on source-aware chunks:

- `tools/rag_mcp/config.py`: source configuration and path resolution.
- `tools/rag_mcp/index.py`: file discovery, chunking, indexing, search.
- `tools/rag_mcp/mcp_server.py`: MCP tool facade.

Good next additions:

- a PDF/EPUB extraction adapter for the programming-books source;
- embeddings and a vector-store backend beside the lexical backend;
- source priority rules, so active language docs outrank drafts and broad
  research notes;
- a prompt wrapper that always asks the model to cite `rag_search` results.
