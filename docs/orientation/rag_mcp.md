# RAG MCP Context

> Status: useful local scaffold.

Nomi now has a small local RAG surface under `tools/rag_mcp/`. It is meant to
make AI questions refer first to:

- this repository's code and active design docs;
- a local programming-books folder, currently named `Local_Programming_Books`
  as a generic placeholder.

This does make sense for Nomi, but as a **source-discovery and citation layer**,
not as an autonomous design authority. Nomi has many overlapping design notes,
research surveys, parser/interpreter files, samples, and tool docs. MCP gives
agents a repeatable way to ask "what does this repo already say?" before they
invent or edit.

The implementation is deliberately dependency-light. It builds a lexical chunk
index from configured text files and exposes it through a stdio MCP server.
Embeddings, vector stores, PDF extraction, and richer source adapters can be
added behind the same retrieval interface later.

Use this when:

- starting a design question and looking for existing docs or research;
- preparing parser/interpreter work that needs nearby implementation context;
- checking whether a proposed change contradicts an active feature note;
- grounding an AI answer in cited repo paths instead of chat memory.

Do not use this as:

- a replacement for reading the active files once they are found;
- a replacement for tests or snapshots;
- a reason to rank old research notes above the active spec/design spine.

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

Sources may include `path_boosts` to steer lexical ranking. The default
configuration boosts `AGENTS.md`, `README.md`, `docs/language/`, and
`docs/features/`, while damping `docs/research/`. This matches the repo rule:
research is evidence, active language and feature docs are closer to current
intent.

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

It also exposes read-only MCP resources for indexed files:

- `resources/list`: list indexed source files.
- `resources/read`: read a listed source file.

Search results include text snippets for older MCP clients and
`structuredContent` for clients that can consume typed tool output.

## OpenCode Configuration

OpenCode supports local MCP servers through the `mcp` config object. Add this
to the project `opencode.json` or to your user config when you want the tools
available during Nomi sessions:

```json
{
  "mcp": {
    "nomi-rag": {
      "type": "local",
      "command": [
        "python3",
        "-m",
        "tools.rag_mcp.mcp_server",
        "--config",
        "config/rag_sources.json"
      ],
      "enabled": true
    }
  }
}
```

OpenCode prefixes MCP tool names with the server name, so these usually appear
as tools like `nomi-rag_rag_search`, `nomi-rag_rag_sources`, and
`nomi-rag_rag_rebuild`.

## Suggested Agent Habit

For Nomi work, use RAG in this order:

1. `rag_sources` to verify the index path and whether optional books exist.
2. `rag_rebuild` after large doc/code changes, or when results seem stale.
3. `rag_search` with a narrow phrase such as `"binding constraints"` or
   `"yield to block reduced interpreter"`.
4. Read the returned files directly before editing.
5. Cite the returned paths in design answers or implementation plans.

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
