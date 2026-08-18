"""MCP Server 冒烟测试：stdio 握手 + 工具列表"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    python = sys.executable
    params = StdioServerParameters(command=python, args=["vision_mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("=== 已注册工具 ===")
            for t in tools.tools:
                print(f"- {t.name}: {t.description[:60]}")
            print("=== 冒烟测试通过 ===")


if __name__ == "__main__":
    asyncio.run(main())
