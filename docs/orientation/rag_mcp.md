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

The default configuration belongs to the source checkout; it is not bundled
with the wheel. For an installed developer tool, supply an absolute config path:

```bash
nomi-rag --config /absolute/path/to/rag_sources.json build
nomi-rag --config /absolute/path/to/rag_sources.json search "binding constraints"
nomi-rag-mcp --config /absolute/path/to/rag_sources.json
```

For an explicitly supplied config, relative source and index paths resolve
against its directory. This keeps the index with your configured material,
rather than indexing the Python installation. A minimal configuration is:

```json
{
  "index_path": ".nomi/rag_index.json",
  "sources": [
    {"name": "notes", "path": "notes", "include": ["**/*.md"]}
  ]
}
```

Create a `notes` directory beside that config and add your Markdown files.
Configure only material you intend to expose through retrieval. Missing or
malformed configuration exits with status 2 and a recovery message on stderr;
MCP startup keeps stdout reserved for protocol JSON. Source include/exclude and
resource boundaries remain described below.

The placeholder books source points at:

```bash
Local_Programming_Books
```

Rename that path in `config/rag_sources.json` when the real folder is known, or
replace it with an absolute path outside the repo.

Sources may include `path_boosts` to steer lexical ranking. The default
configuration gives the strongest document boost to `docs/design/`, a smaller
boost to current implementation orientation, and lower boosts to research and
dated reviews. This matches the authority order in `docs/README.md`.

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
- `resources/templates/list`: list source-specific URI templates such as
  `nomi-rag://nomi-codebase/{path}`.

Search results include text snippets for older MCP clients and
`structuredContent` for clients that can consume typed tool output.

Resource URI paths are relative to their named source, even when search refs
are relative to the project or absolute for an external books directory.
Listing and reads recheck current include/exclude rules through the discovery
iterator. Symlinks cannot escape a declared source or bypass exclusions on
their resolved target. This avoids treating a source root as permission to
read every file beneath it. Broadly configured sources are still broad access;
this is not a filesystem sandbox. Rebuild old indexes after this change or
configuration changes: cached search snippets may otherwise retain old content.

Stdio emits newline-delimited JSON only. Invalid JSON receives parse error
`-32700`; invalid request envelopes receive `-32600`; subsequent valid requests
continue. Notifications do not receive responses. This is a bounded framing
improvement, not full SDK/lifecycle/schema conformance. See the
[MCP stdio contract](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#stdio)
and [JSON-RPC errors](https://www.jsonrpc.org/specification#error_object).

The server also exposes one prompt wrapper:

- `rag_grounded_answer`: ask a Nomi question with an instruction to run
  `rag_search`, read returned files directly, cite paths or refs, and name
  drift when active docs and implementation disagree.

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
  research notes.
