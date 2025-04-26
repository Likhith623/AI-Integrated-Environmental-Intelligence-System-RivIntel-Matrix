import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample climate data for demonstration"""
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='M')
    data = {
        'date': dates,
        'temperature': np.random.normal(25, 5, len(dates)),
        'water_level': np.random.normal(100, 10, len(dates)),
        'pollution_level': np.random.normal(50, 15, len(dates))
    }
    return pd.DataFrame(data)

def get_climate_data():
    """
    Get climate data for visualization.
    
    Returns:
        dict: Climate data including current status and predictions
    """
    # Generate sample data
    df = generate_sample_data()
    
    # Get current status (last month's data)
    current = df.iloc[-1].to_dict()
    
    # Generate predictions for next 12 months
    future_dates = pd.date_range(
        start=df['date'].iloc[-1] + timedelta(days=30),
        periods=12,
        freq='M'
    )
    
    predictions = {
        'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
        'temperature': list(np.random.normal(current['temperature'], 2, 12)),
        'water_level': list(np.random.normal(current['water_level'], 5, 12)),
        'pollution_level': list(np.random.normal(current['pollution_level'], 8, 12))
    }
    
    return {
        'current': {
            'temperature': float(current['temperature']),
            'water_level': float(current['water_level']),
            'pollution_level': float(current['pollution_level']),
            'date': current['date'].strftime('%Y-%m-%d')
        },
        'historical': {
            'dates': [d.strftime('%Y-%m-%d') for d in df['date']],
            'temperature': list(df['temperature']),
            'water_level': list(df['water_level']),
            'pollution_level': list(df['pollution_level'])
        },
        'predictions': predictions
    } 