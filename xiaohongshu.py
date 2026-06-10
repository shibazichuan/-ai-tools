"""
AI 小红书文案生成器 — DeepSeek 版
==================================
输入你的产品，AI 帮你生成小红书风格的种草文案。
直接使用，无需注册。
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
TRANSLATOR_URL = "https://huivet62pgekb3negae9nw.streamlit.app/"

# 有趣的 loading 文案
LOADING_MSGS = [
    "🤔 AI 正在构思创意...",
    "✍️ 正在奋笔疾书...",
    "✨ 灵感迸发中...",
    "🎨 精心排版中...",
    "💡 提炼卖点中...",
    "🔥 文案即将出炉...",
    "📝 打磨每一个字...",
    "🌟 注入种草魔法...",
]

# 页面设置
st.set_page_config(
    page_title="小红书文案生成器 - AI种草文案 | 免费在线写作工具",
    page_icon="✨",
    layout="wide",
)

# SEO 元标签
st.markdown(
    """
    <meta name="description" content="免费 AI 小红书文案生成器，输入产品信息即可生成种草文案。支持5种风格、3种篇幅，DeepSeek 驱动，不用注册直接使用。">
    <meta name="keywords" content="小红书文案,种草文案,AI写文案,小红书生成器,DeepSeek文案,文案生成器,免费文案工具">
    """,
    unsafe_allow_html=True,
)

st.title("✨ AI 小红书文案生成器")
st.caption("输入你的产品，AI 帮你写一篇种草文案。DeepSeek 驱动，完全免费。")

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
# 初始化 session state
# ============================================================
if "xhs_history" not in st.session_state:
    st.session_state.xhs_history = []

# ============================================================
# 侧边栏 — 风格设置
# ============================================================
with st.sidebar:
    st.header("🎨 文案设置")

    style = st.selectbox(
        "文案风格",
        ["种草推荐", "测评对比", "干货分享", "日常Vlog", "教程攻略"],
    )

    st.divider()

    gen_count = st.radio(
        "生成数量",
        [1, 3],
        horizontal=True,
        index=1,
        help="一次生成 1 个或 3 个不同角度的版本，默认 3 个",
    )

    with st.expander("高级设置"):
        temperature = st.slider(
            "创意度",
            min_value=0.0,
            max_value=1.5,
            value=0.8,
            step=0.1,
            help="越高创意越大胆，越低越保守稳定",
        )
        length = st.selectbox(
            "篇幅",
            ["短文案（~200字）", "中文案（~500字）", "长文案（~800字）"],
            index=0,
        )

    st.divider()
    st.caption("🚀 DeepSeek 驱动 · 完全免费")

    st.divider()
    st.markdown("### 🚀 AI 工具箱")

    # 当前工具高亮
    st.markdown(
        '<div style="background:linear-gradient(135deg,#667eea,#764ba2);'
        'color:#fff;padding:6px 12px;border-radius:8px;font-size:0.85rem;'
        'font-weight:600;margin-bottom:4px;">✨ 小红书文案生成器'
        '<span style="font-size:0.7rem;opacity:0.85;"> · 当前</span></div>',
        unsafe_allow_html=True,
    )

    # 另一个工具链接
    st.markdown(
        f'<a href="{TRANSLATOR_URL}" '
        'style="display:block;padding:6px 12px;color:inherit;'
        'text-decoration:none;border-radius:8px;font-size:0.85rem;" '
        'target="_blank" rel="noopener">🌐 AI 翻译助手</a>',
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
# 主区域
# ============================================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 输入产品信息")

    product_name = st.text_input(
        "产品名称",
        placeholder="比如：某某精华液、某品牌蓝牙耳机...",
    )

    product_desc = st.text_area(
        "产品描述（越详细越好）",
        placeholder="描述你的产品特点、优势、适合谁用...\n\n比如：\n- 含3%烟酰胺，美白提亮\n- 质地轻薄不粘腻\n- 适合油皮和混油皮\n- 价格亲民，学生党友好",
        height=200,
    )

    target_user = st.text_input(
        "目标用户（可选）",
        placeholder="比如：学生党、上班族、宝妈...",
    )

    generate_btn = st.button(
        "🚀 生成文案", type="primary", use_container_width=True
    )

with col2:
    st.subheader("✨ 生成的文案")

# ============================================================
# 生成逻辑
# ============================================================
if generate_btn:
    if not product_name:
        st.error("请至少输入产品名称")
    else:
        length_map = {
            "短文案（~200字）": "200字左右",
            "中文案（~500字）": "500字左右",
            "长文案（~800字）": "800字左右",
        }

        prompt = f"""请为以下产品写一篇小红书风格的{style}文案。

产品名称：{product_name}
产品描述：{product_desc}
目标用户：{target_user or "普通消费者"}
篇幅要求：{length_map[length]}

小红书文案写作要点：
1. 开头用吸引眼球的标题（带emoji）
2. 语气亲切自然，像朋友分享
3. 适当使用 emoji，但不要过度
4. 分段清晰，用空行隔开不同要点
5. 结尾加上 3-5 个相关 hashtag
6. 如果是种草风格，要说清楚为什么值得买
7. 适当使用网络热词和口语化表达"""

        if gen_count == 3:
            prompt += """

请生成 3 个不同角度的版本，用 "---VERSION---" 作为分隔符。
3 个版本要求：
- 版本一：主打实用体验，侧重真实使用感受
- 版本二：主打性价比/优惠，侧重购买理由
- 版本三：主打情感共鸣/生活方式，侧重场景化描述
确保 3 个版本有明显差异，各有特色，不要雷同。"""

        with st.spinner(random.choice(LOADING_MSGS)):
            try:
                client = OpenAI(
                    api_key=API_KEY,
                    base_url="https://api.deepseek.com",
                )

                max_tokens = 4096 if gen_count == 3 else 2048

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "你是一个资深的小红书内容创作者，擅长写各种风格的种草文案。"
                                "你的文案接地气、有感染力、转化率高。"
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=30,
                )

                result = response.choices[0].message.content
                tokens = response.usage.total_tokens if response.usage else 0

                # 存入历史
                st.session_state.xhs_history.insert(
                    0,
                    {
                        "product": product_name,
                        "style": style,
                        "result": result,
                        "gen_count": gen_count,
                        "tokens": tokens,
                    },
                )
                st.session_state.xhs_history = (
                    st.session_state.xhs_history[:5]
                )

                with col2:
                    st.success(f"✅ 生成完成！消耗 {tokens} tokens")

                    if gen_count == 3:
                        # 按分隔符拆分版本
                        versions = [
                            v.strip()
                            for v in result.split("---VERSION---")
                            if v.strip()
                        ]

                        if len(versions) == 3:
                            tabs = st.tabs(
                                ["💚 实用体验版", "💰 性价比版", "✨ 生活方式版"]
                            )
                            for tab, version in zip(tabs, versions):
                                with tab:
                                    st.markdown(version)
                                    with st.expander("📋 复制此版本"):
                                        st.code(version, language=None)
                        else:
                            # 解析失败，显示完整结果
                            st.warning(
                                f"版本拆分略有偏差（识别到 {len(versions)} 段），"
                                "显示完整结果："
                            )
                            st.markdown(result)
                            with st.expander("📋 复制文案"):
                                st.code(result, language=None)
                    else:
                        st.markdown(result)
                        with st.expander("📋 复制文案"):
                            st.code(result, language=None)

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
if st.session_state.xhs_history:
    st.divider()
    with st.expander(
        f"📜 历史记录（最近 {len(st.session_state.xhs_history)} 条）"
    ):
        for i, entry in enumerate(st.session_state.xhs_history):
            ver_label = (
                "3版本" if entry["gen_count"] == 3 else "单版本"
            )
            st.caption(
                f"#{i+1}  [{entry['style']}] {entry['product']}"
                f" · {entry['tokens']} tokens · {ver_label}"
            )
            preview = (
                entry["result"][:100]
                + ("..." if len(entry["result"]) > 100 else "")
            )
            st.text(preview)
            if i < len(st.session_state.xhs_history) - 1:
                st.divider()

st.divider()
st.caption(
    f"🚀 by **shibazichuan** · [🏠 工具箱首页]({HOME_URL}) · "
    "完全免费 · 无需注册"
)
st.caption("🔒 我们不保存您的任何输入内容")
