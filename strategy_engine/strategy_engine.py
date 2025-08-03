"""Strategy engine for delta-neutral hedging decisions."""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Optional

from models import PositionSnapshot, HedgeSnapshot
from models.hedge_snapshot import HedgeAction
from exchange_manager import IExchange
from risk_manager import RiskManager
from database_manager import DatabaseManager
from logger_manager import LoggerManager, LogTag
from config_manager import Config


class StrategyEngine:
    """
    Core strategy engine for delta-neutral hedging.

    Analyzes position snapshots and executes hedging decisions
    to maintain delta neutrality.
    """

    def __init__(
        self,
        config: Config,
        exchange: IExchange,
        risk_manager: RiskManager,
        database_manager: Optional[DatabaseManager] = None,
    ):
        """
        Initialize strategy engine.

        Args:
            config: Configuration object
            exchange: Exchange interface for trading
            risk_manager: Risk manager for validations
            database_manager: Optional database for persistence
        """
        self.config = config
        self.exchange = exchange
        self.risk_manager = risk_manager
        self.database_manager = database_manager
        self.logger = LoggerManager()

        # Strategy state
        self.last_hedge_time = datetime.utcnow()
        self.min_hedge_interval = 30  # Minimum seconds between hedges
        self.total_hedges = 0
        self.successful_hedges = 0
        self.failed_hedges = 0

    async def process_position_snapshot(
        self, snapshot: PositionSnapshot
    ) -> Optional[HedgeSnapshot]:
        """
        Process a position snapshot and execute hedging if needed.

        Args:
            snapshot: Current position snapshot

        Returns:
            HedgeSnapshot if hedge was executed, None otherwise
        """
        try:
            # Log snapshot processing
            self.logger.log_info(
                f"Processing snapshot - Delta: {snapshot.delta:.4f} ETH",
                LogTag.STRATEGY,
            )

            # Check if hedging is needed
            should_hedge, hedge_size = self.risk_manager.should_hedge(snapshot)

            if not should_hedge:
                self.logger.log_debug(
                    "No hedge required - within threshold", LogTag.STRATEGY
                )
                return None

            # Check minimum time between hedges
            time_since_last = (datetime.utcnow() - self.last_hedge_time).total_seconds()
            if time_since_last < self.min_hedge_interval:
                self.logger.log_debug(
                    f"Skipping hedge - too soon ({time_since_last:.1f}s < {self.min_hedge_interval}s)",
                    LogTag.STRATEGY,
                )
                return None

            # Execute hedge
            hedge_snapshot = await self.execute_hedge(snapshot, hedge_size)

            if hedge_snapshot and hedge_snapshot.success:
                self.last_hedge_time = datetime.utcnow()
                self.successful_hedges += 1
            else:
                self.failed_hedges += 1

            self.total_hedges += 1

            return hedge_snapshot

        except Exception as e:
            self.logger.log_error("Error processing position snapshot", e)
            return None

    async def execute_hedge(
        self, snapshot: PositionSnapshot, hedge_size: Decimal
    ) -> Optional[HedgeSnapshot]:
        """
        Execute a hedge trade.

        Args:
            snapshot: Current position snapshot
            hedge_size: Size of hedge to execute (positive = open short, negative = close short)

        Returns:
            HedgeSnapshot with execution details
        """
        try:
            # Log calculated hedge
            action = "Open Short" if hedge_size > 0 else "Close Short"
            self.logger.log_calculated_hedge(str(hedge_size), action)

            # Get current market price
            mark_price = await self.exchange.get_mark_price(
                self.config.symbol_perpetual
            )

            # Check slippage
            if not self.risk_manager.check_slippage(mark_price, mark_price):
                self.logger.log_warning("Slippage check failed")
                return None

            # Get account balance for leverage calculation
            balance = await self.exchange.get_balance("USDT")

            # Calculate leverage
            leverage = self.risk_manager.calculate_leverage(
                abs(hedge_size), balance, mark_price
            )

            # Execute trade based on delta
            if hedge_size > 0:
                # Need to open/increase short position
                trade = await self.exchange.open_short_position(
                    symbol=self.config.symbol_perpetual,
                    size=abs(hedge_size),
                    leverage=leverage,
                )
                hedge_action = HedgeAction.OPEN_SHORT
            else:
                # Need to close/reduce short position
                trade = await self.exchange.close_short_position(
                    symbol=self.config.symbol_perpetual, size=abs(hedge_size)
                )
                hedge_action = HedgeAction.CLOSE_SHORT

            # Calculate new delta after hedge
            new_short_size = snapshot.short_position_size
            if hedge_size > 0:
                new_short_size += abs(hedge_size)
            else:
                new_short_size -= abs(hedge_size)

            delta_after = snapshot.reserve_token1 - new_short_size

            # Create hedge snapshot
            hedge_snapshot = HedgeSnapshot(
                action=hedge_action,
                size=abs(hedge_size),
                price=trade.price,
                timestamp=trade.timestamp,
                delta_before=snapshot.delta,
                delta_after=delta_after,
                leverage=leverage,
                exchange="binance",
                order_id=trade.order_id,
                success=True,
            )

            # Save to database
            if self.database_manager:
                self.database_manager.save_hedge_snapshot(hedge_snapshot)
                self.database_manager.save_trade(trade)

            # Record trade for rate limiting
            self.risk_manager.record_trade(
                {
                    "size": abs(hedge_size),
                    "price": trade.price,
                    "action": hedge_action.value,
                }
            )

            # Log success
            self.logger.log_trade(
                hedge_action.value, str(abs(hedge_size)), str(trade.price)
            )

            return hedge_snapshot

        except Exception as e:
            self.logger.log_error(f"Failed to execute hedge", e)

            # Create failed hedge snapshot
            hedge_snapshot = HedgeSnapshot(
                action=(
                    HedgeAction.OPEN_SHORT
                    if hedge_size > 0
                    else HedgeAction.CLOSE_SHORT
                ),
                size=abs(hedge_size),
                price=Decimal("0"),
                timestamp=datetime.utcnow(),
                delta_before=snapshot.delta,
                delta_after=snapshot.delta,
                success=False,
                error_message=str(e),
            )

            if self.database_manager:
                self.database_manager.save_hedge_snapshot(hedge_snapshot)

            return hedge_snapshot

    async def rebalance_position(self, target_delta: Decimal = Decimal("0")) -> bool:
        """
        Rebalance position to target delta.

        Args:
            target_delta: Target delta exposure (default 0 for neutral)

        Returns:
            True if rebalancing was successful
        """
        try:
            # Get current position
            position = await self.exchange.get_current_perpetual_position(
                self.config.symbol_perpetual
            )

            current_short = (
                position["size"] if position["side"] == "short" else Decimal("0")
            )

            # Calculate required adjustment
            # This would need pool reserves to calculate properly
            # For now, return false as we need a snapshot

            self.logger.log_warning("Rebalancing requires position snapshot")

            return False

        except Exception as e:
            self.logger.log_error("Failed to rebalance position", e)
            return False

    def get_strategy_stats(self) -> dict:
        """
        Get strategy performance statistics.

        Returns:
            Dictionary with strategy statistics
        """
        success_rate = 0
        if self.total_hedges > 0:
            success_rate = (self.successful_hedges / self.total_hedges) * 100

        return {
            "total_hedges": self.total_hedges,
            "successful_hedges": self.successful_hedges,
            "failed_hedges": self.failed_hedges,
            "success_rate": f"{success_rate:.1f}%",
            "last_hedge_time": self.last_hedge_time.isoformat(),
            "min_hedge_interval": self.min_hedge_interval,
            "hedge_threshold": str(self.config.hedge_threshold_eth),
            "min_hedge_size": str(self.config.min_hedge_size_eth),
        }

    async def emergency_close_all(self) -> bool:
        """
        Emergency close all positions.

        Returns:
            True if positions were closed successfully
        """
        try:
            self.logger.log_warning("EMERGENCY: Closing all positions")

            # Get current position
            position = await self.exchange.get_current_perpetual_position(
                self.config.symbol_perpetual
            )

            if position["side"] == "short" and position["size"] > 0:
                # Close short position
                trade = await self.exchange.close_short_position(
                    symbol=self.config.symbol_perpetual, size=position["size"]
                )

                self.logger.log_info(
                    f"Emergency closed {position['size']} ETH short at {trade.price}",
                    LogTag.STRATEGY,
                )

                return True

            return True

        except Exception as e:
            self.logger.log_error("Failed to emergency close positions", e)
            return False

    def update_parameters(self, **kwargs) -> None:
        """
        Update strategy parameters.

        Args:
            **kwargs: Parameters to update
        """
        if "min_hedge_interval" in kwargs:
            self.min_hedge_interval = int(kwargs["min_hedge_interval"])
            self.logger.log_info(
                f"Updated min_hedge_interval to {self.min_hedge_interval}s",
                LogTag.STRATEGY,
            )

        # Other parameters are in config, update there
        if any(key in kwargs for key in ["hedge_threshold_eth", "min_hedge_size_eth"]):
            self.config.update_config(**kwargs)
