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

from mcp_aktools.tools import portfolio as portfolio_module

portfolio_add_fn = portfolio_module.portfolio_add.fn
portfolio_view_fn = portfolio_module.portfolio_view.fn
portfolio_chart_fn = portfolio_module.portfolio_chart.fn


def get_unique_portfolio_file(base_dir):
    return Path(base_dir) / f"portfolio_{uuid.uuid4().hex}.json"


class TestPortfolioAdd:
    """Test the portfolio_add tool."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_portfolio = get_unique_portfolio_file(self.temp_dir)
        self.orig_file = utils_module.PORTFOLIO_FILE
        CacheKey.ALL = {}

    def teardown_method(self):
        utils_module.PORTFOLIO_FILE = self.orig_file
        constants.PORTFOLIO_FILE = self.orig_file
        if self.temp_portfolio.exists():
            self.temp_portfolio.unlink()
        if Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_portfolio_record(self):
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        result = portfolio_add_fn(symbol="000001", price=10.5, volume=100, market="sh")

        assert isinstance(result, str)
        assert "成功" in result
        assert "000001" in result

    def test_add_multiple_records(self):
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)

        portfolio_add_fn(symbol="000001", price=10.5, volume=100, market="sh")
        portfolio_add_fn(symbol="000002", price=20.0, volume=200, market="sz")

        with open(self.temp_portfolio, "r") as f:
            data = json.load(f)

        assert "000001.sh" in data
        assert "000002.sz" in data
        assert data["000001.sh"]["price"] == 10.5
        assert data["000002.sz"]["price"] == 20.0


class TestPortfolioView:
    """Test the portfolio_view tool."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_portfolio = get_unique_portfolio_file(self.temp_dir)
        self.orig_file = utils_module.PORTFOLIO_FILE
        CacheKey.ALL = {}

    def teardown_method(self):
        utils_module.PORTFOLIO_FILE = self.orig_file
        constants.PORTFOLIO_FILE = self.orig_file
        if self.temp_portfolio.exists():
            self.temp_portfolio.unlink()
        if Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_portfolio(self):
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        result = portfolio_view_fn()

        assert isinstance(result, str)
        assert "为空" in result

    def test_view_with_holdings(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "日期,开盘,收盘,最高,最低\n2024-01-01,9.5,11.0,11.5,9.0"

        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module.stock_prices, "fn", return_value=mock_prices):
            result = portfolio_view_fn()

            assert isinstance(result, str)
            assert "000001" in result
            assert "成本" in result
            assert "盈亏" in result

    def test_view_handles_price_fetch_failure(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)

        def mock_error(*args, **kwargs):
            raise Exception("API Error")

        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module.stock_prices, "fn", side_effect=mock_error):
            result = portfolio_view_fn()

            assert isinstance(result, str)
            assert "000001" in result
            assert "无法获取" in result


class TestPortfolioChart:
    """Test the portfolio_chart tool."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_portfolio = get_unique_portfolio_file(self.temp_dir)
        self.orig_file = utils_module.PORTFOLIO_FILE
        CacheKey.ALL = {}

    def teardown_method(self):
        utils_module.PORTFOLIO_FILE = self.orig_file
        constants.PORTFOLIO_FILE = self.orig_file
        if self.temp_portfolio.exists():
            self.temp_portfolio.unlink()
        if Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_portfolio_chart(self):
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        result = portfolio_chart_fn()

        assert "为空" in result

    def test_chart_with_positive_returns(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "日期,开盘,收盘,最高,最低\n2024-01-01,9.5,12.0,12.5,9.0"

        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module.stock_prices, "fn", return_value=mock_prices):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "000001" in result
            assert "+" in result

    def test_chart_with_negative_returns(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "日期,开盘,收盘,最高,最低\n2024-01-01,9.5,8.0,10.0,7.5"

        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module.stock_prices, "fn", return_value=mock_prices):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "-" in result

    def test_chart_handles_price_fetch_failure(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)

        def mock_error(*args, **kwargs):
            raise Exception("API Error")

        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module.stock_prices, "fn", side_effect=mock_error):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "0.00%" in result

    def test_chart_with_multiple_holdings(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            },
            "000002.sz": {
                "symbol": "000002",
                "price": 20.0,
                "volume": 50,
                "market": "sz",
                "time": datetime.now().isoformat(),
            },
        }

        os.makedirs(os.path.dirname(self.temp_portfolio), exist_ok=True)
        with open(self.temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "日期,开盘,收盘,最高,最低\n2024-01-01,9.5,11.0,11.5,9.0"

        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        with mock.patch.object(portfolio_module.stock_prices, "fn", return_value=mock_prices):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "000001" in result
            assert "000002" in result
            assert "最大波动" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
