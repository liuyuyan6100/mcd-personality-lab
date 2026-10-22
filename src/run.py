#!/usr/bin/env python3
"""麦门人格鉴定所 · 入口。

用法：
    python run.py --demo                          # 演示模式（合成数据，无需 Token）
    python run.py --token <MCP_TOKEN>             # 拉取真实订单并生成鉴定卡
    python run.py --token <TOKEN> --output out.html

数据链路：mcd-mcp(order-list / query-my-account / list-nutrition-foods)
        → analyze.render_profile → report.render_html → 单文件 HTML 鉴定卡
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from demo_data import build_demo_orders
from mcd_client import McdClient, McdError
from analyze import render_profile, build_nutrition_index
from report import render_html

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")


def fetch_real(token, url):
    client = McdClient(token, url=url)
    orders_raw = client.order_list()
    account = client.my_account()
    try:
        nutrition_raw = client.nutrition_foods()
    except McdError:
        nutrition_raw = []
    return orders_raw, account, build_nutrition_index(nutrition_raw)


def main():
    ap = argparse.ArgumentParser(description="MCD Personality Lab")
    ap.add_argument("--token", help="mcd-mcp token (apply at open.mcd.cn/mcp)")
    ap.add_argument("--url", default="https://mcp.mcd.cn")
    ap.add_argument("--demo", action="store_true", help="use synthetic demo data")
    ap.add_argument("--output", help="output html path")
    args = ap.parse_args()

    demo = args.demo
    nutrition_index = {}

    if demo:
        orders_raw = build_demo_orders()
        account = {"accountId": "DEMO", "accumulativePoint": "1024", "availablePoint": "0", "expiredPoint": "24"}
    elif args.token:
        try:
            orders_raw, account, nutrition_index = fetch_real(args.token, args.url)
        except McdError as e:
            print("[warn] MCP fetch failed: %s" % e, file=sys.stderr)
            print("[warn] falling back to --demo mode", file=sys.stderr)
            orders_raw, account, demo = build_demo_orders(), {}, True
    else:
        ap.error("either --demo or --token is required")

    profile = render_profile(orders_raw, account)
    html_text = render_html(profile, demo=demo, nutrition_index=nutrition_index)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "mcd-personality-%s%s.html" % (profile["cert_id"], "-demo" if demo else "")
    out = args.output or os.path.join(OUT_DIR, fname)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_text)

    summary = {
        "type": profile["type"]["name"],
        "title": profile["type"]["title"],
        "cert_id": profile["cert_id"],
        "orders": profile["metrics"]["n_orders"],
        "spend": round(profile["metrics"]["spend"], 2),
        "dims": {k: round(v) for k, v in profile["metrics"]["dims"].items()},
        "demo": demo,
        "output": os.path.abspath(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
