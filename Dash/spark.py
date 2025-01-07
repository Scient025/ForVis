from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, from_json
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, MapType
from hdfs import InsecureClient

hdfs_client = InsecureClient('http://localhost:9870', user='hadoop')

def create_hdfs_directory(hdfs_path):
    try:
        # Create HDFS directory using the hdfs library
        hdfs_client.makedirs(hdfs_path)
        print(f"Successfully created HDFS directory: {hdfs_path}")
    except Exception as e:
        print(f"Failed to create HDFS directory: {e}")

# Initialize Spark session

spark = SparkSession.builder \
    .appName("F1 Telemetric Processing") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .config("spark.ui.port", "0") \
    .config("spark.hadoop.dfs.client.max.block.size", "2147483648") \
    .config("spark.hadoop.dfs.blocksize", "134217728") \
    .config("spark.rpc.message.maxSize", "2146435072") \
    .getOrCreate()


spark.sparkContext.setLogLevel("WARN")

metadata_directory = "/user/f1/data/metadata"

create_hdfs_directory(metadata_directory)

def load_data_from_hdfs(season, event, session_type):
    try:
        hdfs_path = f"hdfs://localhost:9000/user/f1/data/{season}/{event}/{session_type}_laps.csv"
        df = spark.read.csv(hdfs_path, header=True, inferSchema=True)
        print(f"Successfully loaded data from {hdfs_path}")
        return df
    except Exception as e:
        print(f"Error loading data from HDFS: {e}")
        return None


def transform_data(df, driver_name):
    try:
        # Define schema for the Timings column (array of map where key and value are strings)
        schema = ArrayType(MapType(StringType(), StringType()))
        
        # Parse the Timings column
        df_parsed = df.withColumn("Timings", from_json(col("Timings"), schema))
        
        # Check for successful parsing
        if df_parsed.filter(col("Timings").isNull()).count() > 0:
            print("Warning: Some rows have null values in the Timings column after parsing.")
        
        # Explode the Timings to create a row for each driver's timing
        df_exploded = df_parsed.select(col("number"), explode(col("Timings")).alias("Timing"))
        
        # Filter data for the specific driver
        driver_data = df_exploded.filter(col("Timing.driverId") == driver_name).select("number", "Timing.position", "Timing.time")
        
        return driver_data
    except Exception as e:
        print(f"Error transforming data: {e}")
        return None
