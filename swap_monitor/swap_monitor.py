"""RPC-based swap monitor for on-chain reserve polling."""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth

from models import PositionSnapshot
from exchange_manager import IExchange
from database_manager import DatabaseManager
from logger_manager import LoggerManager, LogTag
from euler_swap import EulerPoolManager


class SwapMonitor:
    """
    Monitors on-chain swap pool reserves and off-chain positions.

    Periodically polls the EulerSwap pool contract for reserve data
    and combines it with exchange position data to create snapshots.
    """

    def __init__(
        self,
        rpc_url: str,
        pool_address: str,
        abi_path: str,
        exchange: IExchange,
        symbol_perpetual: str = "ETH/USDT:USDT",
        database_manager: Optional[DatabaseManager] = None,
    ):
        """
        Initialize the swap monitor.

        Args:
            rpc_url: Ethereum RPC endpoint URL
            pool_address: EulerSwap pool contract address
            abi_path: Path to pool contract ABI
            exchange: Exchange instance for position data
            symbol_perpetual: Perpetual trading symbol
            database_manager: Optional database manager for persistence
        """
        self.rpc_url = rpc_url
        self.pool_address = Web3.to_checksum_address(pool_address)
        self.abi_path = abi_path
        self.exchange = exchange
        self.symbol_perpetual = symbol_perpetual
        self.database_manager = database_manager
        self.logger = LoggerManager()

        # Web3 setup
        self.w3 = Web3(AsyncHTTPProvider(rpc_url))
        self.w3.eth = AsyncEth(self.w3)

        # Load contract ABI
        self.contract_abi = self._load_abi()
        self.contract = self.w3.eth.contract(
            address=self.pool_address, abi=self.contract_abi
        )

        # Monitoring state
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._snapshot_callback: Optional[Callable] = None
        self._last_snapshot: Optional[PositionSnapshot] = None

        # EulerSwap pool manager
        self.pool_manager = EulerPoolManager(self.w3, self.pool_address, self.contract)

    def _load_abi(self) -> list:
        """
        Load contract ABI from file.

        Returns:
            Contract ABI as list
        """
        abi_path = Path(self.abi_path)

        if not abi_path.exists():
            # Create default ABI if not exists
            default_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getReserves",
                    "outputs": [
                        {"name": "reserve0", "type": "uint112"},
                        {"name": "reserve1", "type": "uint112"},
                        {"name": "blockTimestampLast", "type": "uint32"},
                    ],
                    "payable": False,
                    "stateMutability": "view",
                    "type": "function",
                }
            ]
            abi_path.parent.mkdir(parents=True, exist_ok=True)
            with open(abi_path, "w") as f:
                json.dump(default_abi, f, indent=2)
            return default_abi

        with open(abi_path, "r") as f:
            return json.load(f)

    async def fetch_reserves(self) -> tuple[Decimal, Decimal, int]:
        """
        Fetch current reserves from the pool contract.

        Returns:
            Tuple of (reserve0, reserve1, status)
        """
        try:
            # Call getReserves function - returns (reserve0, reserve1, status)
            reserves = await self.contract.functions.getReserves().call()

            # EulerSwap reserves are already in uint112 format
            # Check decimals for each token - USDT typically has 6, WETH has 18
            # For now assume USDT (6 decimals) and WETH (18 decimals)
            reserve0 = Decimal(reserves[0]) / Decimal(10**6)  # USDT with 6 decimals
            reserve1 = Decimal(reserves[1]) / Decimal(10**18)  # WETH with 18 decimals
            status = reserves[2]  # Pool status: 0=unactivated, 1=unlocked, 2=locked

            # Check if pool is active and unlocked
            if status == 0:
                self.logger.log_warning("Pool is not activated")
            elif status == 2:
                self.logger.log_warning("Pool is locked (reentrancy)")

            self.logger.log_debug(
                f"Fetched reserves: USDT={reserve0}, WETH={reserve1}, Status={status}",
                LogTag.RPC,
            )

            return reserve0, reserve1, status

        except Exception as e:
            self.logger.log_error("Failed to fetch reserves", e)
            raise

    async def fetch_short_position(self) -> Decimal:
        """
        Fetch current short position from exchange.

        Returns:
            Current short position size
        """
        try:
            position = await self.exchange.get_current_perpetual_position(
                self.symbol_perpetual
            )

            # Get short position size (negative for shorts)
            if position["side"] == "short":
                return position["size"]

            return Decimal("0")

        except Exception as e:
            self.logger.log_error("Failed to fetch short position", e)
            return Decimal("0")

    async def fetch_snapshot(self) -> PositionSnapshot:
        """
        Fetch a complete position snapshot.

        Returns:
            PositionSnapshot with current data
        """
        try:
            # Get on-chain reserves
            reserve0, reserve1, block_timestamp = await self.fetch_reserves()

            # Get current block number
            block_number = await self.w3.eth.block_number

            # Get off-chain position
            short_position = await self.fetch_short_position()

            # Create snapshot
            snapshot = PositionSnapshot(
                reserve_token0=reserve0,
                reserve_token1=reserve1,
                short_position_size=short_position,
                timestamp=datetime.utcnow(),
                block_number=block_number,
                pool_address=self.pool_address,
            )

            # Save to database if available
            if self.database_manager:
                self.database_manager.save_position_snapshot(snapshot)

            # Log snapshot
            self.logger.log_position_polling(
                {
                    "reserve_token0": str(reserve0),
                    "reserve_token1": str(reserve1),
                    "short_position_size": str(short_position),
                    "delta": str(snapshot.delta),
                }
            )

            # Update last snapshot
            self._last_snapshot = snapshot

            # Trigger callback if set
            if self._snapshot_callback:
                await self._snapshot_callback(snapshot)

            return snapshot

        except Exception as e:
            self.logger.log_error("Failed to fetch snapshot", e)
            raise

    async def start_monitoring(
        self, polling_interval: int = 5, callback: Optional[Callable] = None
    ) -> None:
        """
        Start monitoring pool reserves.

        Args:
            polling_interval: Seconds between polls
            callback: Optional callback for new snapshots
        """
        if self._monitoring:
            self.logger.log_warning("Monitoring already started")
            return

        self._monitoring = True
        self._snapshot_callback = callback

        self.logger.log_info("Starting swap monitoring", LogTag.RPC)

        # Start monitoring task
        self._monitor_task = asyncio.create_task(self._monitor_loop(polling_interval))

    async def stop_monitoring(self) -> None:
        """Stop monitoring pool reserves."""
        if not self._monitoring:
            return

        self._monitoring = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        self.logger.log_info("Stopped swap monitoring", LogTag.RPC)

    async def _monitor_loop(self, polling_interval: int) -> None:
        """
        Main monitoring loop.

        Args:
            polling_interval: Seconds between polls
        """
        while self._monitoring:
            try:
                # Fetch snapshot
                await self.fetch_snapshot()

                # Wait for next poll
                await asyncio.sleep(polling_interval)

            except Exception as e:
                self.logger.log_error("Error in monitoring loop", e)

                # Wait before retrying
                await asyncio.sleep(polling_interval)

    def set_snapshot_callback(self, callback: Callable) -> None:
        """
        Set callback for new snapshots.

        Args:
            callback: Function to call with new snapshots
        """
        self._snapshot_callback = callback

    def get_last_snapshot(self) -> Optional[PositionSnapshot]:
        """
        Get the last fetched snapshot.

        Returns:
            Last PositionSnapshot or None
        """
        return self._last_snapshot

    async def get_historical_snapshots(
        self, hours: int = 24, limit: int = 100
    ) -> list[PositionSnapshot]:
        """
        Get historical snapshots from database.

        Args:
            hours: Number of hours to look back
            limit: Maximum number of snapshots

        Returns:
            List of historical snapshots
        """
        if not self.database_manager:
            return []

        start_time = datetime.utcnow() - timedelta(hours=hours)
        return self.database_manager.get_position_snapshots(
            start_time=start_time, limit=limit
        )

    async def check_connection(self) -> bool:
        """
        Check if RPC and exchange connections are working.

        Returns:
            True if connections are healthy
        """
        try:
            # Check RPC connection
            await self.w3.eth.block_number

            # Check exchange connection
            await self.exchange.get_balance()

            return True

        except Exception as e:
            self.logger.log_error("Connection check failed", e)
            return False
