# IDSE Project

This repository contains two Data Science projects:

1. **IDSEG – Data Quest: The Lost World**: an interactive educational game that teaches Data Science and Machine Learning concepts.
2. **IDSEPR – Netflix Content Analysis**: a data analysis and machine-learning pipeline using Netflix title metadata.

## Repository structure

```text
IDSE-Project/
├── IDSEG/
│   ├── game/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── game/
│   │       ├── state.py
│   │       ├── styles.py
│   │       ├── ui.py
│   │       └── levels/
│   └── IDSE_game .pdf
├── IDSEPR/
│   ├── datapipeline.py
│   ├── netflix.csv
│   ├── netflix_first_1000_cleaned.csv
│   ├── netflix_final_prepared.csv
│   ├── logistic_regression_errors.csv
│   ├── random_forest_errors.csv
│   └── netflix_report_latex.pdf
└── README.md
```

## Project 1: IDSEG – Data Quest: The Lost World

### Overview

Data Quest: The Lost World is an interactive educational game built with Python and Streamlit. The player explores six worlds in the Data Kingdom and completes missions based on Data Science and Machine Learning concepts.

### Concepts covered

- Data cleaning and handling missing or invalid values
- Correlation analysis
- K-Means clustering
- Classification
- Overfitting and underfitting
- Model evaluation using accuracy, precision, recall, F1-score and a confusion matrix

### Technologies

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Plotly

### Run the application

Open a terminal and run:

```bash
cd IDSEG/game
python -m venv .venv
```

Activate the virtual environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and start the game:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will provide a local URL (usually `http://localhost:8501`) to open the game in a browser.

## Project 2: IDSEPR – Netflix Content Analysis

### Overview

This project analyzes Netflix title metadata and explores whether available metadata can be used to classify a title as a **Movie** or a **TV Show**. The pipeline loads the supplied `netflix.csv` dataset, selects the first 1,000 records, performs data cleaning and feature engineering, explores patterns in the data, and trains classification models.

### Main tasks

- Inspect dataset dimensions, data types, summary statistics, missing values and duplicates
- Clean duplicate rows, blank strings and text fields; handle missing categorical values
- Convert date and release-year fields and derive date-added, duration and genre-count features
- Explore genre frequencies, Movie/TV Show counts and release-year patterns
- Detect potential outliers using the IQR method
- Train and compare Logistic Regression and Random Forest classifiers
- Use a train/test split and cross-validation
- Evaluate predictions and inspect model errors
- Compare feature sets with and without genre

The analysis uses the first 1,000 rows of the supplied dataset; results should not be interpreted as representing the entire Netflix catalogue.

### Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Joblib

### Run the pipeline

Open a terminal and run:

```bash
cd IDSEPR
python -m venv .venv
```

Activate the virtual environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install the dependencies and run the script:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn joblib
python datapipeline.py
```

The script expects `netflix.csv` in the `IDSEPR` directory. It writes prepared data and analysis outputs to files as defined in the script.

## Project reports

- `IDSEG/IDSE_game .pdf` – report for Data Quest: The Lost World.
- `IDSEPR/netflix_report_latex.pdf` – report for Netflix Content Analysis.

## Contributors

- Pranamya
- Veeraboyena Venkata Spoorthy Yadav

---

**Note:** Run each project from its own directory as shown above so that relative file paths work correctly.
