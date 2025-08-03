"""Hedge snapshot model for tracking executed hedging operations."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class HedgeAction(Enum):
    """Types of hedging actions."""

    OPEN_SHORT = "open_short"
    CLOSE_SHORT = "close_short"
    ADJUST_SHORT = "adjust_short"


@dataclass
class HedgeSnapshot:
    """
    Represents a hedge operation executed by the bot.

    Attributes:
        action: Type of hedge action taken
        size: Size of the hedge in WETH
        price: Execution price in USDT
        timestamp: When the hedge was executed
        delta_before: Delta exposure before hedging
        delta_after: Delta exposure after hedging
        leverage: Leverage used for the trade
        exchange: Exchange where trade was executed
        order_id: Exchange order ID
        gas_cost: Optional gas cost for on-chain operations
        success: Whether the hedge was successful
        error_message: Error message if hedge failed
    """

    action: HedgeAction
    size: Decimal
    price: Decimal
    timestamp: datetime
    delta_before: Decimal
    delta_after: Decimal
    leverage: Decimal = Decimal("1")
    exchange: str = "binance"
    order_id: Optional[str] = None
    gas_cost: Optional[Decimal] = None
    success: bool = True
    error_message: Optional[str] = None

    @property
    def delta_reduction(self) -> Decimal:
        """Calculate how much delta was reduced by this hedge."""
        return abs(self.delta_before) - abs(self.delta_after)

    @property
    def notional_value(self) -> Decimal:
        """Calculate the notional value of the hedge in USDT."""
        return self.size * self.price

    def to_dict(self) -> dict:
        """Convert hedge snapshot to dictionary."""
        return {
            "action": self.action.value,
            "size": str(self.size),
            "price": str(self.price),
            "timestamp": self.timestamp.isoformat(),
            "delta_before": str(self.delta_before),
            "delta_after": str(self.delta_after),
            "leverage": str(self.leverage),
            "exchange": self.exchange,
            "order_id": self.order_id,
            "gas_cost": str(self.gas_cost) if self.gas_cost else None,
            "success": self.success,
            "error_message": self.error_message,
            "delta_reduction": str(self.delta_reduction),
            "notional_value": str(self.notional_value),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HedgeSnapshot":
        """Create HedgeSnapshot from dictionary."""
        return cls(
            action=HedgeAction(data["action"]),
            size=Decimal(data["size"]),
            price=Decimal(data["price"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            delta_before=Decimal(data["delta_before"]),
            delta_after=Decimal(data["delta_after"]),
            leverage=Decimal(data.get("leverage", "1")),
            exchange=data.get("exchange", "binance"),
            order_id=data.get("order_id"),
            gas_cost=Decimal(data["gas_cost"]) if data.get("gas_cost") else None,
            success=data.get("success", True),
            error_message=data.get("error_message"),
        )
