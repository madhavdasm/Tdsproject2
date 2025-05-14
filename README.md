# 📊 AI-Powered Dataset Analyzer with Visualizations & Narratives 🧠✨

This Python script analyzes CSV datasets using `pandas`, `seaborn`, and `matplotlib`, and then generates insightful narratives using OpenAI models via **AI Proxy API** (secured by `AIPROXY_TOKEN`). It visualizes correlations and distributions, summarizes missing values, and creates a **story-driven analysis** 📖.

---

## 🚀 Features

- ✅ Reads multiple CSV files
- 📈 Creates correlation heatmaps
- 📊 Generates distribution plots
- 🧠 Sends stats to OpenAI GPT (via AI Proxy) for intelligent analysis
- 📝 Saves narrative + visuals to a per-dataset `README.md`

---

## 🔧 Tech Stack & Dependencies

```bash
# Requires Python 3.11+
pandas
numpy
matplotlib
seaborn
requests


````

---

## 🗃️ Usage

1. **Set the API token**
   Export your AI Proxy token as an environment variable:

   ```bash
   export AIPROXY_TOKEN=your_token_here
   ```

2. **Run the script with your CSV files**

   ```bash
   python script.py your_dataset.csv
   ```

3. 📁 For each dataset, you'll get:

   * A folder named after the dataset
   * A `README.md` inside it containing:

     * AI-generated narrative
     * Visualizations (heatmap + distribution plots)



## 🤖 How the AI Works

After basic EDA, it sends the column names, summary stats, and missing value report to OpenAI GPT-4o-mini via [AI Proxy](https://aiproxy.sanand.workers.dev). The model replies with a natural-language narrative and key insights 🧠💡.

---

## 📂 Output Structure

```
your_dataset/
│
├── README.md                 👈 AI-generated analysis
├── correlation_heatmap.png   📊 Correlation visualization
├── <column>_distribution.png 📉 Distribution plots
```

---

## 📌 Note

* Make sure your datasets are CSV files.
* UTF-8 encoding is used by default; falls back to ISO-8859-1 if needed.
* Requires Python 3.11+

---

## 🏁 Sample Command

```bash
python script.py sales_data.csv user_logs.csv
```

🎉 This will create:

```
sales_data/
└── README.md + plots

user_logs/
└── README.md + plots
```

---

## 🧠 Author & License

Feel free to modify and use it for your projects.
📄 MIT License

---

## ⭐️ Show some love

If you find this useful, drop a ⭐ on GitHub or share it with your data science buddies!

```
