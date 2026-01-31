from io import StringIO
from typing import Callable, cast

import pandas as pd
from fastmcp import Context
from pydantic import Field

from ..server import mcp
from ..shared.fields import field_market, field_symbol
from .stocks import stock_info, stock_news, stock_prices


@mcp.tool(
    title="个股综合诊断",
    description="复合技能：一键获取技术面、基本面和消息面的综合诊断数据",
)
async def composite_stock_diagnostic(
    symbol: str = field_symbol,
    market: str = field_market,
    ctx: Context | None = None,
):
    if ctx:
        await ctx.report_progress(0, 100, "开始综合诊断...")

    # 内部组合调用
    stock_prices_fn = cast(Callable[..., str], stock_prices)
    stock_info_fn = cast(Callable[..., str], stock_info)
    stock_news_fn = cast(Callable[..., str], stock_news)

    if ctx:
        await ctx.report_progress(20, 100, "获取历史价格...")
    price_data = stock_prices_fn(symbol, market, limit=5)

    if ctx:
        await ctx.report_progress(40, 100, "获取基本面信息...")
    fundamental = stock_info_fn(symbol, market)

    if ctx:
        await ctx.report_progress(60, 100, "获取新闻动态...")
    news = stock_news_fn(symbol, limit=3)

    if ctx:
        await ctx.report_progress(80, 100, "汇总分析结果...")

    result = (
        f"--- 综合诊断报告: {symbol} ---\n\n[近期价格]\n{price_data}\n\n[基本面]\n{fundamental}\n\n[核心新闻]\n{news}"
    )

    if ctx:
        await ctx.report_progress(100, 100, "诊断完成")

    return result


@mcp.tool(
    title="生成走势字符图",
    description="根据提供的价格列表生成一个简单的 ASCII 走势图，用于直观展示趋势",
)
def draw_ascii_chart(symbol: str = field_symbol, market: str = field_market):
    stock_prices_fn = cast(Callable[..., str], stock_prices)
    data = stock_prices_fn(symbol, market, limit=20)
    lines = data.strip().split("\n")[1:]  # 跳过表头
    prices = [float(l.split(",")[2]) for l in lines]  # 取收盘价

    if not prices:
        return "数据不足，无法绘图"

    min_p, max_p = min(prices), max(prices)
    rng = max_p - min_p or 1
    height = 5
    chart = []

    for h in range(height, -1, -1):
        row = []
        threshold = min_p + (h / height) * rng
        for p in prices:
            if p >= threshold:
                row.append("📈" if h == height else "█")
            else:
                row.append("  ")
        chart.append("".join(row))

    return f"\n{symbol} 最近 20 日走势图:\n" + "\n".join(chart) + f"\n最低: {min_p:.2f}  最高: {max_p:.2f}"


@mcp.tool(
    title="策略回测",
    description="基于历史价格与技术指标进行简单策略回测（SMA/RSI/MACD/BOLL/MA_CROSS/KDJ）",
)
def backtest_strategy(
    symbol: str = field_symbol,
    market: str = field_market,
    strategy: str = Field("SMA", description="策略类型: SMA/RSI/MACD/BOLL/MA_CROSS/KDJ"),
    days: int = Field(252, description="回测天数"),
):
    stock_prices_fn = cast(Callable[..., str], stock_prices)
    data = stock_prices_fn(symbol=symbol, market=market, limit=days)
    if not data or data.startswith("Not Found"):
        return f"未找到可回测数据: {symbol}.{market}"

    try:
        dfs = pd.read_csv(StringIO(data))
    except Exception:
        return "价格数据解析失败"

    if dfs is None or dfs.empty or "收盘" not in dfs.columns:
        return "数据不足，无法回测"

    close = pd.to_numeric(dfs["收盘"], errors="coerce")
    dfs = dfs.assign(收盘=close).dropna(subset=["收盘"])
    if dfs.empty:
        return "数据不足，无法回测"

    strategy_key = (strategy or "").strip().upper()
    if strategy_key == "SMA":
        short_window = 5
        long_window = 20
        dfs["ma_short"] = dfs["收盘"].rolling(short_window).mean()
        dfs["ma_long"] = dfs["收盘"].rolling(long_window).mean()
        signal = pd.Series((dfs["ma_short"] > dfs["ma_long"]).astype(int), index=dfs.index)
        strategy_desc = f"SMA{short_window}/{long_window}"
    elif strategy_key == "RSI":
        if "RSI" not in dfs.columns:
            return "数据缺少 RSI 指标，无法回测"
        rsi = pd.Series(pd.to_numeric(dfs["RSI"], errors="coerce"), index=dfs.index)
        positions = []
        position = 0
        for value in rsi.to_list():
            if pd.isna(value):
                positions.append(position)
                continue
            if value < 30:
                position = 1
            elif value > 70:
                position = 0
            positions.append(position)
        signal = pd.Series(positions, index=dfs.index)
        strategy_desc = "RSI(30/70)"
    elif strategy_key == "MACD":
        if "DIF" not in dfs.columns or "DEA" not in dfs.columns:
            return "数据缺少 MACD 指标，无法回测"
        dif = pd.Series(pd.to_numeric(dfs["DIF"], errors="coerce"), index=dfs.index)
        dea = pd.Series(pd.to_numeric(dfs["DEA"], errors="coerce"), index=dfs.index)
        signal = pd.Series((dif > dea).astype(int), index=dfs.index)
        strategy_desc = "MACD(DIF/DEA)"
    elif strategy_key == "BOLL":
        if "BOLL.U" not in dfs.columns or "BOLL.L" not in dfs.columns:
            return "数据缺少 BOLL 指标，无法回测"
        boll_u = pd.Series(pd.to_numeric(dfs["BOLL.U"], errors="coerce"), index=dfs.index)
        boll_l = pd.Series(pd.to_numeric(dfs["BOLL.L"], errors="coerce"), index=dfs.index)
        positions = []
        position = 0
        for i, price in enumerate(dfs["收盘"].to_list()):
            if pd.isna(boll_u.iloc[i]) or pd.isna(boll_l.iloc[i]):
                positions.append(position)
                continue
            if price <= boll_l.iloc[i]:
                position = 1
            elif price >= boll_u.iloc[i]:
                position = 0
            positions.append(position)
        signal = pd.Series(positions, index=dfs.index)
        strategy_desc = "BOLL(突破下轨买入/上轨卖出)"
    elif strategy_key in ("MA_CROSS", "MACROSS"):
        ma10 = dfs["收盘"].rolling(10).mean()
        ma30 = dfs["收盘"].rolling(30).mean()
        signal = pd.Series((ma10 > ma30).astype(int), index=dfs.index)
        strategy_desc = "MA_CROSS(10/30)"
    elif strategy_key == "KDJ":
        if "KDJ.K" not in dfs.columns or "KDJ.D" not in dfs.columns:
            return "数据缺少 KDJ 指标，无法回测"
        kdj_k = pd.Series(pd.to_numeric(dfs["KDJ.K"], errors="coerce"), index=dfs.index)
        kdj_d = pd.Series(pd.to_numeric(dfs["KDJ.D"], errors="coerce"), index=dfs.index)
        positions = []
        position = 0
        prev_k, prev_d = None, None
        for i in range(len(kdj_k)):
            k_val, d_val = kdj_k.iloc[i], kdj_d.iloc[i]
            if pd.isna(k_val) or pd.isna(d_val):
                positions.append(position)
                prev_k, prev_d = k_val, d_val
                continue
            if prev_k is not None and prev_d is not None:
                if not pd.isna(prev_k) and not pd.isna(prev_d):
                    if prev_k <= prev_d and k_val > d_val:
                        position = 1
                    elif prev_k >= prev_d and k_val < d_val:
                        position = 0
            positions.append(position)
            prev_k, prev_d = k_val, d_val
        signal = pd.Series(positions, index=dfs.index)
        strategy_desc = "KDJ(金叉买入/死叉卖出)"
    else:
        return f"不支持的策略类型: {strategy}"

    returns = dfs["收盘"].pct_change().fillna(0)
    position = signal.shift(1).fillna(0)
    strat_returns = returns.mul(position)
    equity = (1 + strat_returns).cumprod()
    cumulative_return = equity.iloc[-1] - 1
    drawdown = equity / equity.cummax() - 1
    max_drawdown = drawdown.min()

    active = strat_returns[strat_returns != 0]
    win_rate = (active > 0).mean() if not active.empty else None

    start_date = str(dfs["日期"].iloc[0]) if "日期" in dfs.columns else "-"
    end_date = str(dfs["日期"].iloc[-1]) if "日期" in dfs.columns else "-"
    win_text = f"{win_rate:.2%}" if win_rate is not None else "N/A"
    return (
        f"--- 策略回测: {symbol} ({market}) ---\n"
        f"策略: {strategy_desc}\n"
        f"区间: {start_date} ~ {end_date} (样本 {len(dfs)} 日)\n"
        f"累计收益: {cumulative_return:.2%}\n"
        f"最大回撤: {max_drawdown:.2%}\n"
        f"胜率: {win_text}"
    )


@mcp.tool(
    title="给出投资建议",
    description="基于AI对其他工具提供的数据分析结果给出具体投资建议",
)
def trading_suggest(
    symbol: str = Field(description="股票代码或加密币种"),
    action: str = Field(description="推荐操作: buy/sell/hold"),
    score: int = Field(description="置信度，范围: 0-100"),
    reason: str = Field(description="推荐理由"),
):
    return {
        "symbol": symbol,
        "action": action,
        "score": score,
        "reason": reason,
    }


@mcp.tool(
    title="查看缓存状态",
    description="查看当前缓存的键和数量，用于调试和监控",
)
def cache_status():
    from ..cache import CacheKey

    keys = list(CacheKey.ALL.keys())
    if not keys:
        return "当前缓存为空"

    lines = [
        "--- 缓存状态 ---",
        f"缓存条目数: {len(keys)}",
        "",
        "最近缓存键 (最多显示20个):",
    ]
    for key in keys[:20]:
        lines.append(f"  - {key}")
    if len(keys) > 20:
        lines.append(f"  ... 还有 {len(keys) - 20} 个")
    return "\n".join(lines)


@mcp.tool(
    title="清理缓存",
    description="清理指定的缓存键，或清理所有缓存",
)
def cache_clear(
    key: str = Field("", description="要清理的缓存键，留空则清理所有缓存"),
):
    from ..cache import CacheKey

    if not key:
        count = len(CacheKey.ALL)
        for cache_key in list(CacheKey.ALL.values()):
            cache_key.delete()
        CacheKey.ALL.clear()
        return f"已清理所有缓存 ({count} 个条目)"

    if key in CacheKey.ALL:
        CacheKey.ALL[key].delete()
        del CacheKey.ALL[key]
        return f"已清理缓存: {key}"

    return f"未找到缓存键: {key}"
