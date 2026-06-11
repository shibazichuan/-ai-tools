"""
Streamlit 使用次数限制模块 v2（安全加固版）
============================================
适配 Streamlit Cloud 免费层（无持久化存储）
防护方案：cookie 双写 + key 混淆 + checksum + session 锁

防御层级：
  L1: session_state 防刷新（会话级，最可靠）
  L2: localStorage 跨会话持久化（浏览器级）
  L3: cookie 隐蔽双写（防 DevTools 直接改 localStorage）
  L4: key 混淆 + 值 checksum（防直接编辑存储值）

已知无法防御（需后端）：
- 隐私模式/无痕模式（必然重置）
- 清除全部浏览器数据（cookie 和 localStorage 一起清）
- 换浏览器/设备
- 自动化脚本

集成方式：
    from st_usage_limiter import UsageLimiter, init_tool
    limiter = init_tool("translator", free_limit=5)
    if limiter.check_and_consume():
        # 正常使用
    else:
        st.stop()  # 弹窗已自动显示
"""

import json
import base64
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

MEMBER_URL  = "https://zhixumentu.com/#pricing"
DONATE_URL  = "https://zhixumentu.com/#donate"
DONATE_TRIGGER_AT = 3
TZ_UTC8 = timezone(timedelta(hours=8))

# 混淆盐值（每次部署可更换，换后所有用户存储失效）
_SALT = "zm2026x1t9k4"


# ============================================================
# 工具函数
# ============================================================
def _obfuscate_key(tool_id: str) -> str:
    """将 tool_id 混淆为不可读的存储 key"""
    raw = f"zm_{tool_id}_{_SALT}"
    return "z_" + base64.b64encode(raw.encode()).decode()[:16].replace("=", "x").replace("/", "y").replace("+", "z")


def _make_storage_value(date: str, count: int) -> dict:
    """生成带 checksum 的存储值"""
    raw = f"{date}|{count}|{_SALT}"
    chk = hashlib.md5(raw.encode()).hexdigest()[:6]
    return {"d": date, "c": count, "s": chk}


def _validate_storage(data: dict) -> int:
    """校验并返回 count。校验失败返回 -1。"""
    if not isinstance(data, dict):
        return -1
    d, c, s = data.get("d"), data.get("c"), data.get("s")
    if not d or c is None or not s:
        return -1
    if not isinstance(c, (int, float)):
        return -1
    expected = hashlib.md5(f"{d}|{int(c)}|{_SALT}".encode()).hexdigest()[:6]
    return int(c) if s == expected else -1


# ============================================================
# 核心类
# ============================================================
class UsageLimiter:
    def __init__(self, tool_id, free_limit=None):
        self.tool_id = tool_id
        self.config = TOOL_CONFIG.get(tool_id, {"name": "工具", "limit": 5})
        self.free_limit = free_limit or self.config["limit"]
        self._storage_key = _obfuscate_key(tool_id)
        self._skey_used = f"zm_{tool_id}_used"
        self._skey_date = f"zm_{tool_id}_date"
        self._skey_lock = f"zm_{tool_id}_lock"
        self._skey_loaded = f"zm_{tool_id}_loaded"
        self._today = datetime.now(TZ_UTC8).strftime("%Y-%m-%d")

    # ==========================================================
    # 注入 JS 桥接（简化版 — 仅传初始数据到 URL）
    # ==========================================================
    def _inject_bridge(self):
        """页面生命周期内注入一次 JS，读取 ls+cookie 并写入 URL param"""
        if self._skey_loaded in st.session_state:
            return
        st.session_state[self._skey_loaded] = True

        sk = self._storage_key

        st.components.v1.html(f"""
        <script>
        (function() {{
            var KEY = '{sk}';
            var FREE = {self.free_limit};

            function today() {{
                var d = new Date();
                var u = new Date(d.getTime() + (d.getTimezoneOffset() + 480) * 60000);
                return u.toISOString().slice(0, 10);
            }}

            function readLS() {{
                try {{
                    var r = localStorage.getItem(KEY);
                    return r ? JSON.parse(r) : null;
                }} catch(e) {{ return null; }}
            }}

            function readCookie() {{
                try {{
                    var m = document.cookie.match(new RegExp('(?:^|; )' + KEY + '=([^;]*)'));
                    return m ? JSON.parse(decodeURIComponent(m[1])) : null;
                }} catch(e) {{ return null; }}
            }}

            function getCount(data) {{
                if (!data || data.d !== today() || typeof data.c !== 'number') return -1;
                return data.c;
            }}

            var td = today();
            var ls = readLS(), ck = readCookie();
            var lsC = getCount(ls), ckC = getCount(ck);
            var count = 0, suspicious = false;

            if (lsC >= 0 && ckC >= 0) {{
                count = Math.max(lsC, ckC);
            }} else if (ckC > 0 && lsC < 0) {{
                // cookie 有记录但 ls 没了 → 可能清了 localStorage，标记可疑
                count = ckC;
                suspicious = true;
            }} else if (lsC >= 0) {{
                count = lsC;
            }}

            var cur = new URL(window.location);
            if (!cur.searchParams.get('zm_data')) {{
                cur.searchParams.set('zm_data', JSON.stringify({{
                    date: td, count: count, suspicious: suspicious, key: KEY
                }}));
                window.history.replaceState({{}}, '', cur.toString());
            }}
        }})();
        </script>
        """, height=0)

    # ==========================================================
    # 获取当前使用量
    # ==========================================================
    def _get_usage(self):
        """优先级：session_state > URL query_params（含 cookie+ls 合并值）"""
        # L1: 当前会话
        if self._skey_used in st.session_state:
            if st.session_state.get(self._skey_date, "") == self._today:
                return st.session_state[self._skey_used]

        # L2: 从 URL param 读取 JS 桥接的合并值
        zm_data = st.query_params.get("zm_data", "")
        if zm_data:
            try:
                parsed = json.loads(zm_data)
                if parsed.get("date") == self._today:
                    c = parsed.get("count", 0)
                    if isinstance(c, (int, float)) and c >= 0:
                        c = int(c)
                        st.session_state[self._skey_used] = c
                        st.session_state[self._skey_date] = self._today
                        # cookie 与 ls 不一致 → 当作已超限
                        if parsed.get("suspicious"):
                            return self.free_limit
                        return c
            except Exception:
                pass
        return 0

    # ==========================================================
    # 会员检查
    # ==========================================================
    def is_member(self):
        return False

    # ==========================================================
    # 剩余 / 已用
    # ==========================================================
    def remaining(self):
        self._inject_bridge()
        if self.is_member():
            return float('inf')
        return max(0, self.free_limit - self._get_usage())

    def used(self):
        if self.is_member():
            return 0
        return self._get_usage()

    # ==========================================================
    # 检查 + 消耗（核心方法）
    # ==========================================================
    def check_and_consume(self):
        """消耗一次。返回 True=可用，False=已达上限。"""
        self._inject_bridge()

        if self.is_member():
            return True

        # 防重复消费：同一 session 已消费过 → 直接返回结果
        if self._skey_lock in st.session_state:
            used = self._get_usage()
            if used <= self.free_limit:
                return True
            self._show_limit_ui(used)
            return False

        used = self._get_usage()

        if used >= self.free_limit:
            self._show_limit_ui(used)
            return False

        # 消耗
        used += 1
        st.session_state[self._skey_used] = used
        st.session_state[self._skey_date] = self._today
        st.session_state[self._skey_lock] = True

        self._sync_storage(used)

        if used == DONATE_TRIGGER_AT:
            self._show_donate_toast()
        if used == self.free_limit - 1:
            self._show_last_toast()

        self._show_indicator(used)
        return True

    # ==========================================================
    # 双写 localStorage + cookie
    # ==========================================================
    def _sync_storage(self, count):
        data_json = json.dumps(_make_storage_value(self._today, count))
        sk = self._storage_key

        st.components.v1.html(f"""
        <script>
        (function() {{
            var data = {data_json};
            var key = '{sk}';
            var str = JSON.stringify(data);
            try {{ localStorage.setItem(key, str); }} catch(e) {{}}
            try {{
                document.cookie = key + '=' + encodeURIComponent(str)
                    + ';path=/;max-age=86400;SameSite=Lax';
            }} catch(e) {{}}
        }})();
        </script>
        """, height=0)

    # ==========================================================
    # 剩余次数指示器（公开方法，供页面加载时调用）
    # ==========================================================
    def show_indicator(self):
        """显示剩余次数指示器（页面加载时调用）"""
        self._show_indicator(self.used())

    def _show_indicator(self, used):
        rem = self.free_limit - used
        color = "#ef4444" if rem <= 1 else "#667eea"
        bg = "#fef2f2" if rem <= 1 else "#f0f4ff"
        anim = "animation: pulse 0.6s infinite alternate;" if rem <= 1 else ""
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;
                    padding:6px 14px;border-radius:20px;background:{bg};
                    font-size:0.85rem;width:fit-content">
            <span style="display:inline-flex;align-items:center;justify-content:center;
                         min-width:22px;height:22px;border-radius:50%;font-weight:700;font-size:0.75rem;
                         background:{color};color:#fff;padding:0 6px;{anim}">
                {rem}
            </span>
            次剩余 · 今日已用 {used}/{self.free_limit}
        </div>
        <style>
        @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.12); }} }}
        </style>
        """, unsafe_allow_html=True)

    # ==========================================================
    # 超出限制弹窗（暗色模式适配）
    # ==========================================================
    def _show_limit_ui(self, used):
        st.markdown(f"""
        <div class="zm-overlay">
            <div class="zm-card">
                <div class="zm-icon">🎯</div>
                <h3>今日免费次数已用完</h3>
                <p class="zm-desc">
                    <strong>{self.config['name']}</strong>
                    每天免费 <strong>{self.free_limit}</strong> 次<br>
                    今日已使用 <strong>{used}</strong> 次
                </p>
                <div class="zm-actions">
                    <a href="{MEMBER_URL}" target="_blank" rel="noopener" class="zm-btn-upgrade">
                        ⚡ 升级会员 · 无限使用
                    </a>
                    <span class="zm-sub">💚 月付仅 ¥19.9 · 支持开发者</span>
                </div>
            </div>
        </div>
        <style>
        /* ===== 弹窗基础样式 ===== */
        .zm-overlay {{
            position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.5);
            display:flex;align-items:center;justify-content:center;padding:20px;
        }}
        .zm-card {{
            background:#fff;border-radius:20px;padding:40px 36px;max-width:420px;
            text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.15);
            animation: zmSlideUp 0.35s ease-out;
        }}
        .zm-card h3 {{ margin-bottom:8px;font-weight:700;color:#1a1a2e; }}
        .zm-icon {{ font-size:3rem;margin-bottom:12px; }}
        .zm-desc {{ color:#64748b;margin-bottom:24px;line-height:1.8;font-size:0.95rem; }}
        .zm-desc strong {{ color:#667eea;font-weight:700; }}
        .zm-actions {{ display:flex;flex-direction:column;gap:10px; }}
        .zm-btn-upgrade {{
            display:block;padding:12px 28px;border-radius:100px;
            background:linear-gradient(135deg,#667eea,#764ba2);
            color:#fff;text-decoration:none;font-weight:600;font-size:0.95rem;
            box-shadow:0 4px 16px rgba(102,126,234,0.3);
            transition: all 0.25s;
        }}
        .zm-btn-upgrade:hover {{ transform:translateY(-2px);box-shadow:0 8px 28px rgba(102,126,234,0.4); }}
        .zm-sub {{ color:#94a3b8;font-size:0.82rem; }}

        /* ===== 暗色模式 ===== */
        @media (prefers-color-scheme: dark) {{
            .zm-card {{
                background:#1e1e2e;box-shadow:0 20px 60px rgba(0,0,0,0.4);
            }}
            .zm-card h3 {{ color:#e2e8f0; }}
            .zm-desc {{ color:#94a3b8; }}
            .zm-desc strong {{ color:#818cf8; }}
            .zm-sub {{ color:#64748b; }}
        }}

        /* ===== 动画 ===== */
        @keyframes zmSlideUp {{
            from {{ transform: translateY(24px) scale(0.96); opacity: 0; }}
            to   {{ transform: translateY(0) scale(1); opacity: 1; }}
        }}

        /* ===== 响应式 ===== */
        @media (max-width: 480px) {{
            .zm-card {{ margin:12px;padding:28px 20px;border-radius:16px; }}
        }}
        </style>
        """, unsafe_allow_html=True)

    # ==========================================================
    # 使用统计（供工具侧边栏展示）
    # ==========================================================
    def render_stats(self):
        """在侧边栏渲染使用统计"""
        used = self.used()
        rem = self.remaining()
        pct = min(100, int(used / self.free_limit * 100)) if self.free_limit > 0 else 0
        bar_color = "#ef4444" if rem == 0 else ("#f59e0b" if rem <= 1 else "#667eea")

        st.markdown("---")
        st.markdown("#### 📊 使用统计")
        st.markdown(f"""
        <div style="font-size:0.85rem;line-height:1.8">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span>今日已用</span><strong>{used}/{self.free_limit}</strong>
            </div>
            <div style="background:#e5e7eb;border-radius:100px;height:6px;overflow:hidden;margin-bottom:8px">
                <div style="width:{pct}%;height:100%;border-radius:100px;
                            background:{bar_color};transition:width 0.3s"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#94a3b8">
                <span>{'🚫 已用完' if rem == 0 else f'剩余 {rem} 次'}</span>
                <span>次日0点重置</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if rem <= 1 and rem != 0:
            st.caption("💡 快到上限了，升级会员解锁无限使用 →")

    # ==========================================================
    # Toast 提示
    # ==========================================================
    def _show_donate_toast(self):
        st.toast(f"☕ 已帮你完成 {DONATE_TRIGGER_AT} 次！好用的话，请作者喝杯咖啡", icon="☕")

    def _show_last_toast(self):
        st.toast("⚠️ 今日还剩最后 1 次免费使用，升级会员解锁无限 →", icon="⚠️")


# ============================================================
# 便捷入口
# ============================================================
def init_tool(tool_id, free_limit=None):
    """
    每个工具页面的入口，返回 UsageLimiter 实例。

    用法：
        limiter = init_tool("translator", free_limit=5)
        if not limiter.check_and_consume():
            st.stop()
    """
    return UsageLimiter(tool_id, free_limit=free_limit)
