from pydantic import Field
from datetime import datetime
from ..server import mcp
from ..shared.fields import field_market
from ..shared.utils import load_portfolio, save_portfolio
from .stocks import stock_prices


@mcp.tool(
    title="添加持仓记录",
    description="在模拟盘中添加一笔持仓记录，用于后续跟踪盈亏",
)
def portfolio_add(
    symbol: str = Field(description="股票或币种代码"),
    price: float = Field(description="买入价格"),
    volume: float = Field(description="买入数量"),
    market: str = field_market,
):
    p = load_portfolio()
    p[f"{symbol}.{market}"] = {
        "symbol": symbol,
        "price": price,
        "volume": volume,
        "market": market,
        "time": datetime.now().isoformat(),
    }
    save_portfolio(p)
    return f"成功添加持仓: {symbol}, 价格: {price}"


@mcp.tool(
    title="查看模拟盘盈亏",
    description="计算当前所有模拟持仓的实时盈亏情况",
)
def portfolio_view():
    p = load_portfolio()
    if not p:
        return "当前模拟盘为空"
    results = []
    for k, v in p.items():
        try:
            prices = stock_prices(v["symbol"], v["market"], limit=1)
            current_price = float(prices.split("\n")[-1].split(",")[2])
            profit = (current_price - v["price"]) * v["volume"]
            ratio = (current_price / v["price"] - 1) * 100
            results.append(
                f"{k}: 成本 {v['price']:.2f} -> 现价 {current_price:.2f} | 盈亏 {profit:+.2f} ({ratio:+.2f}%)"
            )
        except Exception:
            results.append(f"{k}: 成本 {v['price']:.2f} (无法获取实时现价)")
    return "\n".join(results)
