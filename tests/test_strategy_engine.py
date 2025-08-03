"""Tests for the strategy engine."""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from strategy_engine import StrategyEngine
from models import PositionSnapshot, Trade
from models.trade import OrderSide, OrderType, OrderStatus
from models.hedge_snapshot import HedgeAction


@pytest.mark.asyncio
async def test_process_position_snapshot_no_hedge_needed(
    mock_config, mock_exchange, mock_database_manager
):
    """Test processing snapshot when no hedge is needed."""
    # Create risk manager mock
    risk_manager = Mock()
    risk_manager.should_hedge = Mock(return_value=(False, Decimal("0")))

    # Create strategy engine
    engine = StrategyEngine(
        config=mock_config,
        exchange=mock_exchange,
        risk_manager=risk_manager,
        database_manager=mock_database_manager,
    )

    # Create snapshot with small delta
    snapshot = PositionSnapshot(
        reserve_token0=Decimal("10000"),
        reserve_token1=Decimal("5"),
        short_position_size=Decimal("5"),
        timestamp=datetime.utcnow(),
    )

    # Process snapshot
    result = await engine.process_position_snapshot(snapshot)

    # Verify no hedge was executed
    assert result is None
    risk_manager.should_hedge.assert_called_once_with(snapshot)


@pytest.mark.asyncio
async def test_process_position_snapshot_hedge_executed(
    mock_config, mock_exchange, mock_database_manager
):
    """Test processing snapshot when hedge is needed and executed."""
    # Create risk manager mock
    risk_manager = Mock()
    risk_manager.should_hedge = Mock(return_value=(True, Decimal("0.5")))
    risk_manager.check_slippage = Mock(return_value=True)
    risk_manager.calculate_leverage = Mock(return_value=Decimal("1"))
    risk_manager.record_trade = Mock()

    # Create mock trade
    mock_trade = Trade(
        symbol="ETH/USDT:USDT",
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        size=Decimal("0.5"),
        price=Decimal("2000"),
        timestamp=datetime.utcnow(),
        order_id="12345",
        status=OrderStatus.FILLED,
    )

    mock_exchange.open_short_position = AsyncMock(return_value=mock_trade)

    # Create strategy engine
    engine = StrategyEngine(
        config=mock_config,
        exchange=mock_exchange,
        risk_manager=risk_manager,
        database_manager=mock_database_manager,
    )

    # Create snapshot with delta requiring hedge
    snapshot = PositionSnapshot(
        reserve_token0=Decimal("10000"),
        reserve_token1=Decimal("5.5"),
        short_position_size=Decimal("5"),
        timestamp=datetime.utcnow(),
    )

    # Process snapshot
    result = await engine.process_position_snapshot(snapshot)

    # Verify hedge was executed
    assert result is not None
    assert result.action == HedgeAction.OPEN_SHORT
    assert result.size == Decimal("0.5")
    assert result.success is True

    # Verify calls
    risk_manager.should_hedge.assert_called_once_with(snapshot)
    mock_exchange.get_mark_price.assert_called_once()
    mock_exchange.open_short_position.assert_called_once()
    mock_database_manager.save_hedge_snapshot.assert_called_once()
    mock_database_manager.save_trade.assert_called_once()


@pytest.mark.asyncio
async def test_execute_hedge_open_short(
    mock_config, mock_exchange, mock_database_manager
):
    """Test executing a hedge to open short position."""
    # Create risk manager mock
    risk_manager = Mock()
    risk_manager.check_slippage = Mock(return_value=True)
    risk_manager.calculate_leverage = Mock(return_value=Decimal("2"))
    risk_manager.record_trade = Mock()

    # Create mock trade
    mock_trade = Trade(
        symbol="ETH/USDT:USDT",
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        size=Decimal("1"),
        price=Decimal("2000"),
        timestamp=datetime.utcnow(),
        order_id="12345",
        status=OrderStatus.FILLED,
    )

    mock_exchange.open_short_position = AsyncMock(return_value=mock_trade)

    # Create strategy engine
    engine = StrategyEngine(
        config=mock_config,
        exchange=mock_exchange,
        risk_manager=risk_manager,
        database_manager=mock_database_manager,
    )

    # Create snapshot
    snapshot = PositionSnapshot(
        reserve_token0=Decimal("10000"),
        reserve_token1=Decimal("6"),
        short_position_size=Decimal("5"),
        timestamp=datetime.utcnow(),
    )

    # Execute hedge (positive delta = open short)
    result = await engine.execute_hedge(snapshot, Decimal("1"))

    # Verify result
    assert result is not None
    assert result.action == HedgeAction.OPEN_SHORT
    assert result.size == Decimal("1")
    assert result.price == Decimal("2000")
    assert result.success is True
    assert result.delta_before == Decimal("1")
    assert result.delta_after == Decimal("0")

    # Verify leverage was set
    mock_exchange.open_short_position.assert_called_once_with(
        symbol=mock_config.symbol_perpetual, size=Decimal("1"), leverage=Decimal("2")
    )


@pytest.mark.asyncio
async def test_execute_hedge_close_short(
    mock_config, mock_exchange, mock_database_manager
):
    """Test executing a hedge to close short position."""
    # Create risk manager mock
    risk_manager = Mock()
    risk_manager.check_slippage = Mock(return_value=True)
    risk_manager.calculate_leverage = Mock(return_value=Decimal("1"))
    risk_manager.record_trade = Mock()

    # Create mock trade
    mock_trade = Trade(
        symbol="ETH/USDT:USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        size=Decimal("0.5"),
        price=Decimal("2000"),
        timestamp=datetime.utcnow(),
        order_id="12346",
        status=OrderStatus.FILLED,
    )

    mock_exchange.close_short_position = AsyncMock(return_value=mock_trade)

    # Create strategy engine
    engine = StrategyEngine(
        config=mock_config,
        exchange=mock_exchange,
        risk_manager=risk_manager,
        database_manager=mock_database_manager,
    )

    # Create snapshot
    snapshot = PositionSnapshot(
        reserve_token0=Decimal("10000"),
        reserve_token1=Decimal("4.5"),
        short_position_size=Decimal("5"),
        timestamp=datetime.utcnow(),
    )

    # Execute hedge (negative delta = close short)
    result = await engine.execute_hedge(snapshot, Decimal("-0.5"))

    # Verify result
    assert result is not None
    assert result.action == HedgeAction.CLOSE_SHORT
    assert result.size == Decimal("0.5")
    assert result.price == Decimal("2000")
    assert result.success is True
    assert result.delta_before == Decimal("-0.5")
    assert result.delta_after == Decimal("0")

    # Verify close was called
    mock_exchange.close_short_position.assert_called_once_with(
        symbol=mock_config.symbol_perpetual, size=Decimal("0.5")
    )


@pytest.mark.asyncio
async def test_execute_hedge_failure(mock_config, mock_exchange, mock_database_manager):
    """Test handling of hedge execution failure."""
    # Create risk manager mock
    risk_manager = Mock()
    risk_manager.check_slippage = Mock(return_value=True)
    risk_manager.calculate_leverage = Mock(return_value=Decimal("1"))
    risk_manager.record_trade = Mock()

    # Make exchange raise an error
    mock_exchange.open_short_position = AsyncMock(side_effect=Exception("API Error"))

    # Create strategy engine
    engine = StrategyEngine(
        config=mock_config,
        exchange=mock_exchange,
        risk_manager=risk_manager,
        database_manager=mock_database_manager,
    )

    # Create snapshot
    snapshot = PositionSnapshot(
        reserve_token0=Decimal("10000"),
        reserve_token1=Decimal("6"),
        short_position_size=Decimal("5"),
        timestamp=datetime.utcnow(),
    )

    # Execute hedge
    result = await engine.execute_hedge(snapshot, Decimal("1"))

    # Verify failure handling
    assert result is not None
    assert result.success is False
    assert result.error_message == "API Error"
    assert result.delta_after == result.delta_before  # Delta unchanged

    # Verify database still saved the failed hedge
    mock_database_manager.save_hedge_snapshot.assert_called_once()


@pytest.mark.asyncio
async def test_emergency_close_all(mock_config, mock_exchange, mock_database_manager):
    """Test emergency close all positions."""
    # Setup mock exchange with existing position
    mock_exchange.get_current_perpetual_position = AsyncMock(
        return_value={
            "symbol": "ETH/USDT:USDT",
            "size": Decimal("10"),
            "side": "short",
            "entry_price": Decimal("2000"),
        }
    )

    mock_trade = Trade(
        symbol="ETH/USDT:USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        size=Decimal("10"),
        price=Decimal("2000"),
        timestamp=datetime.utcnow(),
        order_id="emergency",
        status=OrderStatus.FILLED,
    )

    mock_exchange.close_short_position = AsyncMock(return_value=mock_trade)

    # Create strategy engine
    risk_manager = Mock()
    engine = StrategyEngine(
        config=mock_config,
        exchange=mock_exchange,
        risk_manager=risk_manager,
        database_manager=mock_database_manager,
    )

    # Execute emergency close
    result = await engine.emergency_close_all()

    # Verify position was closed
    assert result is True
    mock_exchange.close_short_position.assert_called_once_with(
        symbol=mock_config.symbol_perpetual, size=Decimal("10")
    )


def test_get_strategy_stats(mock_config, mock_exchange, mock_database_manager):
    """Test getting strategy statistics."""
    risk_manager = Mock()
    engine = StrategyEngine(
        config=mock_config,
        exchange=mock_exchange,
        risk_manager=risk_manager,
        database_manager=mock_database_manager,
    )

    # Set some stats
    engine.total_hedges = 10
    engine.successful_hedges = 8
    engine.failed_hedges = 2

    # Get stats
    stats = engine.get_strategy_stats()

    # Verify stats
    assert stats["total_hedges"] == 10
    assert stats["successful_hedges"] == 8
    assert stats["failed_hedges"] == 2
    assert stats["success_rate"] == "80.0%"
    assert "last_hedge_time" in stats
    assert stats["hedge_threshold"] == str(mock_config.hedge_threshold_eth)
