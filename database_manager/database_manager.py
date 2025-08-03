"""Database manager for handling all database operations."""

import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Generator, Any
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from models import PositionSnapshot, HedgeSnapshot, Trade
from models.trade import OrderStatus
from .models import Base, PositionSnapshotDB, HedgeSnapshotDB, TradeDB


class DatabaseManager:
    """
    Manages all database operations for the bot.

    Provides methods for storing and retrieving position snapshots,
    hedge operations, and trades.
    """

    def __init__(self, database_url: str = "sqlite:///noether_bot.db"):
        """
        Initialize the database manager.

        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args=(
                {"check_same_thread": False} if "sqlite" in database_url else {}
            ),
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.logger = logging.getLogger(__name__)

        # Create tables if they don't exist
        self.create_tables()

    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating database tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, Any, None]:
        """
        Provide a transactional scope for database operations.

        Yields:
            Session: Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def save_position_snapshot(self, snapshot: PositionSnapshot) -> int:
        """
        Save a position snapshot to the database.

        Args:
            snapshot: PositionSnapshot to save

        Returns:
            ID of the saved snapshot
        """
        with self.get_session() as session:
            db_snapshot = PositionSnapshotDB(
                reserve_token0=snapshot.reserve_token0,
                reserve_token1=snapshot.reserve_token1,
                short_position_size=snapshot.short_position_size,
                delta=snapshot.delta,
                timestamp=snapshot.timestamp,
                block_number=snapshot.block_number,
                pool_address=snapshot.pool_address,
            )
            session.add(db_snapshot)
            session.flush()
            return db_snapshot.id

    def get_latest_position_snapshot(self) -> Optional[PositionSnapshot]:
        """
        Get the most recent position snapshot.

        Returns:
            Latest PositionSnapshot or None if no snapshots exist
        """
        with self.get_session() as session:
            db_snapshot = (
                session.query(PositionSnapshotDB)
                .order_by(desc(PositionSnapshotDB.timestamp))
                .first()
            )

            if db_snapshot:
                return PositionSnapshot(
                    reserve_token0=Decimal(str(db_snapshot.reserve_token0)),
                    reserve_token1=Decimal(str(db_snapshot.reserve_token1)),
                    short_position_size=Decimal(str(db_snapshot.short_position_size)),
                    timestamp=db_snapshot.timestamp,
                    block_number=db_snapshot.block_number,
                    pool_address=db_snapshot.pool_address,
                )
            return None

    def get_position_snapshots(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[PositionSnapshot]:
        """
        Get position snapshots within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of snapshots to return

        Returns:
            List of PositionSnapshots
        """
        with self.get_session() as session:
            query = session.query(PositionSnapshotDB)

            if start_time:
                query = query.filter(PositionSnapshotDB.timestamp >= start_time)
            if end_time:
                query = query.filter(PositionSnapshotDB.timestamp <= end_time)

            db_snapshots = (
                query.order_by(desc(PositionSnapshotDB.timestamp)).limit(limit).all()
            )

            return [
                PositionSnapshot(
                    reserve_token0=Decimal(str(snap.reserve_token0)),
                    reserve_token1=Decimal(str(snap.reserve_token1)),
                    short_position_size=Decimal(str(snap.short_position_size)),
                    timestamp=snap.timestamp,
                    block_number=snap.block_number,
                    pool_address=snap.pool_address,
                )
                for snap in db_snapshots
            ]

    def save_hedge_snapshot(self, hedge: HedgeSnapshot) -> int:
        """
        Save a hedge snapshot to the database.

        Args:
            hedge: HedgeSnapshot to save

        Returns:
            ID of the saved hedge
        """
        with self.get_session() as session:
            db_hedge = HedgeSnapshotDB(
                action=hedge.action,
                size=hedge.size,
                price=hedge.price,
                timestamp=hedge.timestamp,
                delta_before=hedge.delta_before,
                delta_after=hedge.delta_after,
                leverage=hedge.leverage,
                exchange=hedge.exchange,
                order_id=hedge.order_id,
                gas_cost=hedge.gas_cost,
                success=hedge.success,
                error_message=hedge.error_message,
            )
            session.add(db_hedge)
            session.flush()
            return db_hedge.id

    def get_hedge_snapshots(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[HedgeSnapshot]:
        """
        Get hedge snapshots within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of hedges to return

        Returns:
            List of HedgeSnapshots
        """
        with self.get_session() as session:
            query = session.query(HedgeSnapshotDB)

            if start_time:
                query = query.filter(HedgeSnapshotDB.timestamp >= start_time)
            if end_time:
                query = query.filter(HedgeSnapshotDB.timestamp <= end_time)

            db_hedges = (
                query.order_by(desc(HedgeSnapshotDB.timestamp)).limit(limit).all()
            )

            return [
                HedgeSnapshot(
                    action=hedge.action,
                    size=Decimal(str(hedge.size)),
                    price=Decimal(str(hedge.price)),
                    timestamp=hedge.timestamp,
                    delta_before=Decimal(str(hedge.delta_before)),
                    delta_after=Decimal(str(hedge.delta_after)),
                    leverage=Decimal(str(hedge.leverage)),
                    exchange=hedge.exchange,
                    order_id=hedge.order_id,
                    gas_cost=Decimal(str(hedge.gas_cost)) if hedge.gas_cost else None,
                    success=hedge.success,
                    error_message=hedge.error_message,
                )
                for hedge in db_hedges
            ]

    def save_trade(self, trade: Trade) -> int:
        """
        Save a trade to the database.

        Args:
            trade: Trade to save

        Returns:
            ID of the saved trade
        """
        with self.get_session() as session:
            db_trade = TradeDB(
                symbol=trade.symbol,
                side=trade.side,
                order_type=trade.order_type,
                size=trade.size,
                price=trade.price,
                timestamp=trade.timestamp,
                order_id=trade.order_id,
                status=trade.status,
                fee=trade.fee,
                fee_currency=trade.fee_currency,
                exchange=trade.exchange,
            )
            session.add(db_trade)
            session.flush()
            return db_trade.id

    def update_trade_status(self, order_id: str, status: OrderStatus) -> bool:
        """
        Update the status of a trade.

        Args:
            order_id: Order ID to update
            status: New status

        Returns:
            True if trade was updated, False if not found
        """
        with self.get_session() as session:
            trade = session.query(TradeDB).filter(TradeDB.order_id == order_id).first()

            if trade:
                trade.status = status
                return True
            return False

    def get_recent_trades(self, hours: int = 24, limit: int = 100) -> List[Trade]:
        """
        Get recent trades.

        Args:
            hours: Number of hours to look back
            limit: Maximum number of trades to return

        Returns:
            List of recent Trades
        """
        with self.get_session() as session:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            db_trades = (
                session.query(TradeDB)
                .filter(TradeDB.timestamp >= cutoff_time)
                .order_by(desc(TradeDB.timestamp))
                .limit(limit)
                .all()
            )

            return [
                Trade(
                    symbol=trade.symbol,
                    side=trade.side,
                    order_type=trade.order_type,
                    size=Decimal(str(trade.size)),
                    price=Decimal(str(trade.price)),
                    timestamp=trade.timestamp,
                    order_id=trade.order_id,
                    status=trade.status,
                    fee=Decimal(str(trade.fee)) if trade.fee else None,
                    fee_currency=trade.fee_currency,
                    exchange=trade.exchange,
                )
                for trade in db_trades
            ]

    def cleanup_old_data(self, days: int = 30) -> int:
        """
        Remove old data from the database.

        Args:
            days: Number of days of data to keep

        Returns:
            Number of records deleted
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0

        with self.get_session() as session:
            # Delete old position snapshots
            deleted = (
                session.query(PositionSnapshotDB)
                .filter(PositionSnapshotDB.timestamp < cutoff_time)
                .delete()
            )
            deleted_count += deleted

            # Delete old hedge snapshots
            deleted = (
                session.query(HedgeSnapshotDB)
                .filter(HedgeSnapshotDB.timestamp < cutoff_time)
                .delete()
            )
            deleted_count += deleted

            # Delete old trades
            deleted = (
                session.query(TradeDB).filter(TradeDB.timestamp < cutoff_time).delete()
            )
            deleted_count += deleted

        self.logger.info(f"Cleaned up {deleted_count} old records")
        return deleted_count
