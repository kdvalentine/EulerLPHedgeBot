"""Trade model for representing individual trades."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class OrderType(Enum):
    """Types of orders."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Side of the order."""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Status of the order."""

    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Trade:
    """
    Represents an individual trade executed on an exchange.

    Attributes:
        symbol: Trading pair symbol (e.g., "ETH/USDT")
        side: Buy or sell
        order_type: Type of order
        size: Size of the trade
        price: Execution price
        timestamp: When the trade was executed
        order_id: Exchange order ID
        status: Current status of the order
        fee: Trading fee
        fee_currency: Currency of the fee
        exchange: Exchange where trade was executed
    """

    symbol: str
    side: OrderSide
    order_type: OrderType
    size: Decimal
    price: Decimal
    timestamp: datetime
    order_id: str
    status: OrderStatus = OrderStatus.PENDING
    fee: Optional[Decimal] = None
    fee_currency: Optional[str] = None
    exchange: str = "binance"

    @property
    def notional(self) -> Decimal:
        """Calculate notional value of the trade."""
        return self.size * self.price

    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost including fees."""
        cost = self.notional
        if self.fee:
            cost += self.fee if self.fee_currency == "USDT" else Decimal("0")
        return cost

    def to_dict(self) -> dict:
        """Convert trade to dictionary."""
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "size": str(self.size),
            "price": str(self.price),
            "timestamp": self.timestamp.isoformat(),
            "order_id": self.order_id,
            "status": self.status.value,
            "fee": str(self.fee) if self.fee else None,
            "fee_currency": self.fee_currency,
            "exchange": self.exchange,
            "notional": str(self.notional),
            "total_cost": str(self.total_cost),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Trade":
        """Create Trade from dictionary."""
        return cls(
            symbol=data["symbol"],
            side=OrderSide(data["side"]),
            order_type=OrderType(data["order_type"]),
            size=Decimal(data["size"]),
            price=Decimal(data["price"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            order_id=data["order_id"],
            status=OrderStatus(data.get("status", "pending")),
            fee=Decimal(data["fee"]) if data.get("fee") else None,
            fee_currency=data.get("fee_currency"),
            exchange=data.get("exchange", "binance"),
        )
