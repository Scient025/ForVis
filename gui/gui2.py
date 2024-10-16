import os
import sys
import shutil
import threading
import pandas as pd
from random import randint
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QComboBox, QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox, QVBoxLayout
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

# stylesheet for progress bar
StyleSheet = '''
#RedProgressBar {
    min-height: 12px;
    max-height: 12px;
    border-radius: 2px;
    border: .5px solid #808080;;
}
#RedProgressBar::chunk {
    border-radius: 2px;
    background-color: #DC0000;
    opacity: 1;
}
.warning-text {
    color:#DC0000
}
'''

# defines progressbar
class ProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super(ProgressBar, self).__init__(*args, **kwargs)
        self.setValue(0)
        if self.minimum() != self.maximum():
            self.timer = QTimer(self, timeout=self.onTimeout)
            self.timer.start(randint(1, 3) * 1000)

    def onTimeout(self):
        if self.value() >= 100:
            self.timer.stop()
            self.timer.deleteLater()
            del self.timer
            return
        self.setValue(self.value() + 1)

# main gui window 
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.UIComponents()

    def initUI(self):
        self.setFixedSize(880, 525)
        self.setWindowTitle('F1 Data Analysis')
        self.setStyleSheet(StyleSheet)

    def UIComponents(self):
        # Create labels
        self.year_label = QLabel('Year:', self)
        self.driver_label = QLabel('Driver:', self)
        self.location_label = QLabel('Location:', self)
        self.session_label = QLabel('Session:', self)
        self.analysis_label = QLabel('Analysis:', self)

        # Create combo boxes
        self.year_combo = QComboBox(self)
        self.driver_combo = QComboBox(self)
        self.location_combo = QComboBox(self)
        self.session_combo = QComboBox(self)
        self.analysis_combo = QComboBox(self)

        # Add items to combo boxes
        self.year_combo.addItems(year)
        self.driver_combo.addItems(driver_name)
        self.location_combo.addItems(location)
        self.session_combo.addItems(session)
        self.analysis_combo.addItems(analysis_type)

        # Create buttons
        self.generate_button = QPushButton('Generate', self)
        self.generate_button.clicked.connect(self.generate_plot)

        # Create progress bar
        self.progress = ProgressBar(self, objectName="RedProgressBar")
        self.progress.setGeometry(30, 40, 200, 25)
        self.progress.setMaximum(100)

        # Create image label
        self.image_label = QLabel(self)
        self.image_label.setGeometry(340, 30, 500, 400)
        pixmap = QPixmap(placeholder_path)
        self.image_label.setPixmap(pixmap)

        # Create layouts
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Add widgets to left layout
        left_layout.addWidget(self.year_label)
        left_layout.addWidget(self.year_combo)
        left_layout.addWidget(self.driver_label)
        left_layout.addWidget(self.driver_combo)
        left_layout.addWidget(self.location_label)
        left_layout.addWidget(self.location_combo)
        left_layout.addWidget(self.session_label)
        left_layout.addWidget(self.session_combo)
        left_layout.addWidget(self.analysis_label)
        left_layout.addWidget(self.analysis_combo)
        left_layout.addWidget(self.generate_button)
        left_layout.addWidget(self.progress)

        # Add widgets to right layout
        right_layout.addWidget(self.image_label)

        # Add layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        # Set main layout
        self.setLayout(main_layout)

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
        self.progress.setValue(0)

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

        # Update progress bar
        for i in range(101):
            self.progress.setValue(i)
            QApplication.processEvents()

        # Display the generated plot
        pixmap = QPixmap(plot_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        # Clean up temporary files
        os.remove(plot_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
