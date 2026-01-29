from .server import mcp


@mcp.resource("skill://trading/logic/technical-analysis")
def resource_tech_analysis():
    """提供技术指标解读技能"""
    return """
    技术指标解读 SOP:
    - MACD: DIF > DEA 且 MACD 柱变长为多头强势；死叉则需警惕。
    - RSI: > 70 为超买，< 30 为超卖。
    - BOLL: 价格触及上轨且缩口表示压力，触及下轨且缩口表示支撑。
    - KDJ: J 线拐头通常是短期转折信号。
    """


@mcp.resource("skill://trading/strategy/risk-management")
def resource_risk_management():
    """提供风险管理技能"""
    return """
    风险管理原则:
    - 单笔交易止损不应超过总资金的 2%。
    - 建议在波动率（ATR）较高时缩小仓位。
    - 严禁在市场关闭前 15 分钟进行无计划的追涨。
    """
