# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base schemas
class DeviceInfoBase(BaseModel):
    model: str
    firmwareVersion: str

class TagBase(BaseModel):
    name: str

# Request schemas
class RawHRVData(BaseModel):
    user_id: str
    device_info: Dict[str, str]
    recordingSessionId: str
    timestamp: str
    rrIntervals: List[int]
    heartRate: Optional[int] = None
    motionArtifacts: bool = False
    tags: List[str] = []

# Response schemas
class SessionMetrics(BaseModel):
    mean_rr: float
    sdnn: float
    rmssd: float
    pnn50: float
    cv_rr: float
    rr_count: int
    lfPower: Optional[float]
    hfPower: Optional[float]
    lfHfRatio: Optional[float]
    breathingRate: Optional[float]
    heartRate: Optional[float]
    motionArtifacts: bool
    valid_rr_percentage: float
    quality_score: float
    outlier_count: int
    filter_method: str
    
    class Config:
        orm_mode = True

class SessionMetadata(BaseModel):
    timestamp: str
    recordingSessionId: str
    user_id: str
    device_info: Dict[str, str]
    tags: List[str]
    valid: bool
    reason: Optional[str] = None
    quality_score: float = 1.0
    quality_label: str = "excellent"
    filter_method: str = "zscore"
    outlier_count: int = 0
    valid_rr_percentage: float = 100.0
    motionArtifacts: bool = False
    
    class Config:
        orm_mode = True

class SessionRecord(BaseModel):
    metadata: SessionMetadata
    metrics: Optional[SessionMetrics] = None
    indexes: Optional[Dict[str, Dict[str, Any]]] = None
    
    class Config:
        orm_mode = True

# Models for database operations
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class TagCreate(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        orm_mode = True

class DeviceCreate(BaseModel):
    model: str
    firmware_version: str

class DeviceResponse(BaseModel):
    id: str
    model: str
    firmware_version: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class HRVSessionResponse(BaseModel):
    id: str
    recording_session_id: str
    timestamp: datetime
    user_id: str
    device: DeviceResponse
    heart_rate: Optional[int]
    motion_artifacts: bool
    tags: List[TagResponse]
    valid: bool
    reason: Optional[str]
    quality_score: float
    quality_label: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class HRVMetricsResponse(BaseModel):
    id: str
    session_id: str
    mean_rr: float
    sdnn: float
    rmssd: float
    pnn50: float
    cv_rr: float
    rr_count: int
    lf_power: Optional[float]
    hf_power: Optional[float]
    lf_hf_ratio: Optional[float]
    breathing_rate: Optional[float]
    indexes: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        orm_mode = True