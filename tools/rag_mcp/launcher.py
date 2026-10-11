"""Launch the checkout's MCP server from any client working directory."""

from pathlib import Path
import sys


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.rag_mcp.mcp_server import main

    main()
