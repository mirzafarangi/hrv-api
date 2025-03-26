# File: core/processor.py
from typing import Dict, Optional, Tuple, Any
from models.session import SessionMetrics, RawHRVData
from models.metadata import SessionMetadata
from models.record import SessionRecord
from core.indexes import build_metric_indexes
from core.validator import HRVValidator
from core.metrics import calculate_basic_metrics

class HRVSessionProcessor:
    def __init__(self, raw_data: RawHRVData):
        self.raw_data = raw_data
        self.cleaned_rr = []
        self.metrics: Optional[SessionMetrics] = None
        self.indexes: Optional[Dict] = None
        self.validation_result: Dict = {}
        self.metadata: Optional[SessionMetadata] = None

    def validate(self) -> bool:
        """Validate and clean the raw RR interval data"""
        validator = HRVValidator(self.raw_data)
        self.cleaned_rr, self.validation_result = validator.process()
        
        # Create the metadata object
        self.metadata = SessionMetadata(
            timestamp=self.raw_data.timestamp,
            recordingSessionId=self.raw_data.recordingSessionId,
            user_id=self.raw_data.user_id,
            device_info=self.raw_data.device_info,
            tags=self.raw_data.tags,
            valid=self.validation_result["valid"],
            reason=self.validation_result.get("reason"),
            quality_score=self.validation_result["quality_score"],
            quality_label=self.validation_result["quality_label"],
            filter_method=self.validation_result["filter_method"],
            outlier_count=self.validation_result["outlier_count"],
            valid_rr_percentage=self.validation_result["valid_rr_percentage"],
            motionArtifacts=self.raw_data.motionArtifacts
        )
        
        return self.validation_result["valid"]

    def compute_metrics(self) -> Optional[SessionMetrics]:
        """Calculate HRV metrics from cleaned RR intervals"""
        if not self.cleaned_rr:
            return None
            
        basic_metrics = calculate_basic_metrics(self.cleaned_rr)
        
        # Combine with validation data and raw data fields
        raw_metrics_dict = {
            **basic_metrics,
            "heartRate": self.raw_data.heartRate,
            "motionArtifacts": self.raw_data.motionArtifacts,
            "valid_rr_percentage": self.validation_result["valid_rr_percentage"],
            "quality_score": self.validation_result["quality_score"],
            "outlier_count": self.validation_result["outlier_count"],
            "filter_method": self.validation_result["filter_method"]
        }
        
        self.metrics = SessionMetrics(**raw_metrics_dict)
        return self.metrics

    def build_indexes(self) -> Optional[Dict]:
        """Build metric indexes from computed metrics"""
        if not self.metrics:
            raise ValueError("Metrics must be computed before building indexes.")
            
        self.indexes = build_metric_indexes(self.metrics)
        return self.indexes
        
    def create_record(self) -> SessionRecord:
        """Create a complete SessionRecord object"""
        if not self.metadata:
            raise ValueError("Validation must be performed before creating a record.")
            
        return SessionRecord(
            metadata=self.metadata,
            metrics=self.metrics,
            indexes=self.indexes
        )
        
    def process(self) -> Tuple[bool, Dict[str, Any]]:
        """Execute the full HRV processing pipeline"""
        valid = self.validate()
        
        if not valid:
            # Create and return a record with just metadata
            record = self.create_record()
            return False, record.dict()
            
        self.compute_metrics()
        self.build_indexes()
        
        # Create and return the full record
        record = self.create_record()
        return True, record.dict()