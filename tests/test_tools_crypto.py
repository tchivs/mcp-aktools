"""Tests for crypto module tools."""

import pytest
import pandas as pd
from unittest import mock

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import crypto as crypto_module

# Get actual functions from FunctionTool objects
_safe_float = crypto_module._safe_float
_safe_int = crypto_module._safe_int
okx_prices_fn = crypto_module.okx_prices.fn
okx_loan_fn = crypto_module.okx_loan_ratios.fn
okx_taker_fn = crypto_module.okx_taker_volume.fn
binance_ai_fn = crypto_module.binance_ai_report.fn
crypto_diag_fn = crypto_module.crypto_composite_diagnostic.fn
draw_crypto_chart_fn = crypto_module.draw_crypto_chart.fn
backtest_crypto_fn = crypto_module.backtest_crypto_strategy.fn
okx_funding_fn = crypto_module.okx_funding_rate.fn
okx_oi_fn = crypto_module.okx_open_interest.fn
fgi_fn = crypto_module.fear_greed_index.fn


class TestSafeFloat:
    """Test _safe_float helper function."""

    def test_handles_empty_string(self):
        assert _safe_float("") == 0.0

    def test_handles_none(self):
        assert _safe_float(None) == 0.0

    def test_handles_valid_string(self):
        assert _safe_float("123.45") == 123.45

    def test_handles_valid_number(self):
        assert _safe_float(123.45) == 123.45

    def test_handles_invalid_string(self):
        assert _safe_float("invalid") == 0.0

    def test_custom_default(self):
        assert _safe_float("", default=1.0) == 1.0


class TestSafeInt:
    """Test _safe_int helper function."""

    def test_handles_empty_string(self):
        assert _safe_int("") == 0

    def test_handles_none(self):
        assert _safe_int(None) == 0

    def test_handles_valid_string(self):
        assert _safe_int("123") == 123

    def test_handles_valid_int(self):
        assert _safe_int(123) == 123

    def test_handles_invalid_string(self):
        assert _safe_int("invalid") == 0


class TestOkxPrices:
    """Test the okx_prices tool."""

    def test_returns_csv_with_indicators(self):
        """Test that function returns price data with technical indicators."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                [
                    "1704067200000",
                    "42000.00",
                    "42500.00",
                    "43000.00",
                    "41500.00",
                    "100.00",
                    "4200000.00",
                    "4200000.00",
                    "1",
                ],
                [
                    "1704153600000",
                    "42500.00",
                    "43000.00",
                    "43500.00",
                    "42000.00",
                    "150.00",
                    "6375000.00",
                    "6375000.00",
                    "1",
                ],
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_prices_fn(instId="BTC-USDT", bar="1H", limit=2)

            assert isinstance(result, str)
            assert "时间" in result
            assert "收盘" in result

    def test_empty_response(self):
        """Test handling of empty response."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": []}

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_prices_fn(instId="BTC-USDT", bar="1H", limit=2)

            # Should handle gracefully
            assert isinstance(result, (str, pd.DataFrame))


class TestOkxLoanRatios:
    """Test the okx_loan_ratios tool."""

    def test_returns_csv(self):
        """Test that function returns loan ratio data."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                ["1704067200000", "1.5"],
                ["1704153600000", "1.6"],
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_loan_fn(symbol="BTC", period="1H")

            assert isinstance(result, str)
            assert "时间" in result
            assert "多空比" in result


class TestOkxTakerVolume:
    """Test the okx_taker_volume tool."""

    def test_returns_csv(self):
        """Test that function returns taker volume data."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                ["1704067200000", "100.00", "150.00"],
                ["1704153600000", "120.00", "180.00"],
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_taker_fn(symbol="BTC", period="1H", instType="SPOT")

            assert isinstance(result, str)
            assert "时间" in result
            assert "卖出量" in result
            assert "买入量" in result


class TestBinanceAiReport:
    """Test the binance_ai_report tool."""

    def test_returns_report_text(self):
        """Test that function returns AI report text."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": {
                "report": {
                    "translated": {
                        "modules": [
                            {"overview": "BTC Analysis", "points": [{"content": "Point 1"}]},
                        ]
                    }
                }
            }
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.post", return_value=mock_response):
            result = binance_ai_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "BTC" in result or "Point 1" in result or "Analysis" in result

    def test_handles_invalid_json(self):
        """Test handling of invalid JSON response."""
        mock_response = mock.Mock()
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_response.text = "Some text response"

        with mock.patch("mcp_aktools.tools.crypto.requests.post", return_value=mock_response):
            result = binance_ai_fn(symbol="BTC")

            assert isinstance(result, str)


class TestCryptoCompositeDiagnostic:
    """Test the crypto_composite_diagnostic tool."""

    @pytest.mark.asyncio
    async def test_returns_composite_report(self):
        """Test that function returns a composite diagnostic report."""
        mock_prices = "时间,开盘,收盘,最高,最低\n2024-01-01,42000,42500,43000,41500"
        mock_loan = "时间,多空比\n2024-01-01,1.5"
        mock_taker = "时间,卖出量,买入量\n2024-01-01,100,150"
        mock_ai = "BTC AI Analysis Report"

        with mock.patch("mcp_aktools.tools.crypto.okx_prices", return_value=mock_prices):
            with mock.patch("mcp_aktools.tools.crypto.okx_loan_ratios", return_value=mock_loan):
                with mock.patch("mcp_aktools.tools.crypto.okx_taker_volume", return_value=mock_taker):
                    with mock.patch("mcp_aktools.tools.crypto.binance_ai_report", return_value=mock_ai):
                        result = await crypto_diag_fn(symbol="BTC")

                        assert isinstance(result, str)
                        assert "加密货币综合诊断" in result
                        assert "近期价格" in result
                        assert "杠杆多空比" in result
                        assert "主动买卖量" in result
                        assert "币安AI报告" in result


class TestDrawCryptoChart:
    """Test the draw_crypto_chart tool."""

    def test_returns_ascii_chart(self):
        """Test that function returns an ASCII chart."""
        mock_prices = "时间,开盘,收盘,最高,最低\n" + "\n".join(
            [f"2024-01-{i + 1:02d},42000,42500,43000,41500" for i in range(20)]
        )

        with mock.patch("mcp_aktools.tools.crypto.okx_prices", return_value=mock_prices):
            result = draw_crypto_chart_fn(symbol="BTC", bar="1D")

            assert isinstance(result, str)
            assert "BTC" in result
            assert "最低" in result
            assert "最高" in result

    def test_handles_insufficient_data(self):
        """Test handling of insufficient data."""
        with mock.patch("mcp_aktools.tools.crypto.okx_prices", return_value=""):
            result = draw_crypto_chart_fn(symbol="BTC", bar="1D")

            assert isinstance(result, str)
            assert "不足" in result or "无法" in result


class TestBacktestCryptoStrategy:
    """Test the backtest_crypto_strategy tool."""

    def test_sma_strategy(self):
        """Test SMA strategy backtest."""
        mock_prices = "时间,开盘,收盘,最高,最低\n" + "\n".join(
            [f"2024-01-{i + 1:02d},42000,{42000 + i * 100},43000,41500" for i in range(30)]
        )

        with mock.patch("mcp_aktools.tools.crypto.okx_prices", return_value=mock_prices):
            result = backtest_crypto_fn(symbol="BTC", strategy="SMA", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "策略回测" in result
            assert "累计收益" in result
            assert "最大回撤" in result


class TestOkxFundingRate:
    """Test the okx_funding_rate tool."""

    def test_returns_funding_rate(self):
        """Test that function returns funding rate data."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "fundingRate": "0.0001",
                    "nextFundingRate": "0.0002",
                    "fundingTime": "1704067200000",
                }
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_funding_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "资金费率" in result
            assert "当前费率" in result

    def test_handles_empty_fields(self):
        """Test handling of empty fields in response."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "fundingRate": "",
                    "nextFundingRate": "",
                    "fundingTime": "",
                }
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_funding_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "BTC" in result


class TestOkxOpenInterest:
    """Test the okx_open_interest tool."""

    def test_returns_open_interest(self):
        """Test that function returns open interest data."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "oi": "1000000",
                    "oiCcy": "1000.00",
                    "ts": "1704067200000",
                }
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_oi_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "持仓量" in result


class TestFearGreedIndex:
    """Test the fear_greed_index tool."""

    def test_returns_index(self):
        """Test that function returns fear & greed index."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "value": "75",
                    "value_classification": "Greed",
                    "timestamp": "1704067200",
                }
            ]
            * 7
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = fgi_fn()

            assert isinstance(result, str)
            assert "恐惧贪婪指数" in result
            assert "75" in result or "Greed" in result


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
