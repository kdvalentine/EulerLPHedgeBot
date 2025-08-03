"""Logger manager for centralized logging with TUI support."""

import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Callable
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text


class LogTag(Enum):
    """Log tags for categorizing log entries."""

    POSITION_POLLING = "POSITION_POLLING"
    CALCULATED_HEDGE = "CALCULATED_HEDGE"
    LEVERAGE = "LEVERAGE"
    OPEN_SHORT_POSITION = "OPEN_SHORT_POSITION"
    CLOSE_SHORT_POSITION = "CLOSE_SHORT_POSITION"
    ADJUST_SHORT_POSITION = "ADJUST_SHORT_POSITION"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    TRADE_EXECUTED = "TRADE_EXECUTED"
    STRATEGY = "STRATEGY"
    RISK = "RISK"
    DATABASE = "DATABASE"
    EXCHANGE = "EXCHANGE"
    RPC = "RPC"
    TUI = "TUI"


@dataclass
class LogEntry:
    """
    Represents a single log entry.

    Attributes:
        timestamp: When the log was created
        tag: Category tag for the log
        message: Log message content
        level: Logging level
        extra_data: Optional additional data
    """

    timestamp: datetime
    tag: LogTag
    message: str
    level: str = "INFO"
    extra_data: Optional[dict] = None

    def format_for_tui(self) -> str:
        """
        Format log entry for TUI display.

        Returns:
            Formatted string for TUI
        """
        time_str = self.timestamp.strftime("%H:%M:%S")
        tag_str = f"[bold green][{self.tag.value}][/bold green]"

        # Color code by level
        if self.level == "ERROR":
            msg_color = "red"
        elif self.level == "WARNING":
            msg_color = "yellow"
        elif self.level == "DEBUG":
            msg_color = "dim"
        else:
            msg_color = "white"

        return f"{time_str} {tag_str} [{msg_color}]{self.message}[/{msg_color}]"

    def __str__(self) -> str:
        """String representation of log entry."""
        return f"{self.timestamp.isoformat()} [{self.tag.value}] {self.message}"


class LoggerManager:
    """
    Centralized logger manager for the bot.

    Manages logging to console, file, and TUI with rich formatting.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger manager."""
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.logs: List[LogEntry] = []
            self.max_logs = 1000
            self.console = Console()
            self.logger = None
            self.file_handler = None
            self.tui_callback: Optional[Callable] = None

            # Setup default logger
            self.setup_logger()

    def setup_logger(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        console_output: bool = True,
    ) -> None:
        """
        Setup the logger with specified configuration.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
            console_output: Whether to output to console
        """
        # Create logger
        self.logger = logging.getLogger("noether_bot")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.handlers.clear()

        # Setup console handler with Rich
        if console_output:
            console_handler = RichHandler(
                console=self.console, show_path=False, markup=True, rich_tracebacks=True
            )
            console_handler.setLevel(getattr(logging, log_level.upper()))

            # Custom formatter
            formatter = logging.Formatter("%(message)s", datefmt="%H:%M:%S")
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Setup file handler
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)

            if self.file_handler:
                self.file_handler.close()

            self.file_handler = logging.FileHandler(log_file)
            self.file_handler.setLevel(getattr(logging, log_level.upper()))

            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            self.file_handler.setFormatter(file_formatter)
            self.logger.addHandler(self.file_handler)

    def set_tui_callback(self, callback: Callable) -> None:
        """
        Set callback function for TUI updates.

        Args:
            callback: Function to call when new logs are added
        """
        self.tui_callback = callback

    def log(
        self,
        tag: LogTag,
        message: str,
        level: str = "INFO",
        extra_data: Optional[dict] = None,
    ) -> None:
        """
        Log a message with a specific tag.

        Args:
            tag: Log category tag
            message: Log message
            level: Logging level
            extra_data: Optional additional data
        """
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            tag=tag,
            message=message,
            level=level.upper(),
            extra_data=extra_data,
        )

        # Add to log history
        self.logs.append(entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

        # Format message with tag
        formatted_msg = f"[bold green][{tag.value}][/bold green] {message}"

        # Log using appropriate level
        if self.logger:
            if level.upper() == "ERROR":
                self.logger.error(formatted_msg)
            elif level.upper() == "WARNING":
                self.logger.warning(formatted_msg)
            elif level.upper() == "DEBUG":
                self.logger.debug(formatted_msg)
            else:
                self.logger.info(formatted_msg)

        # Notify TUI if callback is set
        if self.tui_callback:
            self.tui_callback(entry)

    def log_position_polling(self, snapshot_data: dict) -> None:
        """
        Log position polling event.

        Args:
            snapshot_data: Position snapshot data
        """
        message = (
            f"USDT: {snapshot_data.get('reserve_token0', 'N/A')}, "
            f"WETH: {snapshot_data.get('reserve_token1', 'N/A')}, "
            f"Short: {snapshot_data.get('short_position_size', 'N/A')}"
        )
        self.log(LogTag.POSITION_POLLING, message, extra_data=snapshot_data)

    def log_calculated_hedge(self, delta: str, action: str) -> None:
        """
        Log calculated hedge decision.

        Args:
            delta: Delta value
            action: Action to take
        """
        message = f"Delta: {delta} ETH, Action: {action}"
        self.log(LogTag.CALCULATED_HEDGE, message)

    def log_leverage(self, leverage: str) -> None:
        """
        Log leverage setting.

        Args:
            leverage: Leverage value
        """
        self.log(LogTag.LEVERAGE, f"Using leverage: {leverage}x")

    def log_trade(self, action: str, size: str, price: str) -> None:
        """
        Log trade execution.

        Args:
            action: Trade action
            size: Trade size
            price: Trade price
        """
        if "short" in action.lower():
            if "open" in action.lower():
                tag = LogTag.OPEN_SHORT_POSITION
            elif "close" in action.lower():
                tag = LogTag.CLOSE_SHORT_POSITION
            else:
                tag = LogTag.ADJUST_SHORT_POSITION
        else:
            tag = LogTag.TRADE_EXECUTED

        message = f"Size: {size} ETH @ {price} USDT"
        self.log(tag, message)

    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """
        Log an error.

        Args:
            message: Error message
            exception: Optional exception object
        """
        if exception:
            message = f"{message}: {str(exception)}"
        self.log(LogTag.ERROR, message, level="ERROR")

    def log_warning(self, message: str) -> None:
        """
        Log a warning.

        Args:
            message: Warning message
        """
        self.log(LogTag.WARNING, message, level="WARNING")

    def log_info(self, message: str, tag: LogTag = LogTag.INFO) -> None:
        """
        Log an info message.

        Args:
            message: Info message
            tag: Optional specific tag
        """
        self.log(tag, message, level="INFO")

    def log_debug(self, message: str, tag: LogTag = LogTag.DEBUG) -> None:
        """
        Log a debug message.

        Args:
            message: Debug message
            tag: Optional specific tag
        """
        self.log(tag, message, level="DEBUG")

    def get_recent_logs(
        self, count: int = 50, tag: Optional[LogTag] = None
    ) -> List[LogEntry]:
        """
        Get recent log entries.

        Args:
            count: Number of logs to retrieve
            tag: Optional filter by tag

        Returns:
            List of recent log entries
        """
        if tag:
            filtered_logs = [log for log in self.logs if log.tag == tag]
            return filtered_logs[-count:]
        return self.logs[-count:]

    def clear_logs(self) -> None:
        """Clear all stored logs."""
        self.logs.clear()

    def export_logs(self, filepath: str, tag: Optional[LogTag] = None) -> None:
        """
        Export logs to a file.

        Args:
            filepath: Path to export file
            tag: Optional filter by tag
        """
        logs_to_export = (
            self.logs if not tag else [log for log in self.logs if log.tag == tag]
        )

        with open(filepath, "w") as f:
            for log in logs_to_export:
                f.write(f"{log}\n")

        self.log_info(f"Exported {len(logs_to_export)} logs to {filepath}")

    def get_statistics(self) -> dict:
        """
        Get logging statistics.

        Returns:
            Dictionary with log statistics
        """
        stats = {"total_logs": len(self.logs), "by_level": {}, "by_tag": {}}

        for log in self.logs:
            # Count by level
            stats["by_level"][log.level] = stats["by_level"].get(log.level, 0) + 1

            # Count by tag
            tag_name = log.tag.value
            stats["by_tag"][tag_name] = stats["by_tag"].get(tag_name, 0) + 1

        return stats
