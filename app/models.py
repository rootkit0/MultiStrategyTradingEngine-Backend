import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    BigInteger,
    DECIMAL,
    String,
    DateTime,
    Float,
    ForeignKey,
    Enum as SAEnum,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db import Base

class StrategyInstanceStatusEnum(str, PyEnum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class StrategyInstance(Base):
    __tablename__ = "strategy_instances"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    params = Column(String(50), nullable=False, default="{}")
    initial_equity = Column(Float, nullable=False, default=0.0)
    status = Column(SAEnum(StrategyInstanceStatusEnum), default=StrategyInstanceStatusEnum.CREATED)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trades = relationship("Trade", back_populates="strategy_instance", cascade="all, delete-orphan")
    pnl_snapshots = relationship("PnLSnapshot", back_populates="strategy_instance", cascade="all, delete-orphan")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_instance_id = Column(String(36), ForeignKey("strategy_instances.id"), nullable=False)
    symbol = Column(String(50), nullable=False)
    side = Column(String(50), nullable=False)
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, nullable=False, default=0.0)
    realized_pnl = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    strategy_instance = relationship("StrategyInstance", back_populates="trades")


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("strategy_instance_id", "symbol", name="uq_strategy_symbol"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_instance_id = Column(String(36), ForeignKey("strategy_instances.id"), nullable=False)
    symbol = Column(String(50), nullable=False)
    side = Column(String(50), nullable=False, default="long")
    qty = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PnLSnapshot(Base):
    __tablename__ = "pnl_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_instance_id = Column(String(36), ForeignKey("strategy_instances.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    equity = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False)

    strategy_instance = relationship("StrategyInstance", back_populates="pnl_snapshots")

class Candle(Base):
    __tablename__ = "candles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    interval = Column(String(5), nullable=False)
    open_time = Column(BigInteger, nullable=False)

    open = Column(DECIMAL(18,8), nullable=False)
    high = Column(DECIMAL(18,8), nullable=False)
    low = Column(DECIMAL(18,8), nullable=False)
    close = Column(DECIMAL(18,8), nullable=False)
    volume = Column(DECIMAL(18,8), nullable=False)

    close_time = Column(BigInteger, nullable=False)
