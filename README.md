---
name: "html-screenshot-skill"
description: "一个将 HTML 截图为高清 PNG 文件的 Skill，可以嵌入 `guizang-social-card-skill` 工作流，用于生成公众号封面、海报、卡片等设计图。"
version: 1.0.0
Update date: 2026-06-28
---


## 背景

我经常使用 `guizang-social-card-skill` 生成公众号封面图，但生成后常需要微调文案。如果每次修改 HTML 后都重新跑一遍完整的生成流程，既耗时也消耗大量 Token。这个 Skill 就是为了解决这个环节的效率问题——将「修改文案」与「重新出图」解耦，这个 skill 只负责截图这一子任务。

## 定位

这并非一个通用的截图工具，而是一个嵌入「 `guizang-social-card-skill` 生成封面图」工作流的自动化截图工具，专用于「已完成的 HTML → 精确 PNG」。

### 适用场景

- **工作流中间环节**：你已通过 `guizang-social-card-skill` 生成了 HTML 设计稿（如海报、卡片、公众号封面），需要修改局部文案后重新出图，而不想从头重跑整个生成流程。
- **精确复现**：需要固定 `--scale 2.0`、固定 viewport、特定 CSS 选择器，确保每张输出图尺寸、比例、清晰度完全一致——手动截图难以保证。

### 平台无关

该 Skill 不依赖特定 Agent 平台，WorkBuddy、Claude Code、Cursor 等任何支持命令行调用的 AI Agent 均可使用。

## 特性

- 通过 CSS 选择器精准定位目标元素（卡片、海报、section 等），支持多级选择器优先级回退。
- 支持设备缩放倍率，满足高 DPI 输出需求。
- 延迟等待机制（默认 1500ms），确保 Web 字体和动画渲染完成后再截图。
- 结构化 JSON 输出，便于 Agent 自动解析结果。

---

## 环境配置

强烈建议在 Python 虚拟环境（venv）中运行此脚本，以避免污染系统全局 Python 包环境：

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows 环境运行: .venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器内核
python -m playwright install chromium
```

---

## 使用方法

直接调用本skill，传入目标 HTML 文件的路径即可；或者直接执行脚本。

### 命令行参数说明

| 参数           | 说明                                           | 默认值                                               |
| -------------- | ---------------------------------------------- | ---------------------------------------------------- |
| `--html`       | **（必填）** 目标 HTML 文件的路径              |                                                      |
| `--output-dir` | 截图输出目录                                   | 视环境而定 / 默认为 HTML 文件的父目录                |
| `--selector`   | CSS 选择器列表（英文逗号分隔，按优先级排序）   | `section.poster,.poster,div.card,.card,section,body` |
| `--scale`      | 设备缩放倍率（分辨率缩放系数）                 | `1.0`                                                |
| `--delay`      | 等待网页字体或动画加载的延迟时间（单位：毫秒） | `1500`                                               |
| `--width`      | 浏览器视口宽度                                 | `2400`                                               |
| `--height`     | 浏览器视口高度                                 | `2000`                                               |

---

## 🤖 Agent 集成说明

如果脚本运行在 Agent 沙箱中：
- **依赖缺失信号**：若缺少 `playwright` 库或其浏览器二进制文件，脚本将以状态码 `1` 退出，并将清晰的安装指令输出至 stderr。
- **自动收集产出**：若检测到环境变量 `AGENT_OUTPUT_DIR` 或存在可写的 `/mnt/user-data/outputs` 目录，脚本将优先把截图保存至该位置。
- **结构化输出**：运行成功后，stdout 的最后一行会打印可解析的 JSON 字符串：
  ```json
  {"success": true, "output_dir": "/path/to/output", "files": ["/path/to/output/card-01.png"], "count": 1}
  ```
