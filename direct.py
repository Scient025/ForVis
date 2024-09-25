import fastf1 as f1
import pandas as pd
import requests
from datetime import datetime
from hdfs import InsecureClient
import tempfile

# caching mc
temp_cache_dir = tempfile.gettempdir()

# Enable caching using the temporary directory
f1.Cache.enable_cache(temp_cache_dir)

# have to manually remove the seasons cuz i failed a simple for loop logic
seasons = [2022, 2023, 2024]

# Ergast API URL template
ergast_url_template = "https://ergast.com/api/f1/{year}/{round}/laps.json"

#  FP = Free Practices, Q = Qualifying, R = Race)
session_types = ['FP1', 'FP2', 'FP3', 'Q', 'R']

def fetch_season_data(season):
    
    races = f1.get_event_schedule(season)
    for index, race in races.iterrows():
        event = race['EventName']
        year = race['EventDate'].year
        round_number = race['RoundNumber']
        print(f"Fetching data for {event} - Round {round_number}, {year}")

        # Skip testing 
        if 'testing' in event.lower() or 'pre-season' in event.lower():
            print(f"Skipping testing event: {event}")
            continue

        # Loop 
        for session_type in session_types:
            print(f"Fetching {session_type} session for {event}.")
            try:
                # Fetch session data from FastF1
                session = f1.get_session(year, round_number, session_type)
                session.load()  # Load all available data

                # Check if FastF1 has valid data
                if session.laps is not None and not session.laps.empty:
                    df = pd.DataFrame(session.laps)  # Convert lap data to DataFrame
                    print(f"{session_type} data for {event} fetched successfully from FastF1.")
                    # Store data to HDFS
                    save_to_hdfs(df, season, event, session_type)
                else:
                    print(f"No lap data from FastF1 for {event} {session_type}. Trying Ergast API.")
                    # Fetch data from Ergast API if FastF1 returns empty data
                    fetch_from_ergast(season, round_number, event, session_type)
                    
            except Exception as e:
                print(f"FastF1 API failed for {event} {session_type}: {e}. Trying Ergast API.")
                # Fetch data from Ergast API if FastF1 fails
                fetch_from_ergast(season, round_number, event, session_type)

def fetch_from_ergast(year, round_number, event, session_type):
    # Build the Ergast API request URL
    ergast_url = ergast_url_template.format(year=year, round=round_number)
    try:
        response = requests.get(ergast_url)
        response.raise_for_status()  # Raise exception for any failed request
        data = response.json()
        
        # Process Ergast API response to extract lap data 
        if 'MRData' in data and 'RaceTable' in data['MRData']:
            races = data['MRData']['RaceTable']['Races']
            if races:
                # Assuming lap data is nested in the race structure; customize as needed
                race_data = races[0].get('Laps', [])
                df = pd.json_normalize(race_data)  # Convert to pandas DataFrame
                if not df.empty:
                    print(f"{session_type} data for {event} fetched successfully from Ergast API.")
                    # Store data to HDFS
                    save_to_hdfs(df, year, event, session_type)
                else:
                    print(f"No lap data found in Ergast API for {event} {session_type}.")
            else:
                print(f"No race data found in Ergast API for {event} {session_type}.")
        else:
            print(f"Invalid response structure from Ergast API for {event} {session_type}.")
            
    except Exception as e:
        print(f"Failed to fetch data from Ergast API for {event} {session_type}: {e}")

def save_to_hdfs(df, season, event, session_type):
    # Save data to HDFS with session type in the path
    hdfs_path = f'/user/f1/data/{season}/{event}/{session_type}_laps.csv'
    client = InsecureClient('<your local host and port 9870', user='<your user>')
    
    # Save DataFrame directly to CSV in HDFS
    with client.write(hdfs_path, encoding='utf-8', overwrite=True) as writer:
        df.to_csv(writer, index=False)
    
    print(f"{session_type} data for {event} saved to HDFS at {hdfs_path}")


# Loop through all specified seasons
for season in seasons:
    fetch_season_data(season)
