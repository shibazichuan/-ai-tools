# P0/P1 专业度提升 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 统一品牌配色、工具间互导流、分类错误提示、隐私说明、社交分享标签、README 优化

**Architecture:** 新建 `.streamlit/config.toml` 统一 Streamlit 主题色；改造两个 py 文件的侧边栏/页脚/错误处理；`docs/index.html` 加 OG 标签和隐私说明；`README.md` 重组

**Tech Stack:** Python + Streamlit + OpenAI SDK + 静态 HTML/CSS + Pillow (OG 图片)

---

### Task 1: 新建 `.streamlit/config.toml`

**Files:**
- Create: `.streamlit/config.toml`

- [ ] **Step 1: 写入配置文件**

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#f8f9fc"
secondaryBackgroundColor = "#eef0f6"
textColor = "#1a1a2e"
font = "sans serif"

[browser]
gatherUsageStats = false
```

- [ ] **Step 2: 验证语法**

Run: `python -c "import toml; toml.load('.streamlit/config.toml'); print('OK')"`
Expected: `OK`

- [ ] **Step 3: 添加配置文件到 .gitignore 例外（确保被追踪）**

确认 `.streamlit/config.toml` 不在 `.gitignore` 的 `.streamlit/` 通配后，确保它被 git 追踪：
Run: `git add --dry-run .streamlit/config.toml 2>&1`
Expected: 文件被正常追踪（无 ignored 警告）

- [ ] **Step 4: Commit**

```bash
git add .streamlit/config.toml
git commit -m "feat: 添加 Streamlit 品牌主题配置，统一紫蓝渐变配色

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: 翻译助手 — 侧边栏 + 标签 + 错误处理 + 隐私 + 页脚

**Files:**
- Modify: `translator.py` (全文多处改动)

- [ ] **Step 1: 替换 import 区块，添加 openai 异常类型导入**

当前第 8-12 行：
```python
import streamlit as st
from openai import OpenAI
import random

API_KEY = st.secrets["DEEPSEEK_API_KEY"]
```

替换为：
```python
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
```

- [ ] **Step 2: 在标题下方添加品牌标签**

当前第 44-45 行：
```python
st.title("🌐 AI 翻译助手")
st.caption("中文 ↔ 英文翻译 · 直接使用，完全免费")
```

替换为：
```python
st.title("🌐 AI 翻译助手")
st.caption("中文 ↔ 英文翻译 · 直接使用，完全免费")

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
```

- [ ] **Step 3: 新增侧边栏（翻译助手原本无侧边栏）**

在第 45 行之后（品牌标签之后、`# 初始化 session state` 之前）插入：

```python
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
        f'<a href="https://3hffuxzfc8kwqpjdjtoizx.streamlit.app/" '
        'style="display:block;padding:6px 12px;color:{st.get_option("theme.textColor")};'
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
```

注：`st.get_option("theme.textColor")` 在 Streamlit 1.28+ 返回当前主题文本色，可保证暗色模式兼容。若该 API 不可用，降级为固定颜色 `#1a1a2e`。

- [ ] **Step 4: 替换错误处理（第 161-162 行）**

当前：
```python
            except Exception as e:
                st.error(f"翻译失败：{str(e)}")
```

替换为：
```python
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
```

- [ ] **Step 5: API 调用加 timeout**

在第 120-127 行的 `client.chat.completions.create()` 调用中添加 `timeout=30`：

```python
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    temperature=0.3,
                    timeout=30,
                )
```

- [ ] **Step 6: 替换页脚（第 189-192 行）**

当前：
```python
st.divider()
st.caption(
    "🚀 完全免费 · 直接使用 · 无需注册 · AI 在线翻译工具 · 中英互译"
)
```

替换为：
```python
st.divider()
st.caption(
    f"🚀 by **shibazichuan** · [🏠 工具箱首页]({HOME_URL}) · "
    "完全免费 · 无需注册"
)
st.caption("🔒 我们不保存您的任何输入内容")
```

- [ ] **Step 7: 验证语法**

Run: `python -m py_compile translator.py`
Expected: 无输出（编译成功）

- [ ] **Step 8: Commit**

```bash
git add translator.py
git commit -m "feat(translator): 侧边栏导航 + 品牌标签 + 分类错误处理 + 隐私说明

- 新增侧边栏：工具箱导航 + 工具互链 + 主页入口
- 标题下方添加免费/无需注册/DeepSeek 品牌标签
- 错误分4类提示 + GitHub Issues 反馈引导
- API 调用添加 timeout=30
- 统一页脚含署名和隐私说明

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: 小红书生成器 — 侧边栏导航 + 标签 + 错误处理 + 隐私 + 页脚 + Tab 标签优化

**Files:**
- Modify: `xiaohongshu.py` (全文多处改动)

- [ ] **Step 1: 替换 import 区块**

当前第 8-12 行：
```python
import streamlit as st
from openai import OpenAI
import random

API_KEY = st.secrets["DEEPSEEK_API_KEY"]
```

替换为：
```python
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
```

- [ ] **Step 2: 在标题下方添加品牌标签**

当前第 42-43 行：
```python
st.title("✨ AI 小红书文案生成器")
st.caption("输入你的产品，AI 帮你写一篇种草文案。DeepSeek 驱动，完全免费。")
```

替换为：
```python
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
```

- [ ] **Step 3: 在现有侧边栏底部添加导航区块**

当前第 88 行之后（`st.caption("🚀 DeepSeek 驱动 · 完全免费")` 之后）插入：

```python

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
        'style="display:block;padding:6px 12px;color:{st.get_option("theme.textColor")};'
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
```

- [ ] **Step 4: 替换错误处理（第 237-238 行）**

当前：
```python
            except Exception as e:
                st.error(f"生成失败：{str(e)}")
```

替换为：
```python
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
```

- [ ] **Step 5: API 调用加 timeout**

在第 169-183 行的 `client.chat.completions.create()` 调用中添加 `timeout=30`：

```python
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
```

- [ ] **Step 6: Tab 标签从 "版本一/二/三" 改为语义化标签**

当前第 215-216 行：
```python
                            tabs = st.tabs(
                                ["🔢 版本一", "🔢 版本二", "🔢 版本三"]
                            )
```

替换为：
```python
                            tabs = st.tabs(
                                ["💚 实用体验版", "💰 性价比版", "✨ 生活方式版"]
                            )
```

- [ ] **Step 7: 替换页脚（第 264-267 行）**

当前：
```python
st.divider()
st.caption(
    "🚀 完全免费 · 直接使用 · 无需注册 · AI 种草文案生成器 · 小红书写文助手"
)
```

替换为：
```python
st.divider()
st.caption(
    f"🚀 by **shibazichuan** · [🏠 工具箱首页]({HOME_URL}) · "
    "完全免费 · 无需注册"
)
st.caption("🔒 我们不保存您的任何输入内容")
```

- [ ] **Step 8: 验证语法**

Run: `python -m py_compile xiaohongshu.py`
Expected: 无输出（编译成功）

- [ ] **Step 9: Commit**

```bash
git add xiaohongshu.py
git commit -m "feat(xiaohongshu): 侧边栏导航 + 品牌标签 + 分类错误处理 + 隐私说明 + Tab语义化

- 侧边栏底部新增工具箱导航 + 工具互链 + 主页入口
- 标题下方添加免费/无需注册/DeepSeek 品牌标签
- 错误分4类提示 + GitHub Issues 反馈引导
- API 调用添加 timeout=30
- Tab标签改为语义化描述（实用体验/性价比/生活方式）
- 统一页脚含署名和隐私说明

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: 生成 OG 社交分享图片

**Files:**
- Create: `docs/og-image.png`

- [ ] **Step 1: 安装 Pillow（如未安装）**

Run: `python -c "from PIL import Image; print('Pillow OK')" 2>&1 || pip install Pillow`
Expected: `Pillow OK`

- [ ] **Step 2: 运行图片生成脚本**

在内联 Python 中生成 1200×630 的 OG 图片：

```bash
python -c "
from PIL import Image, ImageDraw, ImageFont
import os

w, h = 1200, 630
img = Image.new('RGBA', (w, h))
draw = ImageDraw.Draw(img)

# 紫蓝渐变背景
for y in range(h):
    t = y / h
    r = int(102 + t * (118 - 102))   # 667eea -> 764ba2
    g = int(126 + t * (75 - 126))
    b = int(234 + t * (162 - 234))
    draw.line([(0, y), (w, y)], fill=(r, g, b))

# 白色半透明装饰圆
for cx, cy, r in [(200, 200, 180), (1000, 450, 240)]:
    for dy in range(-r, r+1):
        dx = int((r**2 - dy**2)**0.5)
        x0 = cx - dx
        x1 = cx + dx
        yy = cy + dy
        if 0 <= yy < h:
            for x in range(max(0,x0), min(w,x1+1)):
                alpha = min(15, int(15 * (1 - abs(dy)/r)))
                orig = img.getpixel((x, yy))
                img.putpixel((x, yy), (
                    min(255, orig[0] + 10),
                    min(255, orig[1] + 10),
                    min(255, orig[2] + 10),
                    orig[3]
                ))

# 文字
try:
    font_title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 60)
    font_sub = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
except:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()

# 居中绘制
from PIL import ImageColor
title = 'shibazichuan  AI 工具箱'
sub = 'DeepSeek 驱动    免费    无需注册'

bbox = draw.textbbox((0,0), title, font=font_title)
tw = bbox[2] - bbox[0]
draw.text(((w - tw) // 2, 230), title, fill='white', font=font_title)

bbox2 = draw.textbbox((0,0), sub, font=font_sub)
sw = bbox2[2] - bbox2[0]
draw.text(((w - sw) // 2, 320), sub, fill='rgba(255,255,255,200)', font=font_sub)

path = 'docs/og-image.png'
img.save(path, 'PNG')
print(f'Saved {path} ({w}x{h})')
"
```

- [ ] **Step 2: 验证文件**

Run: `python -c "from PIL import Image; img=Image.open('docs/og-image.png'); print(f'{img.size[0]}x{img.size[1]}')"`
Expected: `1200x630`

- [ ] **Step 3: Commit**

```bash
git add docs/og-image.png
git commit -m "feat: 添加 Open Graph 社交分享预览图 (1200x630)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: 主页 — Open Graph 标签 + 隐私说明

**Files:**
- Modify: `docs/index.html`

- [ ] **Step 1: 在 <head> 中添加 OG meta 标签**

在现有 `<meta name="baidu-site-verification" ... />` 之后（第 8 行）插入：

```html
    <!-- Open Graph / 社交分享 -->
    <meta property="og:title" content="shibazichuan — AI 工具箱 | 免费在线工具">
    <meta property="og:description" content="DeepSeek 驱动，免费，无需注册。翻译助手、小红书文案生成器。">
    <meta property="og:image" content="https://zhixumentu.com/og-image.png">
    <meta property="og:url" content="https://zhixumentu.com/">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
```

- [ ] **Step 2: 在页脚 visitor 和 copyright 之间添加隐私说明**

在 visitor div 闭合后、copyright 行之前插入：

```html
        <p style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">🔒 我们不保存您的任何输入内容</p>
```

- [ ] **Step 3: 验证 HTML 结构**

Run: `python -c "
import re
html = open('docs/index.html', encoding='utf-8').read()
assert 'og:title' in html, 'Missing og:title'
assert 'og:image' in html, 'Missing og:image'
assert '我们不保存您的任何输入内容' in html, 'Missing privacy text'
print('HTML verification OK')
"`
Expected: `HTML verification OK`

- [ ] **Step 4: Commit**

```bash
git add docs/index.html
git commit -m "feat(homepage): Open Graph 社交分享标签 + 隐私说明

- 添加 og:title/description/image/url/type meta 标签
- 添加 Twitter Card 标签
- 页脚新增隐私说明

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: README.md 优化

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 重写 README**

用以下完整内容替换 `README.md`：

```markdown
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
```

- [ ] **Step 2: 验证 Markdown 渲染**

Run: 检查关键元素存在
```bash
python -c "
md = open('README.md', encoding='utf-8').read()
checks = ['GitHub stars', 'Streamlit', 'License', 'zhixumentu.com',
          '功能亮点', '本地运行', 'API 说明', '一键互换', '一次3版本']
for c in checks:
    assert c in md, f'Missing: {c}'
print('README verification OK')
"
```
Expected: `README verification OK`

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(README): 英文简介 + Badge徽章 + 功能亮点 + 链接区块

- 顶部新增英文简介 + Shields.io 徽章（stars/streamlit/license）
- 工具表格增加"亮点"列展示新功能
- 新增功能亮点章节详细描述两个工具的特色
- 新增主页链接

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: 端到端验证

- [ ] **Step 1: 语法检查所有改动的 py 文件**

Run: `python -m py_compile translator.py && python -m py_compile xiaohongshu.py && echo "All OK"`
Expected: `All OK`

- [ ] **Step 2: 确认 .streamlit/config.toml 被 git 追踪**

Run: `git ls-files .streamlit/config.toml`
Expected: `.streamlit/config.toml`

- [ ] **Step 3: 确认改动范围**

Run: `git diff --stat main~6..HEAD`（6 个 commit）
Expected: 只涉及 `.streamlit/config.toml`、`translator.py`、`xiaohongshu.py`、`docs/index.html`、`docs/og-image.png`、`README.md`

- [ ] **Step 4: 启动翻译助手检查 Streamlit 无报错**

Run: `timeout 6 streamlit run translator.py --server.headless true 2>&1 || true`
Expected: 输出 "You can now view your Streamlit app in your browser."

- [ ] **Step 5: 启动小红书检查 Streamlit 无报错**

Run: `timeout 6 streamlit run xiaohongshu.py --server.headless true 2>&1 || true`
Expected: 输出 "You can now view your Streamlit app in your browser."

- [ ] **Step 6: Commit 验证结果（如无问题则跳过，如有修正则提交）**

```bash
# 如验证全部通过且无修正:
echo "All verified, ready to push"
```

- [ ] **Step 7: Push**

```bash
git push origin main
```
