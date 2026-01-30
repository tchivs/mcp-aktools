"""Tests for portfolio module tools."""

import pytest
import json
import tempfile
import os
import uuid
from datetime import datetime
from pathlib import Path
from unittest import mock

from mcp_aktools.shared import constants
from mcp_aktools.shared import utils as utils_module
from mcp_aktools.cache import CacheKey

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import portfolio as portfolio_module
from mcp_aktools.tools import stocks as stocks_module

# Get actual functions from FunctionTool objects
portfolio_add_fn = portfolio_module.portfolio_add.fn
portfolio_view_fn = portfolio_module.portfolio_view.fn


def get_unique_portfolio_file(base_dir):
    """Generate a unique portfolio file path."""
    return Path(base_dir) / f"portfolio_{uuid.uuid4().hex}.json"


class TestPortfolioAdd:
    """Test the portfolio_add tool."""

    def setup_method(self):
        """Set up temporary portfolio file."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_portfolio = get_unique_portfolio_file(self.temp_dir)
        self.orig_file = utils_module.PORTFOLIO_FILE
        # Clear cache to avoid interference between tests
        CacheKey.ALL = {}

    def teardown_method(self):
        """Clean up temporary files."""
        utils_module.PORTFOLIO_FILE = self.orig_file
        constants.PORTFOLIO_FILE = self.orig_file
        if self.temp_portfolio.exists():
            self.temp_portfolio.unlink()
        if Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_portfolio_record(self):
        """Test adding a portfolio record."""
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        result = portfolio_add_fn(symbol="000001", price=10.5, volume=100, market="sh")
        
        assert isinstance(result, str)
        assert "成功" in result
        assert "000001" in result

    def test_add_multiple_records(self):
        """Test adding multiple portfolio records."""
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        
        portfolio_add_fn(symbol="000001", price=10.5, volume=100, market="sh")
        portfolio_add_fn(symbol="000002", price=20.0, volume=200, market="sz")
        
        # Verify both records exist
        with open(self.temp_portfolio, "r") as f:
            data = json.load(f)
        
        assert "000001.sh" in data
        assert "000002.sz" in data
        assert data["000001.sh"]["price"] == 10.5
        assert data["000002.sz"]["price"] == 20.0


class TestPortfolioView:
    """Test the portfolio_view tool."""

    def setup_method(self):
        """Set up temporary portfolio file."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_portfolio = get_unique_portfolio_file(self.temp_dir)
        self.orig_file = utils_module.PORTFOLIO_FILE
        # Clear cache to avoid interference between tests
        CacheKey.ALL = {}

    def teardown_method(self):
        """Clean up temporary files."""
        utils_module.PORTFOLIO_FILE = self.orig_file
        constants.PORTFOLIO_FILE = self.orig_file
        if self.temp_portfolio.exists():
            self.temp_portfolio.unlink()
        if Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_portfolio(self):
        """Test viewing empty portfolio."""
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        result = portfolio_view_fn()
        
        assert isinstance(result, str)
        assert "为空" in result

    def test_view_with_holdings(self):
        """Test viewing portfolio with holdings."""
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }
        
        # Pre-populate portfolio file
        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)
        
        mock_prices = "日期,开盘,收盘,最高,最低\n2024-01-01,9.5,11.0,11.5,9.0"
        
        # Create a mock function that returns the mock prices
        def mock_stock_prices(symbol, market, limit=1):
            return mock_prices
        
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module, "stock_prices", mock_stock_prices):
            result = portfolio_view_fn()
            
            assert isinstance(result, str)
            assert "000001" in result
            assert "成本" in result

    def test_view_handles_price_fetch_failure(self):
        """Test that view handles failure to fetch current price."""
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }
        
        # Pre-populate portfolio file
        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)
        
        # Create a mock function that raises an exception
        def mock_stock_prices_error(symbol, market, limit=1):
            raise Exception("API Error")
        
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module, "stock_prices", mock_stock_prices_error):
            result = portfolio_view_fn()
            
            assert isinstance(result, str)
            assert "000001" in result
            assert "无法获取" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
