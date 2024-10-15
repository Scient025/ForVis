import vizro
from spark import load_data_from_hdfs, transform_data
import vizro.models as vm


# Filters for user input
year_filter = vm.Filter(column="Year", selector=vm.Dropdown(options=[2022, 2023, 2024]))
driver_filter = vm.Filter(column="Driver", selector=vm.Dropdown(options=[
    "VER", "LEC", "NOR", "PIA", "SAI", "HAM", "RUS", "PER", "ALO", "HUL", 
    "STR", "TSU", "ALB", "RIC", "GAS", "MAG", "OCO", "ZHO", "SAR", "BOT"
]))
track_filter = vm.Filter(column="Track", selector=vm.Dropdown(options=[
    "Italian Grand Prix", "Australian Grand Prix", "British Grand Prix"
]))
session_filter = vm.Filter(column="Session", selector=vm.Dropdown(options=[
    "FP1", "FP2", "FP3", "Qualifying", "Race"
]))

# Dashboard layout
dashboard = vm.Page(
    title="F1 Telemetry Dashboard",
    components=[
        year_filter,
        driver_filter,
        track_filter,
        session_filter,
        # Add visualization components here (e.g., charts)
    ],
)

# Function to update data based on selections
def update_data():
    try:
        selected_year = year_filter.value
        selected_driver = driver_filter.value
        selected_track = track_filter.value
        selected_session = session_filter.value

    # Load data based on user selections
    df = load_data_from_hdfs(selected_year, selected_track, selected_session)
    transformed_data = transform_data(df, selected_driver)
    
    # need to put some telemetric data code here
        # Load data based on user selections
        df = load_data_from_hdfs(selected_year, selected_track, selected_session)
        if df is not None and not df.isEmpty():
            transformed_data = transform_data(df, selected_driver)
            
            # Update visualizations here with transformed_data
            if transformed_data is not None:
                print(f"Updating visualizations for {selected_driver} in {selected_year} {selected_session}")
                # Code to update visualizations goes here
            else:
                print("No data after transformation.")
        else:
            print("No data loaded.")
    except Exception as e:
        print(f"Error updating data: {e}")

# Set up event listeners to call update_data() when selections change
year_filter.on_change(update_data)
driver_filter.on_change(update_data)
track_filter.on_change(update_data)
session_filter.on_change(update_data)

# Launch the dashboard
def run_dashboard():
    vizro.run(dashboard)
