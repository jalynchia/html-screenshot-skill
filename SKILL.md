---
name: html-screenshot-skill
description: >
  使用 Playwright Chromium 渲染本地 HTML 文件并将指定 CSS 选择器对应的 DOM 节点（例如 section.poster, .card）截图输出为 PNG 图片。
  当用户想要重新生成图片、根据已有的 HTML 模板出图、修改 HTML 内容后需要重新截图时，你必须调用此技能，而不要重复执行复杂的页面生成代码。
  支持的中文触发词包括：“截图”、“出图”、“渲染一下”、“导出图片”、“帮我截个图”、“重新截图”、“网页转图片”；英文触发词包括：“re-screenshot”、“export PNGs”、“render the HTML”。
---

# html-screenshot-skill

你的任务是使用 Playwright 渲染本地 HTML 文件，并将指定的页面元素或整个页面截图保存为高分辨率的 PNG 图片。

截图的核心逻辑封装在 `scripts/screenshot.py` 脚本中，你需要通过运行该脚本来执行截图。

---

## 🛠️ 依赖环境与初始化

本 Skill 依赖 Python `playwright` 库及 Chromium 浏览器二进制文件。
在首次使用或运行前，应确保已配置好相关依赖环境：

```bash
# 推荐激活虚拟环境后运行
pip install -r requirements.txt
python -m playwright install chromium
```

---

## 📋 执行工作流 (Your Workflow)

当触发本技能后，你需要按以下步骤执行：

### 第一步：获取上下文 (Context Acquisition)
1. **核对 HTML 文件路径**：
   - 检查用户当前的输入或历史上下文中是否包含目标 HTML 文件的绝对或相对路径。
   - 如果路径缺失或不明确，你**必须向用户提问**以确认正确的 HTML 文件路径。
2. **确认截图比例/清晰度 (Scale)**：
   - 首先读取 HTML 文件或其 CSS 样式，分析并提取出目标截图元素（如 `.card`、`.poster` 等）或 `body` 的设计宽度和高度尺寸。
   - 询问用户期望的缩放比例（默认为 2.0）。**在交互时，你需要根据读取到的实际尺寸，直接计算并列出每个比例下对应的实际像素大小**。
   - 向用户提供具体清晰的选项：
     - **1.0x**（标准清晰度，显示具体的 `W × H px`）
     - **2.0x**（高清，显示具体的 `2W × 2H px`）
     - **3.0x**（超清，显示具体的 `3W × 3H px`）

### 第二步：选择目标节点与输出配置
- **输出目录**：脚本默认会在 HTML 文件的同级目录下自动创建以当前时间戳命名的 `screenshots-YYYYMMDD_HHMMSS` 文件夹，你不需要主动向用户询问输出目录，除非用户有特定要求。
- **目标选择器**：默认选择器为 `section.poster,.poster,div.card,.card,section,body`。如果用户想要截取特定的元素，你可以在执行脚本时通过 `--selector` 传入对应的 CSS 选择器。

### 第三步：调用截图脚本 (Execution)
- 找出本 Skill 所在的绝对路径，并在终端构造并执行以下 Python 命令行来运行截图脚本：

```bash
python <本Skill的绝对路径>/scripts/screenshot.py --html "path/to/index.html" --scale 2.0
```

### 第四步：解析与呈现结果
脚本成功运行后，标准输出（stdout）的最后一行将打印格式化的 JSON：

```json
{"success": true, "output_dir": "/path/to/output", "files": ["/path/to/output/card-01.png"], "count": 1}
```

你必须执行以下后处理步骤：
1. **提取文件路径**：解析输出 JSON 中的 `files` 字段，获取生成的 PNG 文件绝对路径。
2. **向用户呈现图片**：
   - 必须使用 Markdown 图片嵌入格式向用户显示截图：`![screenshot](file:///path/to/output/card-01.png)`。
   - 如果运行环境中包含专门的文件呈现工具，可以使用该工具；否则直接提供图片文件路径和 Markdown 预览，方便用户下载和查看。