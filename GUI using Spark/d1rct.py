from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Initialize a Spark session
spark = SparkSession.builder \
    .appName("F1DataFromHDFS") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://<hdfs-cluster-ip>:9000") \
    .getOrCreate()

# Function to read data from HDFS
def read_hdfs_data(file_path):
    # Use spark to read the data from HDFS
    df = spark.read.option("header", "true").csv(file_path)
    return df

# Function to retrieve specific driver data from the HDFS-stored dataset
def get_driver_data_from_hdfs(driver_id):
    # HDFS path where F1 data is stored
    hdfs_file_path = 'hdfs://<hdfs-cluster-ip>:9000/path/to/f1_driver_data.csv'
    
    # Read data from HDFS
    f1_data_df = read_hdfs_data(hdfs_file_path)
    
    # Filter data based on driverId
    driver_data_df = f1_data_df.filter(f1_data_df['driverId'] == driver_id)
    
    # Show the filtered driver data
    driver_data_df.show()

    return driver_data_df

# Function to convert driver data into telemetry format
def convert_to_telemetry(df):
    # Select only telemetry-related columns
    telemetry_df = df.select("lapNumber", "speed", "throttle", "brake", "gear", "rpm", "driverId")
    
    # Calculate speed difference between consecutive laps
    window_spec = Window.partitionBy("driverId").orderBy("lapNumber")
    telemetry_df = telemetry_df.withColumn("speed_diff", F.lag("speed").over(window_spec))

    # Show the telemetry data with the calculated speed difference
    telemetry_df.show()
    return telemetry_df

# Example usage
if __name__ == "__main__":
    # Specify the driver ID (e.g., 33 for Max Verstappen)
    driver_id = 33
    
    # Fetch driver data from HDFS
    driver_data = get_driver_data_from_hdfs(driver_id)
    
    # Convert the driver data into telemetry format
    telemetry_data = convert_to_telemetry(driver_data)
