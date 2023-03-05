import sys
import os
import pathlib

PROJECT_DIR = pathlib.Path().resolve()
sys.path.append(str(PROJECT_DIR))

import pandas as pd
import plotly.graph_objs as go

"""
This visualization will only work with one or two value columns.
It is a small test to show what's going on.
"""

# Define the path to the directory containing the timeseries files
folder_name = 'generated-timeseries'
folder_path = PROJECT_DIR.joinpath(folder_name)

# Loop through all subdirectories and read the CSV files
for subdir, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(subdir, file)
            df = pd.read_csv(file_path)

            # Create a plot for each value column
            fig = go.Figure()

            # Add the markers for anomalies
            anomalies = df[df['is_anomaly'] == 1]
            fig.add_trace(
                go.Scatter(
                    x=anomalies['timestamp'],
                    y=anomalies['value-0'],
                    mode='markers',
                    marker=dict(color='red', size=5)
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=anomalies['timestamp'],
                    y=anomalies['value-1'],
                    mode='markers',
                    marker=dict(color='red', size=5)
                )
            )

            # Add the lines for the other columns
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['value-0'],
                    mode='lines',
                    line=dict(color='blue')
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['value-1'],
                    mode='lines',
                    line=dict(color='green')
                )
            )

            # Add axis labels and title
            fig.update_layout(
                xaxis_title='Timestamp',
                yaxis_title='Value',
                title={
                    'text': f"{subdir} - {file}",
                    'x': 0.5,
                    'xanchor': 'center'
                }
            )

            # Save the plot to an HTML file
            plot_file_name = os.path.splitext(file)[0] + '.html'
            plot_file_path = os.path.join(subdir, plot_file_name)
            fig.write_html(plot_file_path)
