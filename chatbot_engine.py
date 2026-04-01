# %%
import pandas as pd
import re

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score

import spacy

# %%
nlp = spacy.load("en_core_web_sm")

# %%
df = pd.read_csv("student_weekly_schedule_dataset.csv")

print(df.head())

# %%
def clean_text(text):

    text = str(text).lower()

    text = re.sub(r'[^a-zA-Z\s]', '', text)

    return text

df["clean_description"] = df["Description"].apply(clean_text)

# %%
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=3000
)

X = vectorizer.fit_transform(df["clean_description"])

y = df["Activity_Type"]

# %%
X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,
    test_size=0.2,
    random_state=42

)

# %%
model_lr = LogisticRegression(max_iter=1000)

model_lr.fit(X_train, y_train)

# %%
model_nb = MultinomialNB()

model_nb.fit(X_train, y_train)

# %%
model_svm = LinearSVC()

model_svm.fit(X_train, y_train)

# %%
model_rf = RandomForestClassifier()

model_rf.fit(X_train, y_train)

# %%
pred_lr = model_lr.predict(X_test)
pred_nb = model_nb.predict(X_test)
pred_svm = model_svm.predict(X_test)
pred_rf = model_rf.predict(X_test)

print("Logistic Regression:", accuracy_score(y_test, pred_lr))
print("Naive Bayes:", accuracy_score(y_test, pred_nb))
print("SVM:", accuracy_score(y_test, pred_svm))
print("Random Forest:", accuracy_score(y_test, pred_rf))

# %%
def extract_day(text):

    doc = nlp(text)

    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    ]

    for token in doc:

        if token.text.lower() in days:

            return token.text.lower()

    return None

# %%
from datetime import datetime

# %%
def get_today():

    today = datetime.today().strftime("%A").lower()

    return today

# %%
days = [
"sunday",
"monday",
"tuesday",
"wednesday",
"thursday",
"friday",
"saturday"
]

def get_tomorrow():

    today = datetime.today().strftime("%A").lower()

    index = days.index(today)

    tomorrow = days[(index + 1) % 7]

    return tomorrow

# %%
def next_activity():

    now = datetime.now().hour

    results = df[df["Start_Time"] > now]

    if len(results) > 0:

        next_row = results.iloc[0]

        return next_row

    return None

# %%
def schedule_chatbot():

    print("Smart Student Schedule Bot")
    print("Ask about your schedule")
    print("Type exit to stop")

    while True:

        user = input("You: ").lower()


        if user == "exit":

            print("Bot: Goodbye")

            break


        user_clean = clean_text(user)

        user_vec = vectorizer.transform([user_clean])

        prediction = model_svm.predict(user_vec)[0]


        if "today" in user:

            day = get_today()

        elif "tomorrow" in user:

            day = get_tomorrow()

        else:

            day = extract_day(user)


        if "next" in user:

            nxt = next_activity()

            if nxt is not None:

                print("Bot: Your next activity is", nxt["Activity_Type"])

            else:

                print("Bot: No upcoming activity")

            continue


        if day:

            results = df[df["Day"].str.lower() == day]


            if len(results) == 0:

                print("Bot: No schedule found")

            else:

                print("Bot: Your schedule on", day)

                print(results[["Activity_Type","Start_Time","End_Time"]])

        else:

            print("Bot: This activity looks like:", prediction)

# %%
schedule_chatbot()

# %%
# chatbot_engine.py
def get_chatbot_response(user_input):
    # هنا تضع الكود الخاص بالتحميل والمعالجة (preprocessing)
    # ثم كود التوقع من الموديل
    return "الرد المناسب من البوت"

# %%



