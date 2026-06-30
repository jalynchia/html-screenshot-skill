---
name: "html-screenshot-skill"
description: "一个将 HTML 截图为高清 PNG 文件的 Skill，可以嵌入 `guizang-social-card-skill` 工作流，用于生成公众号封面、海报、卡片等设计图。"
version: 1.0.0
Update date: 2026-06-28
---


## 背景

我经常使用 `guizang-social-card-skill` 生成公众号封面图，但生成后常需要微调文案。如果每次修改 HTML 后都重新跑一遍完整的生成流程，既耗时也消耗大量 Token。这个 Skill 就是为了解决这个环节的效率问题——将「修改文案」与「重新出图」解耦，这个 skill 只负责截图这一子任务。

## 定位

这并非一个通用的截图工具，而是一个嵌入 `guizang-social-card-skill` 生成封面图工作流的自动化截图工具，专用于「已完成的 HTML → 调整 HTML 细节 → 截图」。

### 适用场景

- **工作流中间环节**：你已通过 `guizang-social-card-skill` 或其他功能类似的 Skill 生成了 HTML 设计稿（如海报、卡片、公众号封面等），需要修改局部文案后重新出图，而不想从头重跑整个生成流程。
- **精确复现**：需要确保每张输出图尺寸、比例、清晰度完全一致，但手动截图难以保证时。

### 平台无关

该 Skill 不依赖特定 Agent 平台，WorkBuddy、Claude Code、Cursor、Antigravity 等任何支持 Skill 调用的 AI Agent 均可使用。

## 特性

- 通过 CSS 选择器精准定位目标元素（卡片、海报、section 等）；
- 支持设备缩放倍率，满足高 DPI 输出需求；
- 延迟等待机制（默认 1500ms），确保 Web 字体和动画渲染完成后再截图；
- 结构化 JSON 输出，便于 Agent 自动解析结果。

---

## 使用方法

直接调用本 Skill，传入目标 HTML 文件的路径即可。

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
