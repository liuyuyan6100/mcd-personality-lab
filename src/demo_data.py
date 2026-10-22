"""演示模式合成数据：为「无历史订单」的用户/评委提供一份连贯的样本。

画像设定：麦辣系主导 + 深夜食客 + 中度猎奇 + 中高客单，
保证演示输出非平凡、各维度都有信号。
"""
import random
from datetime import datetime, timedelta

ITEM_POOL = [
    # (名称, 单价, 出现权重)
    ("麦辣鸡腿堡", 21.5, 36),
    ("麦辣鸡翅(2块)", 12.0, 20),
    ("大薯", 13.5, 10),
    ("中薯", 11.0, 8),
    ("可乐(中)", 9.0, 12),
    ("零度可乐(中)", 9.0, 5),
    ("麦旋风", 12.0, 7),
    ("甜筒", 6.0, 6),
    ("巨无霸", 25.5, 7),
    ("板烧鸡腿堡", 22.0, 8),
    ("麦乐鸡(5块)", 12.5, 9),
    ("玉米杯", 8.5, 4),
    ("香芋派", 8.5, 5),
    ("1+1随心配(双层吉士+美式)", 13.9, 10),
    ("安格斯厚牛堡", 32.0, 3),
    ("美式咖啡", 13.0, 4),
    ("麦满分(吉士蛋)", 15.0, 3),
    ("椰子水", 12.0, 2),
    ("鳕鱼堡", 20.0, 2),
    ("薯饼", 7.0, 3),
]

STORES = ["深圳海岸城餐厅", "深圳万象天地餐厅", "深圳科技园得来速", "深圳卓悦中心餐厅"]


def _weighted(pool, k):
    names = [p[0] for p in pool]
    weights = [p[2] for p in pool]
    return random.choices(names, weights=weights, k=k)


def build_demo_orders(seed=1024, count=52, end=None):
    random.seed(seed)
    end = end or datetime(2026, 10, 20, 20, 0, 0)
    start = end - timedelta(days=365)
    orders = []
    for i in range(count):
        # 时间分布：偏向晚间与深夜
        day = start + timedelta(days=random.randint(0, 364))
        hour = random.choices(
            [8, 11, 12, 13, 18, 19, 20, 21, 22, 23],
            weights=[3, 6, 9, 6, 8, 12, 10, 12, 14, 8],
        )[0]
        minute = random.randint(0, 59)
        t = day.replace(hour=hour, minute=minute)
        names = _weighted(ITEM_POOL, random.choices([1, 2, 3, 4], weights=[8, 22, 14, 6])[0])
        price_map = {p[0]: p[1] for p in ITEM_POOL}
        items, total = [], 0.0
        for nm in dict.fromkeys(names):
            qty = 1 if random.random() > 0.15 else 2
            items.append({
                "productName": nm,
                "quantity": qty,
                "price": price_map[nm],
            })
            total += price_map[nm] * qty
        orders.append({
            "orderId": "DEMO%04d" % i,
            "createTime": t.strftime("%Y-%m-%d %H:%M:%S"),
            "storeName": random.choice(STORES),
            "orderType": "1" if random.random() > 0.25 else "2",
            "orderProductList": items,
            "realTotalAmount": "%.2f" % round(total, 2),
        })
    orders.sort(key=lambda o: o["createTime"])
    return orders


if __name__ == "__main__":
    demo = build_demo_orders()
    print("demo orders:", len(demo), "first:", demo[0]["createTime"], "last:", demo[-1]["createTime"])
