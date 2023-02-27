import pandas as pd
import numpy as np

# Set the random seed for reproducibility
np.random.seed(43)

# Create a DataFrame with three columns named "timestamp", "value1", and "value2"
data = pd.DataFrame(columns=["timestamp", "value1", "value2"])

# Add the initial values to the DataFrame
data.loc[0] = [pd.Timestamp('now'), np.random.normal(0, 1), np.random.normal(0, 1)]

# Generate 999 random values for each column using random walk
for i in range(1, 1000):
    timestamp = data["timestamp"].iloc[i-1] + pd.Timedelta(minutes=1)
    value1 = np.random.normal(0, 1) + data["value1"].iloc[i-1]
    value2 = np.random.normal(0, 1) + data["value2"].iloc[i-1]
    data.loc[i] = [timestamp, value1, value2]

# Output the data to a CSV file
data.to_csv("dummy_timeseries_2.csv", index=False)
