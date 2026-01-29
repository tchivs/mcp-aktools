import importlib.metadata
from fastmcp import FastMCP

try:
    __version__ = importlib.metadata.version("aktools-pro")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

mcp = FastMCP(name="aktools-pro", version=__version__)
