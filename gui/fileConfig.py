import os

# Base directory (the directory where the script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data and image paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMG_DIR = os.path.join(BASE_DIR, 'img')
PLOT_DIR = os.path.join(BASE_DIR, 'plot')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# Paths for data files
EVENTS_CSV = os.path.join(DATA_DIR, 'events.csv')
DRIVERS_CSV = os.path.join(DATA_DIR, 'drivers.csv')
RACE_LAPS_CSV = os.path.join(DATA_DIR, 'laps.csv')
PLACEHOLDER_IMG = os.path.join(IMG_DIR, 'placeholder.png')
