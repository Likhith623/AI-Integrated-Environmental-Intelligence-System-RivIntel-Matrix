import cv2
import numpy as np
from datetime import datetime
import os

def detect_drowning(video_file):
    """
    Analyze video for potential drowning incidents using OpenCV.
    
    Args:
        video_file: Uploaded video file
        
    Returns:
        dict: Analysis results including alerts and timestamps
    """
    # Save the uploaded file temporarily
    temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    video_file.save(temp_path)
    
    # Initialize video capture
    cap = cv2.VideoCapture(temp_path)
    if not cap.isOpened():
        return {'error': 'Could not open video file'}
    
    # Initialize variables
    frame_count = 0
    alerts = []
    motion_threshold = 5000  # Adjust based on testing
    
    # Process video frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply motion detection
        if frame_count > 1:
            # Calculate absolute difference between frames
            diff = cv2.absdiff(prev_gray, gray)
            motion = np.sum(diff)
            
            # Check for significant motion
            if motion > motion_threshold:
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                alerts.append({
                    'timestamp': timestamp,
                    'motion_level': float(motion),
                    'frame': frame_count
                })
        
        prev_gray = gray.copy()
    
    # Clean up
    cap.release()
    os.remove(temp_path)
    
    return {
        'total_frames': frame_count,
        'alerts': alerts,
        'potential_incidents': len(alerts)
    } 