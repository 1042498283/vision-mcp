# vision-mcp

基于 **阿里云百炼 DashScope（Qwen-VL）** 的视觉 MCP Server。通过 MCP 协议为 Claude Code、Trae、CodeBuddy 等客户端提供图片理解能力。

## 功能

- `analyze_image` — 通用图片分析（支持本地文件路径 / 公网 URL / data URL）
- `screenshot_analyze` — UI / 界面截图分析

## 支持的模型

| 模型 | 说明 |
|------|------|
| `qwen-vl-max` | 效果最佳，适合复杂图片理解 |
| `qwen-vl-plus` | 效果与速度均衡（默认） |
| `qwen2.5-vl-72b-instruct` | 72B 指令跟随 |
| `qwen2.5-vl-7b-instruct` | 7B 轻量快速 |

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install -r requirements.txt
# Linux / macOS
.venv/bin/pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件（MCP Server 启动时自动读取）：

```env
DASHSCOPE_API_KEY=sk-你的密钥
```

申请地址：[阿里云百炼控制台](https://bailian.console.aliyun.com)

### 3. 启动

```bash
# Windows
.venv\Scripts\python vision_mcp_server.py
# Linux / macOS
.venv/bin/python vision_mcp_server.py
```

列出支持的模型：

```bash
python vision_mcp_server.py --list
```

## 接入 MCP 客户端

在客户端的 MCP 配置（如 `mcp.json` 或 `.mcp.json`）中添加：

```json
{
  "mcpServers": {
    "vision": {
      "command": "/path/to/vision-mcp/.venv/bin/python",
      "args": ["/path/to/vision-mcp/vision_mcp_server.py"],
      "env": {}
    }
  }
}
```

## 测试

```bash
# 协议冒烟测试（无需 API Key）
.venv/bin/python smoke_test.py

# 真实调用测试（需配置 API Key，使用本地测试图）
.venv/bin/python live_test.py
```

## 注意

- DashScope 服务端下载**海外公网图片 URL** 可能超时，建议使用本地文件路径或国内可达的 URL
- API Key 通过 `.env` 文件提供，不会写入配置文件

## License

MIT
