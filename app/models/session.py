# File: models/session.py
from pydantic import BaseModel
from typing import Optional, List

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
    filter_method: str  # "zscore" or "iqr"

class RawHRVData(BaseModel):
    user_id: str
    device_info: dict
    recordingSessionId: str
    timestamp: str
    rrIntervals: List[int]
    heartRate: Optional[int]
    motionArtifacts: bool
    tags: List[str]