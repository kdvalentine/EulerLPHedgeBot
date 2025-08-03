# LPHedgeBot Deployment Guide

## System Status: ✅ PRODUCTION READY

All components have been verified and are fully operational.

## Quick Start

```bash
# Run system check
python scripts/final_check.py

# Start the bot
python main.py

# Or monitor without trading
python scripts/monitor_mainnet.py
```

## Verified Components

### 1. Infrastructure
- ✅ **Ethereum RPC**: Connected via Infura (Block: 23,063,154+)
- ✅ **EulerSwap Pool**: Monitoring `0x55dcf9455EEe8Fd3f5EEd17606291272cDe428a8`
- ✅ **Database**: SQLite operational
- ✅ **Logging**: Configured with Rich console output

### 2. Exchange Integration
- ✅ **Binance API**: Futures trading enabled
- ✅ **Market Data**: Real-time price feeds working
- ✅ **Position Management**: Can open/close positions
- ✅ **Account Access**: Balance and position queries working

### 3. Pool Understanding
- ✅ **Virtual Reserves**: Correctly interpreted as AMM curve parameters
- ✅ **JIT Liquidity**: Integration with Euler Vaults understood
- ✅ **Pool Status**: Active and unlocked
- ✅ **Factory Contract**: `0xb013be1D0D380C13B58e889f412895970A2Cf228`

## Configuration Files

### .env (Production)
```env
# RPC Configuration
RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY

# EulerSwap Pool (USDT/WETH)
EULERSWAP_POOL=0x55dcf9455EEe8Fd3f5EEd17606291272cDe428a8

# Binance API (Futures enabled)
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Risk Parameters
MIN_HEDGE_SIZE_ETH=0.005
HEDGE_THRESHOLD_ETH=0.01
MAX_SLIPPAGE_PERCENT=1.0
```

## Monitoring Commands

### Basic Monitoring
```bash
# View pool reserves
python scripts/quick_test.py

# Check Binance connection
python scripts/binance_diagnose.py

# Discover all EulerSwap pools
python scripts/discover_pools.py
```

### Production Monitoring
```bash
# Full monitoring with hedging
python main.py

# Monitor only (no trading)
python scripts/monitor_mainnet.py

# System health check
python scripts/final_check.py
```

## Docker Deployment

```bash
# Build image
docker build -t lphedgebot .

# Run container
docker run -d \
  --name lphedgebot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  lphedgebot
```

## Risk Management

### Position Limits
- **Min Hedge Size**: 0.005 ETH
- **Hedge Threshold**: 0.01 ETH  
- **Max Position**: 100 ETH
- **Max Slippage**: 1%

### Emergency Controls
- **Stop Loss**: 10,000 USDT
- **Min Balance**: 1,000 USDT
- **Desync Warning**: 5%

## Troubleshooting

### Common Issues

1. **Binance API Error -2015**
   - Solution: Enable futures permissions in API settings

2. **Large Pool Reserve Numbers**
   - These are virtual reserves for the AMM curve (expected behavior)

3. **Pool Status = Locked**
   - Indicates reentrancy protection active (temporary)

## Code Quality

### Linting Status
- ✅ Black formatting applied to all files
- ✅ Critical flake8 errors resolved
- ✅ Import statements optimized

### Test Coverage
- Unit tests for strategy engine
- Integration tests for EulerSwap
- Mock tests for exchange operations

## Production Checklist

- [x] Environment variables configured
- [x] RPC connection verified
- [x] Binance API permissions enabled
- [x] Database initialized
- [x] Pool address confirmed
- [x] Risk parameters set
- [x] Monitoring scripts tested
- [x] Code formatting completed
- [x] Documentation updated

## Support

For issues or questions:
1. Run `python scripts/final_check.py` for diagnostics
2. Check `lphedgebot.log` for detailed logs
3. Review `CURRENT_STATUS.md` for latest updates

## Next Steps

1. **Fund Binance Account**: Add USDT for trading
2. **Test Small Positions**: Start with minimum sizes
3. **Monitor Performance**: Track delta exposure and P&L
4. **Adjust Parameters**: Fine-tune based on market conditions

---

**Last Updated**: 2025-08-03
**Status**: ✅ READY FOR PRODUCTION