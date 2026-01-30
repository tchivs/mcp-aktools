"""Tests for progress reporting in async tools."""

import pytest
from unittest import mock

from mcp_aktools.tools import stocks, analysis, crypto, precious_metals

# Get actual functions from FunctionTool objects
search_fn = stocks.search.fn
composite_stock_diagnostic_fn = analysis.composite_stock_diagnostic.fn
crypto_composite_diagnostic_fn = crypto.crypto_composite_diagnostic.fn
pm_composite_diagnostic_fn = precious_metals.pm_composite_diagnostic.fn


@pytest.mark.asyncio
async def test_search_reports_progress():
    """Test that search tool reports progress."""
    mock_ctx = mock.AsyncMock()

    with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=None):
        result = await search_fn(keyword="test", market="sh", ctx=mock_ctx)

    # Verify progress was reported at least twice (start and end)
    assert mock_ctx.report_progress.call_count >= 2
    assert result == "Not Found for test"


@pytest.mark.asyncio
async def test_composite_stock_diagnostic_reports_progress():
    """Test that composite_stock_diagnostic reports progress."""
    mock_ctx = mock.AsyncMock()

    # Mock the sub-tools to return simple strings
    with (
        mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value="price_data"),
        mock.patch("mcp_aktools.tools.analysis.stock_info", return_value="info_data"),
        mock.patch("mcp_aktools.tools.analysis.stock_news", return_value="news_data"),
    ):
        result = await composite_stock_diagnostic_fn(symbol="000001", market="sh", ctx=mock_ctx)

    # Verify progress was reported at least 5 times (start + 3 steps + end)
    assert mock_ctx.report_progress.call_count >= 5
    assert "综合诊断报告" in result


@pytest.mark.asyncio
async def test_crypto_composite_diagnostic_reports_progress():
    """Test that crypto_composite_diagnostic reports progress."""
    mock_ctx = mock.AsyncMock()

    # Mock the sub-tools to return simple strings
    with (
        mock.patch("mcp_aktools.tools.crypto.okx_prices", return_value="price_data"),
        mock.patch("mcp_aktools.tools.crypto.okx_loan_ratios", return_value="loan_data"),
        mock.patch("mcp_aktools.tools.crypto.okx_taker_volume", return_value="taker_data"),
        mock.patch("mcp_aktools.tools.crypto.binance_ai_report", return_value="ai_report"),
    ):
        result = await crypto_composite_diagnostic_fn(symbol="BTC", ctx=mock_ctx)

    # Verify progress was reported at least 4 times (start + 2 steps + end)
    assert mock_ctx.report_progress.call_count >= 4
    assert "加密货币综合诊断" in result


@pytest.mark.asyncio
async def test_pm_composite_diagnostic_reports_progress():
    """Test that pm_composite_diagnostic reports progress."""
    mock_ctx = mock.AsyncMock()

    # Mock the sub-tools to return simple strings
    with (
        mock.patch("mcp_aktools.tools.precious_metals.pm_spot_prices", return_value="spot_data"),
        mock.patch("mcp_aktools.tools.precious_metals.pm_international_prices", return_value="intl_data"),
        mock.patch("mcp_aktools.tools.precious_metals.pm_etf_holdings", return_value="etf_data"),
        mock.patch("mcp_aktools.tools.precious_metals.pm_comex_inventory", return_value="comex_data"),
        mock.patch("mcp_aktools.tools.precious_metals.pm_basis", return_value="basis_data"),
        mock.patch("mcp_aktools.tools.precious_metals.pm_benchmark_price", return_value="benchmark_data"),
    ):
        result = await pm_composite_diagnostic_fn(metal="gold", ctx=mock_ctx)

    # Verify progress was reported at least 7 times (start + 6 steps + end)
    assert mock_ctx.report_progress.call_count >= 7
    assert "贵金属综合诊断" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
