![output1](https://github.com/user-attachments/assets/7d2964c5-690e-40f8-ad92-a7df3cb775e0)# F1 Data Visualization 🏎️

A comprehensive data visualization tool built with Python to analyze Formula 1 telemetry and real-time data. This application provides insights into race performance, lap times, and various other metrics through an interactive GUI interface.

## 🌟 Features

- Real-time telemetry data visualization
- Multiple analysis types:

  - Lap Time Analysis
  - Fastest Lap Comparison
  - Fastest Sectors Analysis
  - Full Telemetry Visualization
  - Tyre Compound and Stint Analysis
  - Pit Stop Impact Analysis
  - Fuel Usage Impact Analysis
  - Position Changes Tracking

- Machine Learning predictions for pit stop strategies
- Interactive GUI with customizable parameters
- Support for historical race data analysis
- Multi-driver comparison capabilities

## 🔧 Technologies Used

- **Python 3.12.0**
- **PyQt5** - GUI Framework
- **FastF1** - F1 Data Access
- **Pandas** - Data Manipulation
- **Matplotlib/Seaborn** - Data Visualization
- **Scikit-learn** - Machine Learning
- **Apache Spark** - Big Data Processing
- **Dash** - Web-based Visualization
- **HDFS** - Data Storage

## 📋 Prerequisites

- Python 3.8 or higher
- Apache Spark installation
- HDFS setup (for big data storage)

## 🚀 Installation

1. Clone the repository.

2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure HDFS connection:
   - Update the HDFS cluster IP in `spark.py`
   - Ensure proper permissions for data access

## 💻 Usage

### GUI Application

Run the main GUI application:

```bash
python gui.py
```

### Model Prediction Window

For standalone model predictions:

```bash
python gui_model.py
```

### Web Dashboard

Launch the Dash web interface:

```bash
python app.py
```

## 📊 Available Analysis Types

1. **Lap Time Analysis**

   - Compare lap times between drivers
   - Track performance evolution

2. **Fastest Lap Analysis**

   - Identify and analyze fastest laps
   - Sector-by-sector breakdown

3. **Full Telemetry**

   - Speed traces
   - Throttle/brake patterns
   - Gear usage analysis

4. **Strategy Analysis**
   - Tyre compound impact
   - Pit stop timing
   - Fuel load effects

## 🔄 Data Pipeline

1. Data Collection (`fastf1`)

   - Live timing data
   - Historical race data
   - Driver telemetry

2. Processing (Spark)

   - Data cleaning
   - Feature engineering
   - Performance calculations

3. Storage (HDFS)

   - Raw data storage
   - Processed datasets
   - Model artifacts

4. Analysis
   - Statistical analysis
   - Machine learning predictions
   - Performance comparisons

## 🤖 Machine Learning Features

- Pit stop prediction model
- Performance trend analysis
- Anomaly detection
- Strategy optimization

## Output Images
1. Visualization GUI -
   
  ![output1](https://github.com/user-attachments/assets/ad5e5a13-6ce2-4175-a242-8e6aced8f6ce)


  ![output2](https://github.com/user-attachments/assets/941d60ba-b915-4328-8ca2-aaaaef90ebde)


  ![output3](https://github.com/user-attachments/assets/91f34012-4fd4-4e51-a45d-efc89f8079cf)


  ![output4](https://github.com/user-attachments/assets/dc9abb1f-7bb3-4b7f-9e83-f702e1090793)

