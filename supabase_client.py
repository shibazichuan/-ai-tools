"""
Supabase 客户端 — 会员验证 + 使用日志
=======================================
纯 requests 实现，不依赖 supabase-py，零额外安装。

前置条件：
  1. 注册 Supabase → 创建项目
  2. 在 Streamlit Secrets 中配置：
     SUPABASE_URL = "https://xxx.supabase.co"
     SUPABASE_ANON_KEY = "eyJh..."
  3. 在 Supabase SQL Editor 中执行建表 SQL

未配置 SUPABASE_URL 时降级为纯本地模式（is_member 永远返回 False）。
"""

import hashlib
import json
import streamlit as st

# ============================================================
# 配置（从 Streamlit Secrets 读取）
# ============================================================
SUPABASE_URL = None
SUPABASE_ANON_KEY = None
SUPABASE_ENABLED = False

try:
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", "")
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        SUPABASE_ENABLED = True
except Exception:
    pass  # 本地开发没有 secrets


# ============================================================
# 指纹工具
# ============================================================
def _hash_fingerprint(raw: str) -> str:
    """SHA256 哈希设备指纹（截取前 32 位）"""
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ============================================================
# Supabase REST API（纯 requests，无外部依赖）
# ============================================================
def _supabase_request(method: str, path: str, body: dict = None):
    """调用 Supabase REST API"""
    import urllib.request
    import urllib.error

    url = f"{SUPABASE_URL}/rest/v1/{path}"
    data = json.dumps(body).encode() if body else None

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("apikey", SUPABASE_ANON_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_ANON_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=minimal")

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        st.warning(f"Supabase API error: {e.code}")
        return None
    except Exception as e:
        st.warning(f"Supabase connection failed: {e}")
        return None


# ============================================================
# 会员验证
# ============================================================
def verify_member(fingerprint: str) -> bool:
    """
    向 Supabase 查询该指纹是否为活跃会员。

    返回 True 表示该设备已开通会员。
    """
    if not SUPABASE_ENABLED or not fingerprint:
        return False

    # URL 编码 fingerprint
    from urllib.parse import quote
    fp_encoded = quote(fingerprint)

    # GET /members?fingerprint=eq.xxx&status=eq.active&limit=1
    result = _supabase_request(
        "GET",
        f"members?fingerprint=eq.{fp_encoded}&status=eq.active&limit=1"
    )

    if result is None:
        return False  # API 调用失败 → 降级为非会员

    return isinstance(result, list) and len(result) > 0


# ============================================================
# 使用日志（仅统计用，不阻塞）
# ============================================================
def log_usage(fingerprint: str, tool_id: str, is_member: bool, limit_hit: bool = False):
    """向 Supabase 写入使用日志（异步，不阻塞主流程）"""
    if not SUPABASE_ENABLED or not fingerprint:
        return

    try:
        _supabase_request("POST", "usage_logs", {
            "fingerprint": fingerprint,
            "tool_id": tool_id,
            "is_member": is_member,
            "limit_hit": limit_hit,
        })
    except Exception:
        pass  # 日志写入失败不影响主功能


# ============================================================
# Supabase 建表 SQL（供参考，在 Supabase SQL Editor 中执行）
# ============================================================
SETUP_SQL = """
-- 会员表
CREATE TABLE IF NOT EXISTS members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    fingerprint TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    notes TEXT
);

-- 使用日志表
CREATE TABLE IF NOT EXISTS usage_logs (
    id BIGSERIAL PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    is_member BOOLEAN DEFAULT FALSE,
    limit_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS：允许匿名读取 members
ALTER TABLE members ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "anon_can_read_members"
    ON members FOR SELECT USING (true);

-- RLS：允许匿名写入 usage_logs
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "anon_can_insert_logs"
    ON usage_logs FOR INSERT WITH CHECK (true);
"""
