# app/core/crud.py
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.sql_models import User, Device, Tag, HRVSession, HRVMetrics, RRInterval
from app.models.schemas import RawHRVData, UserCreate, DeviceCreate, TagCreate
from datetime import datetime
import uuid

def get_or_create_user(db: Session, email: str) -> User:
    """Get a user by email (used as user_id) or create if not exists"""
    # First check if user exists with this email
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Generate a username from the email (part before @)
        username = email.split('@')[0]
        
        # Create a new user with email as both id and email
        user = User(
            id=email,  # Using email as the ID
            username=username,
            email=email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def get_or_create_device(db: Session, device_info: Dict[str, str]) -> Device:
    """Get a device by model and firmware version or create if not exists"""
    device = db.query(Device).filter(
        Device.model == device_info.get("model"),
        Device.firmware_version == device_info.get("firmwareVersion")
    ).first()
    
    if not device:
        device = Device(
            model=device_info.get("model"),
            firmware_version=device_info.get("firmwareVersion")
        )
        db.add(device)
        db.commit()
        db.refresh(device)
    
    return device

def get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    """Get or create tags from a list of tag names"""
    tags = []
    for tag_name in tag_names:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    return tags

def create_hrv_session(db: Session, raw_data: RawHRVData, valid: bool, validation_result: Dict) -> HRVSession:
    """Create a new HRV session record"""
    # Get or create related entities
    user = get_or_create_user(db, raw_data.user_id)
    device = get_or_create_device(db, raw_data.device_info)
    tags = get_or_create_tags(db, raw_data.tags)
    
    # Parse timestamp
    try:
        timestamp = datetime.fromisoformat(raw_data.timestamp.replace('Z', '+00:00'))
    except ValueError:
        # Fallback to current time if parsing fails
        timestamp = datetime.utcnow()
    
    # Create the session
    session = HRVSession(
        recording_session_id=raw_data.recordingSessionId,
        timestamp=timestamp,
        user_id=user.id,
        device_id=device.id,
        heart_rate=raw_data.heartRate,
        motion_artifacts=raw_data.motionArtifacts,
        valid=valid,
        reason=validation_result.get("reason"),
        quality_score=validation_result.get("quality_score", 1.0),
        quality_label=validation_result.get("quality_label", "excellent"),
        filter_method=validation_result.get("filter_method", "zscore"),
        outlier_count=validation_result.get("outlier_count", 0),
        valid_rr_percentage=validation_result.get("valid_rr_percentage", 100.0)
    )
    
    # Add tags
    session.tags = tags
    
    # Add to database
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Add RR intervals
    for i, rr_value in enumerate(raw_data.rrIntervals):
        rr_interval = RRInterval(
            session_id=session.id,
            position=i,
            value=rr_value,
            is_valid=True  # Assume all intervals are valid initially
        )
        db.add(rr_interval)
    
    db.commit()
    
    return session

def create_hrv_metrics(db: Session, session_id: str, metrics_dict: Dict[str, Any], indexes: Dict[str, Any]) -> HRVMetrics:
    """Create HRV metrics record for a session"""
    metrics = HRVMetrics(
        session_id=session_id,
        mean_rr=metrics_dict.get("mean_rr"),
        sdnn=metrics_dict.get("sdnn"),
        rmssd=metrics_dict.get("rmssd"),
        pnn50=metrics_dict.get("pnn50"),
        cv_rr=metrics_dict.get("cv_rr"),
        rr_count=metrics_dict.get("rr_count"),
        lf_power=metrics_dict.get("lfPower"),
        hf_power=metrics_dict.get("hfPower"),
        lf_hf_ratio=metrics_dict.get("lfHfRatio"),
        breathing_rate=metrics_dict.get("breathingRate"),
        indexes=indexes
    )
    
    db.add(metrics)
    db.commit()
    db.refresh(metrics)
    
    return metrics

def get_session_by_recording_id(db: Session, recording_session_id: str) -> Optional[HRVSession]:
    """Get a session by its recording ID"""
    return db.query(HRVSession).filter(HRVSession.recording_session_id == recording_session_id).first()

def get_sessions_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[HRVSession]:
    """Get all sessions for a specific user"""
    return db.query(HRVSession).filter(HRVSession.user_id == user_id).offset(skip).limit(limit).all()

def get_sessions_by_tag(db: Session, tag_name: str, skip: int = 0, limit: int = 100) -> List[HRVSession]:
    """Get all sessions with a specific tag"""
    return db.query(HRVSession).join(HRVSession.tags).filter(Tag.name == tag_name).offset(skip).limit(limit).all()

def get_metrics_by_session(db: Session, session_id: str) -> Optional[HRVMetrics]:
    """Get metrics for a specific session"""
    return db.query(HRVMetrics).filter(HRVMetrics.session_id == session_id).first()

def get_rr_intervals_by_session(db: Session, session_id: str) -> List[RRInterval]:
    """Get all RR intervals for a specific session"""
    return db.query(RRInterval).filter(RRInterval.session_id == session_id).order_by(RRInterval.position).all()