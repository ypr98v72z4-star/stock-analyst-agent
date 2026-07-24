"""
数据抓取模块 — 从 yfinance 获取行情与新闻数据
"""
import yfinance as yf
import pandas as pd
from datetime import datetime


def fetch_stock_data(symbol: str, period: str = "5d", interval: str = "1d") -> dict:
    """抓取单只股票的行情数据"""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)

    info = {}
    try:
        fast = ticker.fast_info
        info = {
            "last_price": getattr(fast, "last_price", None),
            "previous_close": getattr(fast, "previous_close", None),
            "market_cap": getattr(fast, "market_cap", None),
            "fifty_day_avg": getattr(fast, "fifty_day_average", None),
            "two_hundred_day_avg": getattr(fast, "two_hundred_day_average", None),
        }
    except Exception:
        pass

    return {
        "symbol": symbol,
        "history": hist,
        "info": info,
    }


def fetch_news(symbol: str, max_items: int = 5) -> list[dict]:
    """抓取单只股票的相关新闻"""
    ticker = yf.Ticker(symbol)
    try:
        news = ticker.news or []
        results = []
        for item in news[:max_items]:
            results.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", ""),
                "link": item.get("link", ""),
                "publish_time": item.get("providerPublishTime", ""),
            })
        return results
    except Exception:
        return []


def fetch_benchmark(symbol: str, period: str = "5d") -> dict:
    """抓取指数基准数据"""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)

    if hist.empty:
        return {"symbol": symbol, "change_pct": None}

    latest = hist["Close"].iloc[-1]
    prev = hist["Close"].iloc[0]
    change_pct = ((latest - prev) / prev) * 100

    return {
        "symbol": symbol,
        "latest": round(latest, 2),
        "change_pct": round(change_pct, 2),
    }


def fetch_all(config: dict) -> dict:
    """
    抓取所有配置中定义的股票和指数数据
    返回: {
        "date": str,
        "benchmarks": list,
        "stocks": {symbol: {data, news, indicators}}
    }
    """
    from scripts.calculate_indicators import calculate_indicators

    ds = config["data_sources"]
    period = ds["market_data"]["period"]
    interval = ds["market_data"]["interval"]
    max_news = ds["news"]["max_per_stock"]

    today = datetime.now().strftime("%Y-%m-%d")

    # 基准指数
    benchmarks = []
    for bm in config["benchmarks"]:
        benchmarks.append(fetch_benchmark(bm["symbol"], period))

    # 股票池
    stocks = {}
    all_watchlist = config["watchlist"].get("hk", []) + config["watchlist"].get("us", [])
    for item in all_watchlist:
        sym = item["symbol"]
        name = item["name"]

        data = fetch_stock_data(sym, period, interval)
        news = fetch_news(sym, max_news)
        indicators = calculate_indicators(data["history"])

        stocks[sym] = {
            "name": name,
            "info": data["info"],
            "indicators": indicators,
            "news": news,
        }

    return {
        "date": today,
        "benchmarks": benchmarks,
        "stocks": stocks,
    }
