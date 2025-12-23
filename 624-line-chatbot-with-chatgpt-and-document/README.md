# 624 - LINE Chatbot with ChatGPT and Document (OpenAI Assistant)

![Python](https://img.shields.io/badge/Python-3.x-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-Assistant-green)
![LINE](https://img.shields.io/badge/LINE-Bot-00C300)
![Flask](https://img.shields.io/badge/Flask-Webhook-orange)

LINE Chatbot ที่เชื่อมต่อกับ OpenAI Assistant API สามารถตอบคำถามจากเอกสารและข้อมูลที่ upload ไว้ พร้อมระบบจดจำบทสนทนา

## 📖 คำอธิบาย

โปรเจคนี้เป็น LINE Chatbot ที่ใช้ OpenAI **Assistant API** ซึ่งมีความสามารถพิเศษในการเข้าถึงเอกสาร (File Search) และจดจำบริบทของการสนทนา (Thread Management) เหมาะสำหรับสร้างบอทที่ต้องการตอบคำถามจากเอกสารหรือฐานความรู้

## ✨ ฟีเจอร์

- ✅ LINE Chatbot แบบ Real-time
- ✅ เชื่อมต่อกับ OpenAI Assistant API
- ✅ ค้นหาข้อมูลจากเอกสารที่ upload ไว้ (File Search)
- ✅ จดจำบริบทการสนทนา (Thread Management)
- ✅ ตอบคำถามภาษาไทยได้เป็นธรรมชาติ
- ✅ รองรับการสนทนาแบบต่อเนื่อง
- ✅ ใช้ Flask เป็น Webhook Server

## 🔧 เทคโนโลยีที่ใช้

- **OpenAI Assistant API** - ระบบ AI พร้อม File Search
- **LINE Messaging API** - แพลตฟอร์ม Chatbot
- **Flask** - Web Framework สำหรับ Webhook
- **Python 3.x** - ภาษาโปรแกรม

## 📦 การติดตั้ง

```bash
pip install openai flask line-bot-sdk
```

## 🔑 การตั้งค่า

### 1. OpenAI Assistant Setup

#### สร้าง Assistant (ทำผ่าน Platform หรือ API)

**วิธีที่ 1: ผ่าน OpenAI Platform**
1. ไปที่ [OpenAI Platform - Assistants](https://platform.openai.com/assistants)
2. คลิก "Create Assistant"
3. กำหนดชื่อและคำแนะนำ (Instructions)
4. เปิด Tools: **File Search**
5. Upload เอกสาร (PDF, TXT, DOCX, etc.)
6. คัดลอก **Assistant ID**

**วิธีที่ 2: ผ่าน API**
```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

# สร้าง Assistant
assistant = client.beta.assistants.create(
    name="EPT Chatbot",
    instructions="คุณคือผู้ช่วยที่เชี่ยวชาญในการตอบคำถามจากเอกสาร",
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}]
)

print(f"Assistant ID: {assistant.id}")
```

### 2. LINE Bot Setup

1. ไปที่ [LINE Developers Console](https://developers.line.biz/)
2. สร้าง Provider และ Messaging API Channel
3. ไปที่แท็บ "Messaging API"
4. คัดลอก:
   - **Channel Secret**
   - **Channel Access Token**
5. ตั้งค่า Webhook URL: `https://your-domain.com/`
6. เปิด "Use webhook" และปิด "Auto-reply messages"

### 3. ตั้งค่าใน Code

```python
# Configuration
assistant_id = "asst_xxxxxxxxxxxxx"  # จาก OpenAI
channel_secret = "your-channel-secret"  # จาก LINE
channel_access_token = "your-channel-access-token"  # จาก LINE
api_key = "your-openai-api-key"  # จาก OpenAI
```

## 🚀 การใช้งาน

### 1. รันโปรแกรมในเครื่อง (Development)

```bash
python 624.py
```

Flask จะรันที่ `http://localhost:5000`

### 2. ใช้ ngrok สำหรับทดสอบ

```bash
# ติดตั้ง ngrok
# https://ngrok.com/download

# รัน ngrok
ngrok http 5000
```

คัดลอก HTTPS URL (เช่น `https://abc123.ngrok.io`) ไปตั้งค่าเป็น Webhook URL ใน LINE Developers

### 3. Deploy บน Server (Production)

#### ใช้ Heroku
```bash
# สร้างไฟล์ Procfile
web: python 624.py

# สร้างไฟล์ requirements.txt
pip freeze > requirements.txt

# Deploy
heroku create your-app-name
git push heroku main
```

#### ใช้ Railway/Render
- Upload โค้ดไปยัง GitHub
- Connect กับ Railway/Render
- ตั้งค่า Environment Variables
- Deploy

## 📝 โครงสร้างโค้ด

```python
from openai import OpenAI
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 1. Initialize Clients
client = OpenAI(api_key="...")
line_bot_api = LineBotApi("...")
handler = WebhookHandler("...")

# 2. Flask Webhook
@app.route("/", methods=["GET", "POST"])
def home():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return "Hello, this is EPT-Chatbot"

# 3. Handle Messages
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    input_text = event.message.text
    
    # สร้าง Thread ใหม่สำหรับแต่ละการสนทนา
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": input_text}]
    )
    
    # รัน Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    # รอผลลัพธ์
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(2)
    
    # ดึงคำตอบ
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    output_text = messages.data[0].content[0].text.value
    
    # ส่งกลับไปยัง LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=output_text)
    )
```

## ⚙️ OpenAI Assistant Features

### 1. File Search
```python
# Upload ไฟล์เอกสาร
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="assistants"
)

# เพิ่มไฟล์ให้ Assistant
assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    file_ids=[file.id]
)
```

### 2. Thread Management (จดจำบทสนทนา)
```python
# สร้าง Thread ใหม่สำหรับผู้ใช้แต่ละคน
user_threads = {}

if user_id not in user_threads:
    thread = client.beta.threads.create()
    user_threads[user_id] = thread.id
else:
    thread_id = user_threads[user_id]

# เพิ่มข้อความใหม่ใน Thread
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=input_text
)
```

### 3. Instructions (กำหนดบุคลิก)
```python
instructions = """
คุณคือผู้ช่วยที่เชี่ยวชาญด้าน:
- ตอบคำถามจากเอกสารที่ให้มา
- พูดภาษาไทยอย่างสุภาพ
- ให้ข้อมูลที่ถูกต้องและครบถ้วน
- ถ้าไม่มีข้อมูลในเอกสาร ให้บอกตรงๆ
"""
```

## 🎯 Use Cases

1. **Customer Support Bot** - ตอบคำถามจาก FAQ
2. **Document Q&A** - ค้นหาข้อมูลในเอกสาร
3. **Knowledge Base** - ฐานความรู้องค์กร
4. **Educational Bot** - ตอบคำถามจากตำรา
5. **Product Information** - ข้อมูลสินค้า/บริการ

## 💰 ราคา

### OpenAI Assistant API
- **gpt-4o-mini**: $0.150 / 1M input tokens, $0.600 / 1M output tokens
- **File Storage**: $0.10 / GB / day
- **File Search**: $0.10 / GB (one-time per file)

### LINE Messaging API
- **Free Tier**: 500 messages/month
- **Paid**: 0.30-0.50 บาท/message (ขึ้นกับแพ็กเกจ)

## 📊 การจัดการ Thread

### เก็บ Thread ID ของแต่ละ User

```python
# ใช้ Dictionary (Temporary)
user_threads = {}

# หรือใช้ Database (Recommended)
import sqlite3

def get_or_create_thread(user_id):
    # ดึงจาก DB
    thread_id = db.get_thread(user_id)
    
    if not thread_id:
        # สร้างใหม่
        thread = client.beta.threads.create()
        db.save_thread(user_id, thread.id)
        return thread.id
    
    return thread_id
```

## ⚠️ ข้อควรระวัง

1. **Thread Limit**
   - แต่ละ Assistant รองรับหลาย Threads
   - ควรลบ Thread เก่าที่ไม่ใช้แล้ว

2. **File Size**
   - Max file size: 512 MB
   - รองรับ: PDF, TXT, DOCX, JSON, etc.
   - ไม่รองรับภาพ

3. **Response Time**
   - การรอผลลัพธ์อาจใช้เวลา 5-10 วินาที
   - LINE timeout ภายใน 30 วินาที
   - ควรมี fallback message

4. **ความปลอดภัย**
   - ❌ ห้ามเผยแพร่ API Keys
   - ✅ ใช้ Environment Variables
   - ✅ เข้ารหัส Channel Secret

## 🐛 การแก้ปัญหา

### บอทไม่ตอบ
```python
# เพิ่ม timeout และ error handling
import time

max_wait = 30  # วินาที
start_time = time.time()

while run.status != "completed":
    if time.time() - start_time > max_wait:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ขออภัย กำลังประมวลผลนานเกินไป กรุณาลองใหม่")
        )
        break
    
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    time.sleep(2)
```

### Webhook Failed
```python
# ตรวจสอบ Signature
try:
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
except Exception as e:
    print(f"Error: {e}")
    return "OK"  # Return OK เพื่อป้องกัน retry
```

### Assistant ตอบไม่ตรงคำถาม
- ✅ ปรับ Instructions ให้ชัดเจนขึ้น
- ✅ ตรวจสอบว่า File Search เปิดอยู่
- ✅ ตรวจสอบว่าเอกสารมีข้อมูลที่ต้องการ

## 📚 เอกสารเพิ่มเติม

- [OpenAI Assistant API](https://platform.openai.com/docs/assistants/overview)
- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [ngrok Documentation](https://ngrok.com/docs)

## 🔒 Best Practices

1. **ใช้ Environment Variables** สำหรับ credentials
2. **เก็บ Thread ID** ในฐานข้อมูล
3. **จัดการ Timeout** ให้เหมาะสม
4. **ลบ Thread เก่า** เป็นระยะ
5. **Monitor Usage** เพื่อควบคุมต้นทุน
6. **Log Conversations** สำหรับ debugging

## 🚀 การพัฒนาต่อ

### เพิ่ม Rich Menu
```python
# สร้าง Rich Menu ใน LINE
# ให้ผู้ใช้เลือกหัวข้อคำถาม
```

### เพิ่ม Database
```python
# เก็บประวัติการสนทนา
# Track user behavior
```

### Multi-Language Support
```python
# ตรวจจับภาษาและตอบกลับตามภาษานั้น
```

---

💡 **Pro Tip**: ใช้ OpenAI Playground ทดสอบ Assistant ก่อน integrate กับ LINE เพื่อปรับ Instructions ให้ได้ผลลัพธ์ที่ดี
