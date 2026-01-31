"""Tests for macro module tools."""

import pytest
import pandas as pd
from unittest import mock

from mcp_aktools.tools import macro as macro_module

macro_gdp_fn = macro_module.macro_gdp.fn
macro_cpi_fn = macro_module.macro_cpi.fn
macro_pmi_fn = macro_module.macro_pmi.fn
macro_interest_rate_fn = macro_module.macro_interest_rate.fn
macro_money_supply_fn = macro_module.macro_money_supply.fn


class TestMacroGDP:
    """Test the macro_gdp tool."""

    def test_macro_gdp_returns_csv_string(self):
        """Test that macro_gdp returns CSV string."""
        mock_df = pd.DataFrame(
            {
                "季度": ["2025Q1", "2025Q2"],
                "国内生产总值-绝对值": [300000, 310000],
                "国内生产总值-同比增长": [5.3, 5.5],
            }
        )

        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=mock_df):
            result = macro_gdp_fn(limit=2)

            assert isinstance(result, str)
            assert "季度" in result
            assert "国内生产总值" in result

    def test_macro_gdp_empty_dataframe(self):
        """Test macro_gdp with empty DataFrame."""
        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=pd.DataFrame()):
            result = macro_gdp_fn(limit=10)

            assert isinstance(result, str)


class TestMacroCPI:
    """Test the macro_cpi tool."""

    def test_macro_cpi_returns_csv_string(self):
        """Test that macro_cpi returns CSV string."""
        mock_df = pd.DataFrame(
            {
                "月份": ["2025-01", "2025-02"],
                "全国-当月": [102.5, 102.8],
                "全国-同比": [2.5, 2.8],
            }
        )

        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=mock_df):
            result = macro_cpi_fn(limit=2)

            assert isinstance(result, str)
            assert "月份" in result or "全国" in result

    def test_macro_cpi_empty_dataframe(self):
        """Test macro_cpi with empty DataFrame."""
        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=pd.DataFrame()):
            result = macro_cpi_fn(limit=12)

            assert isinstance(result, str)


class TestMacroPMI:
    """Test the macro_pmi tool."""

    def test_macro_pmi_returns_csv_string(self):
        """Test that macro_pmi returns CSV string."""
        mock_df = pd.DataFrame(
            {
                "月份": ["2025-01", "2025-02"],
                "制造业PMI": [50.5, 51.2],
            }
        )

        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=mock_df):
            result = macro_pmi_fn(limit=2)

            assert isinstance(result, str)
            assert "月份" in result or "PMI" in result

    def test_macro_pmi_empty_dataframe(self):
        """Test macro_pmi with empty DataFrame."""
        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=pd.DataFrame()):
            result = macro_pmi_fn(limit=12)

            assert isinstance(result, str)


class TestMacroInterestRate:
    """Test the macro_interest_rate tool."""

    def test_macro_interest_rate_returns_csv_string(self):
        """Test that macro_interest_rate returns CSV string."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-20", "2025-02-20"],
                "LPR1Y": [3.45, 3.40],
                "LPR5Y": [3.95, 3.90],
            }
        )

        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=mock_df):
            result = macro_interest_rate_fn(limit=2)

            assert isinstance(result, str)
            assert "日期" in result or "LPR" in result

    def test_macro_interest_rate_empty_dataframe(self):
        """Test macro_interest_rate with empty DataFrame."""
        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=pd.DataFrame()):
            result = macro_interest_rate_fn(limit=12)

            assert isinstance(result, str)


class TestMacroMoneySupply:
    """Test the macro_money_supply tool."""

    def test_macro_money_supply_returns_csv_string(self):
        """Test that macro_money_supply returns CSV string."""
        mock_df = pd.DataFrame(
            {
                "月份": ["2025-01", "2025-02"],
                "货币和准货币(M2)-数量(亿元)": [280000, 285000],
                "货币和准货币(M2)-同比增长": [8.5, 8.8],
            }
        )

        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=mock_df):
            result = macro_money_supply_fn(limit=2)

            assert isinstance(result, str)
            assert "月份" in result or "货币" in result or "M2" in result

    def test_macro_money_supply_empty_dataframe(self):
        """Test macro_money_supply with empty DataFrame."""
        with mock.patch("mcp_aktools.tools.macro.ak_cache", return_value=pd.DataFrame()):
            result = macro_money_supply_fn(limit=12)

            assert isinstance(result, str)
