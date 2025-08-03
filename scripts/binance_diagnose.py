#!/usr/bin/env python3
"""
Binance API Diagnostic Tool

Helps diagnose API key issues and provides specific solutions.
"""

import asyncio
import os
import hmac
import hashlib
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
import ccxt.async_support as ccxt
import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console()


class BinanceDiagnostic:
    """Diagnose Binance API issues."""

    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        self.base_url = "https://fapi.binance.com"  # Futures API

    async def test_key_format(self):
        """Check if API keys have correct format."""
        console.print("\n[bold]1. Checking API Key Format[/bold]")
        console.print("-" * 40)

        issues = []

        # Check API key
        if not self.api_key:
            issues.append("❌ API Key is empty")
        elif len(self.api_key) != 64:
            issues.append(f"⚠️  API Key length is {len(self.api_key)}, expected 64")
        else:
            console.print(f"✅ API Key format looks correct (64 chars)")
            console.print(f"   Key: {self.api_key[:8]}...{self.api_key[-4:]}")

        # Check API secret
        if not self.api_secret:
            issues.append("❌ API Secret is empty")
        elif len(self.api_secret) != 64:
            issues.append(
                f"⚠️  API Secret length is {len(self.api_secret)}, expected 64"
            )
        else:
            console.print(f"✅ API Secret format looks correct (64 chars)")

        if issues:
            for issue in issues:
                console.print(issue)
            return False

        return True

    async def test_spot_vs_futures(self):
        """Test if the key works for spot vs futures."""
        console.print("\n[bold]2. Testing Spot vs Futures Access[/bold]")
        console.print("-" * 40)

        # Test Spot API
        console.print("Testing Spot API...")
        spot_exchange = ccxt.binance(
            {
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
            }
        )

        try:
            await spot_exchange.load_markets()
            balance = await spot_exchange.fetch_balance()
            console.print("✅ Spot API works!")
            spot_works = True
        except Exception as e:
            console.print(f"❌ Spot API failed: {str(e)[:100]}")
            spot_works = False
        finally:
            await spot_exchange.close()

        # Test Futures API
        console.print("\nTesting Futures API...")
        futures_exchange = ccxt.binance(
            {
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "future"},
            }
        )

        try:
            await futures_exchange.load_markets()
            balance = await futures_exchange.fetch_balance()
            console.print("✅ Futures API works!")
            futures_works = True
        except Exception as e:
            if "-2015" in str(e):
                console.print(
                    "❌ Futures API failed: Invalid API-key, IP, or permissions"
                )
                console.print(
                    "\n[yellow]This key doesn't have futures permissions![/yellow]"
                )
            else:
                console.print(f"❌ Futures API failed: {str(e)[:100]}")
            futures_works = False
        finally:
            await futures_exchange.close()

        return spot_works, futures_works

    async def test_direct_api_call(self):
        """Make a direct API call to test signature."""
        console.print("\n[bold]3. Testing Direct API Call (Manual Signature)[/bold]")
        console.print("-" * 40)

        # Prepare request
        timestamp = int(time.time() * 1000)
        params = {"timestamp": timestamp}

        # Create signature
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        params["signature"] = signature

        # Make request
        url = f"{self.base_url}/fapi/v2/account"
        headers = {"X-MBX-APIKEY": self.api_key}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    status = response.status
                    text = await response.text()

                    if status == 200:
                        console.print("✅ Direct API call successful!")
                        return True
                    else:
                        console.print(f"❌ API returned status {status}")
                        console.print(f"   Response: {text[:200]}")

                        # Parse specific errors
                        if "-2015" in text:
                            console.print(
                                "\n[red]Error -2015: Invalid API-key, IP, or permissions[/red]"
                            )
                        elif "-1022" in text:
                            console.print("\n[red]Error -1022: Invalid signature[/red]")
                        elif "-1021" in text:
                            console.print(
                                "\n[red]Error -1021: Timestamp outside of recvWindow[/red]"
                            )

                        return False

            except Exception as e:
                console.print(f"❌ Request failed: {e}")
                return False

    async def test_ip_whitelist(self):
        """Get current IP and check if whitelisting might be the issue."""
        console.print("\n[bold]4. Checking IP Address[/bold]")
        console.print("-" * 40)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.ipify.org?format=json") as response:
                    data = await response.json()
                    current_ip = data["ip"]

            console.print(f"📍 Your current IP: {current_ip}")
            console.print("\nIf you have IP restrictions enabled on Binance:")
            console.print(
                f"  1. Go to: https://www.binance.com/en/my/settings/api-management"
            )
            console.print(f"  2. Click 'Edit' on your API key")
            console.print(f"  3. Add this IP: {current_ip}")
            console.print(f"  4. Or disable IP restrictions (less secure)")

            return current_ip

        except Exception as e:
            console.print(f"❌ Could not get IP: {e}")
            return None

    def print_solutions(self, spot_works, futures_works):
        """Print specific solutions based on test results."""
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]Diagnosis & Solutions[/bold cyan]")
        console.print("=" * 60)

        if spot_works and not futures_works:
            console.print(
                Panel.fit(
                    "[bold yellow]Issue: API key works for Spot but not Futures[/bold yellow]\n\n"
                    "[bold]Solution:[/bold]\n"
                    "1. Log into Binance\n"
                    "2. Go to API Management\n"
                    "3. Find your API key\n"
                    "4. Click 'Edit'\n"
                    "5. Enable 'Enable Futures' permission\n"
                    "6. Save changes\n\n"
                    "Note: You might need to create a new API key\n"
                    "specifically for futures trading.",
                    border_style="yellow",
                )
            )

        elif not spot_works and not futures_works:
            console.print(
                Panel.fit(
                    "[bold red]Issue: API key not working at all[/bold red]\n\n"
                    "[bold]Possible causes:[/bold]\n"
                    "1. Invalid API key or secret\n"
                    "2. IP address not whitelisted\n"
                    "3. API key disabled\n\n"
                    "[bold]Solutions:[/bold]\n"
                    "• Double-check the API key and secret\n"
                    "• Ensure no extra spaces or characters\n"
                    "• Check IP whitelist settings\n"
                    "• Try creating a new API key",
                    border_style="red",
                )
            )

        elif spot_works and futures_works:
            console.print(
                Panel.fit(
                    "[bold green]Success! API keys are working[/bold green]\n\n"
                    "Both Spot and Futures access confirmed.\n"
                    "The bot should be able to trade.",
                    border_style="green",
                )
            )

    async def run_diagnosis(self):
        """Run complete diagnosis."""
        console.print(
            Panel.fit(
                "[bold cyan]Binance API Diagnostic Tool[/bold cyan]\n"
                "Checking API configuration and permissions...",
                border_style="cyan",
            )
        )

        # Check key format
        format_ok = await self.test_key_format()
        if not format_ok:
            console.print("\n[red]Fix the API key format issues first![/red]")
            return

        # Test spot vs futures
        spot_works, futures_works = await self.test_spot_vs_futures()

        # Test direct API call
        await self.test_direct_api_call()

        # Check IP
        await self.test_ip_whitelist()

        # Print solutions
        self.print_solutions(spot_works, futures_works)

        # Summary table
        console.print("\n[bold]Summary:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Check", style="cyan", width=20)
        table.add_column("Result", width=15)

        table.add_row("Key Format", "✅ Valid" if format_ok else "❌ Invalid")
        table.add_row("Spot API", "✅ Working" if spot_works else "❌ Failed")
        table.add_row("Futures API", "✅ Working" if futures_works else "❌ Failed")

        console.print(table)


async def main():
    diagnostic = BinanceDiagnostic()
    await diagnostic.run_diagnosis()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Binance API Diagnostic Tool")
    print("=" * 60)

    asyncio.run(main())
