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

app = FastAPI()

# 1. إعداد CORS والملفات الثابتة
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="."), name="static")

# 2. تحميل الموديلات (تأكد من وجود مجلد models)
classifier = joblib.load("models/classifier.pkl")
regressor = joblib.load("models/regressor.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

def clean_text(text: str):
    text = text.lower().strip()
    return re.sub(r"[^\w\s]", "", text)

# 3. دالة توزيع المهام بناءً على الوقت المتوقع من AI
def build_ai_day_schedule(tasks_with_ai, start_hour=8):
    sessions = []
    current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")
    
    for task in tasks_with_ai:
        # استخدام الوقت المتوقع من Regressor (بالدقائق)
        duration = int(task["predicted_duration"])
        duration = max(30, min(duration, 180)) # ضمان وقت منطقي بين 30 و 180 دقيقة
        
        start_str = current_time.strftime("%H:%M")
        end_time = current_time + timedelta(minutes=duration)
        end_str = end_time.strftime("%H:%M")
        
        sessions.append({
            "task": task["name"],
            "category": task["category"],
            "start": start_str,
            "end": end_str
        })
        # إضافة فجوة 30 دقيقة بين المهام
        current_time = end_time + timedelta(minutes=30)
        
    return sessions

class TaskInput(BaseModel):
    tasks: list[str]

@app.post("/predict")
async def predict_task(data: TaskInput):
    tasks_details = []
    for task_desc in data.tasks:
        cleaned = clean_text(task_desc)
        vector = vectorizer.transform([cleaned])
        
        # التوقع بالنوع والمدة
        category = classifier.predict(vector)[0]
        duration = regressor.predict(vector)[0]
        
        tasks_details.append({
            "name": task_desc,
            "category": category,
            "predicted_duration": duration
        })

    # توليد جدول لـ 7 أيام
    weekly_schedule = []
    today = datetime.now()
    for i in range(7):
        actual_date = today + timedelta(days=i)
        
        # خلط المهام يومياً للتنوع
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

@app.get("/")
async def read_index():
    return FileResponse('index.html')
# أضف هذا المسار ليتمكن السيرفر من قراءة صفحة الجدول
@app.get("/schedule")
async def read_schedule():
    return FileResponse('schedule.html')