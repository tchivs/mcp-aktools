"""Tests for forex module tools."""

import pytest
import pandas as pd
from unittest import mock

from mcp_aktools.tools import forex as fx_module

fx_spot_rates_fn = fx_module.fx_spot_rates.fn
fx_history_fn = fx_module.fx_history.fn
fx_cross_rates_fn = fx_module.fx_cross_rates.fn


class TestFxSpotRates:
    """Test the fx_spot_rates tool."""

    def test_returns_csv(self):
        """Test that function returns spot rate data."""
        mock_df = pd.DataFrame(
            {
                "货币对": ["USDCNY", "EURUSD", "USDJPY"],
                "最新价": [7.2500, 1.0850, 148.50],
                "涨跌幅": [0.15, -0.25, 0.35],
            }
        )

        with mock.patch("mcp_aktools.tools.forex.ak_cache", return_value=mock_df):
            result = fx_spot_rates_fn(pair="USDCNY")

            assert isinstance(result, str)
            assert "货币对" in result or "最新价" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.forex.ak_cache", return_value=mock_df):
            result = fx_spot_rates_fn(pair="USDCNY")

            assert isinstance(result, pd.DataFrame)


class TestFxHistory:
    """Test the fx_history tool."""

    def test_returns_csv(self):
        """Test that function returns historical rate data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "开盘价": [7.2400, 7.2450, 7.2500],
                "收盘价": [7.2450, 7.2500, 7.2550],
                "最高价": [7.2500, 7.2550, 7.2600],
                "最低价": [7.2350, 7.2400, 7.2450],
            }
        )

        with mock.patch("mcp_aktools.tools.forex.ak_cache", return_value=mock_df):
            result = fx_history_fn(pair="USDCNY", limit=10)

            assert isinstance(result, str)
            assert "日期" in result or "收盘价" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.forex.ak_cache", return_value=mock_df):
            result = fx_history_fn(pair="USDCNY", limit=10)

            assert isinstance(result, pd.DataFrame)

    def test_handles_time_column(self):
        """Test handling when DataFrame has '时间' instead of '日期'."""
        mock_df = pd.DataFrame(
            {
                "时间": ["2025-01-01 10:00", "2025-01-02 10:00"],
                "开盘价": [7.2400, 7.2450],
                "收盘价": [7.2450, 7.2500],
            }
        )

        with mock.patch("mcp_aktools.tools.forex.ak_cache", return_value=mock_df):
            result = fx_history_fn(pair="USDCNY", limit=10)

            assert isinstance(result, str)
            assert "日期" in result or "开盘价" in result


class TestFxCrossRates:
    """Test the fx_cross_rates tool."""

    def test_returns_csv(self):
        """Test that function returns cross rate data."""
        mock_df = pd.DataFrame(
            {
                "货币对": ["USDCNY", "EURUSD", "USDJPY", "GBPUSD"],
                "最新价": [7.2500, 1.0850, 148.50, 1.2650],
                "涨跌幅": [0.15, -0.25, 0.35, 0.10],
            }
        )

        with mock.patch("mcp_aktools.tools.forex.ak_cache", return_value=mock_df):
            result = fx_cross_rates_fn()

            assert isinstance(result, str)
            assert "货币对" in result or "最新价" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.forex.ak_cache", return_value=mock_df):
            result = fx_cross_rates_fn()

            assert isinstance(result, pd.DataFrame)
