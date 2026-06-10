"""
AI 翻译助手 — Streamlit 网页版
==============================
中文 ↔ 英文双向翻译 · DeepSeek 驱动
直接使用，无需注册
"""

import streamlit as st
from openai import OpenAI
import random

API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# 有趣的 loading 文案
LOADING_MSGS = [
    "🤔 AI 正在思考...",
    "📝 正在组织语言...",
    "✨ 魔法施展中...",
    "🔍 翻阅词典中...",
    "💡 寻找最佳表达...",
    "🎨 润色措辞中...",
    "⏳ 马上就好...",
    "🌍 跨越语言障碍...",
]

# ============================================================
# 页面设置
# ============================================================
st.set_page_config(
    page_title="AI 翻译助手 - 中英双向翻译 | 免费在线翻译工具",
    page_icon="🌐",
    layout="centered",
)

# SEO 元标签
st.markdown(
    """
    <meta name="description" content="免费在线 AI 翻译助手，中文英文双向翻译，DeepSeek 驱动。支持多行文本，翻译自然流畅，不用注册直接使用。">
    <meta name="keywords" content="AI翻译,中英翻译,在线翻译,免费翻译,DeepSeek翻译,英语翻译,中文翻译英文">
    """,
    unsafe_allow_html=True,
)

st.title("🌐 AI 翻译助手")
st.caption("中文 ↔ 英文翻译 · 直接使用，完全免费")

# ============================================================
# 初始化 session state
# ============================================================
if "translator_history" not in st.session_state:
    st.session_state.translator_history = []
if "last_translation" not in st.session_state:
    st.session_state.last_translation = ""

# ============================================================
# 主区域
# ============================================================
direction = st.radio(
    "翻译方向",
    ["中文 → 英文", "英文 → 中文"],
    horizontal=True,
    key="direction",
)

text = st.text_area(
    "输入文本",
    height=200,
    key="translator_input",
    placeholder="在这里输入要翻译的内容...\n\n支持多行文本，一次翻译一段。",
)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    translate_btn = st.button(
        "🔄 翻译", type="primary", use_container_width=True
    )
with col2:
    swap_btn = st.button(
        "⇆ 互换",
        use_container_width=True,
        disabled=not bool(st.session_state.last_translation),
        help="将上次翻译结果设为输入，并切换翻译方向",
    )

# 互换逻辑
if swap_btn and st.session_state.last_translation:
    st.session_state.translator_input = st.session_state.last_translation
    st.session_state.direction = (
        "英文 → 中文" if direction == "中文 → 英文" else "中文 → 英文"
    )
    st.rerun()

# ============================================================
# 翻译逻辑
# ============================================================
if translate_btn:
    if not text.strip():
        st.error("❌ 请输入要翻译的文本")
    else:
        with st.spinner(random.choice(LOADING_MSGS)):
            try:
                client = OpenAI(
                    api_key=API_KEY,
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
                tokens = response.usage.total_tokens if response.usage else 0

                # 存储结果（用于互换）
                st.session_state.last_translation = result

                # 存入历史
                st.session_state.translator_history.insert(
                    0,
                    {
                        "source": text,
                        "result": result,
                        "direction": direction,
                        "tokens": tokens,
                    },
                )
                # 只保留最近 5 条
                st.session_state.translator_history = (
                    st.session_state.translator_history[:5]
                )

                # 显示结果
                st.divider()
                st.subheader("📝 翻译结果")
                st.markdown(result)

                # 一键复制
                with st.expander("📋 点击复制结果"):
                    st.code(result, language=None)

                st.caption(f"消耗 {tokens} tokens")

            except Exception as e:
                st.error(f"翻译失败：{str(e)}")

# ============================================================
# 历史记录
# ============================================================
if st.session_state.translator_history:
    st.divider()
    with st.expander(
        f"📜 历史记录（最近 {len(st.session_state.translator_history)} 条）"
    ):
        for i, entry in enumerate(st.session_state.translator_history):
            src_preview = (
                entry["source"][:60]
                + ("..." if len(entry["source"]) > 60 else "")
            )
            res_preview = (
                entry["result"][:80]
                + ("..." if len(entry["result"]) > 80 else "")
            )
            st.caption(
                f"#{i+1}  [{entry['direction']}] · {entry['tokens']} tokens"
            )
            st.text(src_preview)
            st.markdown(f"→ *{res_preview}*")
            if i < len(st.session_state.translator_history) - 1:
                st.divider()

st.divider()
st.caption(
    "🚀 完全免费 · 直接使用 · 无需注册 · AI 在线翻译工具 · 中英互译"
)
