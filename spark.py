from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("F1 telemetric processing") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate() 

def load_data_from_hdfs(season, event, session_type):
    hdfs_path = f"hdfs://localhost:9870/user/f1/data/{season}/{event}/{session_type}_laps.csv"
    df = spark.read.csv(hdfs_path, header=True, inferSchema=True)
    return df

def transform_data(df, driver_name):
    return df.filter(df['Driver'] == driver_name)
