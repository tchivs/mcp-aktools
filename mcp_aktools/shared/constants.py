import os

OKX_BASE_URL = os.getenv("OKX_BASE_URL") or "https://www.okx.com"
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL") or "https://www.binance.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10) AppleWebKit/537.36 Chrome/139"
PORTFOLIO_FILE = os.path.expanduser("~/.cache/mcp_aktools/portfolio.json")
