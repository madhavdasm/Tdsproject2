# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "numpy",
#   "seaborn",
#   "matplotlib",
#   "requests",
# ]
# ///

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
import requests
import json
from datetime import datetime

# Set up API with the AIPROXY_TOKEN from environment
AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN is not set in the environment variables.")
    sys.exit(1)

# Test the connection to AI Proxy by listing available models
try:
    response = requests.get(
        "https://aiproxy.sanand.workers.dev/openai/v1/models",
        headers={"Authorization": f"Bearer {AIPROXY_TOKEN}"}
    )
    response.raise_for_status()
    print("API connection successful!")
except requests.exceptions.RequestException as e:
    print(f"Error connecting to API: {e}")
    sys.exit(1)

def generate_narrative(df, dataset_name):
    # Basic summary statistics
    summary = {
        "columns": list(df.columns),
        "summary_stats": df.describe().to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
    }

    prompt = f"""
    I have a dataset named {dataset_name} with the following columns: {summary['columns']}.
    Here are some summary statistics:
    {summary['summary_stats']}

    And here are the missing values:
    {summary['missing_values']}

    Based on this data, provide an analysis and a story with insights and implications.
    """

    # Prepare the API request payload
    payload = {
        "model": "gpt-4o-mini",  # Using GPT-4o-Mini model from AI Proxy
        "messages": [{"role": "user", "content": prompt}],
    }

    # Send the request to AI Proxy for narrative generation
    try:
        response = requests.post(
            "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {AIPROXY_TOKEN}", "Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        response.raise_for_status()
        narrative = response.json()['choices'][0]['message']['content'].strip()
        return narrative if narrative else "No narrative generated."
    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return "Error occurred during API call."

# Debugging: Checking arguments passed
print(f"Arguments passed: {sys.argv}")

if len(sys.argv) < 2:
    print("Please provide CSV file(s) as arguments.")
    sys.exit(1)

# Process each dataset provided in arguments
csv_files = sys.argv[1:]
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')  # Try UTF-8 first
    except UnicodeDecodeError:
        print("UTF-8 encoding failed. Trying 'ISO-8859-1'...")
        try:
            df = pd.read_csv(csv_file, encoding='ISO-8859-1')  # Fallback to ISO-8859-1
        except Exception as e:
            print(f"Error loading CSV file {csv_file}: {e}")
            continue

    print(f"Dataset loaded: {csv_file}")
    print(f"Columns: {df.columns}")

    # Summary Statistics
    print(f"Summary Statistics:\n{df.describe()}")
    print(f"Missing Values:\n{df.isnull().sum()}")

    # Filter out non-numeric columns for correlation calculation
    numeric_df = df.select_dtypes(include=[np.number])

    # Handle missing values (drop or fill)
    numeric_df = numeric_df.dropna()  # Or use numeric_df.fillna(0)

    # Calculate the correlation matrix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_name = os.path.splitext(os.path.basename(csv_file))[0]
    if not numeric_df.empty:
        corr = numeric_df.corr()

        # Generate a heatmap for the correlation matrix
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title(f"Correlation Heatmap for {dataset_name}")
        heatmap_file = f"{dataset_name}_correlation_heatmap_{timestamp}.png"
        plt.savefig(heatmap_file)
        plt.close()

        print(f"Correlation heatmap saved as '{heatmap_file}'.")
    else:
        print(f"No numeric columns available for correlation heatmap in {dataset_name}.")

    # Limit to 2 distribution plots
    max_plots = 2
    columns_to_plot = numeric_df.columns[:max_plots]

    # Generate distribution plots for the first few numeric columns
    plot_files = []
    for column in columns_to_plot:
        plt.figure(figsize=(8, 6))
        sns.histplot(numeric_df[column], kde=True)
        plt.title(f"Distribution of {column} in {dataset_name}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plot_file = f"{dataset_name}_{column}_distribution_{timestamp}.png"
        plt.savefig(plot_file)
        plt.close()
        plot_files.append(plot_file)
        print(f"Distribution plot saved as '{plot_file}'.")

    # Generate the narrative based on the dataset
    narrative = generate_narrative(df, dataset_name)

    def save_to_readme(narrative, dataset_name, plot_files, heatmap_file):
        readme_path = f"{dataset_name}/README.md"
        os.makedirs(os.path.dirname(readme_path), exist_ok=True)
        with open(readme_path, "a") as f:  # Append mode to prevent overwriting
            f.write(f"# Dataset Analysis for {dataset_name} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n")
            f.write("## Summary\n")
            f.write(narrative + "\n\n")
            f.write("## Visualizations\n")
            for plot_file in plot_files:
                f.write(f"![Distribution of {os.path.basename(plot_file)}]({plot_file})\n")
            if heatmap_file:
                f.write(f"![Correlation Heatmap]({heatmap_file})\n")

    # Save the analysis and visualizations to README.md
    save_to_readme(narrative, dataset_name, plot_files, heatmap_file)

print("Analysis and visualizations for all datasets saved to their respective README.md files.")
