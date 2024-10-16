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

# imports script.py, used for creating plots
import script
import fileConfig

# paths for race data
events = pd.read_csv(fileConfig.EVENTS_CSV)
drivers = pd.read_csv(fileConfig.DRIVERS_CSV)
race_laps = pd.read_csv(fileConfig.RACE_LAPS_CSV)
placeholder_path = fileConfig.PLACEHOLDER_IMG

# active race years
year = events.columns[1:].tolist()
year.insert(0, 'Select Year')

# values for dropdown labels
location = ['Select Location']
session = ['Race', 'Qualifying', 'FP1', 'FP2', 'FP3']
driver_name = ['Select Driver']
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
        self.setWindowIcon(QtGui.QIcon(os.path.join(fileConfig.IMG_DIR, 'f1.png')))
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

        self.drop_year = QComboBox()
        self.drop_grand_prix = QComboBox()
        self.drop_session = QComboBox()
        self.drop_driver1 = QComboBox()
        self.drop_driver2 = QComboBox()
        self.drop_analysis = QComboBox()
        self.lap_number = QComboBox()

        self.warning_box = QMessageBox(self)
        self.warning_box.setWindowTitle('Error!')
        self.warning_box.setText('Select a valid race year.')
        self.warning_box.setDefaultButton(QMessageBox.Ok)

        labels = [
            QLabel('Year:'),
            QLabel('Grand Prix Location:'),
            QLabel('Session:'),
            QLabel('Driver 1:'),
            QLabel('Driver 2:'),
            QLabel('Analysis Type:')
        ]

        self.run_button = QPushButton('Run Analysis')
        self.save_button = QPushButton('Save Plot to Desktop')

        self.pbar = ProgressBar(self, textVisible=False)

        self.drop_year.addItems(year)
        self.drop_grand_prix.addItems(location)
        self.drop_session.addItems(session)
        self.drop_driver1.addItems(driver_name)
        self.drop_driver2.addItems(driver_name)
        self.drop_analysis.addItems(analysis_type)

        for i, label in enumerate(labels):
            fields_layout.addWidget(label, i, 0)
            fields_layout.addWidget([self.drop_year, self.drop_grand_prix, self.drop_session, 
                                     self.drop_driver1, self.drop_driver2, self.drop_analysis][i], i, 1)

        fields_layout.addWidget(self.lap_number, len(labels), 0, 1, 2)
        self.lap_number.hide()
        fields_layout.addWidget(self.pbar, len(labels) + 1, 0, 1, 2)
        self.pbar.hide()
        fields_layout.addWidget(self.run_button, len(labels) + 2, 0)
        fields_layout.addWidget(self.save_button, len(labels) + 2, 1)
        self.save_button.hide()

        # Plot Area
        plot_area = QWidget()
        plot_layout = QGridLayout()
        plot_area.setLayout(plot_layout)
        grid_layout.addWidget(plot_area, 1, 1)  # Adjusted position for side-by-side layout
        plot_area.setStyleSheet("class: plot-area")

        # Make the image larger
        self.img_plot = QLabel()
        self.img_plot.setPixmap(QPixmap(placeholder_path).scaled(1200, 900, Qt.KeepAspectRatio))
        plot_layout.addWidget(self.img_plot, 0, 0)

        # Setting the size policies
        self.drop_year.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.drop_grand_prix.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.drop_session.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.drop_driver1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.drop_driver2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.drop_analysis.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.drop_year.currentTextChanged.connect(self.update_lists)
        self.run_button.clicked.connect(self.thread_script)
        self.save_button.clicked.connect(self.save_plot)
        self.drop_analysis.currentTextChanged.connect(self.add_laps)
        self.drop_grand_prix.currentTextChanged.connect(self.update_laps)

    def current_text(self):
        input_data = [
            self.drop_year.currentText(),
            self.drop_grand_prix.currentText(),
            self.drop_session.currentText(),
            self.drop_driver1.currentText(),
            self.drop_driver2.currentText(),
            self.drop_analysis.currentText(),
            self.lap_number.currentText()
        ]
        return input_data

    def display_plot(self, plot_path):
        self.img_plot.setPixmap(QPixmap(plot_path).scaled(1200, 900, Qt.KeepAspectRatio))

    def save_plot(self):
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shutil.copy(self.plot_path, desktop_path)

    def add_laps(self):
        self.lap_number.setVisible(self.drop_analysis.currentText() == 'Fastest Sectors')

    def update_laps(self):
        if self.drop_grand_prix.currentText():
            self.lap_number.clear()
            lap_val = ['Select Lap']
            race = self.drop_grand_prix.currentText()
            total_laps = race_laps.loc[race_laps.event == race, 'laps'].values[0]
            lap_val.extend(map(str, range(1, total_laps + 1)))
            self.lap_number.addItems(lap_val)

    def thread_script(self):
        threading.Thread(target=self.button_listen).start()

    def button_listen(self):
        input_data = self.current_text()
        if input_data[0] == 'Select Year':
            self.run_button.setText('Run Analysis (Select Valid Year)')
        else:
            self.run_button.setText('Running . . .')
            self.save_button.hide()
            self.pbar.show()
            script.get_race_data(input_data)
            self.plot_path = os.path.join(fileConfig.PLOT_DIR, f"{input_data[5]}.png")
            self.display_plot(self.plot_path)
            self.pbar.hide()
            self.run_button.setText('Run New Analysis')
            self.save_button.show()

    def update_lists(self):
        sel_year = self.drop_year.currentText()
        if sel_year != 'Select Year':
            self.drop_grand_prix.clear()
            self.drop_driver1.clear()
            self.drop_driver2.clear()
            valid_grand_prix = events[str(sel_year)].dropna().to_list()
            valid_drivers = drivers[str(sel_year)].dropna().to_list()
            self.drop_grand_prix.addItems(valid_grand_prix)
            self.drop_driver1.addItems(valid_drivers)
            self.drop_driver2.addItems(valid_drivers)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
