"""
generate_data.py
商业模拟数据生成器
生成客户信息、产品信息、交易记录等完整商业数据集。
包含客户收入、产品成本、利润等字段，支持RFM等多维度分析。
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker("zh_CN")
Faker.seed(42)
np.random.seed(42)

OUTPUT_DIR = "data"


def ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_customers(n=500) -> pd.DataFrame:
    """生成客户信息表——包含收入、细分、区域等字段"""
    genders = np.random.choice(["男", "女"], size=n, p=[0.48, 0.52])
    ages = np.random.randint(18, 65, size=n)
    
    regions = np.random.choice(["华东", "华南", "华北", "华中", "西南", "西北", "东北"], size=n,
                                p=[0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.10])
    
    # 各区域对应的城市
    city_map = {
        "华东": ["上海", "杭州", "南京", "苏州", "宁波"],
        "华南": ["广州", "深圳", "东莞", "佛山", "厦门"],
        "华北": ["北京", "天津", "石家庄", "太原", "济南"],
        "华中": ["武汉", "长沙", "郑州", "南昌", "合肥"],
        "西南": ["成都", "重庆", "昆明", "贵阳", "拉萨"],
        "西北": ["西安", "兰州", "银川", "西宁", "乌鲁木齐"],
        "东北": ["沈阳", "大连", "哈尔滨", "长春", "大庆"],
    }
    
    cities = []
    for r in regions:
        cities.append(np.random.choice(city_map[r]))
    
    # 年收入：用对数正态分布模拟真实收入分布
    annual_incomes = np.round(np.random.lognormal(mean=10.5, sigma=0.6, size=n), 0).astype(int)
    annual_incomes = np.clip(annual_incomes, 30000, 500000)
    
    # 客户细分
    segments = np.random.choice(
        ["高价值客户", "普通客户", "新客户", "沉睡客户", "VIP客户"],
        size=n, p=[0.15, 0.35, 0.20, 0.18, 0.12]
    )
    
    # 注册日期
    reg_days = np.random.randint(0, 1095, size=n)
    reg_dates = [datetime.today() - timedelta(days=int(d)) for d in reg_days]
    
    df = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(1, n + 1)],
        "name": [fake.name() for _ in range(n)],
        "gender": genders,
        "age": ages,
        "region": regions,
        "city": cities,
        "annual_income": annual_incomes,
        "segment": segments,
        "registration_date": reg_dates,
    })
    # 2% 缺失值
    for col in ["annual_income", "segment"]:
        missing_idx = np.random.choice(df.index, size=int(n * 0.02), replace=False)
        df.loc[missing_idx, col] = np.nan
    return df


def generate_products(n=200) -> pd.DataFrame:
    """生成产品信息表——包含成本价，用于计算利润"""
    categories = np.random.choice(
        ["电子产品", "服装鞋帽", "食品饮料", "家居用品", "图书文具", "美妆护肤", "运动户外", "母婴用品"],
        size=n, p=[0.18, 0.16, 0.14, 0.13, 0.12, 0.10, 0.09, 0.08]
    )
    brand_prefixes = ["极速", "暖阳", "清爽", "智能", "简约", "经典", "轻盈", "舒适"]
    
    prices = np.round(np.random.uniform(10, 5000, size=n), 2)
    # 成本为价格的 40%-80%
    cost_ratios = np.random.uniform(0.4, 0.8, size=n)
    costs = np.round(prices * cost_ratios, 2)
    stocks = np.random.randint(0, 1000, size=n)
    
    names = []
    for cat in categories:
        type_map = {
            "电子产品": ["无线耳机", "充电宝", "键盘", "鼠标", "台灯", "智能音箱"],
            "服装鞋帽": ["运动鞋", "卫衣", "牛仔裤", "T恤", "帽子", "外套"],
            "食品饮料": ["坚果礼盒", "咖啡豆", "花茶", "巧克力", "蜂蜜"],
            "家居用品": ["抱枕", "香薰", "收纳盒", "保温杯", "毛巾套装"],
            "图书文具": ["笔记本", "钢笔", "日历", "手账本", "书签"],
            "美妆护肤": ["精华液", "面膜", "防晒霜", "唇膏", "洁面乳"],
            "运动户外": ["背包", "瑜伽垫", "水壶", "跳绳", "护膝"],
            "母婴用品": ["婴儿湿巾", "摇铃", "奶瓶", "围兜", "故事书"],
        }
        t = np.random.choice(type_map.get(cat, ["通用商品"]))
        brand = np.random.choice(brand_prefixes)
        names.append(f"{brand}{t}")
    
    df = pd.DataFrame({
        "product_id": [f"P{i:04d}" for i in range(1, n + 1)],
        "product_name": names,
        "category": categories,
        "price": prices,
        "cost": costs,
        "profit_margin": np.round((prices - costs) / prices * 100, 2),
        "stock": stocks,
    })
    return df


def generate_transactions(customers: pd.DataFrame, products: pd.DataFrame, n=10000) -> pd.DataFrame:
    """生成交易记录表——包含利润、n_items等字段"""
    start_date = datetime.today() - timedelta(days=365)
    dates = [start_date + timedelta(days=int(d)) for d in np.random.randint(0, 365, size=n)]
    customer_ids = np.random.choice(customers["customer_id"], size=n)
    product_ids = np.random.choice(products["product_id"], size=n)
    
    price_map = products.set_index("product_id")["price"].to_dict()
    cost_map = products.set_index("product_id")["cost"].to_dict()
    
    quantities = np.random.randint(1, 10, size=n)
    unit_prices = [price_map[pid] for pid in product_ids]
    unit_costs = [cost_map[pid] for pid in product_ids]
    
    total_amounts = np.round(np.array(unit_prices) * quantities * np.random.uniform(0.9, 1.1, size=n), 2)
    total_costs = np.round(np.array(unit_costs) * quantities * np.random.uniform(0.9, 1.1, size=n), 2)
    profits = total_amounts - total_costs
    
    payment_methods = np.random.choice(
        ["微信支付", "支付宝", "银行卡", "信用卡"], size=n, p=[0.35, 0.30, 0.20, 0.15]
    )
    statuses = np.random.choice(["已完成", "已完成", "已完成", "已退款", "处理中"], size=n,
                                 p=[0.80, 0.05, 0.05, 0.06, 0.04])
    
    df = pd.DataFrame({
        "transaction_id": [f"T{i:06d}" for i in range(1, n + 1)],
        "customer_id": customer_ids,
        "product_id": product_ids,
        "quantity": quantities,
        "n_items": quantities,
        "unit_price": unit_prices,
        "total_amount": total_amounts,
        "cost": total_costs,
        "profit": np.round(profits, 2),
        "transaction_date": dates,
        "payment_method": payment_methods,
        "status": statuses,
    })
    return df


def save_data():
    ensure_dir()
    customers = generate_customers(500)
    products = generate_products(200)
    transactions = generate_transactions(customers, products, 10000)

    customers.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False, encoding="utf-8-sig")
    products.to_csv(f"{OUTPUT_DIR}/products.csv", index=False, encoding="utf-8-sig")
    transactions.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False, encoding="utf-8-sig")

    print(f"✅ 数据生成完成！")
    print(f"   - 客户表: {len(customers)} 条 -> data/customers.csv")
    print(f"   - 产品表: {len(products)} 条 -> data/products.csv")
    print(f"   - 交易表: {len(transactions)} 条 -> data/transactions.csv")


if __name__ == "__main__":
    save_data()
