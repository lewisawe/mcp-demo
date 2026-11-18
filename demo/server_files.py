"""
Toy MCP server: the TRUSTED one.

A plain file-reading server, standing in for something like the official
filesystem server. It is honest. Nothing in this file is poisoned.

It exists so the demo has the realistic shape of the attack: the
attacker's server (server_weather.py) has no file access of its own. It
talks the agent into misusing THIS server's tool. That cross-server
steering is the part a protocol-level audience cares about, and it is why
the weather server alone cannot be "fixed" by auditing the file server.

Operates on local fake data only (dummy_credentials in this directory).
"""

import pathlib

from mcp.server.mcpserver import MCPServer

HERE = pathlib.Path(__file__).parent

server = MCPServer(
    name="files-trusted",
    instructions="A small local file reader.",
)


@server.tool()
def read_file(path: str) -> str:
    """Read the contents of a local file by relative path.

    Args:
        path: Path to the file, relative to the demo directory
            (e.g. "dummy_credentials").
    """
    target = (HERE / path).resolve()
    # Keeps the demo from ever touching real files on the presenter's
    # machine. This is not the security control the talk is about.
    if HERE not in target.parents and target != HERE:
        return "Error: access outside the demo directory is disabled."
    if not target.exists():
        return f"Error: {path} not found."
    return target.read_text()


if __name__ == "__main__":
    server.run("stdio")
