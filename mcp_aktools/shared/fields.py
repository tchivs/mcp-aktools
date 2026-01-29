from pydantic import Field

field_symbol = Field(description="股票代码")
field_market = Field(
    "sh",
    description="股票市场，仅支持: sh(上证), sz(深证), hk(港股), us(美股), 不支持加密货币",
)
