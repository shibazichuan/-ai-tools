"""
AI 翻译助手 — Streamlit 网页版
==============================
中文 ↔ 英文双向翻译 · DeepSeek 驱动
直接使用，无需注册
"""

import streamlit as st
from openai import (
    OpenAI,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
)
import random

API_KEY = st.secrets["DEEPSEEK_API_KEY"]

GITHUB_ISSUES = "https://github.com/shibazichuan/-ai-tools/issues"
HOME_URL = "https://zhixumentu.com"

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

# ============================================================
# 次数限制 — 必须在所有业务逻辑之前
# ============================================================
from st_usage_limiter import init_tool

limiter = init_tool("translator", free_limit=5)

# SEO 元标签
st.markdown(
    """
    <meta name="description" content="免费在线 AI 翻译助手，中文英文双向翻译，DeepSeek 驱动。支持多行文本，翻译自然流畅，不用注册直接使用。">
    <meta name="keywords" content="AI翻译,中英翻译,在线翻译,免费翻译,DeepSeek翻译,英语翻译,中文翻译英文">
    """,
    unsafe_allow_html=True,
)

st.title("🌐 AI 翻译助手")
st.caption("中文 ↔ 英文翻译 · 每日免费5次")

# 剩余次数指示器（仅显示，不阻止渲染 — check_and_consume 在翻译按钮点击时调用）
_rem = limiter.remaining()
_rem_color = "#ef4444" if _rem <= 1 else "#667eea"
_rem_bg = "#fef2f2" if _rem <= 1 else "#f0f4ff"
st.markdown(f"""
<div style="display:flex;align-items:center;gap:6px;margin-bottom:12px;
            padding:5px 14px;border-radius:20px;background:{_rem_bg};
            font-size:0.82rem;width:fit-content">
    <span style="display:inline-flex;align-items:center;justify-content:center;
                 min-width:20px;height:20px;border-radius:50%;font-weight:700;font-size:0.72rem;
                 background:{_rem_color};color:#fff;padding:0 6px;
                 {'animation: pulse 0.6s infinite alternate;' if _rem <= 1 else ''}">
        {_rem if _rem != float('inf') else '∞'}
    </span>
    次剩余 · 每日免费 {limiter.free_limit} 次 · 用完可升级会员
</div>
<style>
@keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.12); }} }}
</style>
""", unsafe_allow_html=True)

# 品牌标签
col_t1, col_t2, col_t3, col_t4 = st.columns([0.7, 0.7, 1, 4])
with col_t1:
    st.markdown(
        '<span style="background:linear-gradient(135deg,#22c55e,#16a34a);'
        'color:#fff;padding:3px 14px;border-radius:100px;font-size:0.78rem;'
        'font-weight:700;white-space:nowrap;">永久免费</span>',
        unsafe_allow_html=True,
    )
with col_t2:
    st.markdown(
        '<span style="background:linear-gradient(135deg,#f59e0b,#d97706);'
        'color:#fff;padding:3px 14px;border-radius:100px;font-size:0.78rem;'
        'font-weight:700;white-space:nowrap;">无需注册</span>',
        unsafe_allow_html=True,
    )
with col_t3:
    st.markdown(
        '<span style="background:linear-gradient(135deg,#667eea,#764ba2);'
        'color:#fff;padding:3px 14px;border-radius:100px;font-size:0.78rem;'
        'font-weight:700;white-space:nowrap;">DeepSeek 驱动</span>',
        unsafe_allow_html=True,
    )

# ============================================================
# 侧边栏 — 工具箱导航
# ============================================================
with st.sidebar:
    st.markdown("### 🚀 AI 工具箱")

    # 当前工具高亮
    st.markdown(
        '<div style="background:linear-gradient(135deg,#667eea,#764ba2);'
        'color:#fff;padding:6px 12px;border-radius:8px;font-size:0.85rem;'
        'font-weight:600;margin-bottom:4px;">🌐 翻译助手'
        '<span style="font-size:0.7rem;opacity:0.85;"> · 当前</span></div>',
        unsafe_allow_html=True,
    )

    # 另一个工具链接
    st.markdown(
        '<a href="https://3hffuxzfc8kwqpjdjtoizx.streamlit.app/" '
        'style="display:block;padding:6px 12px;color:inherit;'
        'text-decoration:none;border-radius:8px;font-size:0.85rem;" '
        'target="_blank" rel="noopener">✨ 小红书文案生成器</a>',
        unsafe_allow_html=True,
    )

    st.divider()

    # 主页链接
    st.markdown(
        f'<a href="{HOME_URL}" '
        'style="display:block;padding:6px 12px;color:#667eea;'
        'text-decoration:none;border-radius:8px;font-size:0.85rem;'
        'font-weight:500;">🏠 回到工具箱首页</a>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("by shibazichuan\n完全免费 · 无需注册")

    limiter.render_stats()

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
    _no_remaining = limiter.remaining() == 0
    translate_btn = st.button(
        "🔄 翻译" if not _no_remaining else "🚫 今日次数已用完",
        type="primary",
        use_container_width=True,
        disabled=_no_remaining,
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
    elif not limiter.check_and_consume():
        st.stop()  # 超出限制，弹窗已自动显示
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
                    timeout=30,
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

            except AuthenticationError:
                st.error("🔑 API 密钥配置有误，请联系站长修复。")
            except RateLimitError:
                st.error("⏳ 当前使用人数较多，请稍后再试。")
            except (APIConnectionError, APITimeoutError):
                st.error("🌐 网络连接失败，请检查网络后重试。")
            except Exception:
                st.error(
                    "⚠️ 服务暂时不可用，请稍后重试。"
                    f"如持续出现请通过 [GitHub Issues]({GITHUB_ISSUES}) 反馈。"
                )

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
    f"🚀 by **shibazichuan** · [🏠 工具箱首页]({HOME_URL}) · "
    "完全免费 · 无需注册"
)
st.caption("🔒 我们不保存您的任何输入内容")
