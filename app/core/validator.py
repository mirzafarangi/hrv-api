# File: core/validator.py
import numpy as np
from typing import List, Tuple, Dict
from models.session import RawHRVData

class HRVValidator:
    MIN_RR = 300  # ms
    MAX_RR = 2000  # ms
    MIN_RR_COUNT = 30
    MIN_VALID_PERCENTAGE = 90.0
    
    def __init__(self, raw_data: RawHRVData):
        self.raw_data = raw_data
        self.outlier_count = 0
        self.valid_rr_percentage = 100.0
        self.quality_score = 1.0
        self.filter_method = "zscore"
        self.valid = True
        self.reasons = []
        self.cleaned_rr = []
    
    def validate_range(self) -> List[int]:
        """Apply range filter to RR intervals"""
        valid_rr = []
        for rr in self.raw_data.rrIntervals:
            if self.MIN_RR <= rr <= self.MAX_RR:
                valid_rr.append(rr)
            else:
                self.outlier_count += 1
        
        total_rr = len(self.raw_data.rrIntervals)
        if total_rr > 0:
            self.valid_rr_percentage = (len(valid_rr) / total_rr) * 100
        
        if len(valid_rr) < self.MIN_RR_COUNT:
            self.valid = False
            self.reasons.append("Too few valid RR intervals")
        
        if self.valid_rr_percentage < self.MIN_VALID_PERCENTAGE:
            self.valid = False
            self.reasons.append("Low valid RR percentage")
        
        return valid_rr
    
    def remove_statistical_outliers(self, rr_list: List[int]) -> List[int]:
        """Remove statistical outliers using Z-score method"""
        if not rr_list:
            return []
            
        rr_array = np.array(rr_list)
        if self.filter_method == "zscore":
            z_scores = np.abs((rr_array - np.mean(rr_array)) / np.std(rr_array))
            filtered_rr = rr_array[z_scores <= 3]
            self.outlier_count += len(rr_array) - len(filtered_rr)
            return filtered_rr.tolist()
        elif self.filter_method == "iqr":
            q1, q3 = np.percentile(rr_array, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)
            filtered_rr = rr_array[(rr_array >= lower_bound) & (rr_array <= upper_bound)]
            self.outlier_count += len(rr_array) - len(filtered_rr)
            return filtered_rr.tolist()
        else:
            return rr_list
    
    def check_motion_artifacts(self):
        """Check for motion artifacts"""
        if self.raw_data.motionArtifacts:
            self.valid = False
            self.reasons.append("Motion artifact detected")
    
    def calculate_quality_score(self):
        """Calculate quality score based on outliers"""
        total_rr = len(self.raw_data.rrIntervals)
        if total_rr > 0:
            self.quality_score = 1 - (self.outlier_count / total_rr)
            
        if self.quality_score < 0.6:
            self.valid = False
            self.reasons.append("Poor quality score")
        
        # Add quality label
        if self.quality_score > 0.95:
            self.quality_label = "excellent"
        elif self.quality_score > 0.80:
            self.quality_label = "acceptable"
        elif self.quality_score > 0.60:
            self.quality_label = "borderline"
        else:
            self.quality_label = "poor"
    
    def process(self) -> Tuple[List[int], Dict]:
        """Process the raw data through all validation steps"""
        self.check_motion_artifacts()
        
        if self.valid:
            range_filtered = self.validate_range()
            self.cleaned_rr = self.remove_statistical_outliers(range_filtered)
            self.calculate_quality_score()
        
        validation_result = {
            "valid": self.valid,
            "reason": " + ".join(self.reasons) if self.reasons else None,
            "quality_score": self.quality_score,
            "quality_label": self.quality_label,
            "filter_method": self.filter_method,
            "outlier_count": self.outlier_count,
            "valid_rr_percentage": self.valid_rr_percentage
        }
        
        return self.cleaned_rr, validation_result
