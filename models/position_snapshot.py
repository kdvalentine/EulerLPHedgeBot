"""Position snapshot model representing the current state of reserves and positions."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class PositionSnapshot:
    """
    Represents a snapshot of pool reserves and short positions at a specific time.

    Attributes:
        reserve_token0: USDT reserve amount in the pool
        reserve_token1: WETH reserve amount in the pool
        short_position_size: Current short position size on CEX
        timestamp: Time when the snapshot was taken
        block_number: Optional Ethereum block number for the snapshot
        pool_address: Address of the EulerSwap pool
    """

    reserve_token0: Decimal  # USDT
    reserve_token1: Decimal  # WETH
    short_position_size: Decimal
    timestamp: datetime
    block_number: Optional[int] = None
    pool_address: Optional[str] = None

    @property
    def delta(self) -> Decimal:
        """Calculate the delta exposure (WETH reserves - short position)."""
        return self.reserve_token1 - self.short_position_size

    @property
    def is_delta_neutral(self, threshold: Decimal = Decimal("0.005")) -> bool:
        """Check if position is within delta-neutral threshold."""
        return abs(self.delta) <= threshold

    def to_dict(self) -> dict:
        """Convert snapshot to dictionary for serialization."""
        return {
            "reserve_token0": str(self.reserve_token0),
            "reserve_token1": str(self.reserve_token1),
            "short_position_size": str(self.short_position_size),
            "timestamp": self.timestamp.isoformat(),
            "block_number": self.block_number,
            "pool_address": self.pool_address,
            "delta": str(self.delta),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PositionSnapshot":
        """Create PositionSnapshot from dictionary."""
        return cls(
            reserve_token0=Decimal(data["reserve_token0"]),
            reserve_token1=Decimal(data["reserve_token1"]),
            short_position_size=Decimal(data["short_position_size"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            block_number=data.get("block_number"),
            pool_address=data.get("pool_address"),
        )
