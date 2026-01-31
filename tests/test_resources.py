"""Tests for MCP resources."""

from mcp_aktools.server import mcp


def test_stock_dynamic_analysis_template():
    """Test that stock dynamic analysis resource returns correct content."""
    # Get the resource template from the resource manager
    template = mcp._resource_manager._templates.get("stock://{symbol}/analysis")
    assert template is not None, "stock://{symbol}/analysis template not registered"

    # Call the underlying function with a test symbol
    result = template.fn(symbol="600519")

    # Verify symbol is interpolated
    assert "600519" in result
    assert "专属分析建议" in result

    # Verify recommended tools are mentioned
    assert "stock_prices" in result
    assert "stock_news" in result
    assert "draw_ascii_chart" in result
    assert "stock_indicators_a" in result

    # Verify analysis structure
    assert "推荐工具链" in result
    assert "关键指标关注" in result
    assert "分析流程" in result

    # Verify technical indicators mentioned
    assert "MACD" in result
    assert "RSI" in result
    assert "布林带" in result


def test_sector_flow_guide_template():
    """Test that sector flow guide resource returns correct content."""
    # Get the resource template from the resource manager
    template = mcp._resource_manager._templates.get("market://{sector}/flow")
    assert template is not None, "market://{sector}/flow template not registered"

    # Call the underlying function with a test sector
    result = template.fn(sector="半导体")

    # Verify sector is interpolated
    assert "半导体" in result
    assert "板块资金流向分析" in result

    # Verify recommended tools are mentioned
    assert "stock_sector_fund_flow_rank" in result
    assert "stock_zt_pool_em" in result
    assert "northbound_funds" in result

    # Verify analysis structure
    assert "推荐工具" in result
    assert "分析要点" in result
    assert "操作建议" in result

    # Verify key concepts mentioned
    assert "主力净流入" in result
    assert "北向资金" in result
    assert "涨停股" in result


def test_tech_analysis_resource():
    """Test that technical analysis resource returns correct content."""
    # Get the resource from the resource manager
    resource = mcp._resource_manager._resources.get("skill://trading/logic/technical-analysis")
    assert resource is not None, "skill://trading/logic/technical-analysis resource not registered"

    # Call the underlying function
    result = resource.fn()

    # Verify technical indicators are explained
    assert "MACD" in result
    assert "RSI" in result
    assert "BOLL" in result
    assert "KDJ" in result

    # Verify it's a SOP guide
    assert "技术指标解读 SOP" in result


def test_risk_management_resource():
    """Test that risk management resource returns correct content."""
    # Get the resource from the resource manager
    resource = mcp._resource_manager._resources.get("skill://trading/strategy/risk-management")
    assert resource is not None, "skill://trading/strategy/risk-management resource not registered"

    # Call the underlying function
    result = resource.fn()

    # Verify risk management principles
    assert "风险管理原则" in result
    assert "止损" in result
    assert "仓位" in result
    assert "波动率" in result


def test_crypto_analysis_resource():
    """Test that crypto analysis resource returns correct content."""
    # Get the resource from the resource manager
    resource = mcp._resource_manager._resources.get("skill://crypto/logic/analysis-sop")
    assert resource is not None, "skill://crypto/logic/analysis-sop resource not registered"

    # Call the underlying function
    result = resource.fn()

    # Verify crypto-specific analysis
    assert "加密货币分析 SOP" in result
    assert "多空比" in result
    assert "资金费率" in result
    assert "主动买卖" in result

    # Verify risk warnings
    assert "风险提示" in result
    assert "止损" in result


def test_precious_metals_analysis_resource():
    """Test that precious metals analysis resource returns correct content."""
    # Get the resource from the resource manager
    resource = mcp._resource_manager._resources.get("skill://trading/logic/precious-metals-analysis")
    assert resource is not None, "skill://trading/logic/precious-metals-analysis resource not registered"

    # Call the underlying function
    result = resource.fn()

    # Verify precious metals analysis structure
    assert "贵金属分析 SOP" in result
    assert "价格趋势判断" in result
    assert "资金流向判断" in result
    assert "期现基差解读" in result
    assert "避险情绪指标" in result
    assert "金银比价" in result

    # Verify key concepts
    assert "上海金交所" in result
    assert "伦敦金" in result
    assert "ETF持仓" in result
    assert "COMEX库存" in result


def test_stock_dynamic_analysis_different_symbols():
    """Test stock analysis with different symbols."""
    template = mcp._resource_manager._templates.get("stock://{symbol}/analysis")

    symbols = ["000001", "600000", "AAPL"]
    for symbol in symbols:
        result = template.fn(symbol=symbol)
        assert symbol in result
        assert len(result) > 100  # Should have substantial content


def test_stock_dynamic_analysis_edge_cases():
    """Test stock analysis with edge cases."""
    template = mcp._resource_manager._templates.get("stock://{symbol}/analysis")

    # Empty string
    result = template.fn(symbol="")
    assert isinstance(result, str)
    assert len(result) > 50

    # Special characters
    result = template.fn(symbol="600519.SH")
    assert isinstance(result, str)
    assert "600519.SH" in result


def test_sector_flow_guide_different_sectors():
    """Test sector flow guide with different sectors."""
    template = mcp._resource_manager._templates.get("market://{sector}/flow")

    sectors = ["电子", "医药", "新能源"]
    for sector in sectors:
        result = template.fn(sector=sector)
        assert sector in result
        assert len(result) > 100


def test_sector_flow_guide_edge_cases():
    """Test sector flow guide with edge cases."""
    template = mcp._resource_manager._templates.get("market://{sector}/flow")

    # Empty string
    result = template.fn(sector="")
    assert isinstance(result, str)
    assert len(result) > 50

    # Special characters
    result = template.fn(sector="半导体/芯片")
    assert isinstance(result, str)
    assert "半导体/芯片" in result
