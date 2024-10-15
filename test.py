import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import fastf1



class F1TelemetryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Dropdown for Year
        self.year_dropdown = QComboBox()
        self.year_dropdown.addItems(["2021", "2022", "2023"])
        layout.addWidget(QLabel("Select Year:"))
        layout.addWidget(self.year_dropdown)

        # Dropdown for Race
        self.race_dropdown = QComboBox()
        self.race_dropdown.addItems(["monza", "silverstone", "spa"])
        layout.addWidget(QLabel("Select Race:"))
        layout.addWidget(self.race_dropdown)

        # Dropdown for Driver
        self.driver_dropdown = QComboBox()
        self.driver_dropdown.addItems(["HAM", "VER", "LEC", "ALO"])
        layout.addWidget(QLabel("Select Driver:"))
        layout.addWidget(self.driver_dropdown)

        # Dropdown for Session
        self.session_dropdown = QComboBox()
        self.session_dropdown.addItems(["FP1", "FP2", "FP3", "Q", "R"])
        layout.addWidget(QLabel("Select Session:"))
        layout.addWidget(self.session_dropdown)

        # Button to Load Data
        self.load_button = QPushButton("Load Telemetry")
        self.load_button.clicked.connect(self.load_telemetry_data)
        layout.addWidget(self.load_button)

        # Graph Display Area
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def load_telemetry_data(self):
        year = int(self.year_dropdown.currentText())
        race_name = self.race_dropdown.currentText()
        driver = self.driver_dropdown.currentText()
        session = self.session_dropdown.currentText()

        # Fetch telemetry data
        telemetry = self.get_f1_telemetry(driver, session, year, race_name)
        self.plot_telemetry(telemetry)

    def get_f1_telemetry(self, driver, session, year, race_name):
        event = fastf1.get_event(year, race_name)
        session_data = fastf1.get_session(event, session)
        session_data.load()

        driver_laps = session_data.laps.pick_driver(driver)
        telemetry = driver_laps.get_car_data().add_distance()
        return telemetry

    def plot_telemetry(self, telemetry):
        # Clear previous plot
        self.fig.clear()

        # Plot new telemetry data (Distance vs Speed)
        ax = self.fig.add_subplot(111)
        ax.plot(telemetry['Distance'], telemetry['Speed'])
        ax.set_title(f"Telemetry Data: {self.driver_dropdown.currentText()}")
        ax.set_xlabel('Distance')
        ax.set_ylabel('Speed')

        # Refresh canvas
        self.canvas.draw()


# Main function to run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = F1TelemetryApp()
    window.setWindowTitle('F1 Telemetry Dashboard')
    window.show()
    sys.exit(app.exec_())
