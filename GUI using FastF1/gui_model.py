import sys
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, 
                             QMessageBox)

from model import collect_race_data, prepare_data_for_model, predict

class ModelPredictionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Model Prediction')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.input_label = QLabel("Enter Lap Time and Avg Lap Time (comma separated):")
        layout.addWidget(self.input_label)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.predict_button = QPushButton("Get Prediction")
        self.predict_button.clicked.connect(self.make_prediction)
        layout.addWidget(self.predict_button)

        self.visualize_button = QPushButton("Visualize Predictions")
        self.visualize_button.clicked.connect(self.visualize_predictions)
        layout.addWidget(self.visualize_button)

        self.output_label = QLabel("")  
        layout.addWidget(self.output_label)

        self.setLayout(layout)

    def make_prediction(self):
        try:
            input_data = list(map(float, self.input_field.text().split(',')))
            prediction = predict(input_data)
            self.output_label.setText(f"Predicted Pit Stop: {'Pit Stop' if prediction[0] == 1 else 'No Pit Stop'}")
        except ValueError:
            self.output_label.setText("Error: Please enter valid numeric values.")
        except FileNotFoundError as e:
            self.output_label.setText(f"Error: {str(e)}")
        except Exception as e:
            self.output_label.setText(f"Error: {str(e)}")

    def visualize_predictions(self):
        try:
            race_data = collect_race_data(2023, 5)
            X, y = prepare_data_for_model(race_data)

            plt.figure(figsize=(14, 10))
            sns.scatterplot(data=race_data, x='AvgLapTime', y='LapTime', hue='Driver', style='PitStop', alpha=0.7)
            plt.title('Lap Time vs. Average Lap Time')
            plt.xlabel('Average Lap Time (s)')
            plt.ylabel('Lap Time (s)')
            plt.axhline(race_data['AvgLapTime'].mean(), color='red', linestyle='--', label='Mean Avg Lap Time')
            plt.legend()
            plt.show()
        except Exception as e:
            QMessageBox.critical(self, "Visualization Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModelPredictionWindow()
    window.show()
    sys.exit(app.exec_())
