"""EulerSwap pool parameters model."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class PoolParams:
    """
    EulerSwap pool parameters matching the IEulerSwap.Params struct.

    These parameters define the curve shape and behavior of the pool.
    """

    # Entities
    vault0: str  # Address of vault for token0
    vault1: str  # Address of vault for token1
    euler_account: str  # Address of the Euler account

    # Curve parameters
    equilibrium_reserve0: Decimal  # Equilibrium reserve for token0
    equilibrium_reserve1: Decimal  # Equilibrium reserve for token1
    price_x: Decimal  # Price parameter X (1 <= px <= 1e25)
    price_y: Decimal  # Price parameter Y (1 <= py <= 1e25)
    concentration_x: Decimal  # Concentration factor X (0 <= c <= 1e18)
    concentration_y: Decimal  # Concentration factor Y (0 <= c <= 1e18)

    # Fee parameters
    fee: Decimal  # Swap fee (< 1e18)
    protocol_fee: Decimal  # Protocol fee portion
    protocol_fee_recipient: str  # Address to receive protocol fees

    # Additional tracking
    token0_address: Optional[str] = None  # Underlying asset0 address
    token1_address: Optional[str] = None  # Underlying asset1 address
    token0_decimals: int = 18  # Decimals for token0
    token1_decimals: int = 18  # Decimals for token1

    @property
    def equilibrium_price(self) -> Decimal:
        """Calculate the price at equilibrium point."""
        return self.price_x / self.price_y

    @property
    def is_concentrated(self) -> bool:
        """Check if the pool uses concentrated liquidity."""
        return self.concentration_x > Decimal("0") or self.concentration_y > Decimal(
            "0"
        )

    @property
    def max_swap_size_token0(self) -> Decimal:
        """Maximum theoretical swap size for token0."""
        return self.equilibrium_reserve0

    @property
    def max_swap_size_token1(self) -> Decimal:
        """Maximum theoretical swap size for token1."""
        return self.equilibrium_reserve1

    def to_dict(self) -> dict:
        """Convert parameters to dictionary."""
        return {
            "vault0": self.vault0,
            "vault1": self.vault1,
            "euler_account": self.euler_account,
            "equilibrium_reserve0": str(self.equilibrium_reserve0),
            "equilibrium_reserve1": str(self.equilibrium_reserve1),
            "price_x": str(self.price_x),
            "price_y": str(self.price_y),
            "concentration_x": str(self.concentration_x),
            "concentration_y": str(self.concentration_y),
            "fee": str(self.fee),
            "protocol_fee": str(self.protocol_fee),
            "protocol_fee_recipient": self.protocol_fee_recipient,
            "token0_address": self.token0_address,
            "token1_address": self.token1_address,
            "token0_decimals": self.token0_decimals,
            "token1_decimals": self.token1_decimals,
            "equilibrium_price": str(self.equilibrium_price),
            "is_concentrated": self.is_concentrated,
        }

    @classmethod
    def from_contract(
        cls, params_tuple: tuple, token0_addr: str = None, token1_addr: str = None
    ) -> "PoolParams":
        """
        Create PoolParams from contract getParams() response.

        Args:
            params_tuple: Tuple from getParams() call
            token0_addr: Optional token0 address
            token1_addr: Optional token1 address

        Returns:
            PoolParams instance
        """
        return cls(
            vault0=params_tuple[0],
            vault1=params_tuple[1],
            euler_account=params_tuple[2],
            equilibrium_reserve0=Decimal(params_tuple[3]),
            equilibrium_reserve1=Decimal(params_tuple[4]),
            price_x=Decimal(params_tuple[5]),
            price_y=Decimal(params_tuple[6]),
            concentration_x=Decimal(params_tuple[7]),
            concentration_y=Decimal(params_tuple[8]),
            fee=Decimal(params_tuple[9]) / Decimal(10**18),  # Convert to percentage
            protocol_fee=Decimal(params_tuple[10]) / Decimal(10**18),
            protocol_fee_recipient=params_tuple[11],
            token0_address=token0_addr,
            token1_address=token1_addr,
        )
