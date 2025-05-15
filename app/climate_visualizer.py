import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
import os
import json
from functools import lru_cache

# Global pre-calculated data that stays in memory permanently
_GLOBAL_CLIMATE_DATA = None
_GLOBAL_TEMP_HISTORY = None
_GLOBAL_WATER_HISTORY = None

# Cache file location
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'climate_cache.json')
# Cache expiration time (30 minutes)
CACHE_EXPIRY = 1800

def generate_sample_data():
    """Generate sample climate data with minimal computation"""
    global _GLOBAL_TEMP_HISTORY, _GLOBAL_WATER_HISTORY
    
    # If we already have pre-generated data, return it immediately
    if _GLOBAL_TEMP_HISTORY is not None and _GLOBAL_WATER_HISTORY is not None:
        return pd.DataFrame({
            'date': pd.date_range(end=datetime.now(), periods=12, freq='M'),
            'temperature': _GLOBAL_TEMP_HISTORY,
            'water_level': _GLOBAL_WATER_HISTORY,
            'pollution_level': _GLOBAL_WATER_HISTORY * 0.5  # Derive from water level for speed
        })
    
    # Generate minimal data points - only 12 months
    dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
    size = len(dates)
    
    # Use fixed seed and values for consistent, fast generation
    np.random.seed(42)
    
    # Pre-generate and store these arrays for future reuse
    _GLOBAL_TEMP_HISTORY = 25 + 5 * np.random.normal(0, 1, size=size)
    _GLOBAL_WATER_HISTORY = 100 + 10 * np.random.normal(0, 1, size=size)
    
    # Create DataFrame with minimal computation
    return pd.DataFrame({
        'date': dates,
        'temperature': _GLOBAL_TEMP_HISTORY,
        'water_level': _GLOBAL_WATER_HISTORY,
        'pollution_level': _GLOBAL_WATER_HISTORY * 0.5  # Derive from water level for speed
    })

def get_climate_data(use_cache=True):
    """
    Get climate data for visualization with aggressive caching.
    
    Args:
        use_cache: Whether to use cached data (default True)
    
    Returns:
        dict: Climate data including current status and predictions
    """
    global _GLOBAL_CLIMATE_DATA
    
    # Fast path: return global pre-calculated data if available
    if _GLOBAL_CLIMATE_DATA is not None:
        return _GLOBAL_CLIMATE_DATA
    
    # Try to load from disk cache
    if use_cache:
        try:
            if os.path.exists(CACHE_FILE):
                file_age = time.time() - os.path.getmtime(CACHE_FILE)
                if file_age < CACHE_EXPIRY:
                    with open(CACHE_FILE, 'r') as f:
                        _GLOBAL_CLIMATE_DATA = json.load(f)
                        return _GLOBAL_CLIMATE_DATA
        except Exception as e:
            print(f"Cache load error (continuing with fresh data): {e}")
    
    # Generate minimal sample data
    df = generate_sample_data()
    
    # Extract values directly, with minimal processing
    current_temp = float(df['temperature'].iloc[-1])
    current_water = float(df['water_level'].iloc[-1])
    current_date = df['date'].iloc[-1]
    
    # Highly simplified future predictions - use just 6 points with minimal calculations
    future_temps = current_temp + np.random.normal(0, 0.5, 6)
    future_water = current_water + np.random.normal(0, 1, 6)
    
    # Minimize formatting operations
    historical_dates = [f"{d.month:02d}-{d.day:02d}" for d in df['date']]
    future_dates = [f"{(current_date + timedelta(days=30*i)).month:02d}-{(current_date + timedelta(days=30*i)).day:02d}" for i in range(1, 7)]
    
    # Create highly optimized output - rounded values, smaller data
    result = {
        'current': {
            'temperature': round(current_temp, 1),
            'water_level': round(current_water, 1),
            'pollution_level': round(current_water * 0.5, 1),
            'date': current_date.strftime('%m-%d')
        },
        'historical': {
            'dates': historical_dates,
            'temperature': [round(x, 1) for x in df['temperature']],
            'water_level': [round(x, 1) for x in df['water_level']]
        },
        'predictions': {
            'dates': future_dates,
            'temperature': [round(x, 1) for x in future_temps],
            'water_level': [round(x, 1) for x in future_water]
        }
    }
    
    # Save to global cache
    _GLOBAL_CLIMATE_DATA = result
    
    # Save to disk cache without blocking
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(result, f)
    except Exception as e:
        print(f"Cache save error: {e}")
    
    return result

def precalculate_climate_data():
    """Pre-calculate climate data to make it instantly available when needed"""
    global _GLOBAL_CLIMATE_DATA
    
    # If data is already calculated, don't recalculate
    if _GLOBAL_CLIMATE_DATA is not None:
        return _GLOBAL_CLIMATE_DATA
        
    # Force fresh calculation
    _GLOBAL_CLIMATE_DATA = get_climate_data(use_cache=False)
    print("Climate data pre-calculated and cached")
    return _GLOBAL_CLIMATE_DATA

# Pre-calculate on module import for instant availability
try:
    precalculate_climate_data()
except Exception as e:
    print(f"Error pre-calculating climate data: {e}") 