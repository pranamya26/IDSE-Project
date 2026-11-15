# ============================================================
# NETFLIX CONTENT ANALYSIS
# ============================================================

# PART 1: IMPORT LIBRARIES

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# ============================================================
# PART 2: LOAD DATASET
# ============================================================

df = pd.read_csv("netflix.csv")

print("\nOriginal Dataset Shape:", df.shape)
print(df.head())

# ============================================================
# PART 3: SELECT FIRST 1000 ROWS
# ============================================================

df = df.head(1000).copy()

print("\nSelected Dataset Shape:", df.shape)

# ============================================================
# PART 4: DATA UNDERSTANDING
# ============================================================

print("\nDataset Information:")
print(df.info())

print("\nStatistical Summary:")
print(df.describe(include="all"))

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:", df.duplicated().sum())

# ============================================================
# PART 5: DATA CLEANING
# ============================================================

# Remove duplicate rows
df = df.drop_duplicates().copy()

# Replace empty strings with NaN
df = df.replace(r"^\s*$", np.nan, regex=True)

# Remove extra spaces from text columns
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()

# Fill missing categorical values
categorical_columns = ["director", "cast", "country", "rating"]

for col in categorical_columns:
    df[col] = df[col].fillna("Unknown")

# Convert date_added into datetime
df["date_added"] = pd.to_datetime(
    df["date_added"],
    errors="coerce"
)

# Extract year and month
df["date_added_year"] = df["date_added"].dt.year
df["date_added_month"] = df["date_added"].dt.month

# Convert release_year into numeric
df["release_year"] = pd.to_numeric(
    df["release_year"],
    errors="coerce"
)

# Extract duration value and unit
df["duration_value"] = pd.to_numeric(
    df["duration"].str.extract(r"(\d+)")[0],
    errors="coerce"
)

df["duration_unit"] = df["duration"].str.extract(
    r"([A-Za-z]+)"
)

# Count genres
df["genre_count"] = df["listed_in"].apply(
    lambda x: len(str(x).split(","))
)

print("\nMissing Values After Cleaning:")
print(df.isnull().sum())

print("\nCleaned Dataset Shape:", df.shape)

df.to_csv("netflix_first_1000_cleaned.csv", index=False)

# ============================================================
# PART 6: GENRE ANALYSIS
# ============================================================

genre_data = df[["show_id", "listed_in"]].copy()

genre_data["listed_in"] = genre_data["listed_in"].fillna("Unknown")

genre_data["listed_in"] = genre_data["listed_in"].str.split(", ")

genre_data = genre_data.explode("listed_in")

genre_counts = genre_data["listed_in"].value_counts()

print("\nTop 10 Genres:")
print(genre_counts.head(10))

plt.figure(figsize=(12, 6))
genre_counts.head(10).plot(kind="bar")
plt.title("Top 10 Netflix Genres")
plt.xlabel("Genre")
plt.ylabel("Number of Titles")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ============================================================
# PART 7: MOVIES VS TV SHOWS ANALYSIS
# ============================================================

type_counts = df["type"].value_counts()

print("\nMovies vs TV Shows:")
print(type_counts)

plt.figure(figsize=(6, 5))
type_counts.plot(kind="bar")
plt.title("Movies vs TV Shows")
plt.xlabel("Content Type")
plt.ylabel("Number of Titles")
plt.tight_layout()
plt.show()

# ============================================================
# PART 8: RELEASE YEAR ANALYSIS
# ============================================================

release_counts = df["release_year"].value_counts().sort_index()

plt.figure(figsize=(12, 5))
release_counts.plot()
plt.title("Netflix Content by Release Year")
plt.xlabel("Release Year")
plt.ylabel("Number of Titles")
plt.tight_layout()
plt.show()

print("\nTop 10 Release Years:")
print(df["release_year"].value_counts().head(10))

# ============================================================
# PART 9: OUTLIER DETECTION
# ============================================================

outlier_columns = [
    "release_year",
    "duration_value"
]

for col in outlier_columns:

    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)

    IQR = Q3 - Q1

    lower_limit = Q1 - 1.5 * IQR
    upper_limit = Q3 + 1.5 * IQR

    outliers = df[
        (df[col] < lower_limit) |
        (df[col] > upper_limit)
    ]

    print("\nOutliers in", col, ":", len(outliers))

    plt.figure(figsize=(7, 4))
    sns.boxplot(x=df[col])
    plt.title("Outlier Detection - " + col)
    plt.tight_layout()
    plt.show()

# ============================================================
# PART 10: SAVE FINAL PREPARED DATASET
# ============================================================

df.to_csv("netflix_final_prepared.csv", index=False)

# ============================================================
# PART 11: PREPARE DATA FOR MACHINE LEARNING
# ============================================================

ml_df = df.copy()

# Clean target column
ml_df["type"] = ml_df["type"].astype("string").str.strip()

ml_df["type"] = ml_df["type"].replace(
    ["", "nan", "NaN", "None", "NULL", "<NA>"],
    pd.NA
)

# Remove rows with missing or invalid target
ml_df = ml_df.dropna(subset=["type"]).copy()

ml_df = ml_df[
    ml_df["type"].isin(["Movie", "TV Show"])
].copy()

# Features
# Duration is excluded because it directly reveals content type.

X = ml_df[
    ["release_year", "rating", "country", "listed_in"]
].copy()

y = ml_df["type"].copy()

print("\nMachine Learning Dataset Shape:", X.shape)

print("\nTarget Distribution:")
print(y.value_counts())

# ============================================================
# PART 12: TRAIN TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining Samples:", len(X_train))
print("Testing Samples:", len(X_test))

# ============================================================
# PART 13: DATA PREPROCESSING
# ============================================================

numerical_features = ["release_year"]

categorical_features = [
    "rating",
    "country",
    "listed_in"
]

numerical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ]
)

categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="constant",
                fill_value="Unknown"
            )
        ),
        (
            "encoder",
            OneHotEncoder(handle_unknown="ignore")
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numerical_transformer,
            numerical_features
        ),
        (
            "cat",
            categorical_transformer,
            categorical_features
        )
    ]
)

# ============================================================
# PART 14: DEFINE MACHINE LEARNING MODELS
# ============================================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )

}

# ============================================================
# PART 15: TRAIN MODELS
# ============================================================

trained_models = {}

for name, model in models.items():

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    pipeline.fit(X_train, y_train)

    trained_models[name] = pipeline

    print("\n", name, "Training Completed")

# ============================================================
# PART 16: CROSS VALIDATION
# ============================================================

print("\nCROSS VALIDATION RESULTS")

for name, model in trained_models.items():

    scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=5,
        scoring="f1_macro"
    )

    print("\n", name)
    print("Cross Validation Scores:", scores)
    print("Mean CV Score:", scores.mean())

# ============================================================
# PART 17: SAVE TRAINED MODELS
# ============================================================

joblib.dump(
    trained_models["Logistic Regression"],
    "logistic_model.pkl"
)

joblib.dump(
    trained_models["Random Forest"],
    "random_forest_model.pkl"
)

print("\nModels Saved Successfully")

# ============================================================
# PART 18: MAKE PREDICTIONS
# ============================================================

lr_predictions = trained_models[
    "Logistic Regression"
].predict(X_test)

rf_predictions = trained_models[
    "Random Forest"
].predict(X_test)

predictions = {

    "Logistic Regression": lr_predictions,

    "Random Forest": rf_predictions

}

# ============================================================
# PART 19: MODEL EVALUATION
# ============================================================

results = []

for name, pred in predictions.items():

    accuracy = accuracy_score(y_test, pred)

    precision = precision_score(
        y_test,
        pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        pred,
        average="weighted",
        zero_division=0
    )

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    print("\n================================")
    print(name)
    print("================================")

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            pred,
            zero_division=0
        )
    )

# ============================================================
# PART 20: CONFUSION MATRICES
# ============================================================

for name, pred in predictions.items():

    cm = confusion_matrix(
        y_test,
        pred,
        labels=["Movie", "TV Show"]
    )

    plt.figure(figsize=(6, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Movie", "TV Show"],
        yticklabels=["Movie", "TV Show"]
    )

    plt.title(name + " Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.show()

# ============================================================
# PART 21: MODEL COMPARISON
# ============================================================

comparison = pd.DataFrame(results)

print("\nMODEL COMPARISON:")
print(comparison)

comparison.set_index("Model").plot(
    kind="bar",
    figsize=(10, 6)
)

plt.title("Logistic Regression vs Random Forest")
plt.ylabel("Score")
plt.ylim(0, 1)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# ============================================================
# PART 22: LOGISTIC REGRESSION ERROR ANALYSIS
# ============================================================

error_analysis = pd.DataFrame({

    "Actual": y_test,
    "Predicted": lr_predictions

})

error_analysis = error_analysis[
    error_analysis["Actual"] !=
    error_analysis["Predicted"]
].copy()

# Add title using original row indices
error_analysis["Title"] = ml_df.loc[
    error_analysis.index,
    "title"
]

print("\nLOGISTIC REGRESSION ERROR ANALYSIS")

print(
    "Number of incorrect predictions:",
    len(error_analysis)
)

print(error_analysis.head(20))

print("\nLogistic Regression Classification Report:")

print(
    classification_report(
        y_test,
        lr_predictions,
        zero_division=0
    )
)

error_analysis.to_csv(
    "logistic_regression_errors.csv",
    index=True
)

# ============================================================
# PART 23: CONTENT TYPE DISTRIBUTION
# ============================================================

print("\nACTUAL CONTENT TYPE DISTRIBUTION")

content_counts = y.value_counts()

content_percentages = (
    y.value_counts(normalize=True) * 100
)

print("\nContent Counts:")
print(content_counts)

print("\nContent Percentages:")
print(content_percentages)

plt.figure(figsize=(6, 5))

content_counts.plot(
    kind="pie",
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Netflix Content Type Distribution")
plt.ylabel("")
plt.tight_layout()
plt.show()

# ============================================================
# PART 24: RANDOM FOREST ERROR ANALYSIS
# ============================================================

rf_error_analysis = pd.DataFrame({

    "Actual": y_test,
    "Predicted": rf_predictions

})

rf_error_analysis = rf_error_analysis[
    rf_error_analysis["Actual"] !=
    rf_error_analysis["Predicted"]
].copy()

rf_error_analysis["Title"] = ml_df.loc[
    rf_error_analysis.index,
    "title"
]

print("\nRANDOM FOREST ERROR ANALYSIS")

print(
    "Number of incorrect predictions:",
    len(rf_error_analysis)
)

print(rf_error_analysis.head(20))

print("\nRandom Forest Classification Report:")

print(
    classification_report(
        y_test,
        rf_predictions,
        zero_division=0
    )
)

rf_error_analysis.to_csv(
    "random_forest_errors.csv",
    index=True
)

# ============================================================
# PART 25: RANDOM FOREST CLASS DISTRIBUTION
# ============================================================

print("\nRANDOM FOREST PREDICTION DISTRIBUTION")

rf_counts = pd.Series(rf_predictions).value_counts()

rf_percentages = (
    pd.Series(rf_predictions).value_counts(normalize=True) * 100
)

print("\nPrediction Counts:")
print(rf_counts)

print("\nPrediction Percentages:")
print(rf_percentages)

plt.figure(figsize=(6, 5))

rf_counts.plot(
    kind="bar",
    color="orange"
)

plt.title("Random Forest Prediction Distribution")
plt.xlabel("Predicted Content Type")
plt.ylabel("Number of Predictions")
plt.tight_layout()
plt.show()

# ============================================================
# PART 26: COMPARE ERROR COUNTS
# ============================================================

lr_errors = len(error_analysis)

rf_errors = len(rf_error_analysis)

print("\nERROR COUNT COMPARISON")

print("Logistic Regression Errors:", lr_errors)

print("Random Forest Errors:", rf_errors)

if lr_errors < rf_errors:

    print("Logistic Regression has fewer errors.")

elif rf_errors < lr_errors:

    print("Random Forest has fewer errors.")

else:

    print("Both models have the same number of errors.")

# ============================================================
# PART 27: FEATURE COMPARISON
# ============================================================

print("\nFEATURE COMPARISON")

# Features without genre
X_without_genre = ml_df[
    ["release_year", "rating", "country"]
].copy()

# Features with genre
X_with_genre = ml_df[
    ["release_year", "rating", "country", "listed_in"]
].copy()

y_feature = ml_df["type"].copy()

X_train_without, X_test_without, y_train_feature, y_test_feature = train_test_split(
    X_without_genre,
    y_feature,
    test_size=0.20,
    random_state=42,
    stratify=y_feature
)

X_train_with, X_test_with, _, _ = train_test_split(
    X_with_genre,
    y_feature,
    test_size=0.20,
    random_state=42,
    stratify=y_feature
)

def create_preprocessor(numerical, categorical):

    num_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ]
    )

    cat_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value="Unknown"
                )
            ),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore")
            )
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", num_transformer, numerical),
            ("cat", cat_transformer, categorical)
        ]
    )

# Preprocessor without genre
preprocessor_without = create_preprocessor(
    ["release_year"],
    ["rating", "country"]
)

# Preprocessor with genre
preprocessor_with = create_preprocessor(
    ["release_year"],
    ["rating", "country", "listed_in"]
)

feature_models = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )

}

feature_results = []

for name, model in feature_models.items():

    # Without genre
    pipeline_without = Pipeline(
        steps=[
            ("preprocessor", preprocessor_without),
            ("model", model)
        ]
    )

    pipeline_without.fit(
        X_train_without,
        y_train_feature
    )

    pred_without = pipeline_without.predict(
        X_test_without
    )

    accuracy_without = accuracy_score(
        y_test_feature,
        pred_without
    )

    # With genre
    pipeline_with = Pipeline(
        steps=[
            ("preprocessor", preprocessor_with),
            ("model", model)
        ]
    )

    pipeline_with.fit(
        X_train_with,
        y_train_feature
    )

    pred_with = pipeline_with.predict(
        X_test_with
    )

    accuracy_with = accuracy_score(
        y_test_feature,
        pred_with
    )

    feature_results.append({

        "Model": name,
        "Accuracy Without Genre": accuracy_without,
        "Accuracy With Genre": accuracy_with

    })

feature_comparison = pd.DataFrame(feature_results)

print("\nFEATURE COMPARISON RESULTS")

print(feature_comparison)

feature_comparison.set_index("Model").plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Model Accuracy With and Without Genre")
plt.ylabel("Accuracy")
plt.ylim(0, 1)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# ============================================================
# PART 28: FINAL SUMMARY
# ============================================================

print("\n======================================")
print("NETFLIX CONTENT ANALYSIS COMPLETED")
print("======================================")

print("\nTotal Dataset Rows:", len(df))

print("Machine Learning Rows:", len(ml_df))

print("\nFinal Model Results:")

print(comparison)

print("\nFiles Generated:")
print("1. netflix_first_1000_cleaned.csv")
print("2. netflix_final_prepared.csv")
print("3. logistic_model.pkl")
print("4. random_forest_model.pkl")
print("5. logistic_regression_errors.csv")
print("6. random_forest_errors.csv")

print("\nPROJECT COMPLETED SUCCESSFULLY!")