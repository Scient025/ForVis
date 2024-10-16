# imports
import os
import matplotlib
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import fileConfig2 

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Formula1Analysis") \
    .getOrCreate()

# Function to read data from HDFS
def read_hdfs_data(hdfs_path):
    return spark.read.parquet(hdfs_path)

# Function to get race data from HDFS based on input parameters
def get_race_data(input_data):
    year, event, session = input_data[0], input_data[1], input_data[2]
    
    hdfs_path = f"/user/f1/data/{year}/{event}/{session}/data.parquet"
    
    race_data = read_hdfs_data(hdfs_path)
    
    if input_data[5] == 'Lap Time':
        plot_laptime(race_data, input_data)
    elif input_data[5] == 'Fastest Lap':
        plot_fastest_lap(race_data, input_data)
    elif input_data[5] == 'Fastest Sectors':
        plot_fastest_sectors(race_data, input_data)
    elif input_data[5] == 'Full Telemetry':
        plot_full_telemetry(race_data, input_data)

# Function to get sectors data
def get_sectors(average_speed, input_data):
    sectors_combined = average_speed.groupBy("Driver", "Minisector").agg({"Speed": "mean"}).withColumnRenamed("avg(Speed)", "Speed")
    
    d1 = sectors_combined.filter(col("Driver") == input_data[3].split()[0])
    d2 = sectors_combined.filter(col("Driver") == input_data[4].split()[0])
    
    d1_pd = d1.toPandas()
    d2_pd = d2.toPandas()
    
    final = pd.DataFrame(columns=['Driver', 'Minisector', 'Speed'])
    
    for i in range(len(d1_pd)):
        d1_speed = d1_pd.iloc[i]['Speed']
        d2_speed = d2_pd.iloc[i]['Speed']
        if d1_speed > d2_speed:
            final = final.append(d1_pd.iloc[i], ignore_index=True)
        else:
            final = final.append(d2_pd.iloc[i], ignore_index=True)
    
    return final

# Function to plot lap time
def plot_laptime(race_data, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    laps_d1 = race_data.filter(col("Driver") == d1).toPandas()
    laps_d2 = race_data.filter(col("Driver") == d2).toPandas()

    color1 = 'red'
    color2 = 'blue'

    fig, ax = plt.subplots()
    ax.plot(laps_d1['LapNumber'], laps_d1['LapTime'], color=color1, label=input_data[3])
    ax.plot(laps_d2['LapNumber'], laps_d2['LapTime'], color=color2, label=input_data[4])
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time')
    ax.legend()
    plt.suptitle(f"Lap Time Comparison \n {input_data[0]} {input_data[1]} {input_data[2]}")

    if not os.path.exists(fileConfig2.PLOT_DIR):
        os.makedirs(fileConfig2.PLOT_DIR)
    img_path = os.path.join(fileConfig2.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)

# Function to plot fastest lap
def plot_fastest_lap(race_data, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    fastest_lap_d1 = race_data.filter(col("Driver") == d1).orderBy(col("LapTime").asc()).limit(1).toPandas()
    fastest_lap_d2 = race_data.filter(col("Driver") == d2).orderBy(col("LapTime").asc()).limit(1).toPandas()

    color1 = 'red'
    color2 = 'blue'

    fig, ax = plt.subplots()
    ax.plot(fastest_lap_d1['Distance'], fastest_lap_d1['Speed'], color=color1, label=input_data[3])
    ax.plot(fastest_lap_d2['Distance'], fastest_lap_d2['Speed'], color=color2, label=input_data[4])
    ax.set_xlabel('Distance')
    ax.set_ylabel('Speed')
    ax.legend()
    plt.suptitle(f"Fastest Lap Comparison \n {input_data[0]} {input_data[1]} {input_data[2]}")

    if not os.path.exists(fileConfig2.PLOT_DIR):
        os.makedirs(fileConfig2.PLOT_DIR)
    img_path = os.path.join(fileConfig2.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)

# Function to plot fastest sectors
def plot_fastest_sectors(race_data, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    sectors_d1 = race_data.filter(col("Driver") == d1).select("Sector1Time", "Sector2Time", "Sector3Time").toPandas()
    sectors_d2 = race_data.filter(col("Driver") == d2).select("Sector1Time", "Sector2Time", "Sector3Time").toPandas()

    fastest_sectors_d1 = sectors_d1.min()
    fastest_sectors_d2 = sectors_d2.min()

    sectors = ['Sector 1', 'Sector 2', 'Sector 3']
    x = np.arange(len(sectors))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x - width/2, fastest_sectors_d1, width, label=input_data[3])
    ax.bar(x + width/2, fastest_sectors_d2, width, label=input_data[4])

    ax.set_ylabel('Time')
    ax.set_title(f"Fastest Sectors Comparison \n {input_data[0]} {input_data[1]} {input_data[2]}")
    ax.set_xticks(x)
    ax.set_xticklabels(sectors)
    ax.legend()

    if not os.path.exists(fileConfig2.PLOT_DIR):
        os.makedirs(fileConfig2.PLOT_DIR)
    img_path = os.path.join(fileConfig2.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)

# Function to plot full telemetry
def plot_full_telemetry(race_data, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    telemetry_d1 = race_data.filter(col("Driver") == d1).toPandas()
    telemetry_d2 = race_data.filter(col("Driver") == d2).toPandas()

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

    ax1.plot(telemetry_d1['Distance'], telemetry_d1['Speed'], label=input_data[3])
    ax1.plot(telemetry_d2['Distance'], telemetry_d2['Speed'], label=input_data[4])
    ax1.set_ylabel('Speed')
    ax1.legend()

    ax2.plot(telemetry_d1['Distance'], telemetry_d1['Throttle'], label=input_data[3])
    ax2.plot(telemetry_d2['Distance'], telemetry_d2['Throttle'], label=input_data[4])
    ax2.set_ylabel('Throttle')
    ax2.legend()

    ax3.plot(telemetry_d1['Distance'], telemetry_d1['Brake'], label=input_data[3])
    ax3.plot(telemetry_d2['Distance'], telemetry_d2['Brake'], label=input_data[4])
    ax3.set_xlabel('Distance')
    ax3.set_ylabel('Brake')
    ax3.legend()

    plt.suptitle(f"Full Telemetry Comparison \n {input_data[0]} {input_data[1]} {input_data[2]}")

    if not os.path.exists(fileConfig2.PLOT_DIR):
        os.makedirs(fileConfig2.PLOT_DIR)
    img_path = os.path.join(fileConfig2.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)

# Stop the Spark session when you're done
spark.stop()