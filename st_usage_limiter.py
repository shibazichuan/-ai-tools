"""
Streamlit 使用次数限制模块
==========================
适配 Streamlit Cloud 免费层（无持久化存储）
方案：localStorage（跨会话） + session_state（防刷新作弊）

集成方式：
    from st_usage_limiter import UsageLimiter
    limiter = UsageLimiter(tool_id="translator", free_limit=5)
    if limiter.check_and_consume():
        st.success("✅ 可以使用")
    else:
        st.stop()  # 弹窗已自动显示
"""

import json
import time
import hashlib
import streamlit as st
from datetime import datetime, timezone, timedelta

# ============================================================
# 配置
# ============================================================
TOOL_CONFIG = {
    "translator":   {"name": "AI 翻译助手",     "limit": 5},
    "xhs_writer":   {"name": "小红书文案生成器", "limit": 5},
    "ai_writer":    {"name": "AI 写作助手",      "limit": 5},
    "pdf_summary":  {"name": "PDF 总结器",       "limit": 3},
    "code_helper":  {"name": "AI 代码助手",      "limit": 5},
    "resume_ai":    {"name": "AI 简历优化器",     "limit": 3},
    "prompt_gen":   {"name": "提示词优化器",      "limit": 5},
    "video_script": {"name": "短视频脚本生成器",  "limit": 5},
}

MEMBER_URL  = "https://zhixumentu.com/#pricing"      # 会员页
DONATE_URL  = "https://zhixumentu.com/#donate"       # 赞赏页
DONATE_TRIGGER_AT = 3               # 第N次触发赞赏
TZ_UTC8 = timezone(timedelta(hours=8))


# ============================================================
# 核心类
# ============================================================
class UsageLimiter:
    def __init__(self, tool_id, free_limit=None):
        self.tool_id = tool_id
        self.config = TOOL_CONFIG.get(tool_id, {"name": "工具", "limit": 5})
        self.free_limit = free_limit or self.config["limit"]
        self._skey_used  = f"zm_{tool_id}_used"
        self._skey_ls    = f"zm_{tool_id}_ls"
        self._skey_member = "zm_member"
        self._today = datetime.now(TZ_UTC8).strftime("%Y-%m-%d")

    # ==========================================================
    # 注入 JS → 读写 localStorage
    # ==========================================================
    def _inject_bridge(self):
        """页面加载时注入一次 localStorage ↔ Streamlit 通信桥"""
        if self._skey_ls in st.session_state:
            return  # 已注入过

        st.session_state[self._skey_ls] = True

        # 用 st.query_params 传递数据：URL?zm_data=xxx
        qp = st.query_params
        ls_data = qp.get("zm_data", "")

        if ls_data:
            try:
                parsed = json.loads(ls_data)
                st.session_state[self._skey_used] = parsed.get("count", 0)
                st.session_state["zm_date"] = parsed.get("date", "")
            except Exception:
                pass

        # 通过隐藏组件持续桥接
        st.components.v1.html(f"""
        <script>
        const TOOL_ID = '{self.tool_id}';
        const LS_KEY = 'zm_usage_' + TOOL_ID;

        function getToday() {{
            const d = new Date();
            const utc8 = new Date(d.getTime() + (d.getTimezoneOffset() + 480) * 60000);
            return utc8.toISOString().slice(0, 10);
        }}

        function readLS() {{
            try {{
                const raw = localStorage.getItem(LS_KEY);
                if (!raw) return {{ date: getToday(), count: 0 }};
                const data = JSON.parse(raw);
                if (data.date !== getToday()) return {{ date: getToday(), count: 0 }};
                return data;
            }} catch(e) {{ return {{ date: getToday(), count: 0 }}; }}
        }}

        function writeLS(count) {{
            const data = {{ date: getToday(), count: count }};
            localStorage.setItem(LS_KEY, JSON.stringify(data));
        }}

        // 监听 Streamlit 发送的消息
        window.addEventListener('message', function(e) {{
            if (e.data.type === 'zm_consume') {{
                const current = readLS();
                current.count += 1;
                writeLS(current.count);
                window.parent.postMessage({{
                    type: 'zm_consumed',
                    count: current.count,
                    limit: {self.free_limit}
                }}, '*');
            }}
            if (e.data.type === 'zm_get_usage') {{
                const current = readLS();
                window.parent.postMessage({{
                    type: 'zm_usage_data',
                    count: current.count,
                    date: current.date,
                    limit: {self.free_limit}
                }}, '*');
            }}
        }});

        // 首次加载 → 把数据写入 URL hash
        const data = readLS();
        const currentUrl = new URL(window.location);
        const needsUpdate = !currentUrl.searchParams.get('zm_data');
        if (needsUpdate && data.count > 0) {{
            // 页面静默刷新传递初始值（仅一次）
            currentUrl.searchParams.set('zm_data', JSON.stringify({{count: data.count, date: data.date}}));
            window.history.replaceState({{}}, '', currentUrl.toString());
        }}
        </script>
        """, height=0)

    # ==========================================================
    # 获取当前使用量
    # ==========================================================
    def _get_usage(self):
        # 优先 session_state（当前会话内的准确计数）
        if self._skey_used in st.session_state:
            date = st.session_state.get("zm_date", "")
            if date == self._today:
                return st.session_state[self._skey_used]

        # 从 query_params 读取跨会话数据
        qp = st.query_params
        ls_data = qp.get("zm_data", "")
        if ls_data:
            try:
                parsed = json.loads(ls_data)
                if parsed.get("date") == self._today:
                    return parsed.get("count", 0)
            except Exception:
                pass
        return 0

    # ==========================================================
    # 检查是否会员
    # ==========================================================
    def is_member(self):
        if self._skey_member in st.session_state:
            return st.session_state[self._skey_member]
        # 检查 query_params 中的 member token
        token = st.query_params.get("zm_token", "")
        if token:
            # 简单校验（后续接入 Supabase 验证）
            try:
                payload = json.loads(
                    hashlib.sha256(token.encode()).hexdigest()[:20]
                )
                return False  # 先全部返回 False，待 Supabase 接入后实现
            except Exception:
                pass
        return False

    # ==========================================================
    # 剩余次数
    # ==========================================================
    def remaining(self):
        if self.is_member():
            return float('inf')
        return max(0, self.free_limit - self._get_usage())

    def used(self):
        if self.is_member():
            return 0
        return self._get_usage()

    # ==========================================================
    # 检查 + 消耗（一步完成）
    # ==========================================================
    def check_and_consume(self):
        self._inject_bridge()

        if self.is_member():
            return True

        used = self._get_usage()

        # 超过限制 → 展示 UI
        if used >= self.free_limit:
            self._show_limit_ui(used)
            return False

        # 消耗1次
        used += 1
        st.session_state[self._skey_used] = used
        st.session_state["zm_date"] = self._today

        # 同步到 localStorage
        self._sync_to_ls(used)

        # 触发赞赏提示（第3次）
        if used == DONATE_TRIGGER_AT:
            self._show_donate_toast()

        # 最后1次提示
        if used == self.free_limit - 1:
            self._show_last_toast()

        self._show_indicator(used)
        return True

    # ==========================================================
    # 同步到 localStorage
    # ==========================================================
    def _sync_to_ls(self, count):
        st.components.v1.html(f"""
        <script>
        const LS_KEY = 'zm_usage_{self.tool_id}';
        const d = new Date();
        const utc8 = new Date(d.getTime() + (d.getTimezoneOffset() + 480) * 60000);
        const today = utc8.toISOString().slice(0, 10);
        localStorage.setItem(LS_KEY, JSON.stringify({{ date: today, count: {count} }}));
        </script>
        """, height=0)

    # ==========================================================
    # 剩余次数指示器
    # ==========================================================
    def _show_indicator(self, used):
        rem = self.free_limit - used
        color = "#ef4444" if rem <= 1 else "#667eea"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;
                    padding:6px 14px;border-radius:20px;background:{'#fef2f2' if rem<=1 else '#f0f4ff'};
                    font-size:0.85rem;width:fit-content">
            <span style="display:inline-flex;align-items:center;justify-content:center;
                         min-width:22px;height:22px;border-radius:50%;font-weight:700;font-size:0.75rem;
                         background:{color};color:#fff;padding:0 6px;
                         {'animation: pulse 0.6s infinite alternate;' if rem <= 1 else ''}">
                {rem}
            </span>
            次剩余 · 今日已用 {used}/{self.free_limit}
        </div>
        <style>
        @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.12); }} }}
        </style>
        """, unsafe_allow_html=True)

    # ==========================================================
    # 超出限制弹窗
    # ==========================================================
    def _show_limit_ui(self, used):
        st.markdown(f"""
        <div style="position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.5);
                    display:flex;align-items:center;justify-content:center;padding:20px">
            <div style="background:white;border-radius:20px;padding:40px 36px;
                        max-width:420px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.15);
                        animation: slideUp 0.35s ease-out">
                <div style="font-size:3rem;margin-bottom:12px">🎯</div>
                <h3 style="margin-bottom:8px;font-weight:700">今日免费次数已用完</h3>
                <p style="color:#64748b;margin-bottom:24px;line-height:1.8">
                    <strong style="color:#667eea">{self.config['name']}</strong>
                    每天免费 <strong>{self.free_limit}</strong> 次<br>
                    今日已使用 <strong>{used}</strong> 次
                </p>
                <div style="display:flex;flex-direction:column;gap:10px">
                    <a href="{MEMBER_URL}" target="_self"
                       style="display:block;padding:12px 28px;border-radius:100px;
                              background:linear-gradient(135deg,#667eea,#764ba2);
                              color:white;text-decoration:none;font-weight:600;
                              box-shadow:0 4px 16px rgba(102,126,234,0.3)">
                        ⚡ 升级会员 · 无限使用
                    </a>
                    <span style="color:#94a3b8;font-size:0.82rem">
                        💚 月付仅 ¥19.9 · 支持开发者
                    </span>
                </div>
            </div>
        </div>
        <style>
        @keyframes slideUp {{
            from {{ transform: translateY(24px) scale(0.96); opacity: 0; }}
            to   {{ transform: translateY(0) scale(1); opacity: 1; }}
        }}
        </style>
        """, unsafe_allow_html=True)

    # ==========================================================
    # 赞赏 Toast
    # ==========================================================
    def _show_donate_toast(self):
        st.toast(f"☕ 已帮你完成 {DONATE_TRIGGER_AT} 次！好用的话，请作者喝杯咖啡", icon="☕")

    # ==========================================================
    # 最后1次警告
    # ==========================================================
    def _show_last_toast(self):
        st.toast("⚠️ 今日还剩最后 1 次免费使用，升级会员解锁无限 →", icon="⚠️")


# ============================================================
# Streamlit 页面初始化（放在每个工具页面的最前面）
# ============================================================
def init_tool(tool_id, free_limit=None):
    """
    每个工具页面的入口，返回 UsageLimiter 实例。

    用法：
        limiter = init_tool("translator", free_limit=5)
        if not limiter.check_and_consume():
            st.stop()  # 超出限制，停止渲染

    建议放在 st.set_page_config() 之后，其他内容之前。
    """
    limiter = UsageLimiter(tool_id, free_limit=free_limit)
    return limiter
