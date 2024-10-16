import os
import sys
import shutil
import threading
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QComboBox, QApplication, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QFrame, QMessageBox, QDesktopWidget,
                             QMainWindow, QSizePolicy)

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

StyleSheet = '''
QWidget {
    background-color: #e8f5e9;
    font-family: Arial, sans-serif;
}
QLabel {
    font-size: 14px;
    font-weight: bold;
}
QComboBox {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 5px;
    min-width: 200px;
    font-size: 14px;
}
QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 3px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #1976D2;
}
QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 3px;
    text-align: center;
    font-size: 12px;
}
QProgressBar::chunk {
    background-color: #2196F3;
}
'''

class ProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super(ProgressBar, self).__init__(*args, **kwargs)
        self.setValue(0)
        self.setTextVisible(True)
        self.setRange(0, 0)  # Indeterminate mode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = placeholder_path
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Formula 1 Telemetry Analytics')
        self.setWindowIcon(QtGui.QIcon(os.path.join(fileConfig.IMG_DIR, 'f1.png')))
        self.setStyleSheet(StyleSheet)

        # Get screen resolution
        screen = QDesktopWidget().screenNumber(QDesktopWidget().cursor().pos())
        screen_size = QDesktopWidget().screenGeometry(screen).size()
        self.screen_width = screen_size.width()
        self.screen_height = screen_size.height()

        # Set window size to 80% of screen size
        window_width = int(self.screen_width * 0.8)
        window_height = int(self.screen_height * 0.8)
        self.setGeometry((self.screen_width - window_width) // 2, 
                         (self.screen_height - window_height) // 2, 
                         window_width, window_height)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title and description
        title = QLabel("Formula 1 Telemetry Analytics")
        title.setStyleSheet(f"font-size: {self.font_size(28)}px; font-weight: bold;")
        description = QLabel("Analyze race telemetry data and visualize performance metrics.")
        description.setStyleSheet(f"font-size: {self.font_size(18)}px;")
        main_layout.addWidget(title)
        main_layout.addWidget(description)

        # Content area
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Left side - Form
        form_layout = QVBoxLayout()
        form_frame = QFrame()
        form_frame.setLayout(form_layout)
        form_frame.setFrameShape(QFrame.StyledPanel)
        content_layout.addWidget(form_frame, 1)

        # Create and add form elements
        self.drop_year = self.create_form_element(form_layout, "Year:", year)
        self.drop_grand_prix = self.create_form_element(form_layout, "Grand Prix Location:", location)
        self.drop_session = self.create_form_element(form_layout, "Session:", session)
        self.drop_driver1 = self.create_form_element(form_layout, "Driver 1:", driver_name)
        self.drop_driver2 = self.create_form_element(form_layout, "Driver 2:", driver_name)
        self.drop_analysis = self.create_form_element(form_layout, "Analysis Type:", analysis_type)

        self.lap_number = self.create_form_element(form_layout, "Lap Number:", ['Select Lap'])
        self.lap_number.hide()

        self.run_button = QPushButton("Run Analysis")
        self.run_button.setStyleSheet(f"font-size: {self.font_size(14)}px;")
        form_layout.addWidget(self.run_button)

        self.save_button = QPushButton("Save Plot to Desktop")
        self.save_button.setStyleSheet(f"font-size: {self.font_size(14)}px;")
        form_layout.addWidget(self.save_button)
        self.save_button.hide()

        self.pbar = ProgressBar(self)
        form_layout.addWidget(self.pbar)
        self.pbar.hide()

        form_layout.addStretch(1)  # Add stretch to push elements to the top

        # Right side - Plot area
        self.plot_area = QLabel()
        self.plot_area.setAlignment(Qt.AlignCenter)
        self.plot_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update_plot(placeholder_path)
        content_layout.addWidget(self.plot_area, 3)

        # Connect signals
        self.run_button.clicked.connect(self.thread_script)
        self.save_button.clicked.connect(self.save_plot)
        self.drop_year.currentTextChanged.connect(self.update_lists)
        self.drop_analysis.currentTextChanged.connect(self.add_laps)
        self.drop_grand_prix.currentTextChanged.connect(self.update_laps)

        self.warning_box = QMessageBox(self)
        self.warning_box.setWindowTitle('Error!')
        self.warning_box.setText('Select a valid race year.')
        self.warning_box.setDefaultButton(QMessageBox.Ok)

    def create_form_element(self, layout, label_text, items):
        label = QLabel(label_text)
        label.setStyleSheet(f"font-size: {self.font_size(16)}px;")
        combobox = QComboBox()
        combobox.addItems(items)
        combobox.setStyleSheet(f"font-size: {self.font_size(16)}px;")
        layout.addWidget(label)
        layout.addWidget(combobox)
        return combobox

    def font_size(self, base_size):
        # Scale font size based on screen resolution
        return int(base_size * min(self.screen_width / 1920, self.screen_height / 1080))

    def update_plot(self, image):
        if isinstance(image, str):
            self.current_image_path = image
            pixmap = QPixmap(image)
        elif isinstance(image, QPixmap):
            pixmap = image
        else:
            return

        scaled_pixmap = pixmap.scaled(self.plot_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.plot_area.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'plot_area'):
            self.update_plot(self.current_image_path)

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
            self.current_image_path = self.plot_path  # Update this line
            self.update_plot(self.plot_path)
            self.pbar.hide()
            self.run_button.setText('Run New Analysis')
            self.save_button.show()

    def current_text(self):
        return [
            self.drop_year.currentText(),
            self.drop_grand_prix.currentText(),
            self.drop_session.currentText(),
            self.drop_driver1.currentText(),
            self.drop_driver2.currentText(),
            self.drop_analysis.currentText(),
            self.lap_number.currentText()
        ]

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
    mw.show()  # Changed from showFullScreen() to show()
    sys.exit(app.exec_())
