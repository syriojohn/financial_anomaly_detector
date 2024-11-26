import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def setup_plot_style():
    """Set up the plotting style for consistent visualization"""
    plt.style.use('seaborn')
    sns.set_palette("husl")
    
def create_time_series_plot(data, anomaly_scores, anomalies, feature_name, save_dir):
    """
    Create a time series plot highlighting anomalies.
    
    Args:
        data (pd.Series): Time series data
        anomaly_scores (np.ndarray): Anomaly scores
        anomalies (np.ndarray): Boolean array indicating anomalies
        feature_name (str): Name of the feature being plotted
        save_dir (str): Directory to save the plot
    """
    setup_plot_style()
    plt.figure(figsize=(12, 6))
    
    # Plot the time series
    plt.plot(data.index, data.values, label='Original Data', alpha=0.7)
    
    # Highlight anomalies
    anomaly_points = data[anomalies]
    plt.scatter(anomaly_points.index, anomaly_points.values, 
               color='red', label='Anomalies', zorder=5)
    
    plt.title(f'Anomalies in {feature_name}')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save plot
    filename = f"{feature_name.lower().replace(' ', '_')}_anomalies.png"
    plt.savefig(os.path.join(save_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()

def create_score_distribution_plot(anomaly_scores, threshold, save_dir):
    """
    Create a distribution plot of anomaly scores.
    
    Args:
        anomaly_scores (np.ndarray): Array of anomaly scores
        threshold (float): Threshold used for anomaly detection
        save_dir (str): Directory to save the plot
    """
    setup_plot_style()
    plt.figure(figsize=(10, 6))
    
    # Plot the distribution
    sns.histplot(anomaly_scores, bins=50, kde=True)
    
    # Add threshold line
    plt.axvline(x=threshold, color='r', linestyle='--', 
                label=f'Threshold ({threshold:.2f})')
    
    plt.title('Distribution of Anomaly Scores')
    plt.xlabel('Anomaly Score')
    plt.ylabel('Count')
    plt.legend()
    
    # Save plot
    plt.savefig(os.path.join(save_dir, 'score_distribution.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_feature_correlation_plot(data, save_dir):
    """
    Create a correlation heatmap of features.
    
    Args:
        data (pd.DataFrame): DataFrame containing features
        save_dir (str): Directory to save the plot
    """
    setup_plot_style()
    plt.figure(figsize=(10, 8))
    
    # Calculate and plot correlation matrix
    corr = data.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm', center=0,
                fmt='.2f', square=True, linewidths=0.5)
    
    plt.title('Feature Correlation Matrix')
    
    # Save plot
    plt.savefig(os.path.join(save_dir, 'feature_correlation.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
