# imports
import os
import matplotlib
import numpy as np
import pandas as pd
import fastf1 as ff1
from fastf1 import api
from fastf1 import utils
from fastf1 import plotting
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import fileConfig
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# enables cache, allows storage of race data locally
# ff1.Cache.enable_cache('formula/cache')

# patches matplotlib for time delta support
ff1.plotting.setup_mpl(mpl_timedelta_support = True, color_scheme = 'fastf1')

# gets race data from fastf1 based on input data parameter
# runs appropriate plot function based on user input
def get_race_data(input_data):
    try:
        year = int(input_data[0])
        gp = input_data[1]
        session = input_data[2]
        print(f"Loading data for {year} {gp} {session}")
        race = ff1.get_session(year, gp, session)
        race.load()
        print(f"Loaded data for {len(race.laps)} laps")
        print(f"Available drivers: {race.drivers}")
        
        if input_data[5] == 'Temperature and Tyre Life vs. Lap Time':
            plot_temp_tyre_laptime(race, input_data)
        elif input_data[5] == 'Lap Time':
            plot_laptime(race, input_data)
        elif input_data[5] == 'Fastest Lap':
            plot_fastest_lap(race, input_data)
        elif input_data[5] == 'Fastest Sectors':
            plot_fastest_sectors(race, input_data)
        elif input_data[5] == 'Full Telemetry':
            plot_full_telemetry(race, input_data)
        elif input_data[5] == 'Tyre Compound and Stint Analysis':
            plot_tyre_stint_analysis(race, input_data)
        elif input_data[5] == 'Position Changes':
            plot_position_changes(race, input_data)
    except Exception as e:
        print(f"An error occurred in get_race_data: {str(e)}")
        print("Error details:")
        import traceback
        traceback.print_exc()

# takes in speed/distance data for both drivers and determines which is faster
# returns dataframe of which driver was the fastest in each sector
def get_sectors(average_speed, input_data):
    sectors_combined = average_speed.groupby(['Driver', 'Minisector'])['Speed'].mean().reset_index()
    final = pd.DataFrame({
        'Driver': [],
        'Minisector': [],
        'Speed': []
    })

    d1 = sectors_combined.loc[sectors_combined['Driver'] == input_data[3].split()[0]]
    d2 = sectors_combined.loc[sectors_combined['Driver'] == input_data[4].split()[0]]

    for i in range(0, len(d1)): #issue, sometimes length of d1 is not 25
        d1_sector = d1.iloc[[i]].values.tolist()
        d1_speed = d1_sector[0][2]
        d2_sector = d2.iloc[[i]].values.tolist()
        d2_speed = d2_sector[0][2]
        if d1_speed > d2_speed:
            final.loc[len(final)] = d1_sector[0]
        else:
            final.loc[len(final)] = d2_sector[0]

    return final

# plots a laptime/distance comparison for both specified drivers
# returns a saved version of the generated plot
def plot_laptime(race, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    laps_d1 = race.laps.pick_driver(d1)
    laps_d2 = race.laps.pick_driver(d2)

    color1 = ff1.plotting.driver_color(input_data[3])
    color2 = ff1.plotting.driver_color(input_data[4])

    fig, ax = plt.subplots()
    ax.plot(laps_d1['LapNumber'], laps_d1['LapTime'], color = color1, label = input_data[3])
    ax.plot(laps_d2['LapNumber'], laps_d2['LapTime'], color = color2, label = input_data[4])
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time')
    ax.legend()
    plt.suptitle(f"Lap Time Comparison \n" f"{race.event.year} {race.event['EventName']} {input_data[2]}")

    if not os.path.exists(fileConfig.PLOT_DIR):
        os.makedirs(fileConfig.PLOT_DIR)
    img_path = os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)

# speed comaprison by distance for the fastest lap of both drivers
# returns a saved version of the generated plot
def plot_fastest_lap(race, input_data):
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    fastest_d1 = race.laps.pick_driver(d1).pick_fastest()
    fastest_d2 = race.laps.pick_driver(d2).pick_fastest()

    tel_d1 = fastest_d1.get_car_data().add_distance()
    tel_d2 = fastest_d2.get_car_data().add_distance()

    color1 = ff1.plotting.driver_color(input_data[3])
    color2 = ff1.plotting.driver_color(input_data[4])

    fig, ax = plt.subplots()
    ax.plot(tel_d1['Distance'], tel_d1['Speed'], color = color1, label = input_data[3])
    ax.plot(tel_d2['Distance'], tel_d2['Speed'], color = color2, label = input_data[4])
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Speed (km/h)')
    ax.legend()
    plt.suptitle(f"Fastest Lap Comparison \n" f"{race.event.year} {race.event['EventName']} {input_data[2]}")

    if not os.path.exists(fileConfig.PLOT_DIR):
        os.makedirs(fileConfig.PLOT_DIR)
    img_path = os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)


# compares the sector speeds for each driver, and generates a map of the circuit, with color coded sectors for the fastest driver.
# returns a saved version of the generated plot
def plot_fastest_sectors(race, input_data):
    plt.clf()
    laps = race.laps
    drivers = [input_data[3].split()[0], input_data[4].split()[0]]
    telemetry = pd.DataFrame()
    
    # list of each driver
    for driver in drivers:
        driver_laps = laps.pick_driver(driver)

        # gets telemetry data for each driver on each lap
        for lap in driver_laps.iterlaps():
            driver_telemtry = lap[1].get_telemetry().add_distance()
            driver_telemtry['Driver'] = driver
            driver_telemtry['Lap'] = lap[1]['LapNumber']

            telemetry = telemetry.append(driver_telemtry)

    # keeping important columns
    telemetry = telemetry[['Lap', 'Distance', 'Driver', 'Speed', 'X', 'Y']]

    # creating minisectors
    total_minisectors = 25
    telemetry['Minisector'] = pd.cut(telemetry['Distance'], total_minisectors, labels = False) + 1
    
    average_speed = telemetry.groupby(['Lap', 'Minisector', 'Driver'])['Speed'].mean().reset_index()
    
    # calls function to returns fastest driver in each sector
    best_sectors = get_sectors(average_speed, input_data)
    best_sectors = best_sectors[['Driver', 'Minisector']].rename(columns = {'Driver': 'fastest_driver'})

    # merges telemetry df with minisector df
    telemetry = telemetry.merge(best_sectors, on = ['Minisector'])
    telemetry = telemetry.sort_values(by = ['Distance'])

    telemetry.loc[telemetry['fastest_driver'] == input_data[3].split()[0], 'fastest_driver_int'] = 1
    telemetry.loc[telemetry['fastest_driver'] == input_data[4].split()[0], 'fastest_driver_int'] = 2
    
    # gets x,y data for a single lap. useful for drawing circuit.
    # x,y values can be inconsistent, causing strange behavior.
    single_lap = telemetry.loc[telemetry['Lap'] == int(input_data[6])]
    lap_x = np.array(single_lap['X'].values)
    lap_y = np.array(single_lap['Y'].values)

    # points and segments for drawing lap
    points = np.array([lap_x, lap_y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # grabs which driver (1/2) is fastest # POTENTIAL PROBLEM, ENSURE THIS IS BEST SECTOR DATA
    which_driver = single_lap['fastest_driver_int'].to_numpy().astype(float)

    # getting colormap for two drivers
    color1 = ff1.plotting.driver_color(input_data[3])
    color2 = ff1.plotting.driver_color(input_data[4])
    color1 = matplotlib.colors.to_rgb(color1)
    color2 = matplotlib.colors.to_rgb(color2)
    colors = [color1, color2]
    cmap = matplotlib.colors.ListedColormap(colors)

    lc_comp = LineCollection(segments, norm = plt.Normalize(1, cmap.N), cmap = cmap)
    lc_comp.set_array(which_driver)
    lc_comp.set_linewidth(2)

    plt.rcParams['figure.figsize'] = [6.25, 4.70]
    plt.suptitle(f"Average Fastest Sectors Lap {input_data[6]}\n" f"{race.event.year} {race.event['EventName']} {input_data[2]}") #edit
    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    legend_lines = [Line2D([0], [0], color = color1, lw = 1),
                    Line2D([0], [0], color = color2, lw = 1)]

    plt.legend(legend_lines, [input_data[3], input_data[4]])

    if not os.path.exists(fileConfig.PLOT_DIR):
        os.makedirs(fileConfig.PLOT_DIR)
    img_path = os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)

# plots a speed, throttle, brake, rpm, gear, and drs comparison for both drivers
# returns a saved version of the generated plot
def plot_full_telemetry(race, input_data): # speed, throttle, brake, rpm, gear, drs 
    plt.clf()
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    fastest_d1 = race.laps.pick_driver(d1).pick_fastest()
    fastest_d2 = race.laps.pick_driver(d2).pick_fastest()

    tel_d1 = fastest_d1.get_car_data().add_distance()
    tel_d1['Brake'] = tel_d1['Brake'].astype(int)
    tel_d2 = fastest_d2.get_car_data().add_distance()
    tel_d2['Brake'] = tel_d2['Brake'].astype(int)

    delta_time, ref_tel, compare_tel = utils.delta_time(fastest_d1, fastest_d2)

    telem_data_combined = [tel_d1, tel_d2]
    colors = [ff1.plotting.driver_color(input_data[3]), ff1.plotting.driver_color(input_data[4])]

    fig, ax = plt.subplots(6)
    for telem, color in zip(telem_data_combined, colors):
        ax[0].axhline(0, color = 'White', linewidth = .50)
        ax[0].plot(ref_tel['Distance'], delta_time, color = color, linewidth = .75)
        ax[1].plot(telem['Distance'], telem['Speed'], color = color, linewidth = .75)
        ax[2].plot(telem['Distance'], telem['Throttle'], color = color, linewidth = .75)
        ax[3].plot(telem['Distance'], telem['Brake'], color = color, linewidth = .75) # might have to convert to binary 
        ax[4].plot(telem['Distance'], telem['RPM'], color = color, linewidth = .75)
        ax[5].plot(telem['Distance'], telem['nGear'], color = color, linewidth = .75)

    ax[0].set(ylabel = 'Delta (s)')
    ax[1].set(ylabel = 'Speed')
    ax[2].set(ylabel = 'Throttle')
    ax[3].set(ylabel = 'Brake')
    ax[4].set(ylabel = 'RPM')
    ax[5].set(ylabel = 'Gear')

    plt.suptitle(f"Fastest Lap Telemetry - {input_data[3]} vs {input_data[4]} \n {race.event.year} {race.event['EventName']} {input_data[2]}")

    legend_lines = [Line2D([0], [0], color = colors[0], lw = 1),
        Line2D([0], [0], color = colors[1], lw = 1)]

    ax[0].legend(legend_lines, [input_data[3], input_data[4]], loc = 'lower right', prop={'size': 5})

    if not os.path.exists(fileConfig.PLOT_DIR):
        os.makedirs(fileConfig.PLOT_DIR)
    img_path = os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700)

def plot_tyre_stint_analysis(race, input_data):
    plt.clf()
    fig, ax = plt.subplots(figsize=(15, 10))
    fig.patch.set_facecolor('#2F2F2F')
    ax.set_facecolor('#2F2F2F')

    # Get list of drivers
    drivers = race.results['Abbreviation'].tolist()

    # Create a dictionary to store tyre data for each driver
    tyre_data = {driver: [] for driver in drivers}

    # Collect tyre data for each driver
    for driver in drivers:
        stints = race.laps.pick_driver(driver).groupby('Stint')
        for stint, data in stints:
            compound = data['Compound'].iloc[0]
            start_lap = data['LapNumber'].min()
            end_lap = data['LapNumber'].max()
            tyre_data[driver].append((start_lap, end_lap, compound))

    # Define colors for each compound
    compound_colors = {
        'SOFT': 'red',
        'MEDIUM': 'yellow',
        'HARD': 'white',
        'INTERMEDIATE': 'green',
        'WET': 'blue'
    }

    gap = 0.1  # Size of the gap between different tyre compounds

    # Plot tyre stints for each driver
    for i, (driver, stints) in enumerate(tyre_data.items()):
        previous_compound = None
        for start, end, compound in stints:
            if previous_compound and previous_compound != compound:
                # Add a small gap if the compound has changed
                start += gap / 2
            
            ax.barh(i, end - start, left=start, height=0.6, 
                    color=compound_colors.get(compound, 'gray'), alpha=0.7)
            ax.text((start + end) / 2, i, compound, ha='center', va='center', color='black', fontweight='bold')
            
            previous_compound = compound

    # Customize the plot
    ax.set_yticks(range(len(drivers)))
    ax.set_yticklabels(drivers, color='white')
    ax.set_xlabel('Lap Number', color='white')
    ax.set_title(f'Tyre Stint Analysis - {race.event.year} {race.event["EventName"]} {input_data[2]}', color='white')

    # Add a legend
    legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='none', alpha=0.7, label=compound)
                       for compound, color in compound_colors.items()]
    ax.legend(handles=legend_elements, loc='upper right', title='Tyre Compounds', facecolor='#2F2F2F', edgecolor='white')
    ax.get_legend().get_title().set_color('white')
    for text in ax.get_legend().get_texts():
        text.set_color('white')

    # Add grid lines
    ax.grid(True, axis='x', linestyle='--', alpha=0.3, color='white')

    # Set x-axis color to white
    ax.tick_params(axis='x', colors='white')

    # Adjust layout and save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png"), facecolor='#2F2F2F', edgecolor='none')
    plt.close(fig)

def plot_pitstop_impact(race, input_data):
    plt.clf()
    
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    laps_d1 = race.laps.pick_driver(d1)
    laps_d2 = race.laps.pick_driver(d2)

    fig, ax = plt.subplots(figsize=(15, 8))

    for driver, laps, color in zip([d1, d2], [laps_d1, laps_d2], ['blue', 'red']):
        ax.plot(laps['LapNumber'], laps['LapTime'], color=color, label=driver)
        
        pit_stops = laps[laps['PitOutTime'].notnull()]
        for _, pit_stop in pit_stops.iterrows():
            ax.axvline(x=pit_stop['LapNumber'], color=color, linestyle='--', alpha=0.5)
            ax.text(pit_stop['LapNumber'], ax.get_ylim()[1], f"{driver} Pit", 
                    rotation=90, verticalalignment='top', color=color)

    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time')
    ax.set_title(f'Pit Stop Impact on Race Pace\n{race.event.year} {race.event["EventName"]} {input_data[2]}')
    ax.legend()

    plt.tight_layout()
    
    if not os.path.exists(fileConfig.PLOT_DIR):
        os.makedirs(fileConfig.PLOT_DIR)
    img_path = os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=700, bbox_inches='tight')
    plt.close(fig)

def plot_position_changes(race, input_data):
    plt.clf()
    
    year = int(input_data[0])
    gp = input_data[1]
    session = input_data[2]
    d1 = input_data[3].split()[0]
    d2 = input_data[4].split()[0]

    print(f"Plotting position changes for {year} {gp} {session}")
    
    # Ensure we're using the correct race data
    race = ff1.get_session(year, gp, session)
    race.load()

    laps_d1 = race.laps.pick_driver(d1)
    laps_d2 = race.laps.pick_driver(d2)

    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor('#2F2F2F')
    ax.set_facecolor('#2F2F2F')

    colors = ['#00FFFF', '#FF69B4']  # Cyan and Hot Pink for better visibility
    for driver, laps, color in zip([d1, d2], [laps_d1, laps_d2], colors):
        # Get starting position
        try:
            starting_position = race.results.loc[race.results['Abbreviation'] == driver, 'GridPosition'].values[0]
        except IndexError:
            print(f"Warning: Starting position not found for {driver}. Using first lap position.")
            starting_position = laps['Position'].iloc[0] if not laps.empty else 20  # Default to last place if no data

        # Create a new DataFrame with starting position
        position_data = pd.DataFrame({'LapNumber': [0] + laps['LapNumber'].tolist(),
                                      'Position': [starting_position] + laps['Position'].tolist()})
        
        ax.plot(position_data['LapNumber'], position_data['Position'], color=color, label=f"{driver}", linewidth=2)
        
        # Highlight pit stops
        pit_stops = laps[laps['PitOutTime'].notnull()]
        for _, pit_stop in pit_stops.iterrows():
            ax.scatter(pit_stop['LapNumber'], pit_stop['Position'], color=color, s=100, marker='s')
            ax.annotate('Pit', (pit_stop['LapNumber'], pit_stop['Position']), xytext=(5, 5), 
                        textcoords='offset points', color=color, fontsize=10, fontweight='bold')

    # Highlight safety car periods
    safety_car_periods = race.laps['IsAccurate'] == False
    if safety_car_periods.any():
        safety_car_starts = race.laps.loc[safety_car_periods & ~safety_car_periods.shift(1, fill_value=False)]['LapNumber']
        safety_car_ends = race.laps.loc[safety_car_periods & ~safety_car_periods.shift(-1, fill_value=False)]['LapNumber']
        for start, end in zip(safety_car_starts, safety_car_ends):
            ax.axvspan(start, end, alpha=0.3, color='yellow')
            ax.annotate('SC', (start, ax.get_ylim()[0]), xytext=(0, 10), 
                        textcoords='offset points', color='yellow', fontsize=12, fontweight='bold')

    ax.set_xlabel('Lap Number', color='white', fontsize=12)
    ax.set_ylabel('Position', color='white', fontsize=12)
    ax.set_title(f'Position Changes Over Time\n{year} {gp} {session}', 
                 color='white', fontsize=16, fontweight='bold')
    
    ax.legend(fontsize=12, loc='upper right', facecolor='#2F2F2F', edgecolor='white', labelcolor='white')
    ax.grid(True, color='gray', alpha=0.3)
    ax.tick_params(colors='white', labelsize=10)
    
    ax.set_ylim(20.5, 0.5)  # Reverse y-axis and set integer ticks
    ax.set_yticks(range(1, 21))
    ax.set_xlim(left=0)

    plt.tight_layout()
    
    if not os.path.exists(fileConfig.PLOT_DIR):
        os.makedirs(fileConfig.PLOT_DIR)
    img_path = os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png")
    plt.savefig(img_path, dpi=300, bbox_inches='tight', facecolor='#2F2F2F')
    plt.close(fig)

    print(f"Position changes plot saved for {year} {gp} {session}")

def plot_temp_tyre_laptime(race, input_data):
    driver = input_data[3]
    laps = race.laps.pick_drivers(driver).reset_index()
    
    print(f"Total laps for {driver}: {len(laps)}")
    
    if len(laps) == 0:
        print(f"No lap data found for driver {driver}")
        return

    print("Available columns:", laps.columns.tolist())

    # Ensure required columns are present
    required_cols = ['LapNumber', 'LapTime', 'TyreLife', 'TrackStatus', 'LapStartDate']
    missing_cols = [col for col in required_cols if col not in laps.columns]
    if missing_cols:
        print(f"Missing columns: {missing_cols}")
        return

    # Convert LapTime to seconds
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    # Ensure TyreLife is numeric
    laps['TyreLife'] = pd.to_numeric(laps['TyreLife'], errors='coerce')

    # Sort by LapNumber
    laps = laps.sort_values(by='LapNumber')

    # Use TrackStatus as a proxy for Track Temperature if actual temperature is not available
    if 'TrackTemp' not in laps.columns:
        print("TrackTemp not found. Using TrackStatus as a proxy.")
        laps['TrackTemp'] = laps['TrackStatus'].astype(float)

    print("Data summary:")
    print(laps[['LapNumber', 'LapTimeSeconds', 'TyreLife', 'TrackTemp']].describe())
    print("\nFirst few rows:")
    print(laps[['LapNumber', 'LapTimeSeconds', 'TyreLife', 'TrackTemp']].head())

    if laps['LapTimeSeconds'].isnull().all() or laps['TyreLife'].isnull().all():
        print("All LapTimeSeconds or TyreLife values are null. Cannot plot.")
        return

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(12, 8))

    # Plot Lap Time vs. Tyre Life
    sns.scatterplot(x='TyreLife', y='LapTimeSeconds', data=laps, ax=ax1, hue='TrackTemp', palette='coolwarm', legend=False)
    sns.lineplot(x='TyreLife', y='LapTimeSeconds', data=laps, ax=ax1, color='blue', alpha=0.5)

    # Set axis labels and title
    ax1.set_xlabel('Tyre Life (Laps)')
    ax1.set_ylabel('Lap Time (seconds)')
    plt.title(f'{driver} - Tyre Life and Track Temperature vs Lap Time\n{race.event.year} {race.event["EventName"]} {input_data[2]}')

    # Add a color bar for the track temperature
    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(vmin=laps['TrackTemp'].min(), vmax=laps['TrackTemp'].max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax1)
    cbar.set_label('Track Temperature Proxy')

    # Add annotations for pit stops
    pit_stops = laps[laps['PitOutTime'].notnull()]
    for idx, pit_stop in pit_stops.iterrows():
        ax1.annotate('Pit', (pit_stop['TyreLife'], pit_stop['LapTimeSeconds']),
                     xytext=(5, 5), textcoords='offset points', ha='left', va='bottom',
                     bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                     arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    # Add a grid for better readability
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Adjust layout and save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png"))
    plt.close()

    print(f"Plot saved as {input_data[5]}.png")

def plot_any_function(race, input_data):
    year = int(input_data[0])
    gp = input_data[1]
    session = input_data[2]
    driver1 = input_data[3]
    driver2 = input_data[4]
    analysis_type = input_data[5]
    lap_number = input_data[6] if len(input_data) > 6 else None

    # Use these variables in your function
    # ...

    plt.title(f"{analysis_type}\n{year} {gp} {session}")
    # ... rest of the plotting code ...




