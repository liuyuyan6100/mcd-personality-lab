"""人格引擎：订单数据 → 麦门人格。

输入：MCP order-list 原始订单（或演示数据）
输出：metrics（统计指标）+ profile（人格类型、判词、五维分数）
"""
import hashlib
from collections import Counter
from datetime import datetime

from taxonomy import classify, CATEGORY_LABELS

# ---------------------------------------------------------------- 类型定义

TYPES = {
    "spicy": {
        "name": "麦辣鸡型人格",
        "title": "外酥内嫩 · 不可貌相",
        "verdict": "麦门庇佑。过去 {months} 个月，你在麦门神殿叩首 {orders} 次，奉上香火钱 {spend} 元，其中 {spicy_pct} 的餐盘里燃着同一簇火。麦辣鸡腿堡是你的权杖——外人看你温和稳妥，唯有麦门知道，你的辣藏在酥皮之下，咬到底才会呛出眼泪。麦门纪年载：外酥内嫩者，不可貌相。",
        "traits": ["辣度耐受点满", "表面温和", "底线清晰"],
        "advice": "下次试试辣翅蘸甜筒酱，麦门称此法为「冰火赦免」。",
        "slogan": "我的辣，酥皮之下才见面。",
    },
    "midnight": {
        "name": "深夜食堂型人格",
        "title": "情绪食客 · 夜的共犯",
        "verdict": "城市的灯一盏盏灭了，你的屏幕还亮着。{night_pct} 的订单发生在 21 点之后——那是麦门为夜猫预留的时辰。你不是饿，是需要一个仪式，把白天咽下去的话，换成一口烫嘴的辣翅。麦门懂得所有深夜的饿，那不过是灵魂在敲门。",
        "traits": ["夜猫指数爆表", "情绪感知力强", "需要仪式感"],
        "advice": "深夜加餐记得配零度可乐，麦门与你的胃都希望如此。",
        "slogan": "白天的我咽下去，深夜的麦门吐出来。",
    },
    "value": {
        "name": "穷鬼套餐型人格",
        "title": "性价比祭司 · 1+1 信徒",
        "verdict": "世人笑你穷鬼，你笑世人看不穿。{orders} 次叩首，{spend} 元香火，客单 {avg} 元——1+1 随心配不是将就，是信仰。在麦门的经济学里，用最少的金币换最稳的饱足，才是大智慧。麦门记载：性价比祭司，永远不会被生活噎住。",
        "traits": ["精打细算", "反消费主义", "稳如老狗"],
        "advice": "你的卡包里应该常备自动领取的券，祭司也要会用工具。",
        "slogan": "不是穷，是精通麦门汇率。",
    },
    "sweet": {
        "name": "甜筒型人格",
        "title": "治愈系 · 免罪券持有者",
        "verdict": "甜筒不是甜品，是麦门发给你的免罪券。{dessert_pct} 的订单里有甜——生活已经够苦了，何必再亏待舌头。你的治愈不需要道理，6 块钱一个圆锥体，旋转着就能把心情拉回正轨。麦门赐福：心甜的人，运气不会太差。",
        "traits": ["治愈系", "快乐门槛低", "温柔有钝感"],
        "advice": "试试麦旋风倒过来吃，第一口和最后一口都是精华。",
        "slogan": "生活再苦，甜筒是顺时针的。",
    },
    "boss": {
        "name": "巨无霸型人格",
        "title": "压场干将 · 主食尊严",
        "verdict": "出手即压场。{orders} 次叩首，客单 {avg} 元，{top_cat} 是你的标配。你点单从不犹豫，因为你知道自己要什么——巨无霸的层次感就是你的层次感，一口三层，层层有料。麦门批注：压场型人格，走到哪都是主食。",
        "traits": ["决策果断", "自我认知清晰", "主食尊严捍卫者"],
        "advice": "偶尔试试小食区，压场的人也需要配角。",
        "slogan": "一口三层，层层有料。",
    },
    "happy": {
        "name": "麦乐鸡型人格",
        "title": "快乐小狗 · 社交货币",
        "verdict": "麦乐鸡是你的社交货币，小食是你的快乐开关。{orders} 次点单里，{top_item} 出现了 {top_count} 次——你未必是最饿的，但一定是最会分享的。人群里递出一盒麦乐鸡的人，灵魂都闪着光。麦门认证：快乐小狗，人见人爱。",
        "traits": ["分享型人格", "群体粘合剂", "快乐传染源"],
        "advice": "你的隐藏菜单：麦乐鸡蘸麦旋风，麦门内部称「黄金圣衣」。",
        "slogan": "分享装一开，朋友自然来。",
    },
    "explorer": {
        "name": "探险家型人格",
        "title": "猎奇派 · 菜单开疆者",
        "verdict": "麦门菜单百品，你已阅 {unique}。猎奇是你的美德，从限定新品到隐藏吃法，你的餐盘永远在开疆拓土。{orders} 次点单，很少重复同一种人生。麦门嘉奖：猎奇者，先尝世界。",
        "traits": ["好奇心驱动", "拒绝套路", "新品雷达"],
        "advice": "本月限定已刷新，猎奇者的日程该更新了。",
        "slogan": "同样的麦门，我吃出新大陆。",
    },
    "morning": {
        "name": "早安型人格",
        "title": "晨型人 · 开机仪式派",
        "verdict": "当城市还在赖床，你已经在麦门用早餐签到。{breakfast_pct} 的订单发生在清晨——猪柳蛋麦满分的香气是你一天的开机音乐。晨型人的世界，连薯饼都是热的。麦门注脚：早安的人，先赢一半。",
        "traits": ["晨型作息", "仪式感强", "效率至上"],
        "advice": "早餐配咖啡，你的开机速度还能再快 15%。",
        "slogan": "我的一天，从麦满分开始加热。",
    },
    "banzai": {
        "name": "板烧型人格",
        "title": "务实派 · 稳得很",
        "verdict": "{orders} 次点单，{spend} 元，最爱 {top_item}。你不追限定，不凑热闹，板烧鸡腿堡式的踏实是你的底色——没有花哨的层次，但每一口都作数。麦门判定：务实派，稳得很。",
        "traits": ["踏实可靠", "少即是多", "长期主义"],
        "advice": "稳也是一种天赋，偶尔放肆一次，麦门不记账。",
        "slogan": "不花哨，但每一口都作数。",
    },
    "newbie": {
        "name": "麦门新信徒",
        "title": "待鉴定 · 史诗未启",
        "verdict": "麦门新信徒，欢迎。你的积分账户已有 {points} 积分进账，但尚未留下点单史诗。去麦门神殿叩首一次，再来找我做正式鉴定——届时这份报告将因你而具体。",
        "traits": ["潜力未知", "积分已萌芽", "未来可期"],
        "advice": "首单建议从麦辣鸡腿堡开始，麦门的试炼从此开始。",
        "slogan": "今日入麦门，来日定乾坤。",
    },
}

DIMENSIONS = ["犒赏力", "猎奇度", "夜猫指数", "辣度耐受", "甜度依赖"]


# ---------------------------------------------------------------- 数据规整

def normalize_orders(raw_orders):
    orders = []
    for o in raw_orders or []:
        t = o.get("createTime") or o.get("orderTime") or ""
        dt = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S"):
            try:
                dt = datetime.strptime(str(t)[:19], fmt)
                break
            except Exception:
                continue
        items = []
        for p in o.get("orderProductList") or o.get("items") or []:
            name = p.get("productName") or p.get("name") or ""
            if not name:
                continue
            try:
                qty = int(p.get("quantity") or 1)
            except Exception:
                qty = 1
            try:
                price = float(p.get("price") or p.get("realPrice") or 0)
            except Exception:
                price = 0.0
            items.append({"name": name, "qty": qty, "price": price})
        try:
            total = float(o.get("realTotalAmount") or 0)
        except Exception:
            total = sum(i["price"] * i["qty"] for i in items)
        orders.append({
            "time": dt,
            "items": items,
            "total": total,
            "store": o.get("storeName") or "",
            "order_type": str(o.get("orderType") or ""),
        })
    return orders


def _clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def compute_metrics(orders):
    item_counter = Counter()
    cat_counter = Counter()
    stores = Counter()
    spend = 0.0
    night = breakfast = timed = 0
    total_qty = 0
    spicy_qty = dessert_qty = value_qty = snack_qty = 0
    first_t = last_t = None

    for o in orders:
        spend += o["total"]
        if o["time"]:
            timed += 1
            h = o["time"].hour
            if h >= 21 or h < 4:
                night += 1
            if 5 <= h <= 9:
                breakfast += 1
            first_t = o["time"] if first_t is None or o["time"] < first_t else first_t
            last_t = o["time"] if last_t is None or o["time"] > last_t else last_t
        if o["store"]:
            stores[o["store"]] += 1
        for it in o["items"]:
            q = it["qty"]
            item_counter[it["name"]] += q
            total_qty += q
            cat, tags = classify(it["name"])
            cat_counter[cat] += q
            if "辣" in tags:
                spicy_qty += q
            if cat in ("甜筒冰淇淋",):
                dessert_qty += q
            if cat == "穷鬼套餐":
                value_qty += q
            if cat in ("麦乐鸡", "小食"):
                snack_qty += q

    n = len(orders)
    avg = spend / n if n else 0.0
    months = 1
    if first_t and last_t:
        months = max(1, round((last_t - first_t).days / 30.4))

    m = {
        "n_orders": n,
        "spend": spend,
        "avg_price": avg,
        "months": months,
        "first_time": first_t,
        "last_time": last_t,
        "timed_orders": timed,
        "night_orders": night,
        "breakfast_orders": breakfast,
        "night_ratio": night / timed if timed else 0.0,
        "breakfast_ratio": breakfast / timed if timed else 0.0,
        "total_qty": total_qty,
        "unique_items": len(item_counter),
        "exploration": len(item_counter) / total_qty if total_qty else 0.0,
        "spicy_share": spicy_qty / total_qty if total_qty else 0.0,
        "dessert_share": dessert_qty / total_qty if total_qty else 0.0,
        "value_share": value_qty / total_qty if total_qty else 0.0,
        "snack_share": snack_qty / total_qty if total_qty else 0.0,
        "top_items": item_counter.most_common(5),
        "top_cats": [(c, CATEGORY_LABELS.get(c, c)) for c, _ in cat_counter.most_common(3)],
        "cat_counter": cat_counter,
        "top_store": stores.most_common(1)[0] if stores else ("", 0),
        "store_count": len(stores),
    }
    m["dims"] = {
        "犒赏力": _clamp(avg / 55 * 100),
        "猎奇度": _clamp(m["exploration"] * 240),
        "夜猫指数": _clamp(m["night_ratio"] * 100),
        "辣度耐受": _clamp(m["spicy_share"] * 260),
        "甜度依赖": _clamp(m["dessert_share"] * 240),
    }
    return m


def pick_type(m):
    if m["n_orders"] < 3:
        return "newbie"
    if m["avg_price"] <= 16 and m["value_share"] >= 0.12:
        return "value"
    if m["spicy_share"] >= 0.24:
        return "spicy"
    if m["night_ratio"] >= 0.35:
        return "midnight"
    if m["dessert_share"] >= 0.28:
        return "sweet"
    if m["exploration"] >= 0.55:
        return "explorer"
    if m["breakfast_ratio"] >= 0.30:
        return "morning"
    if m["snack_share"] >= 0.40:
        return "happy"
    if m["avg_price"] >= 42:
        return "boss"
    if m["spicy_share"] >= 0.15:
        return "spicy"
    return "banzai"


def _fmt_money(x):
    return "%.1f" % x if x < 100 else "%.0f" % x


def render_profile(raw_orders, account=None):
    """完整链路：原始订单 → 规整 → metrics + 人格判词。"""
    orders = normalize_orders(raw_orders)
    m = compute_metrics(orders)
    type_id = pick_type(m)
    tpl = TYPES[type_id]
    top_name, top_count = (m["top_items"][0] if m["top_items"] else ("麦辣鸡腿堡", 0))
    top_cat_label = m["top_cats"][0][1] if m["top_cats"] else "麦当劳"
    verdict = tpl["verdict"].format(
        months=m["months"],
        orders=m["n_orders"],
        spend=_fmt_money(m["spend"]),
        avg="%.1f" % m["avg_price"],
        spicy_pct="%d%%" % round(m["spicy_share"] * 100),
        dessert_pct="%d%%" % round(m["dessert_share"] * 100),
        night_pct="%d%%" % round(m["night_ratio"] * 100),
        breakfast_pct="%d%%" % round(m["breakfast_ratio"] * 100),
        top_item=top_name,
        top_count=top_count,
        top_cat=top_cat_label,
        unique=m["unique_items"],
        points=(account or {}).get("accumulativePoint", "0"),
    )
    period = ""
    if m["first_time"] and m["last_time"]:
        period = "%s ~ %s" % (m["first_time"].strftime("%Y.%m.%d"), m["last_time"].strftime("%Y.%m.%d"))
    cert = "MCP-" + hashlib.md5(
        ("%s|%s|%s" % ((account or {}).get("accountId", "anon"), period, type_id)).encode("utf-8")
    ).hexdigest()[:8].upper()
    return {
        "type_id": type_id,
        "type": tpl,
        "metrics": m,
        "verdict": verdict,
        "period": period,
        "cert_id": cert,
        "account": account or {},
    }


# ---------------------------------------------------------------- 营养彩蛋

def _to_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().lower().replace("g", "").replace("mg", "").replace("kj", "").replace("kcal", "")
    s = s.replace("千卡", "").replace("大卡", "").replace("克", "").replace("毫克", "").replace("千焦", "")
    try:
        return float(s)
    except Exception:
        return None


def build_nutrition_index(foods):
    """从 list-nutrition-foods 的原始返回中提取 {名称: {energy, sodium}}，字段名宽容匹配。"""
    index = {}

    def walk(x):
        if isinstance(x, dict):
            name = x.get("foodName") or x.get("name") or x.get("productName")
            energy = sodium = None
            for k, v in x.items():
                kl = str(k).lower()
                if energy is None and ("能量" in str(k) or "热量" in str(k) or "energy" in kl or "calorie" in kl or "kcal" in kl):
                    energy = _to_float(v)
                if sodium is None and ("钠" in str(k) or "sodium" in kl):
                    sodium = _to_float(v)
            if name and (energy is not None or sodium is not None):
                index[str(name)] = {"energy": energy, "sodium": sodium}
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(foods)
    return index


def nutrition_eggs(m, index):
    """把 TOP 餐品匹配到营养数据，返回 (明细列表, 累计估算dict)。matched 明细含 name/qty/energy/sodium。"""
    if not index:
        return [], None
    matched, total_e, total_na = [], 0.0, 0.0
    for name, qty in m["top_items"]:
        best = None
        for fname, info in index.items():
            if name in fname or fname in name or (len(name) >= 3 and (name[:3] in fname or fname[:3] in name)):
                best = info
                break
        if best and best.get("energy"):
            e = best["energy"] * qty
            na = (best.get("sodium") or 0) * qty
            matched.append({"name": name, "qty": qty, "energy": e, "sodium": na})
            total_e += e
            total_na += na
    if not matched:
        return [], None
    return matched, {"energy": total_e, "sodium": total_na}
