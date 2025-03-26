# File: models/record.py
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any
from models.session import SessionMetrics
from models.metadata import SessionMetadata

@dataclass
class SessionRecord:
    metadata: SessionMetadata
    metrics: Optional[SessionMetrics] = None
    indexes: Optional[Dict[str, Dict[str, Any]]] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert the record to a dictionary format for API responses"""
        result = {
            "metadata": asdict(self.metadata)
        }
        
        if self.metrics:
            result["metrics"] = self.metrics.dict()
            
        if self.indexes:
            result["indexes"] = self.indexes
            
        return result