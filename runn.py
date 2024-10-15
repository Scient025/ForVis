from app import app  # Import the Dash app
from spark import spark  # Import the Spark session
import threading

# Function to run Spark processing in a separate thread
def run_spark_processing():
    # You can add any Spark processing code here if needed
    # For example, you can load your data or perform transformations here
    print("Starting Spark processing...")

# Start the Spark processing in a separate thread
spark_thread = threading.Thread(target=run_spark_processing)
spark_thread.start()

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
