"""
报告生成模块 — 将 Hermes 分析结果整理为统一日报格式
"""
import os
import json
from datetime import datetime


def build_data_summary(market_data: dict) -> str:
    """
    将原始市场数据整理为 Hermes 可读的文本摘要
    """
    lines = []
    lines.append(f"# 市场数据摘要 ({market_data['date']})")
    lines.append("")

    # 基准指数
    lines.append("## 大盘指数")
    for bm in market_data["benchmarks"]:
        direction = "↑" if bm.get("change_pct", 0) and bm["change_pct"] > 0 else "↓"
        pct = bm.get("change_pct", "N/A")
        lines.append(f"- {bm['symbol']}: {bm.get('latest', 'N/A')} ({direction} {pct}%)")
    lines.append("")

    # 个股数据 (按市场分组)
    lines.append("## 自选股数据")
    
    # 按市场分组
    markets = {}
    for sym, stock in market_data["stocks"].items():
        market = stock.get("market", "其他")
        if market not in markets:
            markets[market] = []
        markets[market].append((sym, stock))
    
    for market_name, stock_list in markets.items():
        lines.append(f"\n### {market_name}")
        for sym, stock in stock_list:
            ind = stock.get("indicators", {})
            info = stock.get("info", {})
            lines.append(f"\n#### {stock['name']} ({sym})")
            lines.append(f"- 收盘价: {ind.get('latest_close', 'N/A')}")
            lines.append(f"- 涨跌幅: {ind.get('change_pct', 'N/A')}%")
            lines.append(f"- 成交量比: {ind.get('volume_ratio', 'N/A')}x 均量")
            if ind.get("rsi"):
                lines.append(f"- RSI: {ind['rsi']}")
            if ind.get("volatility"):
                lines.append(f"- 波动率(年化): {ind['volatility']}%")
            if ind.get("ma5"):
                lines.append(f"- MA5: {ind['ma5']} / MA10: {ind.get('ma10', 'N/A')}")

            # 新闻
            news = stock.get("news", [])
            if news:
                lines.append(f"- 近期新闻:")
                for n in news[:3]:
                    lines.append(f"  - {n['title']}")

    return "\n".join(lines)


def format_report(hermes_analysis: str, market_data: dict) -> str:
    """
    将 Hermes 分析结果格式化为最终日报
    """
    date_str = market_data["date"]

    report = f"""# 📊 股票分析日报 — {date_str}

---

## 一、市场总览

{hermes_analysis}

---

## 二、自选股表现

| 股票 | 收盘价 | 涨跌幅 | RSI | 量能 |
|------|--------|--------|-----|------|
"""
    for sym, stock in market_data["stocks"].items():
        ind = stock.get("indicators", {})
        rsi = ind.get("rsi", "-")
        vol_ratio = ind.get("volume_ratio", "-")
        report += f"| {stock['name']} | {ind.get('latest_close', '-')} | {ind.get('change_pct', '-')}% | {rsi} | {vol_ratio}x |\n"

    report += f"""
---

## 三、风险提示

> ⚠️ 本报告由 AI 自动生成，仅供参考，不构成投资建议。
> 投资有风险，入市需谨慎。

---
*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    return report


def save_report(report: str, output_dir: str = "reports") -> str:
    """保存报告到文件, 返回文件路径"""
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"daily_report_{date_str}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    return filepath
