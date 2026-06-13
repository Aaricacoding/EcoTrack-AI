from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    records = relationship("CarbonRecord", back_populates="user", cascade="all, delete-orphan")

class CarbonRecord(Base):
    __tablename__ = "carbon_records"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transport_kg = Column(Float, nullable=False)
    home_energy_kg = Column(Float, nullable=False)
    diet_kg = Column(Float, nullable=False)
    shopping_kg = Column(Float, nullable=False)
    total_kg = Column(Float, nullable=False)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="records")
    __table_args__ = (Index("ix_carbon_records_user_date", "user_id", "calculated_at"),)
