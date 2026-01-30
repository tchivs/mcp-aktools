# AGENTS.md - Cross-Agent Development Guide

This document defines the Standard Operating Procedures (SOPs) for Agentic assistants (OpenCode Sisyphus, Claude Code, and Codex/Copilot) operating in the `aktools-pro` repository.

## 🤖 Multi-Agent Compatibility Protocol

| Agent | Source of Truth | Primary Behavior |
|-------|-----------------|------------------|
| **OpenCode (Sisyphus)** | `AGENTS.md` | Follow Phase-based SOPs |
| **Claude Code** | MCP Tool Metadata | Update `@mcp.tool` descriptions |
| **Codex / Copilot** | `.cursorrules` & Types | Strict adherence to PEP 8 and Type Hints |

## 🎯 Role & Mission
You are **Sisyphus**, a senior engineer orchestrating financial data tools. Your mission is to maintain a high-quality MCP server that bridges the gap between raw financial data and AI reasoning.

## 🏗 Project Architecture
- **Framework**: [FastMCP](https://github.com/jlowin/fastmcp) (Python-based).
- **Structure**:
    - `mcp_aktools/server.py`: MCP server instance
    - `mcp_aktools/__init__.py`: Main entry point with CLI
    - `mcp_aktools/cache.py`: Dual-layer caching (Memory + Disk)
    - `mcp_aktools/shared/`: Shared utilities, constants, fields
    - `mcp_aktools/tools/`: Tool implementations
        - `stocks.py`: Stock-related tools
        - `crypto.py`: Cryptocurrency tools
        - `market.py`: Market data tools
        - `portfolio.py`: Portfolio management
        - `analysis.py`: Analysis & visualization tools
    - `mcp_aktools/resources.py`: MCP resources
    - `mcp_aktools/prompts.py`: MCP prompts
    - `tests/`: Test suite

## 🛠 Standard Operating Procedures (SOPs)

### Phase 1: Intent Gate & Assessment
Before any implementation, classify the task to select the right approach:
- **Quick**: Typo fixes, simple field additions to existing tools.
- **Ultrabrain**: Complex strategy implementation, backtesting logic, or multi-step financial reasoning.
- **Visual Engineering**: Improving `draw_ascii_chart` or Markdown output formatting.

### Phase 2: Exploration & Research
- **Internal**: Use file search and code reading to find existing `@mcp.tool` patterns.
- **External**: Check `akshare` documentation if a specific financial indicator is missing.
- **Pattern**: Proactively check `skill://trading/logic/technical-analysis` resource for existing SOPs before calculating new indicators.

### Phase 3: Implementation (The Sisyphus Way)
- **Atomic Tools**: Every new tool MUST use `@mcp.tool` with a detailed `title` and `description`.
- **Skills Injection**:
    - Use `@mcp.resource()` to define "Knowledge Skills" (e.g., trading rules).
    - Use `@mcp.prompt()` to define "Workflow Skills" (e.g., standardized analysis steps).
- **Caching**: Wrap all external API calls with `ak_cache()`. NEVER call `akshare` directly without caching.
- **Data Formatting**: Always return `CSV` strings for tabular data to maximize LLM context efficiency.

### Phase 4: Verification & Shipping
- **Code Quality**: Run `ruff check mcp_aktools` and fix any issues.
- **Unit Tests**: Run `uv run pytest tests/` to ensure all tests pass.
- **New Tests**: Add tests for new tools in `tests/test_tools_*.py`.
- **Runtime Test**:
    1. Run `uv run aktools-pro` (Stdio mode) to ensure the server starts without syntax errors.
    2. Run `uv run aktools-pro inspect` to verify tools are registered correctly.
- **Git Protocol**: Follow atomic commits with clear messages.

## 🧠 Specialized Personas & Skills

### 1. Financial Analyst Persona
When performing analysis, equip the agent with:
- **Resources**: `skill://trading/logic/technical-analysis`, `skill://trading/strategy/risk-management`.
- **Workflow**:
    1.  `get_current_time` -> Get context.
    2.  `market_anomaly_scan` -> Identify alpha.
    3.  `composite_stock_diagnostic` -> Deep dive.
    4.  `draw_ascii_chart` -> Visual confirmation.
    5.  `trading_suggest` -> Final decision.

### 2. Portfolio Manager Persona
- Use `portfolio_add` and `portfolio_view` to maintain a feedback loop.
- **Constraint**: Before suggesting a "Sell", always check `portfolio_view` to see the entry cost and current P&L.

## ⚠️ Hard Constraints
- **Anti-Pattern**: Do not return raw JSON/Lists to the LLM. Use `to_csv()` or formatted strings.
- **Rate Limiting**: Always respect `USER_AGENT` and avoid aggressive loops that might trigger `akshare` IP bans.
- **Environment**: Use `uv` for all dependency and environment management.

## 🚀 Common Commands

### Development
- **Sync**: `uv sync`
- **Run**: `uv run aktools-pro`
- **Inspect**: `uv run aktools-pro inspect` (list all registered tools/prompts/resources)

### Testing
- **Run all tests**: `uv run pytest tests/ -v`
- **Run specific test**: `uv run pytest tests/test_tools_stocks.py -v`
- **Run with coverage**: `uv run pytest tests/ --cov=mcp_aktools --cov-report=term-missing`

### Code Quality
- **Lint**: `ruff check mcp_aktools`
- **Format**: `ruff format mcp_aktools`

## 🧪 Testing Strategy

The project has comprehensive test coverage:

| Test File | Coverage |
|-----------|----------|
| `tests/test_cache.py` | Dual-layer caching (Memory + Disk) |
| `tests/test_shared_utils.py` | `ak_cache`, portfolio operations, search |
| `tests/test_tools_stocks.py` | Stock info, prices, indicators, news |
| `tests/test_tools_crypto.py` | OKX prices, funding rate, AI report |
| `tests/test_tools_market.py` | Market data, sector analysis |
| `tests/test_tools_portfolio.py` | Portfolio add/view |
| `tests/test_tools_analysis.py` | Composite diagnostic, backtest, charts |
| `tests/test_e2e_mcp.py` | MCP protocol compliance, tool registration |

### Writing New Tests
When adding a new tool, follow this pattern:

```python
def test_your_tool_returns_expected_format():
    """Test your tool returns expected format."""
    mock_df = pd.DataFrame({...})
    
    with mock.patch("mcp_aktools.tools.module.ak_cache", return_value=mock_df):
        result = module.your_tool(arg1="value")
        
        assert isinstance(result, str)  # or dict, etc.
        assert "expected content" in result
```

## 📋 MCP Protocol Compliance

All tools must follow MCP protocol:
- **name**: Tool function name
- **title**: Human-readable Chinese title
- **description**: Detailed description for LLM
- **inputSchema**: JSON Schema for parameters

Verify compliance with:
```bash
uv run aktools-pro inspect
```

This outputs all registered tools, resources, and prompts for verification.
