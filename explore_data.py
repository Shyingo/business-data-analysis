"""
explore_data.py
数据探索与清洗
对应课程报告中的数据质量检查、基本统计、分布分析、客户分群初步分析、时间趋势探索。
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data():
    customers = pd.read_csv(f"{DATA_DIR}/customers.csv", encoding="utf-8-sig")
    products = pd.read_csv(f"{DATA_DIR}/products.csv", encoding="utf-8-sig")
    transactions = pd.read_csv(f"{DATA_DIR}/transactions.csv", encoding="utf-8-sig")
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
    return customers, products, transactions


def basic_stats(transactions):
    """基本统计与概述——时间跨度、总交易次数、总金额"""
    print("\n" + "=" * 55)
    print("【基本统计与概述】")
    print("=" * 55)
    print(f"时间范围: {transactions['transaction_date'].min()} 至 {transactions['transaction_date'].max()}")
    print(f"总交易次数: {len(transactions)}")
    print(f"总交易金额: ¥{transactions['total_amount'].sum():,.2f}")
    print(f"总利润: ¥{transactions['profit'].sum():,.2f}")
    print(f"平均客单价: ¥{transactions['total_amount'].mean():,.2f}")


def quality_check(customers, products, transactions):
    """数据质量检查——缺失值分析"""
    print("\n" + "=" * 55)
    print("【数据质量检查】")
    print("=" * 55)
    for name, df in [("客户表", customers), ("产品表", products), ("交易表", transactions)]:
        total_cells = df.shape[0] * df.shape[1]
        missing = df.isnull().sum().sum()
        missing_pct = (missing / total_cells) * 100
        print(f"\n{name}:")
        print(f"   形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        print(f"   缺失单元数: {missing} / {total_cells} ({missing_pct:.2f}%)")
        print(f"   重复行数: {df.duplicated().sum()}")
        # 列出具体有缺失的列
        missing_cols = df.isnull().sum()
        missing_cols = missing_cols[missing_cols > 0]
        if len(missing_cols) > 0:
            print(f"   缺失列详情:")
            for col, cnt in missing_cols.items():
                print(f"       {col}: {cnt} 个缺失 ({cnt/len(df)*100:.2f}%)")


def distribution_analysis(customers, products, transactions):
    """分布分析——交易金额、年龄、价格、收入、每单数量、利润率"""
    print("\n" + "=" * 55)
    print("【分布分析】")
    print("=" * 55)
    
    # 交易金额分布
    print(f"\n交易金额:")
    print(f"   均值: ¥{transactions['total_amount'].mean():.2f}")
    print(f"   中位数: ¥{transactions['total_amount'].median():.2f}")
    print(f"   标准差: ¥{transactions['total_amount'].std():.2f}")
    print(f"   最小值: ¥{transactions['total_amount'].min():.2f}")
    print(f"   最大值: ¥{transactions['total_amount'].max():.2f}")
    
    # 客户年龄分布
    print(f"\n客户年龄:")
    print(f"   均值: {customers['age'].mean():.1f} 岁")
    print(f"   中位数: {customers['age'].median():.1f} 岁")
    print(f"   年龄范围: {customers['age'].min()} ~ {customers['age'].max()} 岁")
    
    # 产品价格分布
    print(f"\n产品价格:")
    print(f"   均值: ¥{products['price'].mean():.2f}")
    print(f"   中位数: ¥{products['price'].median():.2f}")
    print(f"   价格范围: ¥{products['price'].min():.2f} ~ ¥{products['price'].max():.2f}")
    
    # 客户收入分布
    print(f"\n客户年收入:")
    print(f"   均值: ¥{customers['annual_income'].mean():,.0f}")
    print(f"   中位数: ¥{customers['annual_income'].median():,.0f}")
    print(f"   收入范围: ¥{customers['annual_income'].min():,.0f} ~ ¥{customers['annual_income'].max():,.0f}")
    
    # 每单商品数量分布
    print(f"\n每单商品数:")
    print(f"   均值: {transactions['n_items'].mean():.1f} 件")
    print(f"   中位数: {transactions['n_items'].median():.1f} 件")
    print(f"   范围: {transactions['n_items'].min()} ~ {transactions['n_items'].max()} 件")
    
    # 利润率分布
    transactions["profit_rate"] = (transactions["profit"] / transactions["total_amount"] * 100)
    print(f"\n利润率 (%):")
    print(f"   均值: {transactions['profit_rate'].mean():.2f}%")
    print(f"   中位数: {transactions['profit_rate'].median():.2f}%")
    print(f"   范围: {transactions['profit_rate'].min():.2f}% ~ {transactions['profit_rate'].max():.2f}%")


def customer_segmentation(customers):
    """客户分群初步分析——地域分布、性别比例、客户细分构成"""
    print("\n" + "=" * 55)
    print("【客户分群初步分析】")
    print("=" * 55)
    
    # 地域分布
    print(f"\n区域分布:")
    region_counts = customers["region"].value_counts()
    for region, count in region_counts.items():
        print(f"   {region}: {count}人 ({count/len(customers)*100:.1f}%)")
    
    # 性别比例
    print(f"\n性别比例:")
    gender_counts = customers["gender"].value_counts()
    for gender, count in gender_counts.items():
        print(f"   {gender}: {count}人 ({count/len(customers)*100:.1f}%)")
    
    # 客户细分构成
    print(f"\n客户细分构成:")
    seg_counts = customers["segment"].value_counts()
    for seg, count in seg_counts.items():
        print(f"   {seg}: {count}人 ({count/len(customers)*100:.1f}%)")


def time_trends(transactions):
    """时间趋势初步探索——月度收入趋势、交易量变化"""
    print("\n" + "=" * 55)
    print("【时间趋势初步探索】")
    print("=" * 55)
    
    transactions["year_month"] = transactions["transaction_date"].dt.to_period("M")
    monthly = transactions.groupby("year_month").agg(
        月总收入=("total_amount", "sum"),
        交易笔数=("transaction_id", "count"),
    ).sort_index()
    
    print(f"\n月度收入趋势:")
    for period, row in monthly.iterrows():
        print(f"   {period}: ¥{row['月总收入']:>10,.2f}  |  {int(row['交易笔数'])} 笔")
    
    # 识别峰值月份
    max_month = monthly["月总收入"].idxmax()
    print(f"\n📈 收入峰值月份: {max_month} (¥{monthly.loc[max_month, '月总收入']:,.2f})")


def clean_and_save(customers, products, transactions):
    """清洗数据并保存"""
    print("\n" + "=" * 55)
    print("【数据清洗】")
    print("=" * 55)
    
    # 客户表清洗
    c = customers.copy()
    c["annual_income"] = c["annual_income"].fillna(c["annual_income"].median())
    c["segment"] = c["segment"].fillna("未知")
    c = c[(c["age"] >= 18) & (c["age"] <= 65)]
    print(f"   客户表: 缺失值已填充, 异常年龄已过滤 -> {len(c)} 条")
    
    # 产品表清洗
    p = products.copy()
    median_stock = p["stock"].median()
    p["stock"] = p["stock"].fillna(median_stock).astype(int)
    p = p[p["price"] > 0]
    print(f"   产品表: 缺失库存已填充, 异常价格已过滤 -> {len(p)} 条")
    
    # 交易表清洗
    t = transactions.copy()
    before = len(t)
    t = t[t["total_amount"] > 0]
    t = t[t["profit"].notna()]
    print(f"   交易表: 异常金额已过滤 -> {len(t)} 条 (移除 {before - len(t)} 条)")
    
    # 保存清洗后数据
    c.to_csv(f"{OUTPUT_DIR}/customers_clean.csv", index=False, encoding="utf-8-sig")
    p.to_csv(f"{OUTPUT_DIR}/products_clean.csv", index=False, encoding="utf-8-sig")
    t.to_csv(f"{OUTPUT_DIR}/transactions_clean.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ 清洗后数据已保存到 {OUTPUT_DIR}/")
    
    return c, p, t


def main():
    print("📂 加载数据...")
    customers, products, transactions = load_data()
    
    basic_stats(transactions)
    quality_check(customers, products, transactions)
    distribution_analysis(customers, products, transactions)
    customer_segmentation(customers)
    time_trends(transactions)
    clean_and_save(customers, products, transactions)


if __name__ == "__main__":
    main()
