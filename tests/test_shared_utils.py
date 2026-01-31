"""Tests for shared utility functions."""

import json
import os
import tempfile
import pytest
from datetime import datetime, date
from unittest import mock
from pathlib import Path

import pandas as pd

from mcp_aktools.shared.utils import (
    ak_cache,
    recent_trade_date,
    load_portfolio,
    save_portfolio,
    ak_search,
)
from mcp_aktools.shared.constants import PORTFOLIO_FILE
from mcp_aktools.cache import CacheKey


class TestAkCache:
    """Test the ak_cache wrapper function."""

    def test_ak_cache_uses_key(self):
        """Test that ak_cache uses custom key if provided."""
        call_count = [0]

        def mock_fun(arg1):
            call_count[0] += 1
            return pd.DataFrame({"col": [1, 2, 3]})

        unique_key = f"test_ak_cache_uses_key_{id(self)}_{call_count}"
        CacheKey.ALL = {}

        result = ak_cache(mock_fun, "arg1", key=unique_key, ttl=60)

        assert result is not None
        assert call_count[0] == 1

        if unique_key in CacheKey.ALL:
            CacheKey.ALL[unique_key].delete()

    def test_ak_cache_generates_key_from_args(self):
        """Test that ak_cache generates key from function args."""

        def mock_fun(arg1, arg2):
            return pd.DataFrame({"col": [1, 2, 3]})

        result = ak_cache(mock_fun, "arg1", "arg2", ttl=60)

        assert result is not None

    def test_ak_cache_handles_exception(self):
        """Test that ak_cache handles exceptions gracefully."""

        def mock_fun():
            raise Exception("API Error")

        result = ak_cache(mock_fun, ttl=60)

        assert result is None

    def test_ak_cache_returns_cached_value(self):
        """Test that ak_cache returns cached value on second call."""
        df = pd.DataFrame({"col": [1, 2, 3]})
        mock_fun = mock.Mock(return_value=df)

        # First call should hit the function
        result1 = ak_cache(mock_fun, key="cache_test_key", ttl=60)
        call_count = mock_fun.call_count

        # Second call should return cached value without calling function
        result2 = ak_cache(mock_fun, key="cache_test_key", ttl=60)

        assert result1.equals(df)
        assert result2.equals(df)
        assert mock_fun.call_count == call_count  # No additional calls


class TestRecentTradeDate:
    """Test the recent_trade_date function."""

    def test_returns_date_object(self):
        """Test that function returns a date object."""
        result = recent_trade_date()
        assert isinstance(result, (date, datetime))

    def test_returns_not_future_date(self):
        """Test that returned date is not in the future."""
        result = recent_trade_date()
        today = date.today()

        if isinstance(result, datetime):
            result_date = result.date()
        else:
            result_date = result

        assert result_date <= today


class TestPortfolioOperations:
    """Test portfolio load and save operations."""

    def setup_method(self):
        """Set up temporary portfolio file."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_portfolio = Path(self.temp_dir) / "portfolio.json"

    def teardown_method(self):
        """Clean up temporary files."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_portfolio_nonexistent(self):
        """Test loading portfolio when file doesn't exist."""
        with mock.patch("mcp_aktools.shared.utils.PORTFOLIO_FILE", str(self.temp_portfolio)):
            result = load_portfolio()
            assert result == {}

    def test_save_and_load_portfolio(self):
        """Test saving and then loading portfolio data."""
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.5,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        with mock.patch("mcp_aktools.shared.utils.PORTFOLIO_FILE", str(self.temp_portfolio)):
            save_portfolio(test_data)
            result = load_portfolio()

            assert result["000001.sh"]["symbol"] == "000001"
            assert result["000001.sh"]["price"] == 10.5

    def test_save_portfolio_creates_directory(self):
        """Test that save_portfolio creates directory if needed."""
        from mcp_aktools.shared import constants
        from mcp_aktools.shared import utils as utils_module

        nested_dir = Path(self.temp_dir) / "nested" / "dir"
        portfolio_file = nested_dir / "portfolio.json"

        orig_file = utils_module.PORTFOLIO_FILE
        orig_const = constants.PORTFOLIO_FILE
        try:
            utils_module.PORTFOLIO_FILE = str(portfolio_file)
            constants.PORTFOLIO_FILE = str(portfolio_file)
            save_portfolio({"test": "data"})
            # Check that both directory and file exist
            assert nested_dir.exists(), "Directory should be created"
            assert portfolio_file.exists(), "Portfolio file should exist"
        finally:
            utils_module.PORTFOLIO_FILE = orig_file
            constants.PORTFOLIO_FILE = orig_const


class TestAkSearch:
    """Test the ak_search function."""

    def test_search_returns_none_when_no_match(self):
        """Test that search returns None when no match found."""
        with mock.patch("mcp_aktools.shared.utils.ak_cache", return_value=None):
            result = ak_search(symbol="NONEXISTENT")
            assert result is None

    def test_search_by_symbol(self):
        """Test searching by stock symbol."""
        mock_df = pd.DataFrame(
            {
                "code": ["000001"],
                "name": ["平安银行"],
            }
        )

        with mock.patch("mcp_aktools.shared.utils.ak_cache", return_value=mock_df):
            # We need to mock the market lookup as well
            with mock.patch("mcp_aktools.shared.utils.ak_search") as mock_search:
                mock_search.return_value = {"code": "000001", "name": "平安银行"}
                result = ak_search(symbol="000001", market="sh")

                assert result is not None

    def test_search_by_keyword(self):
        """Test searching by keyword."""
        mock_df = pd.DataFrame(
            {
                "code": ["000001"],
                "name": ["平安银行"],
            }
        )

        with mock.patch("mcp_aktools.shared.utils.ak_cache", return_value=mock_df):
            with mock.patch("mcp_aktools.shared.utils.ak_search") as mock_search:
                mock_search.return_value = {"code": "000001", "name": "平安银行"}
                result = ak_search(keyword="平安", market="sh")

                assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
