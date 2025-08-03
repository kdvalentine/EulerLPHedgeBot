#!/usr/bin/env python3
"""
Connection test script for NoetherBot.

Tests all external connections:
1. Infura RPC connection
2. EulerSwap pool contract
3. Binance API (public endpoints only for safety)
4. Database initialization
"""

import asyncio
import sys
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from web3 import Web3
import ccxt.async_support as ccxt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Load environment variables
load_dotenv()

console = Console()


class ConnectionTester:
    """Test all external connections."""

    def __init__(self):
        """Initialize connection tester."""
        self.results = {}
        self.infura_key = os.getenv("RPC_URL", "").split("/")[-1]
        self.binance_api_key = os.getenv("BINANCE_API_KEY", "")

    async def test_infura_connection(self):
        """Test Infura RPC connection."""
        console.print("\n[bold yellow]Testing Infura Connection...[/bold yellow]")

        try:
            # Create Web3 instance
            rpc_url = os.getenv("RPC_URL")
            if not rpc_url:
                raise ValueError("RPC_URL not configured")

            w3 = Web3(Web3.HTTPProvider(rpc_url))

            # Test connection
            is_connected = w3.is_connected()

            if not is_connected:
                raise ConnectionError("Failed to connect to Infura")

            # Get network info
            chain_id = w3.eth.chain_id
            block_number = w3.eth.block_number
            gas_price = w3.eth.gas_price / 10**9  # Convert to Gwei

            # Get syncing status
            syncing = w3.eth.syncing

            self.results["infura"] = {
                "status": "✅ Connected",
                "chain_id": chain_id,
                "block_number": f"{block_number:,}",
                "gas_price": f"{gas_price:.2f} Gwei",
                "syncing": "No" if not syncing else "Yes",
                "endpoint": rpc_url.replace(self.infura_key, "***"),
            }

            console.print(f"  ✅ Connected to Ethereum Mainnet")
            console.print(f"  Chain ID: {chain_id}")
            console.print(f"  Latest Block: {block_number:,}")
            console.print(f"  Gas Price: {gas_price:.2f} Gwei")

            return True

        except Exception as e:
            self.results["infura"] = {"status": f"❌ Failed: {str(e)}", "error": str(e)}
            console.print(f"  [red]❌ Connection failed: {e}[/red]")
            return False

    async def test_eulerswap_pool(self):
        """Test EulerSwap pool contract access."""
        console.print("\n[bold yellow]Testing EulerSwap Pool Contract...[/bold yellow]")

        try:
            rpc_url = os.getenv("RPC_URL")
            pool_address = os.getenv("EULERSWAP_POOL")

            if not rpc_url or not pool_address:
                raise ValueError("RPC_URL or EULERSWAP_POOL not configured")

            w3 = Web3(Web3.HTTPProvider(rpc_url))

            # Check if address is a contract
            code = w3.eth.get_code(pool_address)
            if code == b"":
                raise ValueError(f"No contract at address {pool_address}")

            # Minimal ABI for getReserves
            abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getReserves",
                    "outputs": [
                        {"name": "reserve0", "type": "uint112"},
                        {"name": "reserve1", "type": "uint112"},
                        {"name": "status", "type": "uint32"},
                    ],
                    "type": "function",
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getAssets",
                    "outputs": [
                        {"name": "asset0", "type": "address"},
                        {"name": "asset1", "type": "address"},
                    ],
                    "type": "function",
                },
            ]

            # Create contract instance
            contract = w3.eth.contract(address=pool_address, abi=abi)

            # Test getReserves
            reserves = contract.functions.getReserves().call()
            reserve0 = Decimal(reserves[0]) / Decimal(10**6)  # USDT
            reserve1 = Decimal(reserves[1]) / Decimal(10**18)  # WETH
            status = reserves[2]

            status_msg = "Unknown"
            if status == 0:
                status_msg = "Unactivated"
            elif status == 1:
                status_msg = "Unlocked (Active)"
            elif status == 2:
                status_msg = "Locked"

            # Test getAssets
            try:
                assets = contract.functions.getAssets().call()
                asset0 = assets[0]
                asset1 = assets[1]
            except:
                asset0 = "N/A"
                asset1 = "N/A"

            self.results["eulerswap"] = {
                "status": "✅ Accessible",
                "pool_address": pool_address,
                "pool_status": status_msg,
                "reserve0_usdt": f"{reserve0:,.2f}",
                "reserve1_weth": f"{reserve1:,.4f}",
                "implied_price": f"{reserve0/reserve1:,.2f}" if reserve1 > 0 else "N/A",
                "asset0": asset0,
                "asset1": asset1,
            }

            console.print(f"  ✅ Pool Contract Accessible")
            console.print(f"  Address: {pool_address}")
            console.print(f"  Status: {status_msg}")
            console.print(f"  USDT Reserve: {reserve0:,.2f}")
            console.print(f"  WETH Reserve: {reserve1:,.4f}")
            if reserve1 > 0:
                console.print(f"  Implied Price: {reserve0/reserve1:,.2f} USDT/WETH")

            return True

        except Exception as e:
            self.results["eulerswap"] = {
                "status": f"❌ Failed: {str(e)}",
                "error": str(e),
            }
            console.print(f"  [red]❌ Pool access failed: {e}[/red]")
            return False

    async def test_binance_connection(self):
        """Test Binance API connection (public endpoints only)."""
        console.print("\n[bold yellow]Testing Binance Connection...[/bold yellow]")

        try:
            # Note: We'll only test public endpoints for safety
            # Private endpoints would require the API secret

            exchange = ccxt.binance(
                {
                    "enableRateLimit": True,
                    "options": {"defaultType": "future"},  # Futures market
                }
            )

            # Test public endpoints
            # 1. Check exchange status
            status = await exchange.fetch_status()

            # 2. Load markets
            await exchange.load_markets()

            # 3. Get ETH/USDT perpetual info
            symbol = "ETH/USDT:USDT"
            if symbol not in exchange.markets:
                raise ValueError(f"Market {symbol} not found")

            market = exchange.markets[symbol]

            # 4. Get ticker
            ticker = await exchange.fetch_ticker(symbol)

            # 5. Get funding rate
            funding = await exchange.fetch_funding_rate(symbol)

            # 6. Get order book (top 5 levels)
            orderbook = await exchange.fetch_order_book(symbol, 5)

            self.results["binance"] = {
                "status": "✅ Connected (Public)",
                "exchange_status": status.get("status", "ok"),
                "market": symbol,
                "last_price": f"{ticker['last']:,.2f}",
                "bid": f"{ticker['bid']:,.2f}",
                "ask": f"{ticker['ask']:,.2f}",
                "volume_24h": f"{ticker['quoteVolume']:,.0f} USDT",
                "funding_rate": f"{funding['rate']*100:.4f}%",
                "spread": f"{ticker['ask'] - ticker['bid']:.2f}",
                "api_key_length": (
                    len(self.binance_api_key) if self.binance_api_key else 0
                ),
            }

            console.print(f"  ✅ Binance Futures Connected (Public API)")
            console.print(f"  Market: {symbol}")
            console.print(f"  Price: ${ticker['last']:,.2f}")
            console.print(f"  Bid/Ask: ${ticker['bid']:,.2f} / ${ticker['ask']:,.2f}")
            console.print(f"  24h Volume: ${ticker['quoteVolume']:,.0f}")
            console.print(f"  Funding Rate: {funding['rate']*100:.4f}% per 8h")

            if self.binance_api_key:
                console.print(
                    f"  [yellow]⚠️  API Key configured (length: {len(self.binance_api_key)})[/yellow]"
                )
                console.print(
                    f"  [yellow]    Note: Private endpoints require API Secret[/yellow]"
                )
            else:
                console.print(f"  [yellow]⚠️  No API Key configured[/yellow]")

            await exchange.close()
            return True

        except Exception as e:
            self.results["binance"] = {
                "status": f"❌ Failed: {str(e)}",
                "error": str(e),
            }
            console.print(f"  [red]❌ Binance connection failed: {e}[/red]")

            if exchange:
                await exchange.close()
            return False

    async def test_token_contracts(self):
        """Test token contract accessibility."""
        console.print("\n[bold yellow]Testing Token Contracts...[/bold yellow]")

        try:
            rpc_url = os.getenv("RPC_URL")
            usdt_address = os.getenv("USDT_ADDRESS")
            weth_address = os.getenv("WETH_ADDRESS")

            w3 = Web3(Web3.HTTPProvider(rpc_url))

            # ERC20 ABI for basic functions
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "name",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function",
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function",
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function",
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "totalSupply",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function",
                },
            ]

            tokens = {}

            # Test USDT
            usdt_contract = w3.eth.contract(address=usdt_address, abi=erc20_abi)
            usdt_symbol = usdt_contract.functions.symbol().call()
            usdt_decimals = usdt_contract.functions.decimals().call()
            usdt_supply = usdt_contract.functions.totalSupply().call()

            tokens["USDT"] = {
                "address": usdt_address,
                "symbol": usdt_symbol,
                "decimals": usdt_decimals,
                "total_supply": f"{usdt_supply / 10**usdt_decimals:,.0f}",
            }

            # Test WETH
            weth_contract = w3.eth.contract(address=weth_address, abi=erc20_abi)
            weth_symbol = weth_contract.functions.symbol().call()
            weth_decimals = weth_contract.functions.decimals().call()
            weth_supply = weth_contract.functions.totalSupply().call()

            tokens["WETH"] = {
                "address": weth_address,
                "symbol": weth_symbol,
                "decimals": weth_decimals,
                "total_supply": f"{weth_supply / 10**weth_decimals:,.0f}",
            }

            self.results["tokens"] = {
                "status": "✅ Verified",
                "USDT": tokens["USDT"],
                "WETH": tokens["WETH"],
            }

            console.print(f"  ✅ Token Contracts Verified")
            console.print(f"  USDT: {usdt_symbol} (decimals: {usdt_decimals})")
            console.print(f"  WETH: {weth_symbol} (decimals: {weth_decimals})")

            return True

        except Exception as e:
            self.results["tokens"] = {"status": f"❌ Failed: {str(e)}", "error": str(e)}
            console.print(f"  [red]❌ Token verification failed: {e}[/red]")
            return False

    async def test_database(self):
        """Test database initialization."""
        console.print("\n[bold yellow]Testing Database...[/bold yellow]")

        try:
            from database_manager import DatabaseManager

            db_url = os.getenv("DATABASE_URL", "sqlite:///noether_bot_test.db")
            db = DatabaseManager(db_url)

            # Test by creating a sample snapshot
            from models import PositionSnapshot

            snapshot = PositionSnapshot(
                reserve_token0=Decimal("1000000"),
                reserve_token1=Decimal("500"),
                short_position_size=Decimal("490"),
                timestamp=datetime.utcnow(),
            )

            # Save and retrieve
            snapshot_id = db.save_position_snapshot(snapshot)
            retrieved = db.get_latest_position_snapshot()

            if not retrieved:
                raise ValueError("Could not retrieve saved snapshot")

            self.results["database"] = {
                "status": "✅ Working",
                "type": "SQLite",
                "url": db_url.replace("///", "/"),
                "test_write": "Success",
                "test_read": "Success",
            }

            console.print(f"  ✅ Database Initialized")
            console.print(f"  Type: SQLite")
            console.print(f"  Write/Read: Success")

            return True

        except Exception as e:
            self.results["database"] = {
                "status": f"❌ Failed: {str(e)}",
                "error": str(e),
            }
            console.print(f"  [red]❌ Database test failed: {e}[/red]")
            return False

    def print_summary(self):
        """Print summary of all tests."""
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]Connection Test Summary[/bold cyan]")
        console.print("=" * 60)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Status", width=20)
        table.add_column("Details", style="dim")

        # Infura
        if "infura" in self.results:
            status = self.results["infura"]["status"]
            details = ""
            if "✅" in status:
                details = f"Block: {self.results['infura']['block_number']}, Gas: {self.results['infura']['gas_price']}"
            else:
                details = self.results["infura"].get("error", "Unknown error")
            table.add_row("Infura RPC", status, details)

        # EulerSwap
        if "eulerswap" in self.results:
            status = self.results["eulerswap"]["status"]
            details = ""
            if "✅" in status:
                details = f"Status: {self.results['eulerswap']['pool_status']}, USDT: {self.results['eulerswap']['reserve0_usdt']}"
            else:
                details = self.results["eulerswap"].get("error", "Unknown error")
            table.add_row("EulerSwap Pool", status, details)

        # Binance
        if "binance" in self.results:
            status = self.results["binance"]["status"]
            details = ""
            if "✅" in status:
                details = f"ETH: ${self.results['binance']['last_price']}, Funding: {self.results['binance']['funding_rate']}"
            else:
                details = self.results["binance"].get("error", "Unknown error")
            table.add_row("Binance API", status, details)

        # Tokens
        if "tokens" in self.results:
            status = self.results["tokens"]["status"]
            details = ""
            if "✅" in status:
                details = "USDT & WETH verified"
            else:
                details = self.results["tokens"].get("error", "Unknown error")
            table.add_row("Token Contracts", status, details)

        # Database
        if "database" in self.results:
            status = self.results["database"]["status"]
            details = ""
            if "✅" in status:
                details = "Read/Write working"
            else:
                details = self.results["database"].get("error", "Unknown error")
            table.add_row("Database", status, details)

        console.print(table)

        # Overall status
        all_passed = all("✅" in r.get("status", "") for r in self.results.values())

        if all_passed:
            console.print("\n[bold green]✅ All connections successful![/bold green]")
            console.print("The bot is ready to run.")
        else:
            console.print("\n[bold red]⚠️  Some connections failed[/bold red]")
            console.print("Please check the configuration and try again.")

        # Save results to file
        with open("connection_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        console.print(f"\nDetailed results saved to: connection_test_results.json")

    async def run_all_tests(self):
        """Run all connection tests."""
        console.print(
            Panel.fit(
                "[bold cyan]NoetherBot Connection Test[/bold cyan]\n"
                "Testing all external connections...",
                border_style="cyan",
            )
        )

        # Run tests
        await self.test_infura_connection()
        await self.test_eulerswap_pool()
        await self.test_binance_connection()
        await self.test_token_contracts()
        await self.test_database()

        # Print summary
        self.print_summary()


async def main():
    """Main entry point."""
    tester = ConnectionTester()

    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    console.print("[bold]Starting Connection Tests...[/bold]\n")

    # Check if .env exists
    if not Path(".env").exists():
        console.print("[red]❌ .env file not found![/red]")
        console.print("Please create a .env file with your configuration.")
        sys.exit(1)

    # Run tests
    asyncio.run(main())
