# File: core/metrics.py
import numpy as np
from typing import List, Dict, Optional
from scipy import signal

def calculate_basic_metrics(cleaned_rr: List[int]) -> Dict:
    """Calculate basic HRV metrics from cleaned RR intervals"""
    if not cleaned_rr:
        return {}
    
    rr_array = np.array(cleaned_rr)
    rr_diff = np.diff(rr_array)
    
    # Time domain metrics
    mean_rr = np.mean(rr_array)
    sdnn = np.std(rr_array)
    rmssd = np.sqrt(np.mean(rr_diff ** 2))
    pnn50 = (np.sum(np.abs(rr_diff) > 50) / len(rr_diff)) * 100
    cv_rr = (sdnn / mean_rr) * 100
    
    # Convert RR to time series for frequency domain analysis
    # This is a simplified approach - in production code, use more robust methods
    rr_time = np.cumsum(rr_array) / 1000  # Convert to seconds
    rr_interpolated, t_interpolated = interpolate_rr(rr_array, rr_time)
    
    # Frequency domain metrics
    lf_power, hf_power, lf_hf_ratio, breathing_rate = frequency_analysis(rr_interpolated, t_interpolated)
    
    return {
        "mean_rr": mean_rr,
        "sdnn": sdnn,
        "rmssd": rmssd,
        "pnn50": pnn50,
        "cv_rr": cv_rr,
        "rr_count": len(cleaned_rr),
        "lfPower": lf_power,
        "hfPower": hf_power,
        "lfHfRatio": lf_hf_ratio,
        "breathingRate": breathing_rate
    }

def interpolate_rr(rr_intervals: np.ndarray, rr_time: np.ndarray, fs: float = 4.0):
    """Interpolate RR intervals to create evenly sampled time series"""
    # Create time vector
    t_max = rr_time[-1]
    t_min = rr_time[0]
    t_new = np.arange(t_min, t_max, 1/fs)
    
    # Interpolate
    rr_interpolated = np.interp(t_new, rr_time, rr_intervals)
    
    # Detrend
    rr_interpolated = signal.detrend(rr_interpolated)
    
    return rr_interpolated, t_new

def frequency_analysis(rr_interpolated: np.ndarray, t_interpolated: np.ndarray):
    """Perform frequency domain analysis of HRV"""
    # Calculate sampling frequency
    fs = 1 / np.mean(np.diff(t_interpolated))
    
    # Compute power spectral density
    f, psd = signal.welch(rr_interpolated, fs, nperseg=len(rr_interpolated)//2)
    
    # Define frequency bands
    lf_mask = (f >= 0.04) & (f <= 0.15)
    hf_mask = (f >= 0.15) & (f <= 0.4)
    
    # Calculate powers
    lf_power = np.trapz(psd[lf_mask], f[lf_mask])
    hf_power = np.trapz(psd[hf_mask], f[hf_mask])
    
    # LF/HF ratio
    lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0
    
    # Estimated breathing rate (from HF peak)
    if np.any(hf_mask):
        hf_peak_idx = np.argmax(psd[hf_mask])
        breathing_freq = f[hf_mask][hf_peak_idx]
        breathing_rate = breathing_freq * 60  # Convert to breaths per minute
    else:
        breathing_rate = None
    
    return lf_power, hf_power, lf_hf_ratio, breathing_rate
