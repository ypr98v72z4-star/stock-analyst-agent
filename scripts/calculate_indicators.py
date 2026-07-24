"""
技术指标计算模块
"""
import pandas as pd
import numpy as np


def calculate_indicators(hist: pd.DataFrame) -> dict:
    """
    从历史行情计算关键技术指标
    hist: yfinance 返回的 DataFrame (columns: Open, High, Low, Close, Volume)
    """
    if hist.empty or len(hist) < 2:
        return {}

    close = hist["Close"]
    volume = hist["Volume"]

    latest_close = round(float(close.iloc[-1]), 2)
    prev_close = round(float(close.iloc[-2]), 2)
    change = round(latest_close - prev_close, 2)
    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0

    # 区间高低
    period_high = round(float(hist["High"].max()), 2)
    period_low = round(float(hist["Low"].min()), 2)

    # 成交量变化
    avg_volume = round(float(volume.mean()), 0)
    latest_volume = round(float(volume.iloc[-1]), 0)
    volume_ratio = round(latest_volume / avg_volume, 2) if avg_volume else 0

    # 简单移动平均 (如果数据足够)
    ma5 = round(float(close.rolling(5).mean().iloc[-1]), 2) if len(close) >= 5 else None
    ma10 = round(float(close.rolling(10).mean().iloc[-1]), 2) if len(close) >= 10 else None

    # 波动率 (日收益率标准差, 年化)
    returns = close.pct_change().dropna()
    volatility = round(float(returns.std() * np.sqrt(252) * 100), 2) if len(returns) >= 3 else None

    # RSI (14日, 数据不足时用可用天数)
    rsi = _calc_rsi(close, period=min(14, len(close) - 1))

    return {
        "latest_close": latest_close,
        "prev_close": prev_close,
        "change": change,
        "change_pct": change_pct,
        "period_high": period_high,
        "period_low": period_low,
        "avg_volume": avg_volume,
        "latest_volume": latest_volume,
        "volume_ratio": volume_ratio,
        "ma5": ma5,
        "ma10": ma10,
        "volatility": volatility,
        "rsi": rsi,
    }


def _calc_rsi(series: pd.Series, period: int = 14) -> float | None:
    """计算 RSI"""
    if len(series) < period + 1:
        return None
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)
