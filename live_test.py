"""真实 API 调用测试：用公网图片验证 Qwen-VL 视觉能力"""
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
            tool_names = {t.name for t in tools.tools}
            assert "analyze_image" in tool_names, f"缺少 analyze_image 工具: {tool_names}"

            # 用本地测试图片验证完整链路（本地文件 -> base64 -> API）
            result = await session.call_tool(
                "analyze_image",
                {
                    "image": r"E:\work\vision-mcp\test_image.png",
                    "prompt": "请描述这张图片的内容，包括形状、颜色和文字。",
                },
            )
            for content in result.content:
                print(f"[模型回复] {content.text}")


if __name__ == "__main__":
    asyncio.run(main())
