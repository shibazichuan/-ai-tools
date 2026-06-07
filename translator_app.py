"""
AI 翻译助手 — Streamlit 网页版
==============================
支持中文 ↔ 英文双向翻译，DeepSeek 驱动
用户自行填写 API Key，不上传服务器
"""

import streamlit as st
from openai import OpenAI

# ============================================================
# 页面设置
# ============================================================
st.set_page_config(
    page_title="AI 翻译助手",
    page_icon="🌐",
    layout="centered",
)

st.title("🌐 AI 翻译助手")
st.caption("中文 ↔ 英文翻译 · DeepSeek 驱动 · 完全免费")

# ============================================================
# 侧边栏 — API 配置
# ============================================================
with st.sidebar:
    st.header("⚙️ 设置")

    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-...",
        help="去 platform.deepseek.com 免费注册获取。Key 只在本次浏览器会话中使用，不会上传。",
    )

    st.divider()
    st.caption("💡 DeepSeek 新用户注册送 500 万 tokens，够翻译几千次。")

# ============================================================
# 主区域
# ============================================================
direction = st.radio(
    "翻译方向",
    ["中文 → 英文", "英文 → 中文"],
    horizontal=True,
)

text = st.text_area(
    "输入文本",
    height=200,
    placeholder="在这里输入要翻译的内容...\n\n支持多行文本，一次翻译一段。",
)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    translate_btn = st.button(
        "🔄 翻译", type="primary", use_container_width=True
    )

# ============================================================
# 翻译逻辑
# ============================================================
if translate_btn:
    if not api_key:
        st.error("❌ 请先在左侧边栏填写 DeepSeek API Key")
    elif not text.strip():
        st.error("❌ 请输入要翻译的文本")
    else:
        with st.spinner("翻译中..."):
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com",
                )

                if direction == "中文 → 英文":
                    system_prompt = (
                        "你是一个专业翻译。把用户输入的中文翻译成自然流畅的英文。"
                        "只输出翻译结果，不要加任何解释、注释或额外内容。"
                        "保持原文的语气和风格。"
                    )
                else:
                    system_prompt = (
                        "你是一个专业翻译。把用户输入的英文翻译成自然流畅的中文。"
                        "只输出翻译结果，不要加任何解释、注释或额外内容。"
                        "保持原文的语气和风格。中文表达要地道。"
                    )

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    temperature=0.3,
                )

                result = response.choices[0].message.content

                st.divider()
                st.subheader("📝 翻译结果")
                st.markdown(result)

                # 显示 token 用量
                if response.usage:
                    st.caption(
                        f"消耗 {response.usage.total_tokens} tokens · "
                        f"约 {response.usage.total_tokens / 1_000_000 * 2:.4f} 元"
                    )

            except Exception as e:
                st.error(f"翻译失败：{str(e)}")
                st.info(
                    "常见原因：\n"
                    "1) API Key 填错了（去 platform.deepseek.com 检查）\n"
                    "2) 网络不通（检查科学上网或网络连接）\n"
                    "3) 账号余额不足（DeepSeek 注册送 500 万 tokens 免费额度，一般够用）"
                )

# 底部
st.divider()
st.caption("🔒 你的 API Key 只保存在浏览器中，不会上传到任何服务器。")
