import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

# Load the csv file and consider spaces as NaN, skip the second row
df = pd.read_csv('D:\Github Rep\Bluepump-flask-edition\static\data_analysis_tool\JoinThePipe+Foundation_June+5,+2023_06.14.csv', na_values=' ', skiprows=[1, 2])

def visualize(df, column):
    if df[column].nunique() > 20:
        print(f'Skipped column {column} as it has more than 20 unique values')
        return

    fig, ax = plt.subplots()

    value_counts = df[column].value_counts()
    labels = list(value_counts.index)
    values = list(value_counts.values)

    plt.bar(range(len(labels)), values, tick_label=range(1, len(labels) + 1))
    plt.title(f'Distribution of answers for: {column}')
    plt.xlabel('Answer')
    plt.ylabel('Frequency')

    plt.xticks(rotation=45, ha='right')

    # Create directory to save graphs if it doesn't exist
    if not os.path.exists('graphs'):
        os.makedirs('graphs')

    plt.savefig(f'graphs/{column}.png')
    plt.close(fig)  # Close the figure after saving to prevent it from displaying

    # Writing a mapping file for the x labels
    with open(f'graphs/{column}.txt', 'w') as f:
        for i, label in enumerate(labels):
            f.write(f'{i + 1} = {label}\n')

# Call the visualize function for each question column
columns = ['Consent', 'Age', 'Age_2_TEXT', 'Gender', 'Pre 1', 'Pre 2', 'Pre 3', 'Pre 4', 'Post 1', 'Post 2', 'Post 3', 'Post 4.1', 'Post 4.2', 'Post 5']

for column in columns:
    visualize(df, column)
