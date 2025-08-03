"""Risk manager for validating and managing trading risks."""

from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from models import PositionSnapshot
from logger_manager import LoggerManager, LogTag
from config_manager import Config


class RiskManager:
    """
    Manages risk parameters and validates trading decisions.

    Provides risk checks, leverage calculations, and safety validations
    for all hedging operations.
    """

    def __init__(self, config: Config):
        """
        Initialize risk manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = LoggerManager()

        # Risk parameters
        self.max_position_size = Decimal("100")  # Maximum position size in ETH
        self.max_delta_exposure = Decimal("0.5")  # Maximum allowed delta
        self.min_balance_usdt = Decimal("100")  # Minimum balance to maintain

        # Tracking
        self.recent_trades: list = []
        self.max_trades_per_hour = 20
        self.last_risk_check = datetime.utcnow()

    def calculate_leverage(
        self, position_size: Decimal, account_balance: Decimal, current_price: Decimal
    ) -> Decimal:
        """
        Calculate appropriate leverage for a position.

        Args:
            position_size: Size of position in ETH
            account_balance: Account balance in USDT
            current_price: Current ETH price

        Returns:
            Leverage to use
        """
        # Calculate notional value
        notional_value = position_size * current_price

        # Calculate leverage based on account balance
        if account_balance > 0:
            required_leverage = notional_value / account_balance

            # Cap at configured maximum
            max_leverage = self.config.default_leverage
            leverage = min(required_leverage, max_leverage)

            # Ensure minimum leverage of 1
            leverage = max(leverage, Decimal("1"))
        else:
            leverage = Decimal("1")

        self.logger.log_leverage(str(leverage))
        return leverage

    def validate_hedge_size(self, hedge_size: Decimal) -> bool:
        """
        Validate if hedge size is within acceptable limits.

        Args:
            hedge_size: Proposed hedge size

        Returns:
            True if hedge size is valid
        """
        # Check minimum size
        if abs(hedge_size) < self.config.min_hedge_size_eth:
            self.logger.log_debug(
                f"Hedge size {hedge_size} below minimum {self.config.min_hedge_size_eth}",
                LogTag.RISK,
            )
            return False

        # Check maximum size
        if abs(hedge_size) > self.max_position_size:
            self.logger.log_warning(
                f"Hedge size {hedge_size} exceeds maximum {self.max_position_size}"
            )
            return False

        return True

    def check_slippage(self, expected_price: Decimal, market_price: Decimal) -> bool:
        """
        Check if slippage is within acceptable limits.

        Args:
            expected_price: Expected execution price
            market_price: Current market price

        Returns:
            True if slippage is acceptable
        """
        if expected_price == 0:
            return False

        slippage = abs((market_price - expected_price) / expected_price) * 100

        if slippage > self.config.max_slippage_percent:
            self.logger.log_warning(
                f"Slippage {slippage:.2f}% exceeds maximum {self.config.max_slippage_percent}%"
            )
            return False

        return True

    def check_rate_limits(self) -> bool:
        """
        Check if rate limits allow for another trade.

        Returns:
            True if within rate limits
        """
        # Clean up old trades
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        self.recent_trades = [
            trade for trade in self.recent_trades if trade["timestamp"] > cutoff_time
        ]

        # Check trade count
        if len(self.recent_trades) >= self.max_trades_per_hour:
            self.logger.log_warning(
                f"Rate limit reached: {len(self.recent_trades)} trades in past hour"
            )
            return False

        return True

    def validate_market_conditions(
        self,
        volatility: Optional[Decimal] = None,
        funding_rate: Optional[Decimal] = None,
    ) -> bool:
        """
        Validate if market conditions are suitable for trading.

        Args:
            volatility: Current market volatility
            funding_rate: Current funding rate

        Returns:
            True if conditions are suitable
        """
        # Check volatility if provided
        if volatility and volatility > Decimal("100"):
            self.logger.log_warning(f"High volatility detected: {volatility}%")
            return False

        # Check funding rate if provided
        if funding_rate and abs(funding_rate) > Decimal("0.01"):
            self.logger.log_warning(
                f"High funding rate detected: {funding_rate * 100:.3f}%"
            )
            # Still allow trading but log warning

        return True

    def calculate_position_risk(
        self, snapshot: PositionSnapshot, current_price: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive position risk metrics.

        Args:
            snapshot: Current position snapshot
            current_price: Current ETH price

        Returns:
            Dictionary with risk metrics
        """
        # Calculate exposures
        long_exposure = snapshot.reserve_token1 * current_price
        short_exposure = snapshot.short_position_size * current_price
        net_exposure = long_exposure - short_exposure

        # Calculate risk metrics
        risk_metrics = {
            "long_exposure_usdt": long_exposure,
            "short_exposure_usdt": short_exposure,
            "net_exposure_usdt": net_exposure,
            "delta_eth": snapshot.delta,
            "delta_usdt": snapshot.delta * current_price,
            "is_delta_neutral": snapshot.is_delta_neutral(
                self.config.hedge_threshold_eth
            ),
            "hedge_required": abs(snapshot.delta) > self.config.hedge_threshold_eth,
            "timestamp": datetime.utcnow(),
        }

        # Add risk score (0-100, lower is better)
        delta_ratio = abs(snapshot.delta) / max(
            snapshot.reserve_token1, Decimal("0.01")
        )
        risk_score = min(delta_ratio * 100, Decimal("100"))
        risk_metrics["risk_score"] = risk_score

        return risk_metrics

    def should_hedge(
        self, snapshot: PositionSnapshot, force: bool = False
    ) -> tuple[bool, Decimal]:
        """
        Determine if hedging is needed and calculate size.

        Args:
            snapshot: Current position snapshot
            force: Force hedge regardless of threshold

        Returns:
            Tuple of (should_hedge, hedge_size)
        """
        delta = snapshot.delta

        # Check if delta exceeds threshold
        if not force and abs(delta) <= self.config.hedge_threshold_eth:
            return False, Decimal("0")

        # Check if hedge size meets minimum
        if abs(delta) < self.config.min_hedge_size_eth:
            return False, Decimal("0")

        # Validate hedge size
        if not self.validate_hedge_size(delta):
            return False, Decimal("0")

        # Check rate limits
        if not self.check_rate_limits():
            return False, Decimal("0")

        self.logger.log_info(f"Hedge required: Delta = {delta} ETH", LogTag.RISK)

        return True, delta

    def record_trade(self, trade_data: dict) -> None:
        """
        Record a trade for rate limiting.

        Args:
            trade_data: Trade information
        """
        trade_data["timestamp"] = datetime.utcnow()
        self.recent_trades.append(trade_data)

    def get_risk_summary(self) -> Dict[str, Any]:
        """
        Get current risk parameter summary.

        Returns:
            Dictionary with risk parameters
        """
        return {
            "max_position_size": str(self.max_position_size),
            "max_delta_exposure": str(self.max_delta_exposure),
            "min_balance_usdt": str(self.min_balance_usdt),
            "max_trades_per_hour": self.max_trades_per_hour,
            "recent_trade_count": len(self.recent_trades),
            "min_hedge_size": str(self.config.min_hedge_size_eth),
            "hedge_threshold": str(self.config.hedge_threshold_eth),
            "max_slippage": str(self.config.max_slippage_percent),
            "default_leverage": str(self.config.default_leverage),
        }

    def emergency_stop_check(
        self, losses: Decimal, max_loss: Decimal = Decimal("1000")
    ) -> bool:
        """
        Check if emergency stop conditions are met.

        Args:
            losses: Current losses
            max_loss: Maximum allowed loss

        Returns:
            True if emergency stop should be triggered
        """
        if losses > max_loss:
            self.logger.log_error(
                f"EMERGENCY STOP: Losses ({losses}) exceed maximum ({max_loss})"
            )
            return True

        return False
