from .server import mcp


@mcp.prompt("analyze-stock")
def prompt_analyze_stock(symbol: str):
    """一键触发全方位的个股深度分析技能"""
    return f"""
    你现在是一名资深证券分析师。请针对股票 {symbol} 执行以下深度分析技能：
    1. 获取当前时间确认市场状态。
    2. 使用 `stock_prices` 获取最近 30 天的日线数据，分析 MACD 和布林带走势。
    3. 调用 `stock_indicators` 获取财务摘要，判断基本面。
    4. 检索 `stock_news` 获取最近的新闻动态。
    5. 最后，结合 `skill://trading/logic/technical-analysis` 中的 SOP 给出你的专业评价。
    """


@mcp.prompt("market-pulse")
def prompt_market_pulse():
    """分析当前 A 股大盘整体脉搏"""
    return """
    作为市场观察员，请执行以下技能：
    1. 检查 `stock_zt_pool_em` 看涨停家数和市场高度。
    2. 检查 `stock_sector_fund_flow_rank` 找出今日领涨板块。
    3. 结合龙虎榜 `stock_lhb_ggtj_sina` 分析机构动向。
    请总结当前市场是处于“进攻”、“防守”还是“观望”状态。
    """
