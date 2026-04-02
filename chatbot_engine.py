import pandas as pd
import joblib
import re
import spacy

# تحميل الموديل اللغوي لـ spacy
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # في حال لم يتم تحميله برمجياً سابقاً
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# تحميل البيانات والموديلات
# تأكد أن المسارات صحيحة بالنسبة لمجلد المشروع
df = pd.read_csv("student_weekly_schedule_dataset.csv")
classifier = joblib.load("models/classifier.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

def clean_text(text):
    text = text.lower().strip()
    return re.sub(r"[^\w\s]", "", text)

def get_chatbot_response(user_input):
    """
    الدالة الأساسية التي تستقبل رسالة المستخدم وتعيد الرد
    """
    user_input_cleaned = clean_text(user_input)
    
    # 1. تحليل النية (Intent) باستخدام spaCy
    doc = nlp(user_input_cleaned)
    
    # البحث عن أيام الأسبوع في جملة المستخدم
    days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    found_day = None
    for token in doc:
        if token.text in days:
            found_day = token.text.capitalize()
            break

    # 2. إذا كان المستخدم يسأل عن يوم محدد
    if found_day:
        results = df[df["Day"] == found_day]
        if not results.empty:
            response = f"Your schedule for {found_day} is: \n"
            for _, row in results.iterrows():
                response += f"- {row['Start_Time']} to {row['End_Time']}: {row['Description']} ({row['Activity_Type']})\n"
            return response
        else:
            return f"I couldn't find any activities scheduled for {found_day}."

    # 3. إذا لم يحدد يوماً، نستخدم الموديل لتصنيف نوع النشاط الذي يسأل عنه
    else:
        vector = vectorizer.transform([user_input_cleaned])
        prediction = classifier.predict(vector)[0]
        
        # ردود ذكية بناءً على التصنيف
        if prediction == "Study":
            return "It seems you are asking about study sessions. You can ask me 'What is my schedule on Monday?' to see your plan."
        elif prediction == "Lecture":
            return "Are you looking for your lectures? Tell me which day you want to check."
        elif prediction == "Rest":
            return "Taking a break is important! Do you want to know when your next rest period is? Just specify the day."
        else:
            return f"I think you are talking about {prediction}. Could you please specify a day so I can give you details from your schedule?"