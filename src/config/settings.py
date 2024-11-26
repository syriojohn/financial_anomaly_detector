import os

# Application settings
APP_NAME = "Financial Anomaly Detector"
APP_VERSION = "1.0.0"

# Directory settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
PLOT_DIR = os.path.join(BASE_DIR, 'plots')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Ensure directories exist
for directory in [LOG_DIR, PLOT_DIR, DATA_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Analysis settings
DEFAULT_CONTAMINATION = 0.1  # Default contamination factor for Isolation Forest
MIN_SAMPLES = 100  # Minimum number of samples required for analysis
MAX_SAMPLES = 'auto'  # Maximum number of samples for Isolation Forest

# Feature engineering settings
WINDOW_SIZES = {
    'short': 5,
    'medium': 20,
    'long': 50
}

# GUI settings
WINDOW_SIZE = (1200, 800)
PLOT_SIZE = (800, 600)
MAX_RECENT_FILES = 5

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Plot settings
PLOT_DPI = 300
PLOT_STYLE = 'seaborn'
COLOR_PALETTE = 'husl'
