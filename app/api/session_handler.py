# app/api/session_handler.py
from fastapi import APIRouter, HTTPException, Depends
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session
from app.models.schemas import RawHRVData, SessionRecord
from app.core.processor import HRVSessionProcessor
from app.core.database import get_db
from app.core.crud import (
    create_hrv_session, 
    create_hrv_metrics, 
    get_session_by_recording_id,
    get_sessions_by_user,
    get_sessions_by_tag
)
from app.models.sql_models import User, HRVSession, Device, Tag
from typing import List

router = APIRouter()

@router.post("/hrv/session", response_model=dict)
async def process_hrv_session(raw_data: RawHRVData, db: Session = Depends(get_db)):
    """Process incoming HRV session data and store in database"""
    # Check if session already exists
    existing_session = get_session_by_recording_id(db, raw_data.recordingSessionId)
    if existing_session:
        return {
            "status": "error",
            "message": f"Session with ID {raw_data.recordingSessionId} already exists",
            "data": {"session_id": existing_session.id}
        }
    
    # Process the data
    processor = HRVSessionProcessor(raw_data)
    valid, result = processor.process()
    
    # Create session in database
    db_session = create_hrv_session(db, raw_data, valid, processor.validation_result)
    
    # If valid session, also store metrics
    if valid and "metrics" in result:
        create_hrv_metrics(
            db=db,
            session_id=db_session.id,
            metrics_dict=result["metrics"],
            indexes=result.get("indexes", {})
        )
    
    # Return response
    if not valid:
        return {
            "status": "error",
            "message": f"Invalid HRV session: {result['metadata'].get('reason')}",
            "data": result
        }
    
    return {
        "status": "success",
        "message": "Session processed and stored successfully",
        "data": result
    }

@router.get("/hrv/sessions/user/{user_id}", response_model=List[dict])
async def get_user_sessions(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sessions for a specific user"""
    sessions = get_sessions_by_user(db, user_id, skip, limit)
    if not sessions:
        return []
    
    # Convert to response format
    return [
        {
            "id": session.id,
            "recordingSessionId": session.recording_session_id,
            "timestamp": session.timestamp,
            "valid": session.valid,
            "quality_score": session.quality_score,
            "quality_label": session.quality_label,
            "tags": [tag.name for tag in session.tags]
        }
        for session in sessions
    ]

@router.get("/hrv/sessions/tag/{tag_name}", response_model=List[dict])
async def get_sessions_with_tag(tag_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sessions with a specific tag"""
    sessions = get_sessions_by_tag(db, tag_name, skip, limit)
    if not sessions:
        return []
    
    # Convert to response format
    return [
        {
            "id": session.id,
            "recordingSessionId": session.recording_session_id,
            "timestamp": session.timestamp,
            "valid": session.valid,
            "quality_score": session.quality_score,
            "quality_label": session.quality_label,
            "tags": [tag.name for tag in session.tags]
        }
        for session in sessions
    ]

@router.get("/hrv/session/{session_id}", response_model=dict)
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific session"""
    session = get_session_by_recording_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")
    
    # Build response
    response = {
        "id": session.id,
        "recordingSessionId": session.recording_session_id,
        "timestamp": session.timestamp,
        "user_id": session.user_id,
        "device": {
            "model": session.device.model,
            "firmware_version": session.device.firmware_version
        },
        "valid": session.valid,
        "reason": session.reason,
        "quality_score": session.quality_score,
        "quality_label": session.quality_label,
        "tags": [tag.name for tag in session.tags]
    }
    
    # Add metrics if they exist
    if session.metrics:
        response["metrics"] = {
            "mean_rr": session.metrics.mean_rr,
            "sdnn": session.metrics.sdnn,
            "rmssd": session.metrics.rmssd,
            "pnn50": session.metrics.pnn50,
            "cv_rr": session.metrics.cv_rr,
            "rr_count": session.metrics.rr_count,
            "lfPower": session.metrics.lf_power,
            "hfPower": session.metrics.hf_power,
            "lfHfRatio": session.metrics.lf_hf_ratio,
            "breathingRate": session.metrics.breathing_rate
        }
        response["indexes"] = session.metrics.indexes
    
    return response

@router.get("/hrv/database-stats", response_model=dict)
async def get_database_stats(db: Session = Depends(get_db)):
    """Get basic statistics about the database contents"""
    user_count = db.query(User).count()
    session_count = db.query(HRVSession).count()
    device_count = db.query(Device).count()
    tag_count = db.query(Tag).count()
    
    # Get the latest sessions
    latest_sessions = db.query(HRVSession).order_by(HRVSession.created_at.desc()).limit(5).all()
    
    return {
        "stats": {
            "users": user_count,
            "sessions": session_count,
            "devices": device_count,
            "tags": tag_count
        },
        "latest_sessions": [
            {
                "id": session.id,
                "recording_session_id": session.recording_session_id,
                "timestamp": session.timestamp,
                "user_id": session.user_id,
                "valid": session.valid,
                "created_at": session.created_at
            }
            for session in latest_sessions
        ]
    }



def validate_user_email(email: str, db: Session) -> tuple[bool, str]:
    """Validate email format and check if it already exists"""
    try:
        # Validate email format
        validate_email(email)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)

@router.post("/validate-email", response_model=dict)
async def validate_email_endpoint(data: dict, db: Session = Depends(get_db)):
    """Endpoint to validate an email before using it as user_id"""
    email = data.get("email", "")
    valid, message = validate_user_email(email, db)
    
    return {
        "valid": valid,
        "message": message
    }