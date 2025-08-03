"""Abstract base class for exchange implementations."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime

from models import Trade


class IExchange(ABC):
    """
    Abstract interface for exchange implementations.

    Defines the contract that all exchange implementations must follow.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the exchange."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the exchange."""
        pass

    @abstractmethod
    async def get_mark_price(self, symbol: str) -> Decimal:
        """
        Get the current mark price for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., "ETH/USDT:USDT")

        Returns:
            Current mark price
        """
        pass

    @abstractmethod
    async def get_funding_rate(self, symbol: str) -> Decimal:
        """
        Get the current funding rate for a perpetual contract.

        Args:
            symbol: Trading pair symbol

        Returns:
            Current funding rate
        """
        pass

    @abstractmethod
    async def open_short_position(
        self, symbol: str, size: Decimal, leverage: Decimal = Decimal("1")
    ) -> Trade:
        """
        Open a short position.

        Args:
            symbol: Trading pair symbol
            size: Position size in base currency
            leverage: Leverage to use

        Returns:
            Executed trade details
        """
        pass

    @abstractmethod
    async def close_short_position(self, symbol: str, size: Decimal) -> Trade:
        """
        Close a short position.

        Args:
            symbol: Trading pair symbol
            size: Position size to close

        Returns:
            Executed trade details
        """
        pass

    @abstractmethod
    async def get_current_perpetual_position(self, symbol: str) -> Dict[str, Any]:
        """
        Get current perpetual position details.

        Args:
            symbol: Trading pair symbol

        Returns:
            Position details including size, entry price, PnL, etc.
        """
        pass

    @abstractmethod
    async def set_leverage(self, symbol: str, leverage: Decimal) -> bool:
        """
        Set leverage for a symbol.

        Args:
            symbol: Trading pair symbol
            leverage: Leverage value

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def get_balance(self, currency: str = "USDT") -> Decimal:
        """
        Get account balance for a currency.

        Args:
            currency: Currency to check balance for

        Returns:
            Available balance
        """
        pass

    @abstractmethod
    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get order book for a symbol.

        Args:
            symbol: Trading pair symbol
            limit: Number of price levels to return

        Returns:
            Order book with bids and asks
        """
        pass

    @abstractmethod
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> list:
        """
        Get recent trades for a symbol.

        Args:
            symbol: Trading pair symbol
            limit: Number of trades to return

        Returns:
            List of recent trades
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an open order.

        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol

        Returns:
            True if cancellation was successful
        """
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get status of an order.

        Args:
            order_id: Order ID to check
            symbol: Trading pair symbol

        Returns:
            Order status details
        """
        pass
