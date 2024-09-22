import fastf1 as f1
import pandas as pd
from datetime import datetime
import pyarrow
import pyarrow._hdfs as pahdfs
import tempfile
from hdfs import InsecureClient

# Create a temporary directory for caching
temp_cache_dir = tempfile.gettempdir()

# Disable caching by setting a temporary directory
f1.Cache.enable_cache(temp_cache_dir)

# Specify the seasons you want to fetch data for
seasons = [2022, 2023, 2024]  # Add 2024 when it starts

def fetch_season_data(season):
    # Get all races in the season
    races = f1.get_event_schedule(season)
    for index, race in races.iterrows():
        event = race['EventName']
        race_date = race['EventDate']
        year = race['EventDate'].year
        round_number = race['RoundNumber']
        print(f"Fetching data for {event} - Round {round_number}, {year}")

        # Skip testing sessions
        if 'testing' in event.lower() or 'pre-season' in event.lower():
            print(f"Skipping testing event: {event}")
            continue
        
        # Fetch session data
        session = f1.get_session(year, round_number, 'R')  # 'R' stands for Race session
        session.load()  # Load all available data
        
        # Check if the session has lap data
        if session.laps is not None and not session.laps.empty:
            df = session.laps  # Access lap data
            
            # Convert to pandas DataFrame if needed
            df = pd.DataFrame(df)
            
            # Store to HDFS
            save_to_hdfs(df, season, event)
        else:
            print(f"No lap data available for {event}. Session status: {session.status}")

def save_to_hdfs(df, season, event):
    hdfs_path = f'/user/f1/data/{season}/{event}/laps.csv'
    client = InsecureClient('http://localhost:9870', user='hadoop')
    csv_data = df.to_csv(index=False).encode('utf-8')
    client.write(hdfs_path, csv_data, overwrite=True)
    print(f"Data for {event} saved to HDFS at {hdfs_path}")


# Loop through all specified seasons
for season in seasons:
    fetch_season_data(season)
