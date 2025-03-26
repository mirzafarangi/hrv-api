# app/models/metadata.py
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class SessionMetadata:
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