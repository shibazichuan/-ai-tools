# AI 工具箱

两个基于 DeepSeek API 的 AI 小工具，免费在线使用。

## 🛠️ 工具列表

| 工具 | 说明 | 链接 |
|------|------|------|
| 🌐 **AI 翻译助手** | 中文 ↔ 英文双向翻译 | [打开](https://你的翻译助手链接.streamlit.app) |
| ✨ **小红书文案生成器** | 输入产品信息，AI 生成种草文案 | [打开](https://你的小红书链接.streamlit.app) |

## 🔑 使用前准备

1. 去 [platform.deepseek.com](https://platform.deepseek.com) 注册账号
2. 获取一个 API Key（新用户送 500 万 tokens 免费额度）
3. 在工具页面的侧边栏/输入框中填入你的 Key

> ⚠️ **你的 API Key 只保存在浏览器中，不会上传到任何服务器。**

## 🚀 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行翻译助手
streamlit run translator_app.py

# 运行小红书生成器
streamlit run xiaohongshu_app.py
```

## 💰 成本

- 工具本身：完全免费
- DeepSeek API：约 ¥0.002/次翻译，小红书文案约 ¥0.005/篇
- 新注册用户送 500 万 tokens ≈ 够用几千次

## 📦 部署

本项目部署在 [Streamlit Community Cloud](https://share.streamlit.io)（免费）。

---

*技术栈：Python + Streamlit + DeepSeek API*
