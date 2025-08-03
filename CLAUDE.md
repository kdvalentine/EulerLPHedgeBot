# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LPHedgeBot is a Python framework for automated delta-neutral strategies on EulerSwap, specifically designed for USDT/WETH pools. The bot monitors pool reserves, tracks off-chain short positions, calculates delta exposure, and automatically executes hedge trades to maintain delta neutrality.

## EulerSwap Integration

The bot integrates with the actual EulerSwap protocol contracts:
- **getReserves()** returns 3 values: `(reserve0, reserve1, status)` where status indicates pool state
- **Virtual Reserves**: EulerSwap uses virtual reserves that can desynchronize from actual vault balances
- **Custom Curve**: Uses a specialized AMM curve with equilibrium points and concentration factors
- **EVC Integration**: Integrated with Ethereum Vault Connector for collateral management
- **Flash Swaps**: Supports flash swaps via the `eulerSwapCall` callback mechanism

## Commands

### Installation
```bash
poetry install
```

### Running the Terminal UI
```bash
PYTHONPATH=. poetry run python tui/hedge_tui.py
```

### Environment Configuration
Create a `.env` file with:
```bash
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
RPC_URL=https://your_rpc_url
EULERSWAP_POOL=0xYourEulerSwapPoolAddress
```

## Architecture

The framework follows a modular architecture with clear separation of concerns:

- **SwapMonitor**: Polls on-chain data via RPC to fetch pool reserves
- **StrategyEngine**: Core hedging logic, delta calculations, and threshold management
- **RiskManager**: Risk validation, leverage determination, and slippage control
- **ExchangeManager**: Abstract interface for CEX integration (Binance implementation)
- **DatabaseManager**: In-memory persistence layer (easily extendable to SQLite)
- **ConfigManager**: Centralized configuration and credential management
- **LoggerManager**: Structured logging with TUI integration
- **TUI**: Terminal UI built with Textual for real-time monitoring

## Project Structure

```
lphedgebot/
├── abi/                  # Contract ABIs for EulerSwap
├── config/               # Configuration management
├── database_manager/     # Data persistence layer
├── exchange_manager/     # CEX interface implementations
├── logger_manager/       # Logging utilities
├── models/              # Data models (PositionSnapshot, etc.)
├── risk_manager/        # Risk logic and validations
├── strategy_engine/     # Core hedging algorithms
├── swap_monitor/        # On-chain monitoring via RPC
├── tui/                 # Terminal UI components
└── main.py             # Non-TUI entrypoint
```

## Key Technical Details

- **Python 3.11+** required
- Uses **poetry** for dependency management
- **CCXT** library for exchange integration
- **Web3.py** for Ethereum RPC interaction
- **Textual** framework for terminal UI
- Polling interval: 5 seconds for position monitoring
- Delta hedging threshold: Configurable (default 0.005 WETH)