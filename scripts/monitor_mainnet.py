#!/usr/bin/env python3
"""
Mainnet monitoring script for EulerSwap USDT/WETH pool.

This script monitors the live EulerSwap pool at 0x55dcf9455eee8fd3f5eed17606291272cde428a8
and provides real-time data collection and analysis.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config_manager.mainnet_config import MainnetConfig
from database_manager import DatabaseManager
from logger_manager import LoggerManager, LogTag
from swap_monitor import SwapMonitor
from euler_swap import EulerPoolManager
from exchange_manager import BinanceExchange


class MainnetMonitor:
    """Monitor for mainnet EulerSwap pool."""

    def __init__(self):
        """Initialize mainnet monitor."""
        self.logger = LoggerManager()
        self.logger.setup_logger(log_file="mainnet_monitor.log")

        # Load mainnet configuration
        self.config = MainnetConfig.from_env(".env.mainnet")

        # Validate configuration
        try:
            self.config.validate_mainnet_config()
            self.logger.log_info("Mainnet configuration validated", LogTag.INFO)
        except ValueError as e:
            self.logger.log_error(f"Configuration validation failed: {e}")
            raise

        # Initialize components
        self.database = DatabaseManager(self.config.database_url)
        self.exchange = BinanceExchange(
            api_key=self.config.binance_api_key,
            api_secret=self.config.binance_api_secret,
            testnet=False,  # Mainnet
        )

        # Initialize swap monitor
        self.swap_monitor = SwapMonitor(
            rpc_url=self.config.rpc_url,
            pool_address=self.config.eulerswap_pool,
            abi_path="abi/eulerswap_pool.json",
            exchange=self.exchange,
            symbol_perpetual="ETH/USDT:USDT",
            database_manager=self.database,
        )

        self.running = False

    async def display_pool_info(self):
        """Display pool information."""
        print("\n" + "=" * 60)
        print("EulerSwap USDT/WETH Pool Monitor - Mainnet")
        print("=" * 60)

        pool_info = self.config.get_pool_info()

        print(f"\nNetwork: {pool_info['network']} (Chain ID: {pool_info['chain_id']})")
        print(f"Pool Address: {pool_info['pool']['address']}")
        print(f"\nToken0 (USDT):")
        print(f"  Address: {pool_info['pool']['token0']['address']}")
        print(f"  Decimals: {pool_info['pool']['token0']['decimals']}")
        print(f"  Vault: {pool_info['pool']['token0']['vault']}")
        print(f"\nToken1 (WETH):")
        print(f"  Address: {pool_info['pool']['token1']['address']}")
        print(f"  Decimals: {pool_info['pool']['token1']['decimals']}")
        print(f"  Vault: {pool_info['pool']['token1']['vault']}")

        print(f"\nRisk Parameters:")
        for key, value in pool_info["risk_params"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

        print("\n" + "=" * 60)

    async def monitor_reserves(self):
        """Monitor pool reserves continuously."""
        self.logger.log_info("Starting reserve monitoring", LogTag.INFO)

        while self.running:
            try:
                # Fetch current reserves
                reserve0, reserve1, status = await self.swap_monitor.fetch_reserves()

                # Check pool status
                status_msg = "Unknown"
                if status == 0:
                    status_msg = "Unactivated"
                    self.logger.log_warning("Pool is not activated!")
                elif status == 1:
                    status_msg = "Unlocked"
                elif status == 2:
                    status_msg = "Locked"
                    self.logger.log_warning("Pool is locked (reentrancy)")

                # Display current state
                print(
                    f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Pool Status: {status_msg}"
                )
                print(f"  USDT Reserve: {reserve0:,.2f}")
                print(f"  WETH Reserve: {reserve1:,.4f}")
                print(
                    f"  Implied Price: {reserve0/reserve1 if reserve1 > 0 else 0:,.2f} USDT/WETH"
                )

                # Check for desynchronization
                if self.swap_monitor.pool_manager:
                    is_desynced = (
                        self.swap_monitor.pool_manager.is_reserve_desynchronized(
                            (reserve0, reserve1), self.config.desync_warning_percent
                        )
                    )
                    if is_desynced:
                        print(
                            "  ⚠️  WARNING: Reserves are desynchronized from equilibrium!"
                        )

                # Get Binance position
                try:
                    position = await self.exchange.get_current_perpetual_position(
                        "ETH/USDT:USDT"
                    )
                    short_size = (
                        position["size"]
                        if position["side"] == "short"
                        else Decimal("0")
                    )

                    # Calculate delta
                    delta = reserve1 - short_size

                    print(f"  Short Position: {short_size:,.4f} ETH")
                    print(f"  Delta Exposure: {delta:,.4f} ETH")

                    if abs(delta) > self.config.hedge_threshold_eth:
                        print(
                            f"  🔴 HEDGE NEEDED: Delta exceeds threshold ({self.config.hedge_threshold_eth} ETH)"
                        )
                    elif abs(delta) > self.config.hedge_threshold_eth / 2:
                        print(f"  🟡 WARNING: Delta approaching threshold")
                    else:
                        print(f"  🟢 Delta within acceptable range")

                except Exception as e:
                    print(f"  ⚠️  Could not fetch Binance position: {e}")

                # Get pool parameters if available
                if self.swap_monitor.pool_manager and not hasattr(
                    self, "_params_fetched"
                ):
                    try:
                        params = (
                            await self.swap_monitor.pool_manager.fetch_pool_params()
                        )
                        print(f"\nPool Parameters:")
                        print(f"  Equilibrium USDT: {params.equilibrium_reserve0:,.2f}")
                        print(f"  Equilibrium WETH: {params.equilibrium_reserve1:,.4f}")
                        print(f"  Equilibrium Price: {params.equilibrium_price:,.2f}")
                        print(f"  Swap Fee: {params.fee * 100:.2f}%")
                        print(f"  Protocol Fee: {params.protocol_fee * 100:.4f}%")
                        self._params_fetched = True
                    except Exception as e:
                        self.logger.log_debug(
                            f"Could not fetch pool params: {e}", LogTag.RPC
                        )

                # Wait for next polling interval
                await asyncio.sleep(self.config.polling_interval_seconds)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.log_error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.retry_delay_seconds)

    async def check_funding_rate(self):
        """Check Binance funding rate periodically."""
        while self.running:
            try:
                funding_rate = await self.exchange.get_funding_rate("ETH/USDT:USDT")

                print(f"\n[Funding Rate Update]")
                print(f"  Current Rate: {funding_rate * 100:.4f}% per 8 hours")
                print(f"  Annualized: {funding_rate * 3 * 365 * 100:.2f}%")

                if abs(funding_rate) > self.config.max_funding_rate_percent / 100:
                    print(f"  ⚠️  WARNING: High funding rate detected!")

                # Wait 8 hours for next check
                await asyncio.sleep(self.config.funding_rate_check_interval)

            except Exception as e:
                self.logger.log_error(f"Error checking funding rate: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    async def start(self):
        """Start monitoring."""
        print("\nInitializing Mainnet Monitor...")

        # Display pool information
        await self.display_pool_info()

        # Connect to exchange
        print("\nConnecting to Binance...")
        await self.exchange.connect()
        print("✓ Connected to Binance")

        # Start monitoring
        self.running = True

        print("\nStarting monitoring tasks...")
        print("Press Ctrl+C to stop\n")

        # Create monitoring tasks
        tasks = [
            asyncio.create_task(self.monitor_reserves()),
            asyncio.create_task(self.check_funding_rate()),
        ]

        try:
            # Wait for tasks
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
            self.running = False

            # Cancel tasks
            for task in tasks:
                task.cancel()

            # Disconnect
            await self.exchange.disconnect()

            print("Monitor stopped.")

    async def get_historical_data(self, hours: int = 24):
        """
        Fetch and display historical data.

        Args:
            hours: Number of hours to look back
        """
        print(f"\nFetching last {hours} hours of data...")

        snapshots = self.database.get_position_snapshots(
            start_time=datetime.utcnow() - timedelta(hours=hours)
        )

        if not snapshots:
            print("No historical data available")
            return

        print(f"Found {len(snapshots)} snapshots")

        # Calculate statistics
        deltas = [s.delta for s in snapshots]
        avg_delta = sum(deltas) / len(deltas)
        max_delta = max(deltas, key=abs)
        min_delta = min(deltas, key=abs)

        print(f"\nDelta Statistics:")
        print(f"  Average: {avg_delta:,.4f} ETH")
        print(f"  Maximum: {max_delta:,.4f} ETH")
        print(f"  Minimum: {min_delta:,.4f} ETH")

        # Check hedge events
        hedges = self.database.get_hedge_snapshots(
            start_time=datetime.utcnow() - timedelta(hours=hours)
        )

        if hedges:
            print(f"\nHedge Events: {len(hedges)}")
            successful = sum(1 for h in hedges if h.success)
            print(f"  Successful: {successful}")
            print(f"  Failed: {len(hedges) - successful}")


async def main():
    """Main entry point."""
    monitor = MainnetMonitor()

    try:
        await monitor.start()
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("EulerSwap Mainnet Monitor")
    print("========================")
    print("\nThis tool monitors the live USDT/WETH pool on Ethereum mainnet.")
    print("Pool Address: 0x55dcf9455eee8fd3f5eed17606291272cde428a8")
    print("\nMake sure you have configured your .env.mainnet file with:")
    print("- RPC_URL (Alchemy/Infura endpoint)")
    print("- BINANCE_API_KEY and BINANCE_API_SECRET")
    print("\nStarting in 3 seconds...")

    import time

    time.sleep(3)

    asyncio.run(main())
