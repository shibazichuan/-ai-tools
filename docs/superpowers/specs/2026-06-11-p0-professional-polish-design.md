# P0/P1 专业度提升 — 设计文档

**日期**: 2026-06-11
**状态**: 已确认

---

## 概述

提升 AI 工具箱整体专业度，覆盖品牌统一、错误处理、隐私透明、社交分享、README 展示。

---

## 1. 品牌配色统一

### 新建 `.streamlit/config.toml`

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

配色与 `docs/index.html` 的 CSS 变量完全一致。两个 Streamlit 工具自动继承。

---

## 2. 工具间互导流 + 署名

### 翻译助手 (`translator.py`)

- 新增侧边栏，内容：
  - 导航区块：当前工具高亮 + 链接到另一个工具 + 链接到主页
  - "by shibazichuan · 完全免费 · 无需注册"
- 标题下方加三个标签徽章：`永久免费` `无需注册` `DeepSeek 驱动`
- 统一页脚：`by shibazichuan · 工具箱首页 · 完全免费 · 无需注册`

### 小红书生成器 (`xiaohongshu.py`)

- 现有侧边栏底部加导航区块（同上格式）
- 标题下方加三个标签徽章
- 统一页脚

### 主页 (`docs/index.html`)

- 页脚已有署名，无需大改

---

## 3. 错误处理 — 分类友好提示

### 两个 py 文件统一改造

将 `except Exception as e: st.error(f"xxx失败：{str(e)}")` 替换为：

| 异常类型 | 用户提示 |
|----------|----------|
| `openai.AuthenticationError` | API 密钥配置有误，请联系站长修复 |
| `openai.RateLimitError` | 当前使用人数较多，请稍后再试 |
| `openai.APIConnectionError` / `openai.APITimeoutError` | 网络连接失败，请检查网络后重试 |
| 其他 `Exception` | 服务暂时不可用，请稍后重试。如持续出现请通过 [GitHub Issues](链接) 反馈 |

同时为 API 调用添加 `timeout=30`。

---

## 4. 隐私说明

三个页面统一加一行：

> 🔒 我们不保存您的任何输入内容

- 翻译助手 + 小红书：放在页脚
- 主页：放在页脚

---

## 5. Open Graph 社交分享标签

### `docs/index.html` `<head>` 新增

```html
<meta property="og:title" content="shibazichuan — AI 工具箱 | 免费在线工具">
<meta property="og:description" content="DeepSeek 驱动，免费，无需注册。翻译助手、小红书文案生成器。">
<meta property="og:image" content="https://zhixumentu.com/og-image.png">
<meta property="og:url" content="https://zhixumentu.com/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

### 生成 `docs/og-image.png`

自动生成 1200×630 的社交分享图：
- 紫蓝渐变背景 (#667eea → #764ba2)
- 居中文字：🛠️ shibazichuan · AI 工具箱
- 副标题：DeepSeek 驱动 · 免费 · 无需注册

---

## 6. README.md 优化

新增内容：
- **顶部英文简介** (2-3 句)
- **Shields.io 徽章**：GitHub stars、Streamlit、License MIT
- **截图占位**：两个工具的界面图片（可后续替换为真实截图）
- **直达链接区块**

---

## 涉及文件

| 文件 | 操作 |
|------|------|
| `.streamlit/config.toml` | 新建 |
| `translator.py` | 修改（侧边栏 + 标签 + 错误处理 + 隐私 + 页脚 + timeout） |
| `xiaohongshu.py` | 修改（侧边栏导航 + 标签 + 错误处理 + 隐私 + 页脚 + timeout） |
| `docs/index.html` | 修改（OG 标签 + 隐私说明 + 页脚优化） |
| `docs/og-image.png` | 新建（自动生成） |
| `README.md` | 修改 |

---

## 验证方式

1. `streamlit run translator.py` — 检查侧边栏导航、标签、页脚
2. `streamlit run xiaohongshu.py` — 同上
3. 浏览器打开 `docs/index.html` — 检查 OG 标签、隐私说明
4. `python -m py_compile` 两个 py 文件
5. `git diff --stat` 确认改动范围
