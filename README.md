# AI 工具箱

两个基于 DeepSeek API 的 AI 小工具，免费在线使用，无需注册。

## 🛠️ 工具列表

| 工具 | 说明 | 链接 |
|------|------|------|
| 🌐 **AI 翻译助手** | 中文 ↔ 英文双向翻译 | [打开](https://huivet62pgekb3negae9nw.streamlit.app/) |
| ✨ **小红书文案生成器** | 输入产品信息，AI 生成种草文案 | [打开](https://3hffuxzfc8kwqpjdjtoizx.streamlit.app/) |

> 🚀 **打开即用，无需注册，完全免费。** API Key 已在后台配置好，你只管用。

---

## 🚀 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key（二选一）
# 方式一：创建 .streamlit/secrets.toml
echo 'DEEPSEEK_API_KEY = "你的Key"' > .streamlit/secrets.toml
# 方式二：直接设置环境变量

# 运行翻译助手
streamlit run translator.py

# 运行小红书生成器
streamlit run xiaohongshu.py
```

---

## 🔑 API 说明

- 工具面向用户**免配置**，Key 通过 Streamlit Secrets 在后台注入
- 使用的 API：DeepSeek（`api.deepseek.com`），模型 `deepseek-chat`
- 新用户去 [platform.deepseek.com](https://platform.deepseek.com) 注册送 500 万 tokens
- 成本极低：翻译约 ¥0.002/次，小红书文案约 ¥0.005/篇

---

## 📦 部署

本项目部署在 [Streamlit Community Cloud](https://share.streamlit.io)（免费）。

---

*技术栈：Python + Streamlit + DeepSeek API*
