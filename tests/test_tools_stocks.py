"""Tests for stocks module tools."""

import pytest
import pandas as pd
from datetime import datetime
from unittest import mock
from io import StringIO

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import stocks as stocks_module

# Get actual functions from FunctionTool objects
search_fn = stocks_module.search.fn
stock_info_fn = stocks_module.stock_info.fn
stock_news_fn = stocks_module.stock_news.fn
inst_holding_fn = stocks_module.institutional_holding_summary.fn
stock_prices_fn = stocks_module.stock_prices.fn
indicators_a_fn = stocks_module.stock_indicators_a.fn
indicators_hk_fn = stocks_module.stock_indicators_hk.fn
indicators_us_fn = stocks_module.stock_indicators_us.fn


class TestSearch:
    """Test the search tool."""

    @pytest.mark.asyncio
    async def test_search_returns_string(self):
        """Test that search returns a string result."""
        mock_result = pd.Series(
            {
                "code": "000001",
                "name": "平安银行",
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=mock_result):
            result = await search_fn(keyword="平安", market="sh")

            assert isinstance(result, str)
            assert "平安" in result or "000001" in result

    @pytest.mark.asyncio
    async def test_search_not_found(self):
        """Test search when no results found."""
        with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=None):
            result = await search_fn(keyword="NONEXISTENT", market="sh")

            assert "Not Found" in result


class TestStockInfo:
    """Test the stock_info tool."""

    def test_stock_info_returns_string(self):
        """Test that stock_info returns stock information."""
        mock_df = pd.DataFrame(
            {
                "item": ["名称", "代码"],
                "value": ["平安银行", "000001"],
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = stock_info_fn(symbol="000001", market="sh")

            assert isinstance(result, str)
            assert "平安银行" in result or "000001" in result

    def test_stock_info_not_found(self):
        """Test stock_info when stock not found."""
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=None):
                result = stock_info_fn(symbol="NONEXISTENT", market="sh")

                assert "Not Found" in result


class TestStockNews:
    """Test the stock_news tool."""

    def test_stock_news_returns_csv(self):
        """Test that stock_news returns CSV format data."""
        mock_df = pd.DataFrame(
            {
                "发布时间": ["2024-01-01 10:00", "2024-01-02 11:00"],
                "标题": ["News 1", "News 2"],
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = stock_news_fn(symbol="000001", limit=2)

            assert isinstance(result, str)
            # Should be CSV format
            lines = result.split("\n")
            assert len(lines) > 0

    def test_stock_news_empty(self):
        """Test stock_news when no news available."""
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            result = stock_news_fn(symbol="000001")

            assert "未获取到" in result


class TestInstitutionalHolding:
    """Test the institutional_holding_summary tool."""

    def test_holding_summary_returns_csv(self):
        """Test that holding summary returns CSV format."""
        mock_df = pd.DataFrame(
            {
                "报告期": ["2024Q1", "2024Q2"],
                "机构数": [100, 150],
                "持股比例": [5.5, 6.0],
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = inst_holding_fn(symbol="000001")

            assert isinstance(result, str)
            assert "2024Q1" in result or "报告期" in result

    def test_holding_summary_empty(self):
        """Test holding summary when no data available."""
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            result = inst_holding_fn(symbol="000001")

            assert "未获取到" in result


class TestStockPrices:
    """Test the stock_prices tool."""

    def test_stock_prices_returns_csv_with_indicators(self):
        """Test that stock_prices returns price data with technical indicators."""
        mock_df = pd.DataFrame(
            {
                "日期": pd.date_range("2024-01-01", periods=10),
                "开盘": [10.0] * 10,
                "收盘": [10.5] * 10,
                "最高": [11.0] * 10,
                "最低": [9.5] * 10,
                "成交量": [1000000] * 10,
                "换手率": [1.5] * 10,
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = stock_prices_fn(symbol="000001", market="sh", limit=5)

            assert isinstance(result, str)
            # Should contain headers
            assert "日期" in result
            assert "收盘" in result
            # Should contain technical indicators
            assert "MACD" in result or "RSI" in result or "KDJ" in result

    def test_stock_prices_not_found(self):
        """Test stock_prices when symbol not found."""
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            result = stock_prices_fn(symbol="NONEXISTENT", market="sh", limit=30)

            assert "Not Found" in result


class TestStockIndicators:
    """Test the stock indicators tools (A, HK, US)."""

    def test_stock_indicators_a_returns_csv(self):
        """Test A-share indicators."""
        mock_df = pd.DataFrame(
            {
                "报告期": ["2024Q1"],
                "每股收益": [2.5],
                "净利润": [100000000],
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = indicators_a_fn(symbol="000001")

            assert isinstance(result, str)
            assert "报告期" in result

    def test_stock_indicators_hk_returns_csv(self):
        """Test HK stock indicators."""
        mock_df = pd.DataFrame(
            {
                "报告期": ["2024Q1"],
                "市盈率": [10.5],
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = indicators_hk_fn(symbol="00700")

            assert isinstance(result, str)

    def test_stock_indicators_us_returns_csv(self):
        """Test US stock indicators."""
        mock_df = pd.DataFrame(
            {
                "报告期": ["2024Q1"],
                "市盈率": [25.0],
            }
        )

        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = indicators_us_fn(symbol="AAPL")

            assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
