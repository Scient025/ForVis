import os
from hdfs import InsecureClient
import pandas as pd

# Base directory (the directory where the script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# HDFS configuration
HDFS_URL = "http://localhost:9870"  # Replace with your HDFS URL
HDFS_USER = "hdfs"  # Replace with your HDFS username
hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)

# Update HDFS data paths
HDFS_DATA_DIR = "/user/f1/data"

# ... (keep existing code for local directories)

# Update the read_hdfs_csv function to handle potential file not found errors
def read_hdfs_csv(hdfs_path):
    try:
        with hdfs_client.read(hdfs_path) as reader:
            return pd.read_csv(reader)
    except Exception as e:
        print(f"Error reading {hdfs_path}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if file is not found or other error occurs

# Function to get DataFrame based on user selection
def get_session_data(year, grand_prix, session):
    hdfs_path = f"{HDFS_DATA_DIR}/{year}/{grand_prix}/{session}_laps.csv"
    return read_hdfs_csv(hdfs_path)

# Function to print basic info about DataFrame
def print_df_info(df_name, df):
    print(f"{df_name} shape: {df.shape}")
    print(f"{df_name} columns: {df.columns.tolist()}")
    print(f"{df_name} first few rows:")
    print(df.head())
    print("\n")

# Note: The actual data reading and printing will be done when the user selects options in the GUI
