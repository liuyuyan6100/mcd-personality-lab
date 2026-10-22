# -*- coding: utf-8 -*-
"""用 Playwright 把鉴定卡 HTML 截成 PNG（公众号配图）"""
import os, sys
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "assets")
TARGETS = [
    ("output/mcd-personality-MCP-FCDE86BA-demo.html", "card-demo-malaji.png"),
    ("output/mcd-personality-MCP-15F9CE1F.html", "card-real-newbeliever.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 420, "height": 900}, device_scale_factor=2)
    for src, dst in TARGETS:
        path = os.path.join(BASE, src)
        if not os.path.exists(path):
            print("MISSING:", src); continue
        page.goto("file:///" + path.replace("\\", "/"))
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(OUT, dst), full_page=True)
        print("SHOT:", dst)
    browser.close()
