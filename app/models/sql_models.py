# app/models/sql_models.py
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, JSON, Table, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("HRVSession", back_populates="user")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    model = Column(String, index=True)
    firmware_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("HRVSession", back_populates="device")

# Association table for session-tag many-to-many relationship
session_tags = Table(
    "session_tags",
    Base.metadata,
    Column("session_id", String, ForeignKey("hrv_sessions.id")),
    Column("tag_id", String, ForeignKey("tags.id")),
)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    
    # Relationships
    sessions = relationship("HRVSession", secondary=session_tags, back_populates="tags")

class HRVSession(Base):
    __tablename__ = "hrv_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    recording_session_id = Column(String, index=True, unique=True)
    timestamp = Column(DateTime, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    device_id = Column(String, ForeignKey("devices.id"))
    heart_rate = Column(Integer, nullable=True)
    motion_artifacts = Column(Boolean, default=False)
    valid = Column(Boolean, default=True)
    reason = Column(String, nullable=True)
    quality_score = Column(Float, default=1.0)
    quality_label = Column(String, default="excellent")
    filter_method = Column(String, default="zscore")
    outlier_count = Column(Integer, default=0)
    valid_rr_percentage = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")
    tags = relationship("Tag", secondary=session_tags, back_populates="sessions")
    metrics = relationship("HRVMetrics", back_populates="session", uselist=False, cascade="all, delete-orphan")
    rr_intervals = relationship("RRInterval", back_populates="session", cascade="all, delete-orphan")
    
class HRVMetrics(Base):
    __tablename__ = "hrv_metrics"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("hrv_sessions.id"), unique=True)
    mean_rr = Column(Float)
    sdnn = Column(Float)
    rmssd = Column(Float)
    pnn50 = Column(Float)
    cv_rr = Column(Float)
    rr_count = Column(Integer)
    lf_power = Column(Float, nullable=True)
    hf_power = Column(Float, nullable=True)
    lf_hf_ratio = Column(Float, nullable=True)
    breathing_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Store indexes as JSON
    indexes = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("HRVSession", back_populates="metrics")

class RRInterval(Base):
    __tablename__ = "rr_intervals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("hrv_sessions.id"))
    position = Column(Integer)  # Position in the sequence
    value = Column(Integer)     # RR interval value in ms
    is_valid = Column(Boolean, default=True)
    
    # Relationships
    session = relationship("HRVSession", back_populates="rr_intervals")