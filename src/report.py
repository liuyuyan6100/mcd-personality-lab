"""渲染「麦门人格鉴定卡」：单文件 HTML，移动端优先，可截图分享。

麦当劳品牌色：红 #DA291C / 黄 #FFC72C / 奶油底 #FFF6E5。
零依赖，产出单个 .html 文件。
"""
import html
from datetime import datetime

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#FFF6E5;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;color:#27251F;padding:24px 12px}
.card{max-width:460px;margin:0 auto;background:#FFFFFF;border-radius:20px;overflow:hidden;box-shadow:0 2px 0 #F0E4CC}
.hero{background:#DA291C;color:#FFFFFF;padding:26px 22px 22px;position:relative}
.hero .lab{font-size:11px;letter-spacing:3px;opacity:.85;font-weight:500}
.hero h1{font-size:26px;font-weight:500;margin-top:6px;letter-spacing:1px}
.hero .sub{font-size:12px;opacity:.85;margin-top:8px}
.hero .meta{margin-top:14px;font-size:11px;opacity:.75;display:flex;justify-content:space-between;border-top:1px solid rgba(255,255,255,.25);padding-top:10px}
.badge-demo{position:absolute;top:18px;right:16px;background:#FFC72C;color:#27251F;font-size:10px;font-weight:500;padding:3px 8px;border-radius:99px}
.body{padding:22px}
.type-block{background:#FFF3D6;border:1.5px solid #FFC72C;border-radius:14px;padding:18px 16px;text-align:center}
.type-block .t-name{font-size:23px;font-weight:500;color:#A41E14}
.type-block .t-title{display:inline-block;margin-top:8px;background:#DA291C;color:#FFFFFF;font-size:11px;padding:3px 10px;border-radius:99px}
.verdict{margin-top:14px;font-size:13px;line-height:1.9;color:#4A443C;text-align:justify}
.section-title{font-size:13px;font-weight:500;margin:22px 0 12px;color:#27251F;display:flex;align-items:center;gap:8px}
.section-title::before{content:"";width:4px;height:14px;background:#FFC72C;border-radius:2px}
.dim-row{display:flex;align-items:center;margin-bottom:10px;font-size:12px}
.dim-row .d-label{width:64px;color:#4A443C;flex-shrink:0}
.dim-row .d-track{flex:1;height:8px;background:#F5EDDC;border-radius:4px;overflow:hidden}
.dim-row .d-fill{height:100%;background:#DA291C;border-radius:4px}
.dim-row .d-val{width:38px;text-align:right;color:#A41E14;font-weight:500;flex-shrink:0}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.stat{background:#FAF6EC;border-radius:12px;padding:12px 8px;text-align:center}
.stat .s-val{font-size:17px;font-weight:500;color:#A41E14}
.stat .s-key{font-size:10px;color:#8A8378;margin-top:4px}
.top-item{display:flex;align-items:center;padding:9px 0;border-bottom:1px dashed #F0E4CC;font-size:13px}
.top-item:last-child{border-bottom:none}
.top-item .rank{width:22px;height:22px;border-radius:6px;background:#FFC72C;color:#27251F;font-size:11px;font-weight:500;display:flex;align-items:center;justify-content:center;margin-right:10px;flex-shrink:0}
.top-item .t-name{flex:1;color:#27251F}
.top-item .t-bar{width:90px;height:6px;background:#F5EDDC;border-radius:3px;overflow:hidden;margin:0 10px}
.top-item .t-bar i{display:block;height:100%;background:#DA291C;border-radius:3px}
.top-item .t-cnt{font-size:11px;color:#8A8378;width:30px;text-align:right;flex-shrink:0}
.panel{margin-top:16px;background:#FAF6EC;border-radius:12px;padding:14px}
.panel .p-title{font-size:12px;font-weight:500;color:#4A443C;margin-bottom:8px}
.panel .p-line{font-size:12px;color:#6B6459;line-height:1.8}
.traits{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:12px}
.traits span{background:#FFFFFF;border:1px solid #FFC72C;color:#A41E14;font-size:11px;padding:3px 10px;border-radius:99px}
.advice{margin-top:12px;font-size:12px;color:#8A8378;text-align:center;line-height:1.7}
.share{margin-top:20px;background:#27251F;border-radius:14px;padding:18px 16px;text-align:center}
.share .slogan{color:#FFC72C;font-size:16px;font-weight:500;letter-spacing:.5px}
.share .hint{color:#8A8378;font-size:11px;margin-top:8px}
.footer{padding:16px 22px 22px;text-align:center;font-size:10px;color:#B5AE9F;line-height:1.8}
"""


def _bar(pct):
    return '<div class="d-track"><div class="d-fill" style="width:%.1f%%"></div></div>' % max(2.0, min(100.0, pct))


def render_html(profile, demo=False, nutrition_index=None):
    esc = html.escape
    m = profile["metrics"]
    t = profile["type"]
    acct = profile.get("account") or {}

    dims_html = "".join(
        '<div class="dim-row"><div class="d-label">%s</div>%s<div class="d-val">%d</div></div>'
        % (esc(k), _bar(v), round(v))
        for k, v in m["dims"].items()
    )

    max_cnt = m["top_items"][0][1] if m["top_items"] else 1
    top_html = ""
    for i, (name, cnt) in enumerate(m["top_items"][:5]):
        top_html += (
            '<div class="top-item"><div class="rank">%d</div>'
            '<div class="t-name">%s</div>'
            '<div class="t-bar"><i style="width:%.0f%%"></i></div>'
            '<div class="t-cnt">×%d</div></div>'
        ) % (i + 1, esc(name), cnt / max_cnt * 100 if max_cnt else 0, cnt)

    def stat(val, key):
        return '<div class="stat"><div class="s-val">%s</div><div class="s-key">%s</div></div>' % (esc(str(val)), esc(key))

    if m["n_orders"] >= 3:
        stats_html = "".join([
            stat(m["n_orders"], "麦门叩首(次)"),
            stat("%.0f 元" % m["spend"], "香火钱"),
            stat("%.1f 元" % m["avg_price"], "客单价"),
            stat("%d%%" % round(m["night_ratio"] * 100), "深夜订单占比"),
            stat(m["unique_items"], "吃过的餐品数"),
            stat(m["top_items"][0][0][:6] if m["top_items"] else "-", "本命餐品"),
        ])
    else:
        stats_html = "".join([
            stat(acct.get("accumulativePoint", "0"), "累计积分"),
            stat(acct.get("expiredPoint", "0"), "已过期积分"),
            stat(m["store_count"], "打卡门店数"),
        ])

    from analyze import nutrition_eggs
    matched, total = nutrition_eggs(m, nutrition_index or {})
    nutrition_html = ""
    if matched:
        lines = "".join(
            '<div class="p-line">· %s ×%d ≈ %d 千卡 / 钠 %d mg</div>'
            % (esc(x["name"]), x["qty"], round(x["energy"]), round(x["sodium"]))
            for x in matched[:5]
        )
        bowls = total["energy"] / 1160.0
        salt = total["sodium"] / 1000.0 * 2.5
        nutrition_html = (
            '<div class="panel"><div class="p-title">营养彩蛋 · TOP 餐品估算</div>%s'
            '<div class="p-line" style="margin-top:8px;color:#A41E14">合计 ≈ %d 千卡，约 %.1f 碗米饭；钠 ≈ %.1f 克盐</div>'
            '<div class="p-line" style="margin-top:4px">* 基于 list-nutrition-foods 公开数据 × 点单量估算，仅供娱乐</div></div>'
        ) % (lines, round(total["energy"]), bowls, salt)

    points_html = ""
    if acct.get("accumulativePoint"):
        points_html = (
            '<div class="panel"><div class="p-title">麦享会积分档案</div>'
            '<div class="p-line">累计积分 %s · 可用 %s · 已过期 %s</div>'
            '<div class="p-line">%s</div></div>'
        ) % (
            esc(str(acct.get("accumulativePoint", "0"))),
            esc(str(acct.get("availablePoint", "0"))),
            esc(str(acct.get("expiredPoint", "0"))),
            esc("积分会过期，麦门的爱不会" if str(acct.get("expiredPoint", "0")) != "0" else "积分健康，请继续叩首"),
        )

    traits_html = "".join("<span>%s</span>" % esc(x) for x in t["traits"])
    demo_badge = '<div class="badge-demo">DEMO 演示数据</div>' if demo else ""

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>麦门人格鉴定卡 · %s</title>
<style>%s</style>
</head>
<body>
<div class="card">
  <div class="hero">%s
    <div class="lab">MCD PERSONALITY LAB</div>
    <h1>麦门人格鉴定所</h1>
    <div class="sub">基于麦当劳 MCP 真实订单数据的人格鉴定</div>
    <div class="meta"><span>鉴定编号 %s</span><span>%s</span></div>
  </div>
  <div class="body">
    <div class="type-block">
      <div class="t-name">%s</div>
      <div class="t-title">%s</div>
      <div class="verdict">%s</div>
      <div class="traits">%s</div>
      <div class="advice">麦门建议：%s</div>
    </div>
    <div class="section-title">人格五维</div>
    %s
    <div class="section-title">麦门数据面板</div>
    <div class="stats">%s</div>
    <div class="section-title">本命餐品榜</div>
    <div>%s</div>
    %s
    %s
    <div class="share">
      <div class="slogan">「 %s 」</div>
      <div class="hint">截图保存 · 分享给同修 · 麦门庇佑</div>
    </div>
  </div>
  <div class="footer">由「麦门人格鉴定所」生成 · WorkBuddy × 麦当劳 MCP · %s<br>数据链路：mcd-mcp order-list / list-nutrition-foods / query-my-account</div>
</div>
</body>
</html>
""" % (
        esc(t["name"]), CSS, demo_badge, esc(profile["cert_id"]),
        esc(profile["period"] or "数据周期未知"), esc(t["name"]), esc(t["title"]),
        esc(profile["verdict"]), traits_html, esc(t["advice"]),
        dims_html, stats_html, top_html, nutrition_html, points_html,
        esc(t["slogan"]),
        datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
