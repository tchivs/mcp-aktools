"""宏观经济数据工具模块"""

import akshare as ak
from pydantic import Field

from mcp_aktools.server import mcp
from mcp_aktools.shared.utils import ak_cache


@mcp.tool(
    title="获取GDP数据",
    description="获取中国GDP季度数据，包括季度值、同比增长率、环比增长率等关键指标",
)
def macro_gdp(
    limit: int = Field(20, description="返回数量(int)，建议10-40", strict=False),
):
    """获取中国GDP季度数据"""
    df = ak_cache(ak.macro_china_gdp, ttl=86400 * 7)
    if df is None or df.empty:
        return ""

    df = df.tail(limit).copy()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取CPI通胀数据",
    description="获取中国居民消费价格指数(CPI)月度数据，包括当月同比、环比增长率，用于分析通胀水平",
)
def macro_cpi(
    limit: int = Field(24, description="返回数量(int)，建议12-60", strict=False),
):
    """获取中国CPI月度数据"""
    df = ak_cache(ak.macro_china_cpi, ttl=86400 * 7)
    if df is None or df.empty:
        return ""

    df = df.tail(limit).copy()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取PMI制造业指数",
    description="获取中国制造业采购经理指数(PMI)月度数据，50为荣枯线，高于50表示制造业扩张，低于50表示收缩",
)
def macro_pmi(
    limit: int = Field(24, description="返回数量(int)，建议12-60", strict=False),
):
    """获取中国PMI制造业指数"""
    df = ak_cache(ak.macro_china_pmi, ttl=86400 * 7)
    if df is None or df.empty:
        return ""

    df = df.tail(limit).copy()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取利率数据",
    description="获取中国贷款市场报价利率(LPR)数据，包括1年期和5年期以上LPR，用于分析货币政策和贷款成本",
)
def macro_interest_rate(
    limit: int = Field(24, description="返回数量(int)，建议12-60", strict=False),
):
    """获取中国LPR利率数据"""
    df = ak_cache(ak.macro_china_lpr, ttl=86400 * 7)
    if df is None or df.empty:
        return ""

    df = df.tail(limit).copy()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取货币供应量数据",
    description="获取中国货币供应量(M0/M1/M2)月度数据，包括当月值、同比增长率，用于分析货币政策和流动性",
)
def macro_money_supply(
    limit: int = Field(24, description="返回数量(int)，建议12-60", strict=False),
):
    """获取中国货币供应量数据"""
    df = ak_cache(ak.macro_china_money_supply, ttl=86400 * 7)
    if df is None or df.empty:
        return ""

    df = df.tail(limit).copy()

    return df.to_csv(index=False, float_format="%.2f")
