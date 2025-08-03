#!/usr/bin/env python3
"""Main entry point for NoetherBot."""

import asyncio
import signal
import sys
from pathlib import Path

from config_manager import ConfigManager
from database_manager import DatabaseManager
from exchange_manager import BinanceExchange
from logger_manager import LoggerManager, LogTag
from risk_manager import RiskManager
from strategy_engine import StrategyEngine
from swap_monitor import SwapMonitor


class NoetherBot:
    """Main bot orchestrator."""

    def __init__(self):
        """Initialize the bot."""
        self.logger = LoggerManager()
        self.logger.setup_logger(log_file="noether_bot.log")

        # Initialize components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.database_manager = DatabaseManager(self.config.database_url)
        self.exchange = BinanceExchange(
            api_key=self.config.binance_api_key,
            api_secret=self.config.binance_api_secret,
            testnet=self.config.binance_testnet,
        )
        self.risk_manager = RiskManager(self.config)
        self.strategy_engine = StrategyEngine(
            config=self.config,
            exchange=self.exchange,
            risk_manager=self.risk_manager,
            database_manager=self.database_manager,
        )
        self.swap_monitor = SwapMonitor(
            rpc_url=self.config.rpc_url,
            pool_address=self.config.eulerswap_pool,
            abi_path=self.config_manager.get_abi_path(),
            exchange=self.exchange,
            symbol_perpetual=self.config.symbol_perpetual,
            database_manager=self.database_manager,
        )

        self._running = False

    async def start(self):
        """Start the bot."""
        try:
            self.logger.log_info("Starting NoetherBot...", LogTag.INFO)

            # Connect to exchange
            await self.exchange.connect()

            # Set up snapshot callback
            self.swap_monitor.set_snapshot_callback(
                self.strategy_engine.process_position_snapshot
            )

            # Start monitoring
            await self.swap_monitor.start_monitoring(
                polling_interval=self.config.polling_interval_seconds
            )

            self._running = True
            self.logger.log_info("NoetherBot started successfully", LogTag.INFO)

            # Keep running
            while self._running:
                await asyncio.sleep(1)

                # Periodic health check
                if not await self.swap_monitor.check_connection():
                    self.logger.log_warning("Connection issues detected")

        except Exception as e:
            self.logger.log_error("Failed to start bot", e)
            await self.stop()
            raise

    async def stop(self):
        """Stop the bot."""
        self.logger.log_info("Stopping NoetherBot...", LogTag.INFO)

        self._running = False

        # Stop monitoring
        await self.swap_monitor.stop_monitoring()

        # Disconnect from exchange
        await self.exchange.disconnect()

        # Log final stats
        stats = self.strategy_engine.get_strategy_stats()
        self.logger.log_info(f"Final stats: {stats}", LogTag.INFO)

        self.logger.log_info("NoetherBot stopped", LogTag.INFO)

    def handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.log_info(f"Received signal {signum}, shutting down...", LogTag.INFO)
        asyncio.create_task(self.stop())
        sys.exit(0)


async def main():
    """Main function."""
    bot = NoetherBot()

    # Set up signal handlers
    signal.signal(signal.SIGINT, bot.handle_signal)
    signal.signal(signal.SIGTERM, bot.handle_signal)

    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.stop()
    except Exception as e:
        print(f"Fatal error: {e}")
        await bot.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
