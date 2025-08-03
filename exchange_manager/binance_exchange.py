"""Binance exchange implementation."""

import asyncio
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any
import ccxt.async_support as ccxt

from models import Trade
from models.trade import OrderSide, OrderType, OrderStatus
from logger_manager import LoggerManager, LogTag
from .iexchange import IExchange


class BinanceExchange(IExchange):
    """
    Binance exchange implementation using CCXT.

    Handles all interactions with Binance perpetual futures.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Binance exchange.

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Whether to use testnet
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.logger = LoggerManager()
        self.exchange: Optional[ccxt.binance] = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to Binance exchange."""
        try:
            config = {
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "enableRateLimit": True,
                "options": {
                    "defaultType": "future",  # Use futures market
                    "adjustForTimeDifference": True,
                },
            }

            if self.testnet:
                config["options"]["testnet"] = True
                config["hostname"] = "testnet.binancefuture.com"

            self.exchange = ccxt.binance(config)

            # Load markets
            await self.exchange.load_markets()

            # Test connection
            balance = await self.exchange.fetch_balance()

            self._connected = True
            self.logger.log_info("Connected to Binance exchange", LogTag.EXCHANGE)

        except Exception as e:
            self.logger.log_error(f"Failed to connect to Binance", e)
            raise

    async def disconnect(self) -> None:
        """Disconnect from Binance exchange."""
        if self.exchange:
            await self.exchange.close()
            self._connected = False
            self.logger.log_info("Disconnected from Binance exchange", LogTag.EXCHANGE)

    async def get_mark_price(self, symbol: str) -> Decimal:
        """
        Get the current mark price for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., "ETH/USDT:USDT")

        Returns:
            Current mark price
        """
        self._ensure_connected()

        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            mark_price = Decimal(str(ticker["mark"] or ticker["last"]))

            self.logger.log_debug(
                f"Mark price for {symbol}: {mark_price}", LogTag.EXCHANGE
            )
            return mark_price

        except Exception as e:
            self.logger.log_error(f"Failed to get mark price for {symbol}", e)
            raise

    async def get_funding_rate(self, symbol: str) -> Decimal:
        """
        Get the current funding rate for a perpetual contract.

        Args:
            symbol: Trading pair symbol

        Returns:
            Current funding rate
        """
        self._ensure_connected()

        try:
            funding = await self.exchange.fetch_funding_rate(symbol)
            funding_rate = Decimal(str(funding["rate"]))

            self.logger.log_debug(
                f"Funding rate for {symbol}: {funding_rate}", LogTag.EXCHANGE
            )
            return funding_rate

        except Exception as e:
            self.logger.log_error(f"Failed to get funding rate for {symbol}", e)
            raise

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
        self._ensure_connected()

        try:
            # Set leverage first
            await self.set_leverage(symbol, leverage)

            # Place market sell order to open short
            order = await self.exchange.create_market_sell_order(
                symbol=symbol, amount=float(size)
            )

            # Create trade object
            trade = Trade(
                symbol=symbol,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                size=Decimal(str(order["amount"])),
                price=Decimal(str(order["price"] or order["average"])),
                timestamp=datetime.fromtimestamp(order["timestamp"] / 1000),
                order_id=str(order["id"]),
                status=(
                    OrderStatus.FILLED
                    if order["status"] == "closed"
                    else OrderStatus.OPEN
                ),
                fee=Decimal(str(order["fee"]["cost"])) if order.get("fee") else None,
                fee_currency=order["fee"]["currency"] if order.get("fee") else None,
                exchange="binance",
            )

            self.logger.log_trade("Open Short", str(size), str(trade.price))
            return trade

        except Exception as e:
            self.logger.log_error(f"Failed to open short position", e)
            raise

    async def close_short_position(self, symbol: str, size: Decimal) -> Trade:
        """
        Close a short position.

        Args:
            symbol: Trading pair symbol
            size: Position size to close

        Returns:
            Executed trade details
        """
        self._ensure_connected()

        try:
            # Place market buy order to close short
            order = await self.exchange.create_market_buy_order(
                symbol=symbol, amount=float(size)
            )

            # Create trade object
            trade = Trade(
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                size=Decimal(str(order["amount"])),
                price=Decimal(str(order["price"] or order["average"])),
                timestamp=datetime.fromtimestamp(order["timestamp"] / 1000),
                order_id=str(order["id"]),
                status=(
                    OrderStatus.FILLED
                    if order["status"] == "closed"
                    else OrderStatus.OPEN
                ),
                fee=Decimal(str(order["fee"]["cost"])) if order.get("fee") else None,
                fee_currency=order["fee"]["currency"] if order.get("fee") else None,
                exchange="binance",
            )

            self.logger.log_trade("Close Short", str(size), str(trade.price))
            return trade

        except Exception as e:
            self.logger.log_error(f"Failed to close short position", e)
            raise

    async def get_current_perpetual_position(self, symbol: str) -> Dict[str, Any]:
        """
        Get current perpetual position details.

        Args:
            symbol: Trading pair symbol

        Returns:
            Position details including size, entry price, PnL, etc.
        """
        self._ensure_connected()

        try:
            positions = await self.exchange.fetch_positions([symbol])

            if not positions:
                return {
                    "symbol": symbol,
                    "size": Decimal("0"),
                    "side": None,
                    "entry_price": None,
                    "mark_price": None,
                    "unrealized_pnl": Decimal("0"),
                    "realized_pnl": Decimal("0"),
                    "margin": Decimal("0"),
                    "leverage": Decimal("1"),
                }

            position = positions[0]

            return {
                "symbol": position["symbol"],
                "size": abs(Decimal(str(position["contracts"] or 0))),
                "side": (
                    "short"
                    if position["side"] == "short"
                    else "long" if position["side"] == "long" else None
                ),
                "entry_price": (
                    Decimal(str(position["entryPrice"]))
                    if position["entryPrice"]
                    else None
                ),
                "mark_price": (
                    Decimal(str(position["markPrice"]))
                    if position["markPrice"]
                    else None
                ),
                "unrealized_pnl": Decimal(str(position["unrealizedPnl"] or 0)),
                "realized_pnl": Decimal(str(position["realizedPnl"] or 0)),
                "margin": Decimal(str(position["initialMargin"] or 0)),
                "leverage": Decimal(str(position["leverage"] or 1)),
            }

        except Exception as e:
            self.logger.log_error(f"Failed to get perpetual position for {symbol}", e)
            raise

    async def set_leverage(self, symbol: str, leverage: Decimal) -> bool:
        """
        Set leverage for a symbol.

        Args:
            symbol: Trading pair symbol
            leverage: Leverage value

        Returns:
            True if successful
        """
        self._ensure_connected()

        try:
            # Binance requires symbol without colon for leverage setting
            clean_symbol = symbol.replace(":", "")

            result = await self.exchange.set_leverage(
                leverage=int(leverage), symbol=clean_symbol
            )

            self.logger.log_leverage(str(leverage))
            return True

        except Exception as e:
            self.logger.log_error(f"Failed to set leverage for {symbol}", e)
            return False

    async def get_balance(self, currency: str = "USDT") -> Decimal:
        """
        Get account balance for a currency.

        Args:
            currency: Currency to check balance for

        Returns:
            Available balance
        """
        self._ensure_connected()

        try:
            balance = await self.exchange.fetch_balance()

            if currency in balance:
                available = Decimal(str(balance[currency]["free"] or 0))
                return available

            return Decimal("0")

        except Exception as e:
            self.logger.log_error(f"Failed to get balance for {currency}", e)
            raise

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get order book for a symbol.

        Args:
            symbol: Trading pair symbol
            limit: Number of price levels to return

        Returns:
            Order book with bids and asks
        """
        self._ensure_connected()

        try:
            order_book = await self.exchange.fetch_order_book(symbol, limit)

            return {
                "symbol": symbol,
                "bids": [
                    (Decimal(str(price)), Decimal(str(amount)))
                    for price, amount in order_book["bids"]
                ],
                "asks": [
                    (Decimal(str(price)), Decimal(str(amount)))
                    for price, amount in order_book["asks"]
                ],
                "timestamp": order_book["timestamp"],
                "datetime": order_book["datetime"],
            }

        except Exception as e:
            self.logger.log_error(f"Failed to get order book for {symbol}", e)
            raise

    async def get_recent_trades(self, symbol: str, limit: int = 100) -> list:
        """
        Get recent trades for a symbol.

        Args:
            symbol: Trading pair symbol
            limit: Number of trades to return

        Returns:
            List of recent trades
        """
        self._ensure_connected()

        try:
            trades = await self.exchange.fetch_trades(symbol, limit=limit)

            return [
                {
                    "id": trade["id"],
                    "timestamp": trade["timestamp"],
                    "datetime": trade["datetime"],
                    "symbol": trade["symbol"],
                    "side": trade["side"],
                    "price": Decimal(str(trade["price"])),
                    "amount": Decimal(str(trade["amount"])),
                    "cost": Decimal(str(trade["cost"])),
                }
                for trade in trades
            ]

        except Exception as e:
            self.logger.log_error(f"Failed to get recent trades for {symbol}", e)
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an open order.

        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol

        Returns:
            True if cancellation was successful
        """
        self._ensure_connected()

        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            return result["status"] == "canceled"

        except Exception as e:
            self.logger.log_error(f"Failed to cancel order {order_id}", e)
            return False

    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get status of an order.

        Args:
            order_id: Order ID to check
            symbol: Trading pair symbol

        Returns:
            Order status details
        """
        self._ensure_connected()

        try:
            order = await self.exchange.fetch_order(order_id, symbol)

            return {
                "id": order["id"],
                "symbol": order["symbol"],
                "type": order["type"],
                "side": order["side"],
                "price": Decimal(str(order["price"])) if order["price"] else None,
                "amount": Decimal(str(order["amount"])),
                "filled": Decimal(str(order["filled"])),
                "remaining": Decimal(str(order["remaining"])),
                "status": order["status"],
                "timestamp": order["timestamp"],
                "datetime": order["datetime"],
            }

        except Exception as e:
            self.logger.log_error(f"Failed to get order status for {order_id}", e)
            raise

    def _ensure_connected(self) -> None:
        """Ensure exchange is connected."""
        if not self._connected or not self.exchange:
            raise RuntimeError("Exchange not connected. Call connect() first.")
