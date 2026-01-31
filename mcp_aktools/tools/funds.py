"""基金数据工具模块"""

import akshare as ak
import pandas as pd
from pydantic import Field

from mcp_aktools.server import mcp
from mcp_aktools.shared.utils import ak_cache


@mcp.tool(
    title="获取基金基本信息",
    description="获取基金的基本信息，包括基金名称、类型、规模、管理人等详细信息",
)
def fund_info(
    code: str = Field("000001", description="基金代码，例如: 000001(华夏成长)"),
):
    """获取基金基本信息"""
    df = ak_cache(ak.fund_open_fund_info_em, symbol=code)
    if df is None or df.empty:
        return pd.DataFrame()

    return df.to_csv(index=False)


@mcp.tool(
    title="获取基金净值历史",
    description="获取基金的历史净值数据，包括单位净值、累计净值、日增长率等，用于分析基金业绩表现",
)
def fund_nav(
    code: str = Field("000001", description="基金代码，例如: 000001(华夏成长)"),
    limit: int = Field(30, description="返回数量(int)，建议30-252", strict=False),
):
    """获取基金净值历史"""
    df = ak_cache(ak.fund_open_fund_daily_em, symbol=code)
    if df is None or df.empty:
        return pd.DataFrame()

    # 取最近的数据
    df = df.tail(limit).copy()

    # 确保日期列存在并格式化
    if "净值日期" in df.columns:
        df["净值日期"] = pd.to_datetime(df["净值日期"], errors="coerce")

    return df.to_csv(index=False, float_format="%.4f")


@mcp.tool(
    title="获取基金持仓明细",
    description="获取基金的股票持仓明细，包括持仓股票代码、名称、持仓比例等，用于分析基金投资组合",
)
def fund_holdings(
    code: str = Field("000001", description="基金代码，例如: 000001(华夏成长)"),
):
    """获取基金持仓明细"""
    df = ak_cache(ak.fund_portfolio_hold_em, symbol=code, date="")
    if df is None or df.empty:
        return pd.DataFrame()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取基金排行榜",
    description="获取不同类型基金的排行榜数据，包括收益率、规模等指标，支持按时间周期和基金类型筛选",
)
def fund_ranking(
    type: str = Field(
        "全部",
        description="基金类型，支持: 全部, 股票型, 混合型, 债券型, 指数型, QDII, ETF, LOF",
    ),
):
    """获取基金排行榜"""
    df = ak_cache(ak.fund_open_fund_rank_em, symbol=type)
    if df is None or df.empty:
        return pd.DataFrame()

    # 限制返回数量，避免数据过大
    df = df.head(100).copy()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取ETF历史价格",
    description="获取ETF基金的历史价格数据，包括开盘价、收盘价、最高价、最低价、成交量等，用于分析ETF走势",
)
def etf_prices(
    code: str = Field("159915", description="ETF代码，例如: 159915(创业板ETF)"),
    limit: int = Field(30, description="返回数量(int)，建议30-252", strict=False),
):
    """获取ETF历史价格"""
    df = ak_cache(
        ak.fund_etf_hist_em,
        symbol=code,
        period="daily",
        start_date="20200101",
        end_date="20991231",
        adjust="",
    )
    if df is None or df.empty:
        return pd.DataFrame()

    # 取最近的数据
    df = df.tail(limit).copy()

    # 确保日期列存在并格式化
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")

    return df.to_csv(index=False, float_format="%.4f")
