from mcp.server.fastmcp import FastMCP
from datetime import datetime, date

mcp = FastMCP("time_server")

@mcp.tool()
async def get_local_time() -> str:
    """Get current local time on the server.
    """
    return datetime.now().astimezone().strftime("%m/%d/%Y:%H:%M:%S %Z")

@mcp.tool()
async def get_local_date() -> str:
    """Get current local date on the server.
    """
    return date.today().strftime("%m/%d/%Y")

if __name__ == "__main__":
    mcp.run(transport='stdio')