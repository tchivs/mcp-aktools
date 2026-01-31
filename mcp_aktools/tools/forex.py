"""外汇数据工具模块"""

import akshare as ak
import pandas as pd
from pydantic import Field

from mcp_aktools.server import mcp
from mcp_aktools.shared.utils import ak_cache

# 主要货币对映射
FX_PAIRS = {
    "USDCNY": "美元/人民币",
    "EURUSD": "欧元/美元",
    "USDJPY": "美元/日元",
    "GBPUSD": "英镑/美元",
    "AUDUSD": "澳元/美元",
    "USDCAD": "美元/加元",
    "USDCHF": "美元/瑞郎",
    "NZDUSD": "纽元/美元",
}


@mcp.tool(
    title="获取实时外汇汇率",
    description="获取主要货币对的实时汇率报价，包括美元、欧元、日元、英镑等主流货币",
)
def fx_spot_rates(
    pair: str = Field(
        "USDCNY",
        description="货币对代码，支持: USDCNY(美元/人民币), EURUSD(欧元/美元), USDJPY(美元/日元), GBPUSD(英镑/美元), AUDUSD(澳元/美元), USDCAD(美元/加元), USDCHF(美元/瑞郎), NZDUSD(纽元/美元)",
    ),
):
    """获取实时外汇汇率"""
    df = ak_cache(ak.fx_spot_quote, ttl=300)
    if df is None or df.empty:
        return pd.DataFrame()

    # 如果指定了货币对，尝试过滤
    if pair and pair.upper() in FX_PAIRS:
        # 尝试根据货币对名称过滤
        pair_name = FX_PAIRS[pair.upper()]
        if "货币对" in df.columns:
            df = df[df["货币对"].str.contains(pair, case=False, na=False)]
        elif "名称" in df.columns:
            df = df[df["名称"].str.contains(pair_name, case=False, na=False)]

    return df.to_csv(index=False, float_format="%.4f")


@mcp.tool(
    title="获取外汇历史汇率",
    description="获取指定货币对的历史汇率数据，用于分析汇率走势和波动",
)
def fx_history(
    pair: str = Field(
        "USDCNY",
        description="货币对代码，支持: USDCNY(美元/人民币), EURUSD(欧元/美元), USDJPY(美元/日元), GBPUSD(英镑/美元), AUDUSD(澳元/美元), USDCAD(美元/加元), USDCHF(美元/瑞郎), NZDUSD(纽元/美元)",
    ),
    limit: int = Field(30, description="返回数量(int)，建议30-252", strict=False),
):
    """获取外汇历史汇率"""
    # 使用 akshare 的外汇历史数据接口
    df = ak_cache(ak.fx_pair_quote, symbol=pair.upper())
    if df is None or df.empty:
        return pd.DataFrame()

    # 取最近的数据
    df = df.tail(limit).copy()

    # 确保日期列存在并格式化
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    elif "时间" in df.columns:
        df["日期"] = pd.to_datetime(df["时间"], errors="coerce")
        df = df.drop(columns=["时间"])

    return df.to_csv(index=False, float_format="%.4f")


@mcp.tool(
    title="获取外汇交叉汇率表",
    description="获取主要货币之间的交叉汇率矩阵，方便快速查看多个货币对的汇率关系",
)
def fx_cross_rates():
    """获取外汇交叉汇率表"""
    # 使用 akshare 的外汇交叉汇率接口
    df = ak_cache(ak.fx_spot_quote, ttl=300)
    if df is None or df.empty:
        return pd.DataFrame()

    # 尝试构建交叉汇率表
    # 如果数据包含多个货币对，返回完整列表
    return df.to_csv(index=False, float_format="%.4f")
