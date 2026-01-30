"""Tests for analysis module tools."""

import pytest
import pandas as pd
from unittest import mock
from io import StringIO

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import analysis as analysis_module

# Get actual functions from FunctionTool objects
composite_diag_fn = analysis_module.composite_stock_diagnostic.fn
draw_chart_fn = analysis_module.draw_ascii_chart.fn
backtest_fn = analysis_module.backtest_strategy.fn
trading_suggest_fn = analysis_module.trading_suggest.fn


class TestCompositeStockDiagnostic:
    """Test the composite_stock_diagnostic tool."""

    @pytest.mark.asyncio
    async def test_returns_composite_report(self):
        """Test that function returns a composite diagnostic report."""
        mock_prices = "日期,开盘,收盘,最高,最低\n2024-01-01,10.0,11.0,11.5,9.5"
        mock_info = "股票信息\n名称: 平安银行\n代码: 000001"
        mock_news = "日期,标题\n2024-01-01,Test news"

        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value=mock_prices):
            with mock.patch("mcp_aktools.tools.analysis.stock_info", return_value=mock_info):
                with mock.patch("mcp_aktools.tools.analysis.stock_news", return_value=mock_news):
                    result = await composite_diag_fn(symbol="000001", market="sh")

                    assert isinstance(result, str)
                    assert "综合诊断报告" in result
                    assert "近期价格" in result
                    assert "基本面" in result
                    assert "核心新闻" in result


class TestDrawAsciiChart:
    """Test the draw_ascii_chart tool."""

    def test_returns_chart(self):
        """Test that function returns an ASCII chart."""
        mock_prices = "日期,开盘,收盘,最高,最低\n" + "\n".join(
            [
                "2024-01-01,10.0,10.5,11.0,9.5",
                "2024-01-02,10.5,11.0,11.5,10.0",
                "2024-01-03,11.0,10.8,11.2,10.5",
            ]
        )

        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value=mock_prices):
            result = draw_chart_fn(symbol="000001", market="sh")

            assert isinstance(result, str)
            assert "走势图" in result
            assert "最低" in result
            assert "最高" in result

    def test_handles_empty_data(self):
        """Test that function handles empty price data."""
        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value=""):
            result = draw_chart_fn(symbol="000001", market="sh")

            assert isinstance(result, str)
            # Should either return empty or have some handling


class TestBacktestStrategy:
    """Test the backtest_strategy tool."""

    def test_sma_strategy_returns_report(self):
        """Test SMA strategy backtest."""
        # Create mock price data with enough rows for SMA calculation
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "日期,开盘,收盘,最高,最低\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{10.5 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="SMA", days=30)

            assert isinstance(result, str)
            assert "策略回测" in result
            assert "SMA" in result
            assert "累计收益" in result

    def test_rsi_strategy_returns_report(self):
        """Test RSI strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "日期,开盘,收盘,最高,最低,RSI\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{10.5 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{30 + i}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="RSI", days=30)

            assert isinstance(result, str)
            assert "RSI" in result

    def test_macd_strategy_returns_report(self):
        """Test MACD strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "日期,开盘,收盘,最高,最低,DIF,DEA\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{10.5 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{0.1 + i * 0.01},{0.05 + i * 0.01}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="MACD", days=30)

            assert isinstance(result, str)
            assert "MACD" in result

    def test_invalid_strategy(self):
        """Test backtest with invalid strategy."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "日期,开盘,收盘,最高,最低\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{10.5 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="INVALID", days=30)

            assert isinstance(result, str)
            assert "不支持" in result

    def test_not_found_symbol(self):
        """Test backtest when symbol not found."""
        with mock.patch("mcp_aktools.tools.analysis.stock_prices", return_value="Not Found"):
            result = backtest_fn(symbol="NONEXISTENT", market="sh", strategy="SMA", days=30)

            assert isinstance(result, str)
            assert "未找到" in result


class TestTradingSuggest:
    """Test the trading_suggest tool."""

    def test_returns_dict(self):
        """Test that function returns a dictionary with trade suggestion."""
        result = trading_suggest_fn(
            symbol="000001",
            action="buy",
            score=85,
            reason="技术指标显示买入信号",
        )

        assert isinstance(result, dict)
        assert result["symbol"] == "000001"
        assert result["action"] == "buy"
        assert result["score"] == 85
        assert "买入信号" in result["reason"]

    def test_returns_sell_suggestion(self):
        """Test sell suggestion."""
        result = trading_suggest_fn(
            symbol="000002",
            action="sell",
            score=70,
            reason="达到目标价位",
        )

        assert result["action"] == "sell"
        assert result["score"] == 70


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
