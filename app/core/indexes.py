# app/core/indexes.py
from app.models.schemas import SessionMetrics
from app.constants.interpretations import INTERPRETATIONS_MAP

def interpret(label: str) -> str:
    return INTERPRETATIONS_MAP.get(label, "No interpretation available.")

def build_metric_indexes(metrics: SessionMetrics) -> dict:
    return {
        "Parasympathetic indicators": {
            "rmssd": metrics.rmssd,
            "pnn50": metrics.pnn50,
            "hfPower": metrics.hfPower,
            "Interpretation": interpret("Parasympathetic indicators")
        },
        "Sympathetic influence": {
            "lfPower": metrics.lfPower,
            "lfHfRatio": metrics.lfHfRatio,
            "rmssd": metrics.rmssd,
            "Interpretation": interpret("Sympathetic influence")
        },
        "Autonomic balance": {
            "sdnn": metrics.sdnn,
            "lfHfRatio": metrics.lfHfRatio,
            "cv_rr": metrics.cv_rr,
            "mean_rr": metrics.mean_rr,
            "Interpretation": interpret("Autonomic balance")
        },
        "Respiratory-linked": {
            "hfPower": metrics.hfPower,
            "breathingRate": metrics.breathingRate,
            "Interpretation": interpret("Respiratory-linked")
        },
        "General HRV capacity": {
            "sdnn": metrics.sdnn,
            "cv_rr": metrics.cv_rr,
            "rmssd": metrics.rmssd,
            "pnn50": metrics.pnn50,
            "Interpretation": interpret("General HRV capacity")
        },
        "Signal Quality & Validity": {
            "rr_count": metrics.rr_count,
            "mean_rr": metrics.mean_rr,
            "motionArtifacts": metrics.motionArtifacts,
            "valid_rr_percentage": metrics.valid_rr_percentage,
            "quality_score": metrics.quality_score,
            "outlier_count": metrics.outlier_count,
            "filter_method": metrics.filter_method,
            "Interpretation": interpret("Signal Quality & Validity")
        },
        "Cognitive / Mental Load": {
            "heartRate": metrics.heartRate,
            "rmssd": metrics.rmssd,
            "lfPower": metrics.lfPower,
            "lfHfRatio": metrics.lfHfRatio,
            "Interpretation": interpret("Cognitive / Mental Load")
        },
        "Fatigue / Exhaustion": {
            "rmssd": metrics.rmssd,
            "sdnn": metrics.sdnn,
            "mean_rr": metrics.mean_rr,
            "quality_score": metrics.quality_score,
            "rr_count": metrics.rr_count,
            "Interpretation": interpret("Fatigue / Exhaustion")
        },
        "Circadian patterning": {
            "mean_rr": metrics.mean_rr,
            "hfPower": metrics.hfPower,
            "breathingRate": metrics.breathingRate,
            "heartRate": metrics.heartRate,
            "Interpretation": interpret("Circadian patterning")
        }
    }