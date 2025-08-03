"""Manager for EulerSwap pool interactions."""

import asyncio
from decimal import Decimal
from typing import Optional, Tuple
from web3 import Web3

from logger_manager import LoggerManager, LogTag
from .pool_params import PoolParams


class EulerPoolManager:
    """
    Manages interactions with EulerSwap pools.

    Handles pool parameter fetching, quote calculations, and limit checks.
    """

    def __init__(self, w3: Web3, pool_address: str, contract):
        """
        Initialize the EulerPoolManager.

        Args:
            w3: Web3 instance
            pool_address: Address of the EulerSwap pool
            contract: Pool contract instance
        """
        self.w3 = w3
        self.pool_address = pool_address
        self.contract = contract
        self.logger = LoggerManager()
        self._pool_params: Optional[PoolParams] = None
        self._assets: Optional[Tuple[str, str]] = None

    async def fetch_pool_params(self) -> PoolParams:
        """
        Fetch and cache pool parameters.

        Returns:
            PoolParams instance with current pool configuration
        """
        try:
            # Get pool parameters
            params = await self.contract.functions.getParams().call()

            # Get underlying assets
            assets = await self.contract.functions.getAssets().call()

            # Create PoolParams instance
            self._pool_params = PoolParams.from_contract(
                params, token0_addr=assets[0], token1_addr=assets[1]
            )

            self._assets = (assets[0], assets[1])

            # Determine token decimals based on common tokens
            # USDT/USDC typically have 6 decimals, WETH has 18
            if "USDT" in assets[0].upper() or "USDC" in assets[0].upper():
                self._pool_params.token0_decimals = 6
            if "USDT" in assets[1].upper() or "USDC" in assets[1].upper():
                self._pool_params.token1_decimals = 6

            self.logger.log_info(
                f"Fetched pool params - Equilibrium: {self._pool_params.equilibrium_reserve0}/{self._pool_params.equilibrium_reserve1}, "
                f"Price: {self._pool_params.equilibrium_price:.4f}, Fee: {self._pool_params.fee * 100:.2f}%",
                LogTag.RPC,
            )

            return self._pool_params

        except Exception as e:
            self.logger.log_error("Failed to fetch pool parameters", e)
            raise

    async def get_quote(
        self, amount_in: Decimal, token_in_is_token0: bool = True, exact_in: bool = True
    ) -> Decimal:
        """
        Get a quote for a swap.

        Args:
            amount_in: Amount to swap
            token_in_is_token0: True if swapping token0 for token1
            exact_in: True for exact input, False for exact output

        Returns:
            Quote amount out
        """
        try:
            if not self._pool_params or not self._assets:
                await self.fetch_pool_params()

            token_in = self._assets[0] if token_in_is_token0 else self._assets[1]
            token_out = self._assets[1] if token_in_is_token0 else self._assets[0]

            # Scale amount based on decimals
            decimals_in = (
                self._pool_params.token0_decimals
                if token_in_is_token0
                else self._pool_params.token1_decimals
            )
            amount_scaled = int(amount_in * Decimal(10**decimals_in))

            # Get quote from contract
            quote = await self.contract.functions.computeQuote(
                token_in, token_out, amount_scaled, exact_in
            ).call()

            # Scale output based on decimals
            decimals_out = (
                self._pool_params.token1_decimals
                if token_in_is_token0
                else self._pool_params.token0_decimals
            )
            quote_decimal = Decimal(quote) / Decimal(10**decimals_out)

            self.logger.log_debug(
                f"Quote: {amount_in} -> {quote_decimal} (exact_in={exact_in})",
                LogTag.RPC,
            )

            return quote_decimal

        except Exception as e:
            self.logger.log_error(f"Failed to get quote", e)
            return Decimal("0")

    async def get_swap_limits(
        self, token_in_is_token0: bool = True
    ) -> Tuple[Decimal, Decimal]:
        """
        Get current swap limits for a token pair.

        Args:
            token_in_is_token0: True if checking limits for token0->token1 swap

        Returns:
            Tuple of (max_input, max_output) considering all constraints
        """
        try:
            if not self._assets:
                await self.fetch_pool_params()

            token_in = self._assets[0] if token_in_is_token0 else self._assets[1]
            token_out = self._assets[1] if token_in_is_token0 else self._assets[0]

            # Get limits from contract
            limits = await self.contract.functions.getLimits(token_in, token_out).call()

            # Scale based on decimals
            decimals_in = (
                self._pool_params.token0_decimals
                if token_in_is_token0
                else self._pool_params.token1_decimals
            )
            decimals_out = (
                self._pool_params.token1_decimals
                if token_in_is_token0
                else self._pool_params.token0_decimals
            )

            limit_in = Decimal(limits[0]) / Decimal(10**decimals_in)
            limit_out = Decimal(limits[1]) / Decimal(10**decimals_out)

            self.logger.log_debug(
                f"Swap limits: max_in={limit_in}, max_out={limit_out}", LogTag.RPC
            )

            return limit_in, limit_out

        except Exception as e:
            self.logger.log_error("Failed to get swap limits", e)
            return Decimal("0"), Decimal("0")

    def calculate_price_impact(
        self, amount_in: Decimal, amount_out: Decimal, token_in_is_token0: bool = True
    ) -> Decimal:
        """
        Calculate price impact of a swap.

        Args:
            amount_in: Input amount
            amount_out: Output amount
            token_in_is_token0: Direction of swap

        Returns:
            Price impact as a percentage (0-100)
        """
        if not self._pool_params or amount_in == 0:
            return Decimal("0")

        # Calculate actual price
        actual_price = amount_out / amount_in

        # Get equilibrium price (adjusted for direction)
        equilibrium_price = self._pool_params.equilibrium_price
        if not token_in_is_token0:
            equilibrium_price = Decimal("1") / equilibrium_price

        # Calculate impact
        if equilibrium_price > 0:
            price_impact = (
                abs((actual_price - equilibrium_price) / equilibrium_price) * 100
            )
        else:
            price_impact = Decimal("100")

        return price_impact

    def is_reserve_desynchronized(
        self,
        current_reserves: Tuple[Decimal, Decimal],
        threshold_percent: Decimal = Decimal("5"),
    ) -> bool:
        """
        Check if reserves are desynchronized from equilibrium.

        Args:
            current_reserves: Current (reserve0, reserve1)
            threshold_percent: Threshold for desynchronization warning

        Returns:
            True if reserves are significantly desynchronized
        """
        if not self._pool_params:
            return False

        # Calculate deviation from equilibrium
        deviation0 = abs(current_reserves[0] - self._pool_params.equilibrium_reserve0)
        deviation1 = abs(current_reserves[1] - self._pool_params.equilibrium_reserve1)

        # Calculate percentage deviation
        if self._pool_params.equilibrium_reserve0 > 0:
            percent0 = (deviation0 / self._pool_params.equilibrium_reserve0) * 100
        else:
            percent0 = Decimal("0")

        if self._pool_params.equilibrium_reserve1 > 0:
            percent1 = (deviation1 / self._pool_params.equilibrium_reserve1) * 100
        else:
            percent1 = Decimal("0")

        # Check if either deviation exceeds threshold
        if percent0 > threshold_percent or percent1 > threshold_percent:
            self.logger.log_warning(
                f"Reserves desynchronized - Token0: {percent0:.2f}%, Token1: {percent1:.2f}%"
            )
            return True

        return False

    def get_pool_info(self) -> dict:
        """
        Get comprehensive pool information.

        Returns:
            Dictionary with pool details
        """
        if not self._pool_params:
            return {"pool_address": self.pool_address, "status": "Not initialized"}

        return {
            "pool_address": self.pool_address,
            "token0": self._pool_params.token0_address,
            "token1": self._pool_params.token1_address,
            "equilibrium_reserves": {
                "token0": str(self._pool_params.equilibrium_reserve0),
                "token1": str(self._pool_params.equilibrium_reserve1),
            },
            "equilibrium_price": str(self._pool_params.equilibrium_price),
            "concentration": {
                "x": str(self._pool_params.concentration_x),
                "y": str(self._pool_params.concentration_y),
            },
            "fees": {
                "swap_fee": f"{self._pool_params.fee * 100:.2f}%",
                "protocol_fee": f"{self._pool_params.protocol_fee * 100:.4f}%",
            },
            "vaults": {
                "vault0": self._pool_params.vault0,
                "vault1": self._pool_params.vault1,
            },
        }
