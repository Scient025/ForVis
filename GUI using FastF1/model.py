import fastf1 as ff1
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def collect_race_data(year, race_round):
    session = ff1.get_session(year, race_round, 'R')
    session.load()

    data = []
    for lap in session.laps.iterlaps():
        lap_time = lap[1]['LapTime'].total_seconds()
        driver = lap[1]['Driver']
        lap_number = lap[1]['LapNumber']
        data.append({'Driver': driver, 'LapTime': lap_time, 'LapNumber': lap_number})

    return pd.DataFrame(data)

def prepare_data_for_model(race_data, rolling_window=5, slow_threshold=2, consistency_required=3):
    race_data['AvgLapTime'] = race_data.groupby('Driver')['LapTime'].transform(lambda x: x.rolling(window=rolling_window, min_periods=1).mean())
    race_data['SlowLap'] = race_data['LapTime'] < (race_data['AvgLapTime'] - slow_threshold)
    race_data['ConsecutiveSlows'] = race_data.groupby('Driver')['SlowLap'].transform(lambda x: x.cumsum())
    race_data['PitStop'] = (race_data['ConsecutiveSlows'] >= consistency_required).astype(int)

    features = race_data[['LapTime', 'AvgLapTime']]
    labels = race_data['PitStop']
    return features, labels

def train_model():
    race_data = collect_race_data(2023, 5)
    X, y = prepare_data_for_model(race_data)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, 'model.pkl')

def predict(input_data):
    try:
        model = joblib.load('model.pkl')
        return model.predict([input_data])
    except FileNotFoundError:
        raise FileNotFoundError("Model file not found. Please ensure 'model.pkl' is in the correct directory.")

def load_and_predict(driver_code):
    race_data = collect_race_data(2023, 5)
    driver_data = race_data[race_data['Driver'] == driver_code]
    X, _ = prepare_data_for_model(driver_data)
    model = joblib.load('model.pkl')
    predictions = model.predict(X)
    return predictions
