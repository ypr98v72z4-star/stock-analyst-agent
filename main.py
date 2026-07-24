#!/usr/bin/env python3
"""
股票分析助手 — 主入口
用法:
    python main.py              # 执行完整分析流程
    python main.py --no-hermes  # 仅抓数据生成数据摘要 (不调用 Hermes)
    python main.py --no-push    # 不推送企业微信
"""
import os
import sys
import yaml
import argparse
from datetime import datetime

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.fetch_data import fetch_all
from scripts.generate_report import build_data_summary, format_report, save_report
from scripts.hermes_client import analyze, load_prompt
from scripts.wecom_push import send_wecom, send_summary


def load_config() -> dict:
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="股票分析助手")
    parser.add_argument("--no-hermes", action="store_true", help="仅抓数据，不调用 Hermes")
    parser.add_argument("--no-push", action="store_true", help="不推送企业微信")
    args = parser.parse_args()

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 股票分析助手启动")

    # 1. 加载配置
    config = load_config()
    print("✓ 配置加载完成")

    # 2. 抓取数据
    print("→ 正在抓取市场数据...")
    market_data = fetch_all(config)
    print(f"✓ 数据抓取完成 — {len(market_data['stocks'])} 只股票, {len(market_data['benchmarks'])} 个指数")

    # 保存原始数据
    os.makedirs("data", exist_ok=True)
    data_file = f"data/market_data_{market_data['date']}.json"
    import json
    # 序列化时跳过 DataFrame
    serializable = {
        "date": market_data["date"],
        "benchmarks": market_data["benchmarks"],
        "stocks": {
            sym: {
                "name": s["name"],
                "info": s["info"],
                "indicators": s["indicators"],
                "news": s["news"],
            }
            for sym, s in market_data["stocks"].items()
        },
    }
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"✓ 原始数据已保存: {data_file}")

    # 3. 生成数据摘要
    data_summary = build_data_summary(market_data)

    if args.no_hermes:
        # 仅输出数据摘要
        report_path = save_report(data_summary, config["report"]["output_dir"])
        print(f"✓ 数据摘要已保存: {report_path}")
        return

    # 4. 调用 Hermes 分析
    print("→ 正在调用 Hermes 进行分析...")
    system_prompt = load_prompt("system_prompt.md")
    analysis_template = load_prompt("daily_analysis.md")
    user_prompt = analysis_template.replace("{{data_summary}}", data_summary)

    hermes_analysis = analyze(config, system_prompt, user_prompt)
    print("✓ Hermes 分析完成")

    # 5. 生成最终报告
    report = format_report(hermes_analysis, market_data)
    report_path = save_report(report, config["report"]["output_dir"])
    print(f"✓ 日报已保存: {report_path}")

    # 6. 推送企业微信
    if not args.no_push:
        print("→ 正在推送到企业微信...")
        result = send_wecom(config, report)
        if result.get("errcode") == 0:
            print("✓ 推送成功")
        else:
            print(f"✗ 推送失败: {result}")

        # 额外推送精简摘要
        send_summary(config, report)
    else:
        print("→ 跳过企业微信推送 (--no-push)")

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 分析完成")


if __name__ == "__main__":
    main()
