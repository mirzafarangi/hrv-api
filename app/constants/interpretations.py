# File: constants/interpretations.py
INTERPRETATIONS_MAP = {
    "Parasympathetic indicators": (
        "Captures parasympathetic (vagal) nervous system activity. Reflects your body's ability to rest, recover, and relax. "
        "Higher values mean stronger vagal tone, emotional regulation, and recovery capacity."
    ),
    "Sympathetic influence": (
        "Reflects stress response or mental load. Increased LF activity, LF/HF ratio, and lower RMSSD suggest elevated sympathetic drive or arousal."
    ),
    "Autonomic balance": (
        "Shows coordination between sympathetic and parasympathetic systems. Helps track recovery status or chronic imbalance."
    ),
    "Respiratory-linked": (
        "Highlights breath-driven vagal modulation. Useful for detecting relaxed states, meditation, or sleep-linked variability."
    ),
    "General HRV capacity": (
        "Represents overall variability strength — how resilient and adaptable your nervous system is under stress and recovery."
    ),
    "Signal Quality & Validity": (
        "Assesses trust in data — based on signal cleanliness, completeness, and detection accuracy. Helps flag unreliable sessions."
    ),
    "Cognitive / Mental Load": (
        "Estimates mental strain, focus demand, or executive processing load — useful for tracking attention, alertness, or stress."
    ),
    "Fatigue / Exhaustion": (
        "Captures patterns of recovery depletion — especially post-exertion, stress, or low sleep. Useful for pacing and recovery timing."
    ),
    "Circadian patterning": (
        "Tracks daily HRV rhythm and alignment with biological clocks. Useful for spotting disruption, irregular rest, or phase shifts."
    )
}
