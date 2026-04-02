from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import re
import random
import os
from datetime import datetime, timedelta
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# استيراد الدالة من ملفك الجديد
from chatbot_engine import get_chatbot_response 

app = FastAPI()

# 1. إعداد CORS والملفات الثابتة
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تأكد أن مجلد static يحتوي على ملفات الـ CSS والـ JS
app.mount("/static", StaticFiles(directory="."), name="static")

# 2. تحميل الموديلات 
# ملاحظة: تأكد من وجود مجلد models وبه الملفات المطلوبة
classifier = joblib.load("models/classifier.pkl")
regressor = joblib.load("models/regressor.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

# --- النماذج (Models) لبيانات الدخول ---
class TaskInput(BaseModel):
    tasks: list[str]

class Msg(BaseModel): # تعريفه ضروري لكي يعمل الـ Chat
    msg: str

# --- الدوال المساعدة ---
def clean_text(text: str):
    text = text.lower().strip()
    return re.sub(r"[^\w\s]", "", text)

def build_ai_day_schedule(tasks_with_ai, start_hour=8):
    sessions = []
    current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")
    
    for task in tasks_with_ai:
        duration = int(task["predicted_duration"])
        duration = max(30, min(duration, 180)) 
        
        start_str = current_time.strftime("%H:%M")
        end_time = current_time + timedelta(minutes=duration)
        end_str = end_time.strftime("%H:%M")
        
        sessions.append({
            "task": task["name"],
            "category": task["category"],
            "start": start_str,
            "end": end_str
        })
        current_time = end_time + timedelta(minutes=30)
        
    return sessions

# --- المسارات (Endpoints) ---

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/schedule")
async def read_schedule():
    return FileResponse('schedule.html')

@app.post("/predict")
async def predict_task(data: TaskInput):
    tasks_details = []
    for task_desc in data.tasks:
        cleaned = clean_text(task_desc)
        vector = vectorizer.transform([cleaned])
        
        category = classifier.predict(vector)[0]
        duration = regressor.predict(vector)[0]
        
        tasks_details.append({
            "name": task_desc,
            "category": category,
            "predicted_duration": duration
        })

    weekly_schedule = []
    today = datetime.now()
    for i in range(7):
        actual_date = today + timedelta(days=i)
        shuffled = tasks_details.copy()
        random.seed(i)
        random.shuffle(shuffled)
        
        sessions = build_ai_day_schedule(shuffled)
        weekly_schedule.append({
            "day": actual_date.strftime("%A"),
            "date": actual_date.strftime("%Y-%m-%d"),
            "sessions": sessions
        })

    return {"weekly_schedule": weekly_schedule}

@app.post("/chat")
async def chat(input_data: Msg):
    # استخدام الدالة المستوردة من chatbot_engine.py
    try:
        response = get_chatbot_response(input_data.msg)
    except Exception as e:
        response = f"عذراً، حدث خطأ في محرك الشات: {str(e)}"
    
    return {"reply": response}