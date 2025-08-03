"""SQLAlchemy models for database persistence."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    Numeric,
    Enum as SQLEnum,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models.hedge_snapshot import HedgeAction
from models.trade import OrderType, OrderSide, OrderStatus

Base = declarative_base()


class PositionSnapshotDB(Base):
    """Database model for position snapshots."""

    __tablename__ = "position_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reserve_token0 = Column(Numeric(precision=30, scale=18), nullable=False)
    reserve_token1 = Column(Numeric(precision=30, scale=18), nullable=False)
    short_position_size = Column(Numeric(precision=30, scale=18), nullable=False)
    delta = Column(Numeric(precision=30, scale=18), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    block_number = Column(Integer, nullable=True)
    pool_address = Column(String(42), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HedgeSnapshotDB(Base):
    """Database model for hedge snapshots."""

    __tablename__ = "hedge_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(SQLEnum(HedgeAction), nullable=False)
    size = Column(Numeric(precision=30, scale=18), nullable=False)
    price = Column(Numeric(precision=30, scale=8), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    delta_before = Column(Numeric(precision=30, scale=18), nullable=False)
    delta_after = Column(Numeric(precision=30, scale=18), nullable=False)
    leverage = Column(Numeric(precision=10, scale=2), default=1.0)
    exchange = Column(String(50), default="binance")
    order_id = Column(String(100), nullable=True)
    gas_cost = Column(Numeric(precision=30, scale=18), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TradeDB(Base):
    """Database model for trades."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    size = Column(Numeric(precision=30, scale=18), nullable=False)
    price = Column(Numeric(precision=30, scale=8), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    order_id = Column(String(100), nullable=False, unique=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    fee = Column(Numeric(precision=30, scale=18), nullable=True)
    fee_currency = Column(String(10), nullable=True)
    exchange = Column(String(50), default="binance")
    created_at = Column(DateTime, default=datetime.utcnow)
