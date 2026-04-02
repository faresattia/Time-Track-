function generateLecturesFields() {
    const count = parseInt(document.getElementById('lec_count').value || 0);
    const container = document.getElementById('lectures_container');
    container.innerHTML = '';
    const days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'];
    
    for (let i = 1; i <= count; i++) {
        const div = document.createElement('div');
        div.className = 'lecture-item';
        div.innerHTML = `
            <h4> Lecture ${i}</h4>
            <label> Day:</label>
            <select class="lec-day">
                ${days.map(d => `<option value="${d}">${d}</option>`).join('')}
            </select>
            <label> Subject:</label>
            <input type="text" class="lec-subject" value="Subject ${i}" />
        `;
        container.appendChild(div);
    }
}

// ربط الأحداث
document.getElementById('lec_count').addEventListener('change', generateLecturesFields);

// الحدث الرئيسي عند الضغط على الزرار
document.getElementById("mainForm").addEventListener("submit", async function(e) {
    e.preventDefault(); // منع الريفرش نهائياً
    
    console.log("Starting prediction...");
    const tasks = [];

    // 1. جمع المحاضرات
    document.querySelectorAll(".lecture-item").forEach(el => {
        const day = el.querySelector(".lec-day").value;
        const subject = el.querySelector(".lec-subject").value;
        tasks.push(`Lecture: ${subject} on ${day}`);
    });

    // 2. جمع الهوايات (Interests)
    const interests = document.querySelector('input[name="interests"]').value;
    if (interests) {
        interests.split(',').forEach(item => {
            if(item.trim()) tasks.push(item.trim());
        });
    }

    if (tasks.length === 0) {
        alert("Please add some lectures or hobbies!");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8001/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tasks: tasks })
        });

        if (!response.ok) throw new Error("Server error");

        const data = await response.json();
        console.log("Data received:", data);

        // تخزين البيانات
        localStorage.setItem("schedule", JSON.stringify(data.weekly_schedule));

        // الانتقال للصفحة 
        window.location.href = "/schedule"; 

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to connect to server. Make sure Backend is running on port 8001");
    }
});

const chatWindow = document.getElementById('chatWindow');
const chatTrigger = document.getElementById('chatTrigger');
const closeChat = document.getElementById('closeChat');
const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');
const chatBody = document.getElementById('chatBody');

// فتح وإغلاق الشات
function toggleChat() {
    chatWindow.classList.toggle('open');
    if (chatWindow.classList.contains('open')) {
        chatTrigger.innerHTML = '×';
        userInput.focus();
    } else {
        chatTrigger.innerHTML = '💬';
    }
}

chatTrigger.addEventListener('click', toggleChat);
closeChat.addEventListener('click', toggleChat);

// إرسال الرسالة
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // إضافة رسالة المستخدم للواجهة
    appendMessage(text, 'user');
    userInput.value = '';

    try {
        // الربط مع سيرفر Uvicorn (تأكد من العنوان والـ Port)
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "msg": text })
        });

        const data = await response.json();
        appendMessage(data.reply, 'bot');
    } catch (error) {
        appendMessage('خطأ: تأكد من تشغيل السيرفر (Uvicorn)', 'bot');
    }
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.innerText = text;
    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// تشغيل أولي
generateLecturesFields();