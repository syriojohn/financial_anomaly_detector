import pandas as pd
import numpy as np

def calculate_ratios(data):
    """
    Calculate various financial ratios from the input data.
    
    Args:
        data (pd.DataFrame): Input financial data
        
    Returns:
        pd.DataFrame: DataFrame with calculated ratios
    """
    ratios = pd.DataFrame(index=data.index)
    
    # Price ratios
    if 'High' in data.columns and 'Low' in data.columns:
        ratios['price_range'] = (data['High'] - data['Low']) / data['Low']
    
    if 'Close' in data.columns and 'Open' in data.columns:
        ratios['price_change'] = (data['Close'] - data['Open']) / data['Open']
    
    # Volume based ratios
    if 'Volume' in data.columns and 'Close' in data.columns:
        ratios['volume_price_ratio'] = data['Volume'] * data['Close']
        
        # Calculate moving averages of volume
        ratios['volume_ma5'] = data['Volume'].rolling(window=5).mean()
        ratios['volume_ma20'] = data['Volume'].rolling(window=20).mean()
        
        # Volume ratio
        ratios['volume_ratio'] = data['Volume'] / ratios['volume_ma5']
    
    # Technical indicators
    if 'Close' in data.columns:
        # Moving averages
        ratios['ma5'] = data['Close'].rolling(window=5).mean()
        ratios['ma20'] = data['Close'].rolling(window=20).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        ratios['RSI'] = 100 - (100 / (1 + rs))
        
        # Volatility
        ratios['volatility'] = data['Close'].rolling(window=20).std()
    
    return ratios.fillna(0)  # Replace NaN values with 0

def prepare_features(data, feature_options):
    """
    Prepare features for anomaly detection based on selected options.
    
    Args:
        data (pd.DataFrame): Input financial data
        feature_options (dict): Dictionary of feature options
        
    Returns:
        np.ndarray: Prepared feature matrix
    """
    features = []
    ratios = calculate_ratios(data)
    
    for feature_name, options in feature_options.items():
        if feature_name in data.columns:
            if options.get('use_raw', True):
                features.append(data[feature_name].values.reshape(-1, 1))
            if options.get('use_ratio', True) and feature_name in ratios.columns:
                features.append(ratios[feature_name].values.reshape(-1, 1))
    
    if not features:
        raise ValueError("No features selected for analysis")
    
    return np.hstack(features)
