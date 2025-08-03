# NoetherBot - Automated Delta-Neutral Hedging for EulerSwap

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A production-ready Python framework for automated delta-neutral strategies on EulerSwap JIT liquidity pools. NoetherBot continuously monitors on-chain pool reserves and automatically hedges ETH exposure through perpetual futures, enabling liquidity providers to earn yields while maintaining market neutrality.

## 🏗️ Architecture

```mermaid
graph TB
    subgraph On-Chain
        EP[EulerSwap Pool<br/>USDT/WETH] 
        RPC[Ethereum RPC]
    end
    
    subgraph NoetherBot
        SM[SwapMonitor] --> SE[StrategyEngine]
        SE --> RM[RiskManager]
        SE --> EM[ExchangeManager]
        
        SM --> DB[(Database<br/>SQLite)]
        SE --> DB
        
        CM[ConfigManager] --> SM
        CM --> SE
        CM --> RM
        
        LM[LoggerManager] --> TUI[Terminal UI]
        SM --> LM
        SE --> LM
        RM --> LM
        EM --> LM
    end
    
    subgraph CEX
        BIN[Binance<br/>Perpetuals]
    end
    
    RPC -->|getReserves()| SM
    EM <-->|API| BIN
    
    style EP fill:#e1f5fe
    style BIN fill:#fff3e0
    style DB fill:#f3e5f5
    style TUI fill:#e8f5e9
```

## ✨ Features

- **Real-time Monitoring**: Continuously polls EulerSwap pool reserves via RPC
- **Automated Hedging**: Maintains delta neutrality through perpetual futures
- **Risk Management**: Comprehensive risk checks, position limits, and rate limiting
- **Virtual Reserves**: Correctly interprets EulerSwap's virtual AMM curve parameters
- **JIT Liquidity**: Integrates with Euler Vaults for just-in-time liquidity provision
- **Terminal UI**: Live dashboard with reserve/position graphs and real-time logs
- **Persistent Storage**: SQLite database for historical data and analytics
- **Modular Design**: Clean architecture with separated concerns
- **Production Ready**: Full test coverage, Docker support, and CI/CD pipeline

## 📋 Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Ethereum RPC endpoint (Alchemy, Infura, etc.)
- Binance API credentials (with futures trading enabled)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/noether-bot.git
cd noether-bot
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Configure Environment

For **Ethereum Mainnet** monitoring, use the mainnet configuration:

```bash
cp .env.mainnet .env
```

Edit `.env` with your API keys:

```env
# RPC Configuration (Required)
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY

# Live EulerSwap USDT/WETH Pool (Mainnet)
EULERSWAP_POOL=0x55dcf9455eee8fd3f5eed17606291272cde428a8

# Euler Vaults (Mainnet)
EULER_VAULT_USDT=0x313603FA690301b0CaeEf8069c065862f9162162
EULER_VAULT_WETH=0xD8b27CF359b7D15710a5BE299AF6e7Bf904984C2

# Token Addresses (Mainnet)
USDT_ADDRESS=0xdac17f958d2ee523a2206206994597c13d831ec7
WETH_ADDRESS=0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2

# Binance API (Required)
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret

# Strategy Parameters (Recommended defaults)
MIN_HEDGE_SIZE_ETH=0.005
HEDGE_THRESHOLD_ETH=0.01
MAX_DELTA_EXPOSURE_ETH=0.5
```

### 4. Run the Bot

#### Monitor Mainnet Pool (Live Data)

```bash
PYTHONPATH=. poetry run python scripts/monitor_mainnet.py
```

This monitors the live USDT/WETH pool at `0x55dcf9455eee8fd3f5eed17606291272cde428a8`.

#### Terminal UI Mode (Full Bot)

```bash
PYTHONPATH=. poetry run python tui/hedge_tui.py
```

#### Headless Mode (Automated)

```bash
PYTHONPATH=. poetry run python main.py
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t noether-bot .

# Run with environment file
docker run --env-file .env -it noether-bot
```

### Docker Compose

```bash
docker-compose up
```

## 🧪 Testing

### Run All Tests

```bash
poetry run pytest
```

### Run with Coverage

```bash
poetry run pytest --cov=. --cov-report=html
```

### Run Specific Tests

```bash
poetry run pytest tests/test_strategy_engine.py -v
```

## 📊 Terminal UI

The Terminal UI provides real-time monitoring and control:

### Features

- **Live Graphs**: WETH reserves and short position tracking
- **Position Status**: Current reserves, short size, and delta
- **Strategy Config**: Active parameters and thresholds
- **Real-time Logs**: Color-coded event stream
- **Keyboard Controls**: `q` to quit, more shortcuts available

### UI Layout

```
┌─────────────────────────┬──────────────────────────┐
│   WETH Reserve Graph    │   Current Position       │
│                         │   ─────────────────      │
│   Short Position Graph  │   USDT: 10,000.00       │
│                         │   WETH: 5.25            │
│                         │   Short: 5.20           │
│                         │   Delta: 0.05           │
├─────────────────────────┼──────────────────────────┤
│                         │   Strategy Config        │
│   Real-time Logs        │   ─────────────────     │
│                         │   Threshold: 0.01 ETH   │
│   [POSITION_POLLING]    │   Min Size: 0.005 ETH   │
│   [CALCULATED_HEDGE]    │   Leverage: 1x          │
│   [TRADE_EXECUTED]      │                         │
└─────────────────────────┴──────────────────────────┘
```

## 🔧 Configuration

### Strategy Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MIN_HEDGE_SIZE_ETH` | Minimum hedge size to execute | 0.005 ETH |
| `HEDGE_THRESHOLD_ETH` | Delta threshold to trigger hedge | 0.01 ETH |
| `MAX_SLIPPAGE_PERCENT` | Maximum allowed slippage | 0.5% |
| `DEFAULT_LEVERAGE` | Default leverage for positions | 1x |

### Monitoring Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `POLLING_INTERVAL_SECONDS` | Time between reserve polls | 5 seconds |
| `MAX_RETRIES` | Maximum retry attempts | 3 |
| `RETRY_DELAY_SECONDS` | Delay between retries | 2 seconds |

## 📁 Project Structure

```
noether-bot/
├── abi/                    # Contract ABIs
├── config_manager/         # Configuration management
├── database_manager/       # SQLite persistence
├── exchange_manager/       # CEX integrations
│   ├── iexchange.py       # Abstract interface
│   └── binance_exchange.py # Binance implementation
├── logger_manager/         # Logging system
├── models/                 # Data models
│   ├── position_snapshot.py
│   ├── hedge_snapshot.py
│   └── trade.py
├── risk_manager/          # Risk management
├── strategy_engine/       # Core hedging logic
├── swap_monitor/          # On-chain monitoring
├── tui/                   # Terminal UI
│   └── hedge_tui.py
├── tests/                 # Test suite
├── main.py               # CLI entry point
├── pyproject.toml        # Dependencies
└── Dockerfile            # Container definition
```

## 🔐 Security Considerations

- **API Keys**: Never commit API keys. Use environment variables
- **Rate Limits**: Built-in rate limiting to prevent API bans
- **Risk Checks**: Multiple validation layers before trade execution
- **Emergency Stop**: Manual intervention capabilities
- **Audit Trail**: All actions logged to database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational purposes only. Trading cryptocurrencies carries significant risk. Always perform your own research and testing before using in production. The authors are not responsible for any financial losses.

## 🆘 Support

- **Documentation**: See `/docs` folder for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join our Discord server

## 🙏 Acknowledgments

- EulerSwap team for the innovative JIT liquidity system
- CCXT library for exchange integrations
- Textual framework for the beautiful TUI
- Emmy Noether for the mathematical inspiration