#!/usr/bin/env python3
"""
Comprehensive Binance API test script.

Tests both public and private endpoints with the provided API keys.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv
import ccxt.async_support as ccxt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Load environment
load_dotenv()

console = Console()


class BinanceAPITester:
    """Test Binance API access."""

    def __init__(self):
        """Initialize the tester."""
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.exchange = None
        self.results = {}

    async def connect(self):
        """Connect to Binance."""
        console.print("\n[bold yellow]Connecting to Binance...[/bold yellow]")

        try:
            self.exchange = ccxt.binance(
                {
                    "apiKey": self.api_key,
                    "secret": self.api_secret,
                    "enableRateLimit": True,
                    "options": {
                        "defaultType": "future",  # Use futures/perpetuals
                        "adjustForTimeDifference": True,
                    },
                }
            )

            # Load markets
            await self.exchange.load_markets()
            console.print("  ✅ Connected to Binance Futures")

            return True

        except Exception as e:
            console.print(f"  [red]❌ Connection failed: {e}[/red]")
            return False

    async def test_public_endpoints(self):
        """Test public API endpoints."""
        console.print("\n[bold cyan]Testing Public Endpoints[/bold cyan]")
        console.print("-" * 40)

        results = {}

        try:
            # 1. Exchange Status
            console.print("📊 Exchange Status...")
            status = await self.exchange.fetch_status()
            results["status"] = status.get("status", "ok")
            console.print(f"  Status: {results['status']}")

            # 2. Market Data for ETH/USDT Perpetual
            symbol = "ETH/USDT:USDT"
            console.print(f"\n📈 Market Data for {symbol}...")

            # Ticker
            ticker = await self.exchange.fetch_ticker(symbol)
            results["ticker"] = {
                "last": ticker["last"],
                "bid": ticker["bid"],
                "ask": ticker["ask"],
                "volume_24h": ticker["quoteVolume"],
                "high_24h": ticker["high"],
                "low_24h": ticker["low"],
                "change_24h": ticker["percentage"],
            }

            console.print(f"  Last Price: ${ticker['last']:,.2f}")
            console.print(f"  Bid/Ask: ${ticker['bid']:,.2f} / ${ticker['ask']:,.2f}")
            console.print(f"  Spread: ${ticker['ask'] - ticker['bid']:.2f}")
            console.print(f"  24h Volume: ${ticker['quoteVolume']:,.0f}")
            console.print(f"  24h Change: {ticker['percentage']:.2f}%")

            # 3. Funding Rate
            console.print(f"\n💰 Funding Rate...")
            funding = await self.exchange.fetch_funding_rate(symbol)
            results["funding"] = {
                "rate": funding["rate"],
                "timestamp": funding["timestamp"],
            }

            console.print(f"  Current Rate: {funding['rate']*100:.4f}% per 8h")
            console.print(f"  Annualized: {funding['rate']*3*365*100:.2f}%")

            # 4. Order Book
            console.print(f"\n📖 Order Book (Top 5)...")
            orderbook = await self.exchange.fetch_order_book(symbol, 5)

            best_bid = orderbook["bids"][0] if orderbook["bids"] else [0, 0]
            best_ask = orderbook["asks"][0] if orderbook["asks"] else [0, 0]

            results["orderbook"] = {
                "best_bid": best_bid[0],
                "best_bid_size": best_bid[1],
                "best_ask": best_ask[0],
                "best_ask_size": best_ask[1],
                "spread": (
                    best_ask[0] - best_bid[0] if best_ask[0] and best_bid[0] else 0
                ),
            }

            console.print(f"  Best Bid: ${best_bid[0]:,.2f} ({best_bid[1]:.3f} ETH)")
            console.print(f"  Best Ask: ${best_ask[0]:,.2f} ({best_ask[1]:.3f} ETH)")

            # 5. Recent Trades
            console.print(f"\n📝 Recent Trades...")
            trades = await self.exchange.fetch_trades(symbol, limit=5)

            if trades:
                last_trade = trades[-1]
                console.print(
                    f"  Last Trade: ${last_trade['price']:,.2f} ({last_trade['amount']:.4f} ETH)"
                )
                console.print(
                    f"  Time: {datetime.fromtimestamp(last_trade['timestamp']/1000).strftime('%H:%M:%S')}"
                )

            self.results["public"] = results
            return True

        except Exception as e:
            console.print(f"\n[red]❌ Public endpoint test failed: {e}[/red]")
            self.results["public"] = {"error": str(e)}
            return False

    async def test_private_endpoints(self):
        """Test private API endpoints."""
        console.print("\n[bold cyan]Testing Private Endpoints[/bold cyan]")
        console.print("-" * 40)

        results = {}

        try:
            # 1. Account Balance
            console.print("💼 Account Balance...")
            balance = await self.exchange.fetch_balance()

            # Get USDT balance
            usdt_balance = balance.get("USDT", {})
            results["balance"] = {
                "free": usdt_balance.get("free", 0),
                "used": usdt_balance.get("used", 0),
                "total": usdt_balance.get("total", 0),
            }

            console.print(f"  USDT Free: ${usdt_balance.get('free', 0):,.2f}")
            console.print(f"  USDT Used: ${usdt_balance.get('used', 0):,.2f}")
            console.print(f"  USDT Total: ${usdt_balance.get('total', 0):,.2f}")

            # 2. Current Positions
            console.print(f"\n📊 Current Positions...")
            positions = await self.exchange.fetch_positions()

            eth_position = None
            for pos in positions:
                if "ETH" in pos["symbol"]:
                    eth_position = pos
                    break

            if eth_position:
                results["position"] = {
                    "symbol": eth_position["symbol"],
                    "side": eth_position["side"],
                    "contracts": eth_position["contracts"],
                    "notional": eth_position["notional"],
                    "unrealized_pnl": eth_position["unrealizedPnl"],
                    "percentage": eth_position["percentage"],
                }

                console.print(f"  Symbol: {eth_position['symbol']}")
                console.print(f"  Side: {eth_position['side'] or 'No position'}")
                console.print(f"  Size: {eth_position['contracts'] or 0:.4f} ETH")
                console.print(f"  Notional: ${eth_position['notional'] or 0:,.2f}")
                console.print(
                    f"  Unrealized PnL: ${eth_position['unrealizedPnl'] or 0:,.2f}"
                )
            else:
                console.print("  No ETH positions found")
                results["position"] = None

            # 3. Account Information
            console.print(f"\n👤 Account Info...")
            # For Binance futures, we need to check account status
            account_info = await self.exchange.private_get_account()

            results["account"] = {
                "can_trade": account_info.get("canTrade", False),
                "can_withdraw": account_info.get("canWithdraw", False),
                "fee_tier": account_info.get("feeTier", 0),
            }

            console.print(
                f"  Can Trade: {'✅ Yes' if account_info.get('canTrade') else '❌ No'}"
            )
            console.print(
                f"  Can Withdraw: {'✅ Yes' if account_info.get('canWithdraw') else '❌ No'}"
            )
            console.print(f"  Fee Tier: {account_info.get('feeTier', 'N/A')}")

            # 4. Leverage Settings
            console.print(f"\n⚙️ Leverage Settings...")
            # Get leverage bracket for ETH/USDT
            symbol = "ETH/USDT:USDT"

            # Try to get current leverage
            try:
                leverage_info = await self.exchange.private_get_positionrisk()
                eth_leverage = None
                for pos in leverage_info:
                    if pos["symbol"] == "ETHUSDT":
                        eth_leverage = pos["leverage"]
                        break

                if eth_leverage:
                    results["leverage"] = eth_leverage
                    console.print(f"  Current ETH/USDT Leverage: {eth_leverage}x")
                else:
                    console.print("  No leverage info available")
                    results["leverage"] = None

            except Exception as e:
                console.print(f"  Could not fetch leverage: {e}")
                results["leverage"] = None

            self.results["private"] = results
            return True

        except Exception as e:
            error_msg = str(e)
            console.print(f"\n[red]❌ Private endpoint test failed: {error_msg}[/red]")

            # Check for common API key issues
            if "API-key" in error_msg or "Invalid API" in error_msg:
                console.print(
                    "[yellow]⚠️  API Key might be invalid or not activated for futures[/yellow]"
                )
            elif "Signature" in error_msg:
                console.print("[yellow]⚠️  API Secret might be incorrect[/yellow]")
            elif "IP" in error_msg:
                console.print("[yellow]⚠️  IP address might not be whitelisted[/yellow]")

            self.results["private"] = {"error": error_msg}
            return False

    async def test_trading_capability(self):
        """Test if we can place and cancel orders (test orders only)."""
        console.print("\n[bold cyan]Testing Trading Capability[/bold cyan]")
        console.print("-" * 40)

        console.print(
            "[yellow]⚠️  Note: This will attempt a small test order far from market price[/yellow]"
        )

        try:
            symbol = "ETH/USDT:USDT"

            # Get current price
            ticker = await self.exchange.fetch_ticker(symbol)
            current_price = ticker["last"]

            # Place a limit buy order at 50% below market (won't fill)
            test_price = current_price * 0.5
            test_amount = 0.001  # Minimum size

            console.print(f"\n📝 Placing test order...")
            console.print(f"  Symbol: {symbol}")
            console.print(f"  Type: Limit Buy")
            console.print(f"  Price: ${test_price:.2f} (50% below market)")
            console.print(f"  Amount: {test_amount} ETH")

            try:
                # Create limit buy order
                order = await self.exchange.create_limit_buy_order(
                    symbol, test_amount, test_price
                )

                console.print(f"  ✅ Order placed! ID: {order['id']}")

                # Immediately cancel it
                console.print(f"\n🚫 Cancelling test order...")
                await asyncio.sleep(1)  # Brief delay

                cancelled = await self.exchange.cancel_order(order["id"], symbol)
                console.print(f"  ✅ Order cancelled successfully")

                self.results["trading"] = {
                    "can_place_orders": True,
                    "can_cancel_orders": True,
                    "test_order_id": order["id"],
                }

                return True

            except Exception as e:
                console.print(f"  [red]❌ Trading test failed: {e}[/red]")
                self.results["trading"] = {"can_place_orders": False, "error": str(e)}
                return False

        except Exception as e:
            console.print(f"[red]❌ Could not test trading: {e}[/red]")
            self.results["trading"] = {"error": str(e)}
            return False

    def print_summary(self):
        """Print test summary."""
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]Binance API Test Summary[/bold cyan]")
        console.print("=" * 60)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Feature", style="cyan", width=25)
        table.add_column("Status", width=15)
        table.add_column("Details", style="dim")

        # Public API
        if "public" in self.results:
            if "error" not in self.results["public"]:
                table.add_row(
                    "Public API",
                    "✅ Working",
                    f"ETH: ${self.results['public']['ticker']['last']:,.2f}",
                )
            else:
                table.add_row(
                    "Public API", "❌ Failed", self.results["public"]["error"][:50]
                )

        # Private API
        if "private" in self.results:
            if "error" not in self.results["private"]:
                balance = self.results["private"]["balance"]["free"]
                table.add_row(
                    "Private API", "✅ Working", f"Balance: ${balance:,.2f} USDT"
                )
            else:
                table.add_row(
                    "Private API", "❌ Failed", self.results["private"]["error"][:50]
                )

        # Trading
        if "trading" in self.results:
            if self.results["trading"].get("can_place_orders"):
                table.add_row("Trading", "✅ Enabled", "Can place/cancel orders")
            else:
                table.add_row(
                    "Trading",
                    "❌ Disabled",
                    self.results["trading"].get("error", "Cannot trade")[:50],
                )

        console.print(table)

        # Overall status
        all_working = (
            "public" in self.results
            and "error" not in self.results["public"]
            and "private" in self.results
            and "error" not in self.results["private"]
        )

        if all_working:
            console.print(
                "\n[bold green]✅ Binance API fully operational![/bold green]"
            )
            console.print("The bot can:")
            console.print("  • Monitor market prices and funding rates")
            console.print("  • Check account balance and positions")
            console.print("  • Execute hedging trades")
        else:
            console.print(
                "\n[bold yellow]⚠️  Some API features not working[/bold yellow]"
            )
            console.print("Please check:")
            console.print("  • API keys are correct")
            console.print("  • API keys have futures trading enabled")
            console.print(
                "  • IP address is whitelisted (if IP restriction is enabled)"
            )

    async def run_all_tests(self):
        """Run all Binance API tests."""
        console.print(
            Panel.fit(
                "[bold cyan]Binance API Test Suite[/bold cyan]\n"
                "Testing API access and capabilities...",
                border_style="cyan",
            )
        )

        # Connect
        if not await self.connect():
            return

        # Run tests
        await self.test_public_endpoints()
        await self.test_private_endpoints()

        # Only test trading if private API works
        if "private" in self.results and "error" not in self.results["private"]:
            await self.test_trading_capability()

        # Close connection
        await self.exchange.close()

        # Print summary
        self.print_summary()


async def main():
    """Main entry point."""
    tester = BinanceAPITester()

    # Check if keys are configured
    if not tester.api_key or not tester.api_secret:
        console.print("[red]❌ Binance API keys not found in .env file![/red]")
        console.print("Please configure BINANCE_API_KEY and BINANCE_API_SECRET")
        return

    console.print(f"[dim]API Key: {tester.api_key[:10]}...{tester.api_key[-4:]}[/dim]")
    console.print(f"[dim]Secret: {'*' * 20}[/dim]")

    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Binance API Test")
    print("=" * 60)

    asyncio.run(main())
