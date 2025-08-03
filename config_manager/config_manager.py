"""Configuration manager for centralized config handling."""

import os
import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


@dataclass
class Config:
    """
    Configuration data class containing all bot settings.
    """

    # RPC Configuration
    rpc_url: str
    eulerswap_pool: str

    # Exchange Configuration
    binance_api_key: str
    binance_api_secret: str
    binance_testnet: bool = False

    # Hedge Strategy Configuration
    min_hedge_size_eth: Decimal = Decimal("0.005")
    hedge_threshold_eth: Decimal = Decimal("0.01")
    max_slippage_percent: Decimal = Decimal("0.5")
    default_leverage: Decimal = Decimal("1")

    # Monitoring Configuration
    polling_interval_seconds: int = 5
    max_retries: int = 3
    retry_delay_seconds: int = 2

    # Database Configuration
    database_url: str = "sqlite:///lphedgebot.db"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "lphedgebot.log"

    # Trading Configuration
    symbol_perpetual: str = "ETH/USDT:USDT"

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "rpc_url": self.rpc_url,
            "eulerswap_pool": self.eulerswap_pool,
            "binance_testnet": self.binance_testnet,
            "min_hedge_size_eth": str(self.min_hedge_size_eth),
            "hedge_threshold_eth": str(self.hedge_threshold_eth),
            "max_slippage_percent": str(self.max_slippage_percent),
            "default_leverage": str(self.default_leverage),
            "polling_interval_seconds": self.polling_interval_seconds,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "database_url": self.database_url,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "symbol_perpetual": self.symbol_perpetual,
        }


class ConfigManager:
    """
    Manages configuration loading and access.

    Loads configuration from environment variables and provides
    a centralized interface for accessing config values.
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            env_file: Path to .env file (optional)
        """
        self.logger = logging.getLogger(__name__)
        self._config: Optional[Config] = None
        self._exchange_instance = None

        # Load environment variables
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Load configuration
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from environment variables."""
        try:
            self._config = Config(
                # Required configurations
                rpc_url=self._get_required_env("RPC_URL"),
                eulerswap_pool=self._get_required_env("EULERSWAP_POOL"),
                binance_api_key=self._get_required_env("BINANCE_API_KEY"),
                binance_api_secret=self._get_required_env("BINANCE_API_SECRET"),
                # Optional configurations with defaults
                binance_testnet=self._get_bool_env("BINANCE_TESTNET", False),
                min_hedge_size_eth=Decimal(os.getenv("MIN_HEDGE_SIZE_ETH", "0.005")),
                hedge_threshold_eth=Decimal(os.getenv("HEDGE_THRESHOLD_ETH", "0.01")),
                max_slippage_percent=Decimal(os.getenv("MAX_SLIPPAGE_PERCENT", "0.5")),
                default_leverage=Decimal(os.getenv("DEFAULT_LEVERAGE", "1")),
                polling_interval_seconds=int(
                    os.getenv("POLLING_INTERVAL_SECONDS", "5")
                ),
                max_retries=int(os.getenv("MAX_RETRIES", "3")),
                retry_delay_seconds=int(os.getenv("RETRY_DELAY_SECONDS", "2")),
                database_url=os.getenv("DATABASE_URL", "sqlite:///lphedgebot.db"),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                log_file=os.getenv("LOG_FILE", "lphedgebot.log"),
            )

            self.logger.info("Configuration loaded successfully")
            self._validate_config()

        except KeyError as e:
            self.logger.error(f"Missing required configuration: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise

    def _get_required_env(self, key: str) -> str:
        """
        Get a required environment variable.

        Args:
            key: Environment variable key

        Returns:
            Environment variable value

        Raises:
            KeyError: If environment variable is not set
        """
        value = os.getenv(key)
        if value is None:
            raise KeyError(f"Required environment variable {key} is not set")
        return value

    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean environment variable.

        Args:
            key: Environment variable key
            default: Default value if not set

        Returns:
            Boolean value
        """
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def _validate_config(self) -> None:
        """Validate configuration values."""
        if not self._config:
            raise ValueError("Configuration not loaded")

        # Validate Ethereum address format
        if not self._config.eulerswap_pool.startswith("0x"):
            raise ValueError("Invalid EulerSwap pool address format")

        if len(self._config.eulerswap_pool) != 42:
            raise ValueError("Invalid EulerSwap pool address length")

        # Validate numeric ranges
        if self._config.min_hedge_size_eth <= 0:
            raise ValueError("Minimum hedge size must be positive")

        if self._config.hedge_threshold_eth <= 0:
            raise ValueError("Hedge threshold must be positive")

        if (
            self._config.max_slippage_percent < 0
            or self._config.max_slippage_percent > 100
        ):
            raise ValueError("Max slippage must be between 0 and 100")

        if self._config.default_leverage < 1 or self._config.default_leverage > 100:
            raise ValueError("Leverage must be between 1 and 100")

        if self._config.polling_interval_seconds < 1:
            raise ValueError("Polling interval must be at least 1 second")

        self.logger.info("Configuration validation passed")

    @property
    def config(self) -> Config:
        """
        Get the current configuration.

        Returns:
            Config object

        Raises:
            RuntimeError: If configuration is not loaded
        """
        if not self._config:
            raise RuntimeError("Configuration not loaded")
        return self._config

    def get_exchange(self):
        """
        Get or create exchange instance.

        Returns:
            Exchange instance (BinanceExchange)
        """
        if not self._exchange_instance:
            from exchange_manager import BinanceExchange

            self._exchange_instance = BinanceExchange(
                api_key=self.config.binance_api_key,
                api_secret=self.config.binance_api_secret,
                testnet=self.config.binance_testnet,
            )
        return self._exchange_instance

    def get_abi_path(self) -> str:
        """
        Get the path to the pool ABI file.

        Returns:
            Path to ABI file
        """
        abi_path = Path(__file__).parent.parent / "abi" / "eulerswap_pool.json"
        if not abi_path.exists():
            # Try to create a default ABI if it doesn't exist
            abi_path.parent.mkdir(parents=True, exist_ok=True)
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
            with open(abi_path, "w") as f:
                json.dump(default_abi, f, indent=2)

        return str(abi_path)

    def update_config(self, **kwargs) -> None:
        """
        Update configuration values at runtime.

        Args:
            **kwargs: Configuration values to update
        """
        if not self._config:
            raise RuntimeError("Configuration not loaded")

        for key, value in kwargs.items():
            if hasattr(self._config, key):
                # Convert to appropriate type
                if key in [
                    "min_hedge_size_eth",
                    "hedge_threshold_eth",
                    "max_slippage_percent",
                    "default_leverage",
                ]:
                    value = Decimal(str(value))
                elif key in [
                    "polling_interval_seconds",
                    "max_retries",
                    "retry_delay_seconds",
                ]:
                    value = int(value)
                elif key == "binance_testnet":
                    value = bool(value)

                setattr(self._config, key, value)
                self.logger.info(f"Updated config: {key} = {value}")
            else:
                self.logger.warning(f"Unknown config key: {key}")

        # Revalidate after updates
        self._validate_config()

    def save_config(self, filepath: str) -> None:
        """
        Save current configuration to a JSON file.

        Args:
            filepath: Path to save configuration file
        """
        if not self._config:
            raise RuntimeError("Configuration not loaded")

        config_dict = self.config.to_dict()

        with open(filepath, "w") as f:
            json.dump(config_dict, f, indent=2)

        self.logger.info(f"Configuration saved to {filepath}")

    def load_config_from_file(self, filepath: str) -> None:
        """
        Load configuration from a JSON file.

        Args:
            filepath: Path to configuration file
        """
        with open(filepath, "r") as f:
            config_dict = json.load(f)

        self.update_config(**config_dict)
        self.logger.info(f"Configuration loaded from {filepath}")
