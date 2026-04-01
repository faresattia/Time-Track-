import pandas as pd
import numpy as np
import joblib
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import classification_report, mean_absolute_error

df = pd.read_csv("student_weekly_schedule_dataset.csv")

# ===== حساب duration بالدقايق من Start_Time و End_Time =====
def calc_duration(start, end):
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    start_min = sh * 60 + sm
    end_min = eh * 60 + em
    if end_min < start_min:  # زي Rest اللي بيعدي منتصف الليل
        end_min += 24 * 60
    return end_min - start_min

df["duration_min"] = df.apply(lambda r: calc_duration(r["Start_Time"], r["End_Time"]), axis=1)

# ===== task_description هي الـ Description =====
df["task_description"] = df["Description"].str.lower().str.strip()
df["task_description"] = df["task_description"].apply(lambda x: re.sub(r"[^\w\s]", "", x))

# ===== category هي Activity_Type =====
df["category"] = df["Activity_Type"]

print(df[["task_description", "category", "duration_min"]].head(10))
print(df["category"].value_counts())

# ===== Split =====
X = df["task_description"]
y_category = df["category"]
y_duration = df["duration_min"]

X_train, X_test, y_train_cat, y_test_cat = train_test_split(X, y_category, test_size=0.2, random_state=42)
_, _, y_train_dur, y_test_dur = train_test_split(X, y_duration, test_size=0.2, random_state=42)

# ===== TF-IDF =====
vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# ===== Models =====
classifier = LogisticRegression(max_iter=1000)
classifier.fit(X_train_vec, y_train_cat)
print("Classification Report:")
print(classification_report(y_test_cat, classifier.predict(X_test_vec)))

regressor = RandomForestRegressor(n_estimators=100)
regressor.fit(X_train_vec, y_train_dur)
preds = regressor.predict(X_test_vec)
print("MAE:", mean_absolute_error(y_test_dur, preds))

# ===== Save =====
os.makedirs("models", exist_ok=True)
joblib.dump(classifier, "models/classifier.pkl")
joblib.dump(regressor, "models/regressor.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")
print("Models saved!")