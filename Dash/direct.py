from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

# Function to apply machine learning on telemetry data
def apply_ml_to_data(df):
    # Assemble features: Select telemetry columns to form a feature vector
    assembler = VectorAssembler(
        inputCols=["speed", "throttle", "brake", "gear", "rpm"],
        outputCol="features"
    )
    
    # Transform the dataframe to include the feature vector
    data = assembler.transform(df)

    # Split the data into training and test sets (80% train, 20% test)
    train_data, test_data = data.randomSplit([0.8, 0.2])

    # Train a Linear Regression model on the training set
    lr = LinearRegression(labelCol="speed_diff", featuresCol="features")
    lr_model = lr.fit(train_data)

    # Make predictions on the test set
    predictions = lr_model.transform(test_data)
    
    # Show the predictions alongside actual values
    predictions.select("features", "speed_diff", "prediction").show()

# Example usage of applying machine learning on telemetry data
if __name__ == "__main__":
    # Assuming telemetry_data is obtained from Script 1
    telemetry_data = telemetry_data.dropna()  # Remove rows with null values (optional)
    
    # Apply ML model to telemetry data
    apply_ml_to_data(telemetry_data)
