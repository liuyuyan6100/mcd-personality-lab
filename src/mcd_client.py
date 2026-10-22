"""mcd-mcp JSON-RPC 客户端（streamable HTTP）。

麦当劳 MCP（https://mcp.mcd.cn）返回的 content 是 markdown 包裹的文本，
真正数据在 "## Original Response" 之后的 JSON 里，unwrap() 负责解包。
零第三方依赖，仅标准库。
"""
import json
import re
import uuid
import urllib.request
import urllib.error

DEFAULT_URL = "https://mcp.mcd.cn"
PROTOCOL_VERSION = "2025-03-26"


class McdError(Exception):
    pass


def unwrap_mcp_text(text):
    """从 MCP 工具返回文本中提取 JSON 数据。

    兼容三种形态：
    1. "## Original Response\\n{...}"  markdown 包裹（实测 mcd-mcp 为此形态）
    2. 纯 JSON 文本
    3. 文本中任意位置的第一个 JSON 对象
    """
    if not text:
        return None
    m = re.search(r"##\s*Original Response\s*\n+(\{.*)", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except Exception:
            pass
    m = re.search(r"(\{.*\})", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return None


class McdClient:
    def __init__(self, token, url=DEFAULT_URL, timeout=30):
        if not token:
            raise McdError("missing mcd-mcp token (apply at open.mcd.cn/mcp)")
        self.token = token
        self.url = url
        self.timeout = timeout
        self._initialized = False

    def _rpc(self, method, params=None):
        body = {"jsonrpc": "2.0", "method": method, "id": str(uuid.uuid4())}
        if params:
            body["params"] = params
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, method="POST")
        req.add_header("Authorization", "Bearer " + self.token)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            payload = json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            raise McdError("HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:200]))
        except urllib.error.URLError as e:
            raise McdError("network error: %s" % e)
        if "error" in payload:
            raise McdError("rpc error: %s" % json.dumps(payload["error"], ensure_ascii=False))
        return payload.get("result", {})

    def initialize(self):
        if self._initialized:
            return
        self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "mcd-personality-lab", "version": "1.0.0"},
        })
        self._initialized = True

    def call_tool(self, name, arguments=None):
        """调用工具并返回解包后的 data 对象（失败返回 None）。"""
        self.initialize()
        result = self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        texts = [c.get("text", "") for c in result.get("content", []) if c.get("type") == "text"]
        raw = "\n".join(texts)
        obj = unwrap_mcp_text(raw)
        if obj is None:
            return None
        if isinstance(obj, dict) and "data" in obj:
            return obj.get("data")
        return obj

    def order_list(self):
        """历史订单列表（非商城订单）。"""
        data = self.call_tool("order-list", {})
        if isinstance(data, dict):
            return data.get("list") or []
        return data or []

    def my_account(self):
        data = self.call_tool("query-my-account", {})
        return data if isinstance(data, dict) else {}

    def nutrition_foods(self):
        data = self.call_tool("list-nutrition-foods", {})
        if isinstance(data, dict):
            return data.get("list") or data.get("foods") or []
        return data or []
