"""Qwen-VL 视觉 MCP Server

通过阿里云百炼 DashScope 的 OpenAI 兼容接口调用 Qwen-VL 多模态模型，
为 Claude Code / TraeCode 等 MCP 客户端提供图片理解能力。

环境变量:
    DASHSCOPE_API_KEY: 阿里云百炼 API Key（必填）

用法:
    python vision_mcp_server.py            # 以 stdio 方式运行（MCP 客户端调用）
    python vision_mcp_server.py --list     # 列出支持的模型
"""

from __future__ import annotations

import base64
import mimetypes
import os
import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from openai import OpenAI

# 若脚本同目录存在 .env 文件，则从中加载 DASHSCOPE_API_KEY
_ENV_FILE = Path(__file__).resolve().parent / ".env"
if _ENV_FILE.is_file():
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# DashScope OpenAI 兼容接口
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 常用 Qwen-VL 模型
SUPPORTED_MODELS = {
    "qwen-vl-max": "最强通义千问VL，效果最佳，适合复杂图片理解",
    "qwen-vl-plus": "效果与速度均衡，性价比高",
    "qwen2.5-vl-72b-instruct": "Qwen2.5 系列 72B，指令跟随强",
    "qwen2.5-vl-7b-instruct": "Qwen2.5 系列 7B，轻量快速",
}

DEFAULT_MODEL = "qwen-vl-plus"


def _get_client() -> OpenAI:
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DASHSCOPE_API_KEY。"
            "请在阿里云百炼控制台 (https://bailian.console.aliyun.com) 创建 API Key，"
            "然后设置环境变量后再启动本服务。"
        )
    return OpenAI(api_key=api_key, base_url=DASHSCOPE_BASE_URL)


def _load_image_content(image: str) -> str:
    """将本地路径或公网 URL 转换为 DashScope 可用的图片引用。

    返回 data URL（本地文件）或原始 URL。
    """
    image = image.strip()
    if image.startswith(("http://", "https://", "data:")):
        return image

    path = Path(image)
    if not path.is_file():
        raise FileNotFoundError(f"图片文件不存在: {image}")
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


mcp = FastMCP("vision")


@mcp.tool()
def analyze_image(
    image: str,
    prompt: str = "请详细描述这张图片的内容。",
    model: Literal["qwen-vl-max", "qwen-vl-plus", "qwen2.5-vl-72b-instruct", "qwen2.5-vl-7b-instruct"] = DEFAULT_MODEL,
) -> str:
    """分析一张图片，返回模型的文字描述。

    Args:
        image: 图片来源，支持本地文件路径（如 C:/path/to/img.png）或公网 URL。
        prompt: 告诉模型要看什么/回答什么的问题或指令。
        model: 使用的 Qwen-VL 模型，默认 qwen-vl-plus。
    """
    client = _get_client()
    image_url = _load_image_content(image)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        max_tokens=1024,
    )
    return resp.choices[0].message.content or ""


@mcp.tool()
def screenshot_analyze(
    image_path: str,
    prompt: str = "请描述这个界面截图的内容，包括布局、元素和文字。",
) -> str:
    """分析 UI/界面截图，适合浏览器截图、页面设计稿等。

    Args:
        image_path: 截图文件路径。
        prompt: 分析指令，默认描述界面布局与元素。
    """
    return analyze_image(image=image_path, prompt=prompt, model=DEFAULT_MODEL)


def main() -> None:
    if "--list" in sys.argv:
        print("支持的 Qwen-VL 模型:")
        for name, desc in SUPPORTED_MODELS.items():
            print(f"  - {name}: {desc}")
        return
    mcp.run()


if __name__ == "__main__":
    main()
