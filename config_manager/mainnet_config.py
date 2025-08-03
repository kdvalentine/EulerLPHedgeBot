"""Mainnet-specific configuration for NoetherBot."""

import json
import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Optional

from config_manager import Config


@dataclass
class MainnetConfig(Config):
    """
    Extended configuration for Ethereum mainnet with EulerSwap specifics.
    """

    # Euler Vault Configuration
    euler_vault_usdt: str = "0x313603FA690301b0CaeEf8069c065862f9162162"
    euler_vault_weth: str = "0xD8b27CF359b7D15710a5BE299AF6e7Bf904984C2"

    # Token Addresses
    usdt_address: str = "0xdac17f958d2ee523a2206206994597c13d831ec7"
    weth_address: str = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"

    # Token Decimals
    usdt_decimals: int = 6
    weth_decimals: int = 18

    # Network Configuration
    chain_id: int = 1
    block_time_seconds: int = 12

    # Pool-specific Configuration
    equilibrium_reserve0: Decimal = Decimal("1000000")  # USDT
    equilibrium_reserve1: Decimal = Decimal("500")  # WETH
    equilibrium_price: Decimal = Decimal("2000")  # USDT per WETH

    # Risk Parameters
    desync_warning_percent: Decimal = Decimal("5")
    max_position_size_eth: Decimal = Decimal("100")
    min_balance_usdt: Decimal = Decimal("1000")
    emergency_stop_loss_usdt: Decimal = Decimal("10000")

    # Gas Configuration
    max_gas_price_gwei: Decimal = Decimal("100")
    gas_limit_multiplier: Decimal = Decimal("1.2")

    # Funding Rate Configuration
    max_funding_rate_percent: Decimal = Decimal("0.05")
    funding_rate_check_interval: int = 28800  # 8 hours

    @classmethod
    def from_env(cls, env_file: Optional[str] = ".env.mainnet") -> "MainnetConfig":
        """
        Load mainnet configuration from environment file.

        Args:
            env_file: Path to environment file

        Returns:
            MainnetConfig instance
        """
        from dotenv import load_dotenv

        if env_file and Path(env_file).exists():
            load_dotenv(env_file)

        return cls(
            # Required base configs
            rpc_url=os.getenv("RPC_URL", ""),
            eulerswap_pool=os.getenv(
                "EULERSWAP_POOL", "0x55dcf9455eee8fd3f5eed17606291272cde428a8"
            ),
            binance_api_key=os.getenv("BINANCE_API_KEY", ""),
            binance_api_secret=os.getenv("BINANCE_API_SECRET", ""),
            # Euler Vaults
            euler_vault_usdt=os.getenv(
                "EULER_VAULT_USDT", "0x313603FA690301b0CaeEf8069c065862f9162162"
            ),
            euler_vault_weth=os.getenv(
                "EULER_VAULT_WETH", "0xD8b27CF359b7D15710a5BE299AF6e7Bf904984C2"
            ),
            # Token Addresses
            usdt_address=os.getenv(
                "USDT_ADDRESS", "0xdac17f958d2ee523a2206206994597c13d831ec7"
            ),
            weth_address=os.getenv(
                "WETH_ADDRESS", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
            ),
            # Decimals
            usdt_decimals=int(os.getenv("USDT_DECIMALS", "6")),
            weth_decimals=int(os.getenv("WETH_DECIMALS", "18")),
            # Network
            chain_id=int(os.getenv("CHAIN_ID", "1")),
            block_time_seconds=int(os.getenv("BLOCK_TIME_SECONDS", "12")),
            # Hedge Strategy
            min_hedge_size_eth=Decimal(os.getenv("MIN_HEDGE_SIZE_ETH", "0.005")),
            hedge_threshold_eth=Decimal(os.getenv("HEDGE_THRESHOLD_ETH", "0.01")),
            max_slippage_percent=Decimal(os.getenv("MAX_SLIPPAGE_PERCENT", "1.0")),
            default_leverage=Decimal(os.getenv("DEFAULT_LEVERAGE", "1")),
            # Risk Parameters
            desync_warning_percent=Decimal(os.getenv("DESYNC_WARNING_PERCENT", "5")),
            max_position_size_eth=Decimal(os.getenv("MAX_POSITION_SIZE_ETH", "100")),
            min_balance_usdt=Decimal(os.getenv("MIN_BALANCE_USDT", "1000")),
            emergency_stop_loss_usdt=Decimal(
                os.getenv("EMERGENCY_STOP_LOSS_USDT", "10000")
            ),
            # Gas
            max_gas_price_gwei=Decimal(os.getenv("MAX_GAS_PRICE_GWEI", "100")),
            # Monitoring
            polling_interval_seconds=int(os.getenv("POLLING_INTERVAL_SECONDS", "5")),
            # Database
            database_url=os.getenv("DATABASE_URL", "sqlite:///noether_bot_mainnet.db"),
            # Logging
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "noether_bot_mainnet.log"),
        )

    @classmethod
    def from_json(
        cls, json_file: str = "config/mainnet_config.json"
    ) -> "MainnetConfig":
        """
        Load mainnet configuration from JSON file.

        Args:
            json_file: Path to JSON configuration file

        Returns:
            MainnetConfig instance
        """
        with open(json_file, "r") as f:
            data = json.load(f)

        pool = data["pools"][0]  # First pool configuration
        risk = data["risk_params"]

        return cls(
            # Network
            rpc_url=data["network"]["rpc_url"],
            chain_id=data["network"]["chain_id"],
            block_time_seconds=data["network"]["block_time"],
            # Pool
            eulerswap_pool=pool["address"],
            euler_vault_usdt=pool["token0"]["vault"],
            euler_vault_weth=pool["token1"]["vault"],
            usdt_address=pool["token0"]["address"],
            weth_address=pool["token1"]["address"],
            usdt_decimals=pool["token0"]["decimals"],
            weth_decimals=pool["token1"]["decimals"],
            # Strategy
            min_hedge_size_eth=Decimal(str(risk["hedge"]["min_hedge_size_eth"])),
            hedge_threshold_eth=Decimal(str(risk["hedge"]["hedge_threshold_eth"])),
            max_delta_exposure_eth=Decimal(
                str(risk["hedge"]["max_delta_exposure_eth"])
            ),
            # Risk
            max_position_size_eth=Decimal(
                str(risk["position"]["max_position_size_eth"])
            ),
            min_balance_usdt=Decimal(str(risk["position"]["min_balance_usdt"])),
            desync_warning_percent=Decimal(str(risk["desync"]["warning_percent"])),
            # Slippage
            max_slippage_percent=Decimal(str(risk["slippage"]["max_slippage_percent"])),
            # Gas
            max_gas_price_gwei=Decimal(str(data["gas"]["max_price_gwei"])),
            # Emergency
            emergency_stop_loss_usdt=Decimal(str(data["emergency"]["stop_loss_usdt"])),
            # API credentials (must come from env)
            binance_api_key=os.getenv("BINANCE_API_KEY", ""),
            binance_api_secret=os.getenv("BINANCE_API_SECRET", ""),
        )

    def validate_mainnet_config(self) -> bool:
        """
        Validate mainnet-specific configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate addresses
        if not self.eulerswap_pool == "0x55dcf9455eee8fd3f5eed17606291272cde428a8":
            raise ValueError(f"Invalid pool address: {self.eulerswap_pool}")

        if (
            not self.usdt_address.lower()
            == "0xdac17f958d2ee523a2206206994597c13d831ec7"
        ):
            raise ValueError(f"Invalid USDT address: {self.usdt_address}")

        if (
            not self.weth_address.lower()
            == "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        ):
            raise ValueError(f"Invalid WETH address: {self.weth_address}")

        # Validate decimals
        if self.usdt_decimals != 6:
            raise ValueError(f"USDT should have 6 decimals, got {self.usdt_decimals}")

        if self.weth_decimals != 18:
            raise ValueError(f"WETH should have 18 decimals, got {self.weth_decimals}")

        # Validate network
        if self.chain_id != 1:
            raise ValueError(f"Expected mainnet chain ID 1, got {self.chain_id}")

        return True

    def get_pool_info(self) -> Dict[str, Any]:
        """
        Get formatted pool information.

        Returns:
            Dictionary with pool details
        """
        return {
            "network": "Ethereum Mainnet",
            "chain_id": self.chain_id,
            "pool": {
                "address": self.eulerswap_pool,
                "token0": {
                    "symbol": "USDT",
                    "address": self.usdt_address,
                    "decimals": self.usdt_decimals,
                    "vault": self.euler_vault_usdt,
                },
                "token1": {
                    "symbol": "WETH",
                    "address": self.weth_address,
                    "decimals": self.weth_decimals,
                    "vault": self.euler_vault_weth,
                },
                "equilibrium": {
                    "reserve0": str(self.equilibrium_reserve0),
                    "reserve1": str(self.equilibrium_reserve1),
                    "price": str(self.equilibrium_price),
                },
            },
            "risk_params": {
                "min_hedge_size": f"{self.min_hedge_size_eth} ETH",
                "hedge_threshold": f"{self.hedge_threshold_eth} ETH",
                "max_delta": f"{self.max_delta_exposure_eth} ETH",
                "desync_warning": f"{self.desync_warning_percent}%",
                "max_position": f"{self.max_position_size_eth} ETH",
                "stop_loss": f"{self.emergency_stop_loss_usdt} USDT",
            },
            "monitoring": {
                "polling_interval": f"{self.polling_interval_seconds}s",
                "block_time": f"{self.block_time_seconds}s",
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "euler_vault_usdt": self.euler_vault_usdt,
                "euler_vault_weth": self.euler_vault_weth,
                "usdt_address": self.usdt_address,
                "weth_address": self.weth_address,
                "usdt_decimals": self.usdt_decimals,
                "weth_decimals": self.weth_decimals,
                "chain_id": self.chain_id,
                "block_time_seconds": self.block_time_seconds,
                "desync_warning_percent": str(self.desync_warning_percent),
                "max_position_size_eth": str(self.max_position_size_eth),
                "min_balance_usdt": str(self.min_balance_usdt),
                "emergency_stop_loss_usdt": str(self.emergency_stop_loss_usdt),
                "max_gas_price_gwei": str(self.max_gas_price_gwei),
            }
        )
        return base_dict
