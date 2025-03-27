# File: sample.py
from app.models.session import RawHRVData
from app.core.processor import HRVSessionProcessor
import json

def process_sample_data():
    """Process a sample HRV session and print the results"""
    # Create sample data
    sample_data = RawHRVData(
        user_id="Ashkan",
        device_info={
            "firmwareVersion": "2.1.9",
            "model": "Polar H10"
        },
        recordingSessionId="Ashkan_sample_session_001",
        timestamp="2025-03-25T23:10:00Z",
        rrIntervals=[812, 805, 798, 790, 803, 815, 825, 833, 826, 819, 
                     810, 805, 795, 788, 782, 775, 780, 785, 790, 798, 
                     805, 810, 820, 830, 832, 835, 830, 825, 815, 808, 
                     800, 795, 790, 785, 780, 775, 780, 790, 805, 815, 
                     825, 830, 835, 830, 825, 815, 805, 795, 790, 785],
        heartRate=74,
        motionArtifacts=False,
        tags=["Sleep"]
    )
    
    # Process the data
    processor = HRVSessionProcessor(sample_data)
    valid, result = processor.process()
    
    # Print the result
    print(f"Session valid: {valid}")
    print(f"Result structure:")
    print(json.dumps(result, indent=2, default=str))
    
    if valid:
        print("\nMetadata:")
        for key, value in result["metadata"].items():
            print(f"  {key}: {value}")
        
        print("\nKey HRV Metrics:")
        for key in ["rmssd", "sdnn", "pnn50", "lfHfRatio"]:
            print(f"  {key}: {result['metrics'][key]}")
        
        print("\nIndexes:")
        for index_name, index_data in result["indexes"].items():
            print(f"  {index_name}:")
            for metric, value in index_data.items():
                if metric != "Interpretation":
                    print(f"    {metric}: {value}")

if __name__ == "__main__":
    process_sample_data()