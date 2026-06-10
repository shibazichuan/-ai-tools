# AI Tool Suite | AI 工具箱

[![GitHub stars](https://img.shields.io/github/stars/shibazichuan/-ai-tools?style=social)](https://github.com/shibazichuan/-ai-tools)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-667eea?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

A collection of free, no-registration AI tools powered by **DeepSeek**.
Includes a Chinese-English translator and a Xiaohongshu copywriting generator.

DeepSeek 驱动的免费 AI 小工具集合。**无需注册，打开即用，完全免费。**

---

## 🛠️ 工具列表

| 工具 | 说明 | 亮点 | 链接 |
|------|------|------|------|
| 🌐 **AI 翻译助手** | 中英双向翻译，地道自然 | 一键互换 · 历史记录 · 即抄即用 | [打开](https://huivet62pgekb3negae9nw.streamlit.app/) |
| ✨ **小红书文案生成器** | AI 种草文案，多种风格 | 一次3版本 · 5种风格 · 历史记录 · 一键复制 | [打开](https://3hffuxzfc8kwqpjdjtoizx.streamlit.app/) |

> 🏠 所有工具汇总：**[zhixumentu.com](https://zhixumentu.com)**

---

## 🎨 功能亮点

### 🌐 AI 翻译助手
- 🔄 中英双向翻译，输出自然流畅
- ⇆ 一键互换：译文秒变输入，方向自动翻转
- 📜 自动保存最近 5 条翻译历史
- 📋 一键复制翻译结果
- 🎰 趣味 loading 文案

### ✨ 小红书文案生成器
- 📝 输入产品信息，AI 生成种草文案
- 🔢 一次生成 3 个不同角度版本（实用体验 / 性价比 / 生活方式）
- 🎨 5 种风格 × 3 种篇幅
- 🎚️ 可调节创意度
- 📜 自动保存最近 5 条历史
- 📋 一键复制

---

## 🚀 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 DeepSeek API Key
echo 'DEEPSEEK_API_KEY = "你的Key"' > .streamlit/secrets.toml

# 运行
streamlit run translator.py     # AI 翻译助手
streamlit run xiaohongshu.py    # 小红书文案生成器
```

---

## 🔑 API 说明

- 工具面向用户**免配置**，Key 通过 Streamlit Secrets 在后台注入
- API：DeepSeek（`api.deepseek.com`），模型 `deepseek-chat`
- 新用户去 [platform.deepseek.com](https://platform.deepseek.com) 注册送 500 万 tokens
- 成本极低：翻译约 ¥0.002/次，小红书文案约 ¥0.005/篇

---

## 📦 部署

部署在 [Streamlit Community Cloud](https://share.streamlit.io)（免费）。`main` 分支 push 后自动更新。

主页 `zhixumentu.com` 通过 GitHub Pages（`docs/`）托管，阿里云 DNS。

---

*技术栈：Python + Streamlit + DeepSeek API + GitHub Pages*
