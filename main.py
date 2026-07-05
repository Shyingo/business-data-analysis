"""
main.py
商业数据分析与可视化系统 — 主程序入口
一键运行：生成数据 → 清洗探索 → 可视化（21张图表）
"""

import subprocess
import sys
import os


def print_header():
    print("=" * 55)
    print("   商业数据分析与可视化系统")
    print("   Business Data Analysis & Visualization")
    print("   浙江科技大学 · 数据可视化课程报告")
    print("=" * 55)


def run_step(step_name, script_name):
    print(f"\n{'─' * 55}")
    print(f"  STEP: {step_name}")
    print(f"{'─' * 55}\n")
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    return result.returncode == 0


def main():
    print_header()

    steps = [
        ("1/3  生成模拟数据集", "generate_data.py"),
        ("2/3  数据探索与清洗", "explore_data.py"),
        ("3/3  可视化分析（21张图表）", "visualize.py"),
    ]

    success = True
    for step_name, script in steps:
        if not os.path.exists(script):
            print(f"  ❌ 找不到 {script}")
            success = False
            break
        ok = run_step(step_name, script)
        if not ok:
            print(f"  ❌ {step_name} 执行失败")
            success = False
            break

    if success:
        print(f"\n{'=' * 55}")
        print("  ✅ 所有步骤执行完成！")
        print(f"{'=' * 55}")
        print("\n📁 输出文件：")
        print("   data/")
        print("     ├── customers.csv        # 原始客户数据（含收入/区域/细分）")
        print("     ├── products.csv          # 原始产品数据（含成本/利润率）")
        print("     └── transactions.csv      # 原始交易数据（含利润）")
        print("   output/")
        print("     ├── customers_clean.csv   # 清洗后客户数据")
        print("     ├── products_clean.csv    # 清洗后产品数据")
        print("     ├── transactions_clean.csv # 清洗后交易数据")
        print("     ├── rfm_scores.csv        # RFM评分数据")
        print("     └── charts/              # 21张可视化图表")
        print("\n💡 提示：")
        print("   - 单独运行 python visualize.py 重新出图")
        print("   - 修改 generate_data.py 参数调整数据规模")
        print("   - 图表位于 output/charts/ 目录")
    else:
        print(f"\n  ❌ 执行中断，请检查错误信息")


if __name__ == "__main__":
    main()
