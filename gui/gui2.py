import os
import sys
import shutil
import threading
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QComboBox, QApplication, QWidget, 
                             QGridLayout, QLabel, QPushButton, 
                             QProgressBar, QMessageBox, QSizePolicy)
from pyspark.sql import SparkSession
# imports script2.py, used for creating plots
import fileConfig2
import script2

# Spark session setup
spark = SparkSession.builder.appName("F1Analysis").getOrCreate()

# Read data from HDFS
race_df = spark.read.csv(fileConfig2.HDFS_RACE_CSV, header=True, inferSchema=True).toPandas()

# Extract unique events (assuming we have only one event per file)
events = [race_df['LapStartDate'].iloc[0].split()[0]]  # Extract date as event

# Extract unique drivers
drivers = race_df['Driver'].unique().tolist()

# Extract unique teams
teams = race_df['Team'].unique().tolist()

# Get total number of laps
total_laps = race_df['LapNumber'].max()

# Placeholder path
placeholder_path = fileConfig2.PLACEHOLDER_IMG

# active race year (extract from the date)
year = [race_df['LapStartDate'].iloc[0].split('-')[0]]

# values for dropdown labels
driver_name = ['Select Driver'] + drivers
location = ['Select Location']  # You might need to add this information manually
session = ['Race']  # Since this is race data
analysis_type = ['Lap Time', 'Fastest Lap', 'Fastest Sectors', 'Full Telemetry']

# stylesheet for the application
StyleSheet = '''
QWidget {
    background-color: #e8f5e9;  /* Light green background */
}

QFrame {
    border: 1px solid #cccccc;
    border-radius: 10px;
}

QPushButton {
    background-color: #1976d2;  /* Blue button */
    color: white;
    border: none;
    padding: 12px;
    border-radius: 5px;
    font-size: 14pt;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565c0;  /* Darker blue on hover */
}

QProgressBar {
    min-height: 15px;
    max-height: 15px;
    border-radius: 2px;
}

QProgressBar::chunk {
    border-radius: 2px;
    background-color: #d32f2f;  /* Red progress bar */
    opacity: 1;
}

QLabel {
    font-size: 12pt;
    font-weight: 500;
    font-family: 'Arial', sans-serif;
}

.title {
    font-size: 24pt;  /* Increased title size */
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}

.description {
    font-size: 12pt;  /* Increased description size */
    color: #666;
    margin-bottom: 20px;
}

.header-area {
    background-color: #bbdefb;  /* Light blue background */
    padding: 10px;
    border-radius: 10px;
}

.fields-area {
    background-color: #ffffff;  /* White background for fields */
    padding: 10px;
    margin-top: 10px;
    border-radius: 10px;
}

.plot-area {
    background-color: #bbdefb;  /* Light blue background for plot area */
    padding: 10px;
    margin-top: 10px;
    border-radius: 10px;
}

QComboBox {
    font-size: 14pt;  /* Increased font size for dropdowns */
    padding: 5px;
}
'''

# defines progress bar
class ProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super(ProgressBar, self).__init__(*args, **kwargs)
        self.setValue(0)
        self.setTextVisible(True)
        self.setRange(0, 0)  # Indeterminate mode

# main gui window 
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.UIComponents()

    def initUI(self):
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height())
        self.setWindowTitle('Formula 1 Telemetry Analytics')
        self.setWindowIcon(QtGui.QIcon(os.path.join(fileConfig2.IMG_DIR, 'f1.png')))
        self.setStyleSheet(StyleSheet)

    def UIComponents(self):
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        # Title and Description
        header_area = QWidget()
        header_layout = QGridLayout()
        header_area.setLayout(header_layout)

        title = QLabel("Formula 1 Telemetry Analytics")
        title.setStyleSheet("class: title")
        header_layout.addWidget(title, 0, 0)

        description = QLabel("Analyze race telemetry data and visualize performance metrics.")
        description.setStyleSheet("class: description")
        header_layout.addWidget(description, 1, 0)

        grid_layout.addWidget(header_area, 0, 0, 1, 2)
        header_area.setStyleSheet("class: header-area")

        # Dropdowns
        fields_area = QWidget()
        fields_layout = QGridLayout()
        fields_area.setLayout(fields_layout)
        grid_layout.addWidget(fields_area, 1, 0)
        fields_area.setStyleSheet("class: fields-area")

        self.year_combo = QComboBox()
        self.location_combo = QComboBox()
        self.session_combo = QComboBox()
        self.driver_combo = QComboBox()
        self.analysis_combo = QComboBox()

        self.warning_box = QMessageBox(self)
        self.warning_box.setWindowTitle('Error!')
        self.warning_box.setText('Select a valid race year.')
        self.warning_box.setDefaultButton(QMessageBox.Ok)

        labels = [
            QLabel('Year:'),
            QLabel('Grand Prix Location:'),
            QLabel('Session:'),
            QLabel('Driver:'),
            QLabel('Analysis Type:')
        ]

        self.generate_button = QPushButton('Generate')
        self.save_button = QPushButton('Save Plot to Desktop')

        self.progress = ProgressBar(self, textVisible=False)

        self.year_combo.addItems(year)
        self.location_combo.addItems(location)
        self.session_combo.addItems(session)
        self.driver_combo.addItems(driver_name)
        self.analysis_combo.addItems(analysis_type)

        for i, label in enumerate(labels):
            fields_layout.addWidget(label, i, 0)
            fields_layout.addWidget([self.year_combo, self.location_combo, self.session_combo, 
                                     self.driver_combo, self.analysis_combo][i], i, 1)

        fields_layout.addWidget(self.progress, len(labels), 0, 1, 2)
        self.progress.hide()
        fields_layout.addWidget(self.generate_button, len(labels) + 1, 0)
        fields_layout.addWidget(self.save_button, len(labels) + 1, 1)
        self.save_button.hide()

        # Plot Area
        plot_area = QWidget()
        plot_layout = QGridLayout()
        plot_area.setLayout(plot_layout)
        grid_layout.addWidget(plot_area, 1, 1)  # Adjusted position for side-by-side layout
        plot_area.setStyleSheet("class: plot-area")

        # Make the image larger
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap(placeholder_path).scaled(1200, 900, Qt.KeepAspectRatio))
        plot_layout.addWidget(self.image_label, 0, 0)

        # Setting the size policies
        self.year_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.location_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.session_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.driver_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.analysis_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.year_combo.currentTextChanged.connect(self.update_lists)
        self.generate_button.clicked.connect(self.generate_plot)
        self.save_button.clicked.connect(self.save_plot)

    def generate_plot(self):
        # Get selected values
        selected_year = self.year_combo.currentText()
        selected_driver = self.driver_combo.currentText()
        selected_location = self.location_combo.currentText()
        selected_session = self.session_combo.currentText()
        selected_analysis = self.analysis_combo.currentText()

        # Check if all fields are selected
        if selected_driver == 'Select Driver' or selected_location == 'Select Location':
            QMessageBox.warning(self, 'Warning', 'Please select all fields before generating the plot.')
            return

        # Start progress bar
        self.progress.show()

        # Generate plot in a separate thread
        thread = threading.Thread(target=self.generate_plot_thread, args=(selected_year, selected_driver, selected_location, selected_session, selected_analysis))
        thread.start()

    def generate_plot_thread(self, year, driver, location, session, analysis):
        # Call the appropriate function based on the selected analysis
        if analysis == 'Lap Time':
            plot_path = script2.lap_time_analysis(race_df, driver)
        elif analysis == 'Fastest Lap':
            plot_path = script2.fastest_lap_analysis(race_df, driver)
        elif analysis == 'Fastest Sectors':
            plot_path = script2.fastest_sectors_analysis(race_df, driver)
        elif analysis == 'Full Telemetry':
            plot_path = script2.full_telemetry_analysis(race_df, driver)

        # Display the generated plot
        pixmap = QPixmap(plot_path)
        self.image_label.setPixmap(pixmap.scaled(1200, 900, Qt.KeepAspectRatio))

        # Hide progress bar and show save button
        self.progress.hide()
        self.save_button.show()

        # Store the plot path for saving
        self.plot_path = plot_path

    def save_plot(self):
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shutil.copy(self.plot_path, desktop_path)

    def update_lists(self):
        # This method should be implemented to update other dropdowns based on the selected year
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
