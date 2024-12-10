import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
import requests
import json

# Set up API with the AIPROXY_TOKEN from environment
AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")

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


def generate_narrative(df):
    # Basic summary statistics
    summary = {
        "columns": list(df.columns),
        "summary_stats": df.describe().to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
    }

    prompt = f"""
    I have a dataset with the following columns: {summary['columns']}.
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
        print("AI Narrative Generated:\n", narrative)
        return narrative if narrative else "No narrative generated."
    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return "Error occurred during API call."


# Debugging: Checking arguments passed
print(f"Arguments passed: {sys.argv}")

if len(sys.argv) < 2:
    print("Please provide a CSV file as an argument.")
    sys.exit(1)

# Load the dataset with encoding handling
csv_file = sys.argv[1]
try:
    df = pd.read_csv(csv_file, encoding='utf-8')  # Try UTF-8 first
except UnicodeDecodeError:
    print("UTF-8 encoding failed. Trying 'ISO-8859-1'...")
    try:
        df = pd.read_csv(csv_file, encoding='ISO-8859-1')  # Fallback to ISO-8859-1
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)


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
if not numeric_df.empty:
    corr = numeric_df.corr()

    # Generate a heatmap for the correlation matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.savefig("correlation_heatmap.png")
    plt.close()

    print("Correlation heatmap saved as 'correlation_heatmap.png'.")
else:
    print("No numeric columns available for correlation heatmap.")

# Generate distribution plots for all numeric columns
for column in numeric_df.columns:
    plt.figure(figsize=(8, 6))
    sns.histplot(numeric_df[column], kde=True)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plot_file = f"{column}_distribution.png"
    plt.savefig(plot_file)
    plt.close()
    print(f"Distribution plot saved as '{plot_file}'.")

# Generate the narrative based on the dataset
narrative = generate_narrative(df)

def save_to_readme(narrative):
    with open("README.md", "w") as f:
        f.write("# Dataset Analysis\n\n")
        f.write("## Summary\n")
        f.write(narrative + "\n\n")
        f.write("## Visualizations\n")
        for column in numeric_df.columns:
            f.write(f"![Distribution of {column}]({column}_distribution.png)\n")
        f.write("![Correlation Heatmap](correlation_heatmap.png)\n")

# Save the analysis and visualizations to README.md
save_to_readme(narrative)

print("Analysis and narrative saved to README.md.")
