"""
AI 小红书文案生成器 — DeepSeek 版
==================================
输入你的产品，AI 帮你生成小红书风格的种草文案。
直接使用，无需注册。
"""

import streamlit as st
from openai import OpenAI

API_KEY = st.secrets["DEEPSEEK_API_KEY"]

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

    generate_btn = st.button("🚀 生成文案", type="primary", use_container_width=True)

with col2:
    st.subheader("✨ 生成的文案")
    result_placeholder = st.empty()

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

        with st.spinner("AI 正在创作中..."):
            try:
                client = OpenAI(
                    api_key=API_KEY,
                    base_url="https://api.deepseek.com",
                )

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个资深的小红书内容创作者，擅长写各种风格的种草文案。你的文案接地气、有感染力、转化率高。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=2048,
                )

                result = response.choices[0].message.content

                with col2:
                    st.success("✅ 生成完成！")
                    st.markdown(result)

                    if response.usage:
                        st.caption(f"消耗约 {response.usage.total_tokens} tokens")

            except Exception as e:
                st.error(f"生成失败：{str(e)}")

st.divider()
st.caption("🚀 完全免费 · 直接使用 · 无需注册 · AI 种草文案生成器 · 小红书写文助手")
