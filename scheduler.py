from datetime import datetime, timedelta

def allocate(duration_hours):

    start_time = datetime.now().replace(hour=9, minute=0)
    schedule = []

    block_size = 2
    remaining = duration_hours

    while remaining > 0:
        current_block = min(block_size, remaining)

        end_time = start_time + timedelta(hours=current_block)

        schedule.append({
            "start": start_time.strftime("%Y-%m-%d %H:%M"),
            "end": end_time.strftime("%Y-%m-%d %H:%M")
        })

        start_time = end_time + timedelta(hours=1)
        remaining -= current_block

    return schedule


# ========== أضف الدالة الجديدة هنا ==========
def allocate_weekly(duration_hours, start_day="Monday"):
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_day_index = days_order.index(start_day)  # ← أضف السطر ده
    
    schedule = []
    remaining = duration_hours
    current_hour = 9
    
    while remaining > 0:
        block = min(2, remaining)
        
        today = datetime.now()
        day_date = today + timedelta(days=(current_day_index - today.weekday()) % 7)
        start = f"{day_date.strftime('%A %Y-%m-%d')} {current_hour:02d}:00"
        end = f"{day_date.strftime('%A %Y-%m-%d')} {current_hour + int(block):02d}:00"
        
        schedule.append({
            "start": start,
            "end": end,
            "duration": block
        })
        
        current_hour += int(block) + 1
        remaining -= block
        
        if current_hour >= 17:
            break
    
    return schedule