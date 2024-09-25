import threading
import os
from spark import load_data_from_hdfs, transform_data
from vizro import run_dashboard

os.environ['PYSPARK_PYTHON'] = r'C:\Users\bhate\Documents\ForVis\myenv\Scripts\pyspark_v3.5.2'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\bhate\Documents\ForVis\myenv\Scripts\pyspark_v3.5.2'

# Function to run the Spark ETL process
def run_spark_etl():
    print("Starting Spark ETL process...")

# Function to run the Vizro dashboard
def run_vizro():
    run_dashboard()  # Assuming this is the function that runs the dashboard in vizro.py

# Create threads for Spark ETL and Vizro dashboard
spark_thread = threading.Thread(target=run_spark_etl)
vizro_thread = threading.Thread(target=run_vizro)

# Start the threads
spark_thread.start()
vizro_thread.start()

# Join the threads to wait for their completion
spark_thread.join()
vizro_thread.join()
