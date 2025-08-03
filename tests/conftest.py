"""Pytest configuration and fixtures."""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from models import PositionSnapshot, HedgeSnapshot, Trade
from models.hedge_snapshot import HedgeAction
from models.trade import OrderSide, OrderType, OrderStatus
from config_manager import Config


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return Config(
        rpc_url="http://localhost:8545",
        eulerswap_pool="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
        binance_api_key="test_key",
        binance_api_secret="test_secret",
        binance_testnet=True,
        min_hedge_size_eth=Decimal("0.005"),
        hedge_threshold_eth=Decimal("0.01"),
        max_slippage_percent=Decimal("0.5"),
        default_leverage=Decimal("1"),
        polling_interval_seconds=5,
        database_url="sqlite:///:memory:",
    )


@pytest.fixture
def sample_position_snapshot():
    """Create a sample position snapshot."""
    return PositionSnapshot(
        reserve_token0=Decimal("10000"),
        reserve_token1=Decimal("5.5"),
        short_position_size=Decimal("5.0"),
        timestamp=datetime.utcnow(),
        block_number=18000000,
        pool_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    )


@pytest.fixture
def sample_hedge_snapshot():
    """Create a sample hedge snapshot."""
    return HedgeSnapshot(
        action=HedgeAction.OPEN_SHORT,
        size=Decimal("0.5"),
        price=Decimal("2000"),
        timestamp=datetime.utcnow(),
        delta_before=Decimal("0.5"),
        delta_after=Decimal("0"),
        leverage=Decimal("1"),
        exchange="binance",
        order_id="12345",
        success=True,
    )


@pytest.fixture
def sample_trade():
    """Create a sample trade."""
    return Trade(
        symbol="ETH/USDT:USDT",
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        size=Decimal("0.5"),
        price=Decimal("2000"),
        timestamp=datetime.utcnow(),
        order_id="12345",
        status=OrderStatus.FILLED,
        fee=Decimal("0.001"),
        fee_currency="USDT",
        exchange="binance",
    )


@pytest.fixture
def mock_exchange():
    """Create a mock exchange."""
    exchange = AsyncMock()
    exchange.connect = AsyncMock()
    exchange.disconnect = AsyncMock()
    exchange.get_mark_price = AsyncMock(return_value=Decimal("2000"))
    exchange.get_funding_rate = AsyncMock(return_value=Decimal("0.0001"))
    exchange.get_balance = AsyncMock(return_value=Decimal("10000"))
    exchange.get_current_perpetual_position = AsyncMock(
        return_value={
            "symbol": "ETH/USDT:USDT",
            "size": Decimal("5"),
            "side": "short",
            "entry_price": Decimal("2000"),
            "mark_price": Decimal("2000"),
            "unrealized_pnl": Decimal("0"),
            "realized_pnl": Decimal("0"),
            "margin": Decimal("10000"),
            "leverage": Decimal("1"),
        }
    )
    exchange.set_leverage = AsyncMock(return_value=True)
    return exchange


@pytest.fixture
def mock_database_manager():
    """Create a mock database manager."""
    db = Mock()
    db.save_position_snapshot = Mock(return_value=1)
    db.save_hedge_snapshot = Mock(return_value=1)
    db.save_trade = Mock(return_value=1)
    db.get_latest_position_snapshot = Mock(return_value=None)
    db.get_position_snapshots = Mock(return_value=[])
    db.get_hedge_snapshots = Mock(return_value=[])
    db.get_recent_trades = Mock(return_value=[])
    return db
