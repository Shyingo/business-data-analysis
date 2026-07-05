"""
visualize.py
数据可视化分析
对应课程报告：15+种可视化图表，涵盖分布分析、客户分群、时间趋势、
RFM分析、相关性分析、平行坐标、季节性分析等。
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import rcParams
import os

rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "PingFang SC"]
rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = "output/charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_clean_data():
    customers = pd.read_csv("output/customers_clean.csv", encoding="utf-8-sig")
    products = pd.read_csv("output/products_clean.csv", encoding="utf-8-sig")
    transactions = pd.read_csv("output/transactions_clean.csv", encoding="utf-8-sig")
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
    return customers, products, transactions


# ═══════════════════ 1. 分布分析（6合1子图） ═══════════════════

def plot_distribution_6in1(customers, products, transactions):
    """6种分布：交易金额、年龄、价格、收入、每单数量、利润率"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    transactions["profit_rate"] = (transactions["profit"] / transactions["total_amount"] * 100).clip(-50, 100)
    
    plots = [
        (axes[0, 0], transactions["total_amount"], "交易金额分布", "金额 (¥)", 30, "#5B9BD5"),
        (axes[0, 1], customers["age"], "客户年龄分布", "年龄", 15, "#FF8C94"),
        (axes[0, 2], products["price"], "产品价格分布", "价格 (¥)", 30, "#77DD77"),
        (axes[1, 0], customers["annual_income"], "客户年收入分布", "年收入 (¥)", 30, "#FFD700"),
        (axes[1, 1], transactions["n_items"], "每单商品数量分布", "商品数", range(1, 11), "#C39BD3"),
        (axes[1, 2], transactions["profit_rate"], "利润率分布", "利润率 (%)", 30, "#85C1E9"),
    ]
    
    for ax, data, title, xlabel, bins, color in plots:
        ax.hist(data, bins=bins, color=color, edgecolor="white", alpha=0.8)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel("频数", fontsize=11)
    
    plt.tight_layout(pad=3.0)
    fig.savefig(f"{OUTPUT_DIR}/01_分布分析6合1.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [01/21] 分布分析6合1")


# ═══════════════════ 2. 客户分群初步分析 ═══════════════════

def plot_customer_segmentation(customers):
    """客户分群：区域饼图、性别柱状图、细分柱状图"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 区域饼图
    region_counts = customers["region"].value_counts()
    colors1 = plt.cm.Set3(np.linspace(0, 1, len(region_counts)))
    axes[0].pie(region_counts.values, labels=region_counts.index, autopct="%1.1f%%",
                colors=colors1, startangle=90, textprops={"fontsize": 11})
    axes[0].set_title("客户区域分布", fontsize=14, fontweight="bold")
    
    # 性别柱状图
    gender_counts = customers["gender"].value_counts()
    bars1 = axes[1].bar(gender_counts.index, gender_counts.values,
                        color=["#5B9BD5", "#FF8C94"], edgecolor="white", width=0.4)
    axes[1].set_title("客户性别分布", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("人数", fontsize=11)
    for bar, val in zip(bars1, gender_counts.values):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                     str(val), ha="center", fontsize=12)
    
    # 细分柱状图
    seg_counts = customers["segment"].value_counts()
    colors3 = plt.cm.Set2(np.linspace(0, 1, len(seg_counts)))
    bars2 = axes[2].bar(seg_counts.index, seg_counts.values, color=colors3, edgecolor="white")
    axes[2].set_title("客户细分构成", fontsize=14, fontweight="bold")
    axes[2].set_ylabel("人数", fontsize=11)
    axes[2].set_xticklabels(seg_counts.index, rotation=15)
    for bar, val in zip(bars2, seg_counts.values):
        axes[2].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                     str(val), ha="center", fontsize=10)
    
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/02_客户分群分析.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [02/21] 客户分群分析")


# ═══════════════════ 3. 时间趋势 ═══════════════════

def plot_time_trends(transactions):
    """月度收入+交易量双折线"""
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    monthly = transactions.set_index("transaction_date").resample("ME").agg(
        月总收入=("total_amount", "sum"),
        交易笔数=("transaction_id", "count"),
    )
    
    ax2 = ax1.twinx()
    line1 = ax1.plot(monthly.index, monthly["月总收入"], color="#5B9BD5", linewidth=2,
                     marker="o", markersize=6, label="月总收入")
    line2 = ax2.plot(monthly.index, monthly["交易笔数"], color="#FF8C94", linewidth=2,
                     marker="s", markersize=6, label="交易笔数")
    
    ax1.set_xlabel("月份", fontsize=12)
    ax1.set_ylabel("月总收入 (¥)", fontsize=12, color="#5B9BD5")
    ax2.set_ylabel("交易笔数", fontsize=12, color="#FF8C94")
    ax1.set_title("月度收入与交易量趋势", fontsize=16, fontweight="bold")
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")
    
    ax1.xaxis.set_major_locator(ticker.MonthLocator())
    ax1.xaxis.set_major_formatter(ticker.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    
    fig.savefig(f"{OUTPUT_DIR}/03_月度收入与交易量趋势.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [03/21] 月度收入与交易量趋势")


# ═══════════════════ 4. 每日销售额趋势 ═══════════════════

def plot_daily_sales(transactions):
    fig, ax = plt.subplots(figsize=(14, 5))
    daily = transactions.set_index("transaction_date").resample("D")["total_amount"].sum()
    ax.plot(daily.index, daily.values, color="#5B9BD5", linewidth=1.0, alpha=0.7)
    ax.fill_between(daily.index, daily.values, alpha=0.1, color="#5B9BD5")
    ax.set_xlabel("日期", fontsize=12)
    ax.set_ylabel("销售额 (¥)", fontsize=12)
    ax.set_title("每日销售额趋势", fontsize=16, fontweight="bold")
    ax.xaxis.set_major_locator(ticker.MonthLocator())
    ax.xaxis.set_major_formatter(ticker.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    fig.savefig(f"{OUTPUT_DIR}/04_每日销售额趋势.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [04/21] 每日销售额趋势")


# ═══════════════════ 5. 月度销售额 ═══════════════════

def plot_monthly_sales(transactions):
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly = transactions.set_index("transaction_date").resample("ME")["total_amount"].sum()
    colors = plt.cm.Greens(np.linspace(0.3, 0.8, len(monthly)))
    bars = ax.bar(monthly.index.strftime("%Y-%m"), monthly.values, color=colors, edgecolor="white")
    ax.set_xlabel("月份", fontsize=12)
    ax.set_ylabel("销售额 (¥)", fontsize=12)
    ax.set_title("月度销售额", fontsize=16, fontweight="bold")
    ax.set_xticklabels(monthly.index.strftime("%Y-%m"), rotation=30, ha="right")
    for bar, val in zip(bars, monthly.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                f"¥{val/10000:.1f}万", ha="center", fontsize=9)
    fig.savefig(f"{OUTPUT_DIR}/05_月度销售额.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [05/21] 月度销售额")


# ═══════════════════ 6. 客户基础画像 ═══════════════════

def plot_gender_pie(customers):
    fig, ax = plt.subplots(figsize=(6, 6))
    counts = customers["gender"].value_counts()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%",
           colors=["#5B9BD5", "#FF8C94"], startangle=90, explode=(0.03, 0.03),
           textprops={"fontsize": 13})
    ax.set_title("客户性别分布", fontsize=16, fontweight="bold", pad=20)
    fig.savefig(f"{OUTPUT_DIR}/06_性别分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [06/21] 性别分布")


def plot_age_hist(customers):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(customers["age"], bins=range(15, 70, 5), color="#5B9BD5", edgecolor="white", alpha=0.8)
    ax.set_xlabel("年龄", fontsize=12)
    ax.set_ylabel("人数", fontsize=12)
    ax.set_title("客户年龄分布", fontsize=16, fontweight="bold")
    ax.set_xticks(range(15, 70, 5))
    fig.savefig(f"{OUTPUT_DIR}/07_年龄分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [07/21] 年龄分布")


def plot_city_bar(customers):
    fig, ax = plt.subplots(figsize=(10, 5))
    city_counts = customers["city"].value_counts().head(10)
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(city_counts)))
    bars = ax.bar(city_counts.index, city_counts.values, color=colors, edgecolor="white")
    ax.set_xlabel("城市", fontsize=12)
    ax.set_ylabel("客户数", fontsize=12)
    ax.set_title("Top10 客户城市分布", fontsize=16, fontweight="bold")
    for bar, val in zip(bars, city_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                str(val), ha="center", fontsize=10)
    fig.savefig(f"{OUTPUT_DIR}/08_城市分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [08/21] 城市分布")


def plot_member_level(customers):
    fig, ax = plt.subplots(figsize=(7, 5))
    seg_order = ["高价值客户", "VIP客户", "普通客户", "新客户", "沉睡客户"]
    counts = customers["segment"].value_counts()
    counts = counts.reindex([s for s in seg_order if s in counts.index])
    colors = ["#FFD700", "#00BFFF", "#A0A0A0", "#77DD77", "#FF8C94"]
    bars = ax.barh(counts.index, counts.values, color=colors[:len(counts)], edgecolor="white", height=0.6)
    ax.set_xlabel("人数", fontsize=12)
    ax.set_title("客户细分分布", fontsize=16, fontweight="bold")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=11)
    fig.savefig(f"{OUTPUT_DIR}/09_客户细分分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [09/21] 客户细分分布")


# ═══════════════════ 7. 产品分析 ═══════════════════

def plot_category_bar(products):
    fig, ax = plt.subplots(figsize=(10, 5))
    cat_counts = products["category"].value_counts()
    colors = plt.cm.Set2(np.linspace(0, 1, len(cat_counts)))
    bars = ax.bar(cat_counts.index, cat_counts.values, color=colors, edgecolor="white")
    ax.set_xlabel("品类", fontsize=12)
    ax.set_ylabel("产品数", fontsize=12)
    ax.set_title("产品品类分布", fontsize=16, fontweight="bold")
    ax.set_xticklabels(cat_counts.index, rotation=30, ha="right")
    for bar, val in zip(bars, cat_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(val), ha="center", fontsize=10)
    fig.savefig(f"{OUTPUT_DIR}/10_品类分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [10/21] 品类分布")


def plot_price_box(products):
    fig, ax = plt.subplots(figsize=(12, 6))
    categories = products["category"].unique()
    data = [products[products["category"] == c]["price"].values for c in categories]
    bp = ax.boxplot(data, labels=categories, patch_artist=True, showmeans=True,
                    meanprops={"marker": "D", "markerfacecolor": "red"})
    colors = plt.cm.Set2(np.linspace(0, 1, len(categories)))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_xlabel("品类", fontsize=12)
    ax.set_ylabel("价格 (¥)", fontsize=12)
    ax.set_title("各品类价格分布", fontsize=16, fontweight="bold")
    ax.set_xticklabels(categories, rotation=30, ha="right")
    fig.savefig(f"{OUTPUT_DIR}/11_品类价格箱线图.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [11/21] 品类价格箱线图")


def plot_price_hist(products):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(products["price"], bins=30, color="#FF8C94", edgecolor="white", alpha=0.8)
    ax.set_xlabel("价格 (¥)", fontsize=12)
    ax.set_ylabel("产品数", fontsize=12)
    ax.set_title("产品价格分布", fontsize=16, fontweight="bold")
    fig.savefig(f"{OUTPUT_DIR}/12_价格分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [12/21] 价格分布")


# ═══════════════════ 8. 交易分析 ═══════════════════

def plot_payment_method(transactions):
    fig, ax = plt.subplots(figsize=(6, 6))
    counts = transactions["payment_method"].value_counts()
    colors = ["#5B9BD5", "#FF8C94", "#FFD700", "#77DD77"]
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%",
           colors=colors, startangle=90, explode=[0.03] * len(counts),
           textprops={"fontsize": 12})
    ax.set_title("支付方式分布", fontsize=16, fontweight="bold", pad=20)
    fig.savefig(f"{OUTPUT_DIR}/13_支付方式分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [13/21] 支付方式分布")


def plot_order_status(transactions):
    fig, ax = plt.subplots(figsize=(7, 5))
    counts = transactions["status"].value_counts()
    order = ["已完成", "已退款", "处理中"]
    counts = counts.reindex(order).fillna(0)
    colors_bar = ["#77DD77", "#FF8C94", "#FFD700"]
    bars = ax.bar(counts.index, counts.values, color=colors_bar, edgecolor="white", width=0.5)
    ax.set_ylabel("订单数", fontsize=12)
    ax.set_title("订单状态分布", fontsize=16, fontweight="bold")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                str(int(val)), ha="center", fontsize=12)
    fig.savefig(f"{OUTPUT_DIR}/14_订单状态分布.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [14/21] 订单状态分布")


def plot_top_products(transactions, products):
    fig, ax = plt.subplots(figsize=(10, 6))
    merged = transactions.merge(products, on="product_id")
    top = merged.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(10)
    colors = plt.cm.Oranges(np.linspace(0.3, 0.9, 10))
    bars = ax.barh(top.index[::-1], top.values[::-1], color=colors[::-1], edgecolor="white")
    ax.set_xlabel("销量", fontsize=12)
    ax.set_title("Top10 畅销产品", fontsize=16, fontweight="bold")
    for bar, val in zip(bars, top.values[::-1]):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                str(int(val)), va="center", fontsize=10)
    fig.savefig(f"{OUTPUT_DIR}/15_Top10畅销产品.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [15/21] Top10畅销产品")


def plot_category_sales(transactions, products):
    fig, ax = plt.subplots(figsize=(8, 8))
    merged = transactions.merge(products, on="product_id")
    cat_sales = merged.groupby("category")["total_amount"].sum().sort_values(ascending=False)
    colors = plt.cm.Set3(np.linspace(0, 1, len(cat_sales)))
    ax.pie(cat_sales, labels=cat_sales.index, autopct="%1.1f%%",
           colors=colors, startangle=90, textprops={"fontsize": 10})
    ax.set_title("各品类销售额占比", fontsize=16, fontweight="bold", pad=20)
    fig.savefig(f"{OUTPUT_DIR}/16_品类销售额占比.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [16/21] 品类销售额占比")


# ═══════════════════ 9. RFM 分析 ═══════════════════

def plot_rfm_analysis(transactions, customers):
    """RFM客户价值模型分析"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    ref_date = transactions["transaction_date"].max() + pd.Timedelta(days=1)
    rfm = transactions.groupby("customer_id").agg(
        Recency=("transaction_date", lambda x: (ref_date - x.max()).days),
        Frequency=("transaction_id", "count"),
        Monetary=("total_amount", "sum"),
    ).reset_index()
    
    rfm = rfm.merge(customers[["customer_id", "segment"]], on="customer_id", how="left")
    
    # R、F、M 的分布
    axes[0].hist(rfm["Recency"], bins=20, color="#5B9BD5", edgecolor="white")
    axes[0].set_title("Recency (最近消费天数)", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("天数", fontsize=11)
    axes[0].set_ylabel("客户数", fontsize=11)
    
    axes[1].hist(rfm["Frequency"], bins=20, color="#FF8C94", edgecolor="white")
    axes[1].set_title("Frequency (消费频次)", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("次数", fontsize=11)
    axes[1].set_ylabel("客户数", fontsize=11)
    
    axes[2].hist(rfm["Monetary"], bins=20, color="#77DD77", edgecolor="white")
    axes[2].set_title("Monetary (消费金额)", fontsize=13, fontweight="bold")
    axes[2].set_xlabel("金额 (¥)", fontsize=11)
    axes[2].set_ylabel("客户数", fontsize=11)
    
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/17_RFM分析.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [17/21] RFM分析")
    
    # 保存RFM数据
    rfm.to_csv("output/rfm_scores.csv", index=False, encoding="utf-8-sig")


# ═══════════════════ 10. 交叉分析 ═══════════════════

def plot_segment_sales(transactions, customers):
    """客户细分 vs 消费金额箱线图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    merged = transactions.merge(customers, on="customer_id")
    order = ["高价值客户", "VIP客户", "普通客户", "新客户", "沉睡客户"]
    data = [merged[merged["segment"] == s]["total_amount"].values for s in order if s in merged["segment"].unique()]
    labels = [s for s in order if s in merged["segment"].unique()]
    bp = ax.boxplot(data, labels=labels, patch_artist=True, showmeans=True,
                    meanprops={"marker": "D", "markerfacecolor": "red"})
    colors = ["#FFD700", "#00BFFF", "#A0A0A0", "#77DD77", "#FF8C94"][:len(labels)]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_xlabel("客户细分", fontsize=12)
    ax.set_ylabel("消费金额 (¥)", fontsize=12)
    ax.set_title("客户细分 vs 消费金额", fontsize=16, fontweight="bold")
    fig.savefig(f"{OUTPUT_DIR}/18_客户细分vs消费.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [18/21] 客户细分vs消费")


def plot_scatter_income_spending(transactions, customers):
    """年收入 vs 消费金额散点图 + 趋势线"""
    fig, ax = plt.subplots(figsize=(10, 7))
    customer_spending = transactions.groupby("customer_id")["total_amount"].sum().reset_index()
    customer_spending.columns = ["customer_id", "total_spent"]
    merged = customer_spending.merge(customers, on="customer_id")
    
    ax.scatter(merged["annual_income"], merged["total_spent"], alpha=0.5, s=30, c="#5B9BD5")
    
    z = np.polyfit(merged["annual_income"], merged["total_spent"], 1)
    p = np.poly1d(z)
    x_sorted = np.sort(merged["annual_income"])
    ax.plot(x_sorted, p(x_sorted), "r--", alpha=0.8, linewidth=2, label="趋势线")
    
    ax.set_xlabel("年收入 (¥)", fontsize=12)
    ax.set_ylabel("总消费金额 (¥)", fontsize=12)
    ax.set_title("客户年收入 vs 总消费金额", fontsize=16, fontweight="bold")
    ax.legend(fontsize=12)
    
    fig.savefig(f"{OUTPUT_DIR}/19_收入vs消费散点图.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [19/21] 收入vs消费散点图")


def plot_correlation_heatmap(transactions, customers):
    """相关性热力图"""
    fig, ax = plt.subplots(figsize=(9, 7))
    
    merged = transactions.merge(customers, on="customer_id")
    numeric_cols = ["total_amount", "n_items", "profit", "age", "annual_income"]
    corr_data = merged[numeric_cols].corr()
    
    labels = ["消费金额", "商品数量", "利润", "客户年龄", "客户收入"]
    im = ax.imshow(corr_data.values, cmap="coolwarm", vmin=-1, vmax=1)
    
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11, rotation=30, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_title("数值变量相关性热力图", fontsize=16, fontweight="bold", pad=20)
    
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr_data.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=12,
                    color="white" if abs(val) > 0.5 else "black")
    
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("相关系数", fontsize=11)
    
    fig.savefig(f"{OUTPUT_DIR}/20_相关性热力图.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [20/21] 相关性热力图")


def plot_seasonal_analysis(transactions):
    """季节性分析——月度模式"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    transactions["month"] = transactions["transaction_date"].dt.month
    monthly_pattern = transactions.groupby("month").agg(
        月总收入=("total_amount", "sum"),
        平均交易额=("total_amount", "mean"),
        交易笔数=("transaction_id", "count"),
        总利润=("profit", "sum"),
    ).reset_index()
    
    month_names = ["1月", "2月", "3月", "4月", "5月", "6月",
                   "7月", "8月", "9月", "10月", "11月", "12月"]
    
    axes[0, 0].bar(monthly_pattern["month"], monthly_pattern["月总收入"],
                   color="#5B9BD5", edgecolor="white")
    axes[0, 0].set_title("月度总收入", fontsize=13, fontweight="bold")
    axes[0, 0].set_xticks(range(1, 13))
    axes[0, 0].set_xticklabels(month_names, rotation=30)
    
    axes[0, 1].plot(monthly_pattern["month"], monthly_pattern["平均交易额"],
                    color="#FF8C94", marker="o", linewidth=2)
    axes[0, 1].set_title("月平均交易额", fontsize=13, fontweight="bold")
    axes[0, 1].set_xticks(range(1, 13))
    axes[0, 1].set_xticklabels(month_names, rotation=30)
    
    axes[1, 0].bar(monthly_pattern["month"], monthly_pattern["交易笔数"],
                   color="#77DD77", edgecolor="white")
    axes[1, 0].set_title("月度交易笔数", fontsize=13, fontweight="bold")
    axes[1, 0].set_xticks(range(1, 13))
    axes[1, 0].set_xticklabels(month_names, rotation=30)
    
    axes[1, 1].plot(monthly_pattern["month"], monthly_pattern["总利润"],
                    color="#FFD700", marker="s", linewidth=2)
    axes[1, 1].set_title("月度总利润", fontsize=13, fontweight="bold")
    axes[1, 1].set_xticks(range(1, 13))
    axes[1, 1].set_xticklabels(month_names, rotation=30)
    
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/21_季节性分析.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("   [21/21] 季节性分析")


# ═══════════════════ 主入口 ═══════════════════

def generate_all():
    print("📂 加载清洗后数据...")
    customers, products, transactions = load_clean_data()
    print(f"   客户: {len(customers)} | 产品: {len(products)} | 交易: {len(transactions)}")
    
    print("\n🎨 生成全部图表 (21张)...\n")
    
    plot_distribution_6in1(customers, products, transactions)
    plot_customer_segmentation(customers)
    plot_time_trends(transactions)
    plot_daily_sales(transactions)
    plot_monthly_sales(transactions)
    plot_gender_pie(customers)
    plot_age_hist(customers)
    plot_city_bar(customers)
    plot_member_level(customers)
    plot_category_bar(products)
    plot_price_box(products)
    plot_price_hist(products)
    plot_payment_method(transactions)
    plot_order_status(transactions)
    plot_top_products(transactions, products)
    plot_category_sales(transactions, products)
    plot_rfm_analysis(transactions, customers)
    plot_segment_sales(transactions, customers)
    plot_scatter_income_spending(transactions, customers)
    plot_correlation_heatmap(transactions, customers)
    plot_seasonal_analysis(transactions)
    
    print(f"\n✅ 全部图表已保存到 {OUTPUT_DIR}/，共21张")


if __name__ == "__main__":
    generate_all()
