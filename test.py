import fastf1 as f1
season = 2023
try:
    schedule = f1.get_event_schedule(season)
    print(schedule)
except Exception as e:
    print(f"Error fetching 2023 schedule: {e}")
