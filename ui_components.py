"""
AI 工具箱 — 共享 UI 组件
========================
提取 translator.py 和 xiaohongshu.py 中的重复代码。

用法：
    from ui_components import render_brand_tags, render_sidebar_nav, render_footer, show_api_error
"""

import streamlit as st

GITHUB_ISSUES = "https://github.com/shibazichuan/-ai-tools/issues"
HOME_URL = "https://zhixumentu.com"
TRANSLATOR_URL = "https://huivet62pgekb3negae9nw.streamlit.app/"
XHS_URL = "https://3hffuxzfc8kwqpjdjtoizx.streamlit.app/"

# 工具元信息
_TOOLS = {
    "translator": {
        "emoji": "🌐", "name": "AI 翻译助手",
        "other": "xhs_writer",
    },
    "xhs_writer": {
        "emoji": "✨", "name": "小红书文案生成器",
        "other": "translator",
    },
}
_OTHER_URL = {"translator": XHS_URL, "xhs_writer": TRANSLATOR_URL}
_OTHER_EMOJI = {"translator": "✨", "xhs_writer": "🌐"}
_OTHER_NAME = {"translator": "小红书文案生成器", "xhs_writer": "AI 翻译助手"}


# ============================================================
# 品牌标签
# ============================================================
def render_brand_tags():
    """永久免费 / 无需注册 / DeepSeek 驱动"""
    c1, c2, c3, c4 = st.columns([0.7, 0.7, 1, 4])
    tags = [
        ("永久免费", "linear-gradient(135deg,#22c55e,#16a34a)"),
        ("无需注册", "linear-gradient(135deg,#f59e0b,#d97706)"),
        ("DeepSeek 驱动", "linear-gradient(135deg,#667eea,#764ba2)"),
    ]
    for col, (text, gradient) in zip([c1, c2, c3], tags):
        with col:
            st.markdown(
                f'<span style="background:{gradient};color:#fff;padding:3px 14px;'
                f'border-radius:100px;font-size:0.78rem;font-weight:700;'
                f'white-space:nowrap;">{text}</span>',
                unsafe_allow_html=True,
            )


# ============================================================
# 侧边栏工具箱导航
# ============================================================
def render_sidebar_nav(current_tool: str):
    """渲染侧边栏：当前工具高亮 + 另一工具链接 + 主页链接"""
    cfg = _TOOLS[current_tool]
    other = cfg["other"]

    st.markdown("### 🚀 AI 工具箱")

    # 当前工具高亮
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);'
        f'color:#fff;padding:6px 12px;border-radius:8px;font-size:0.85rem;'
        f'font-weight:600;margin-bottom:4px;">{cfg["emoji"]} {cfg["name"]}'
        f'<span style="font-size:0.7rem;opacity:0.85;"> · 当前</span></div>',
        unsafe_allow_html=True,
    )

    # 另一个工具链接
    st.markdown(
        f'<a href="{_OTHER_URL[other]}" '
        'style="display:block;padding:6px 12px;color:inherit;'
        'text-decoration:none;border-radius:8px;font-size:0.85rem;" '
        f'target="_blank" rel="noopener">{_OTHER_EMOJI[other]} {_OTHER_NAME[other]}</a>',
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


# ============================================================
# 页脚
# ============================================================
def render_footer():
    """统一页脚"""
    st.divider()
    st.caption(
        f"🚀 by **shibazichuan** · [🏠 工具箱首页]({HOME_URL}) · "
        "完全免费 · 无需注册"
    )
    st.caption("🔒 我们不保存您的任何输入内容")


# ============================================================
# API 错误处理
# ============================================================
def show_api_error(e) -> bool:
    """显示 API 错误的用户友好提示。返回 True 表示已处理。"""
    from openai import (
        AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError,
    )
    if isinstance(e, AuthenticationError):
        st.error("🔑 API 密钥配置有误，请联系站长修复。")
    elif isinstance(e, RateLimitError):
        st.error("⏳ 当前使用人数较多，请稍后再试。")
    elif isinstance(e, (APIConnectionError, APITimeoutError)):
        st.error("🌐 网络连接失败，请检查网络后重试。")
    else:
        st.error(
            "⚠️ 服务暂时不可用，请稍后重试。"
            f"如持续出现请通过 [GitHub Issues]({GITHUB_ISSUES}) 反馈。"
        )
    return True
