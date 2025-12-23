# 625 - LINE Chatbot with ChatGPT and Database

![Python](https://img.shields.io/badge/Python-3.x-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-Assistant-green)
![LINE](https://img.shields.io/badge/LINE-Bot-00C300)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue)
![Flask](https://img.shields.io/badge/Flask-Webhook-orange)

LINE Chatbot ที่เชื่อมต่อกับ OpenAI Assistant และฐานข้อมูล MySQL สามารถตอบคำถามจากข้อมูลในฐานข้อมูล (Database Query) แบบ Natural Language

## 📖 คำอธิบาย

โปรเจคนี้เป็นการพัฒนาต่อยอดจากโปรเจค 624 โดยเพิ่มความสามารถในการเชื่อมต่อและ query ข้อมูลจากฐานข้อมูล MySQL ผ่าน Natural Language ผู้ใช้สามารถถามคำถามเป็นภาษาธรรมดา และ AI จะแปลงเป็น SQL Query และส่งคำตอบกลับมา

## ✨ ฟีเจอร์

- ✅ LINE Chatbot แบบ Real-time
- ✅ เชื่อมต่อกับ OpenAI Assistant API
- ✅ Query ฐานข้อมูล MySQL ด้วย Natural Language
- ✅ แปลงคำถามเป็น SQL Query อัตโนมัติ
- ✅ รองรับ Chinook Database (Music Store)
- ✅ จดจำบริบทการสนทนา
- ✅ ตอบคำถามภาษาไทยได้

## 🔧 เทคโนโลยีที่ใช้

- **OpenAI Assistant API** - AI สำหรับแปลง Natural Language เป็น SQL
- **LINE Messaging API** - แพลตฟอร์ม Chatbot
- **MySQL** - ฐานข้อมูล
- **Flask** - Web Framework สำหรับ Webhook
- **Python 3.x** - ภาษาโปรแกรม

## 📦 การติดตั้ง

```bash
pip install openai flask line-bot-sdk mysql-connector-python
```

## 🗄️ Database Setup

### 1. ติดตั้ง MySQL

```bash
# Windows
# ดาวน์โหลดจาก: https://dev.mysql.com/downloads/installer/

# macOS
brew install mysql

# Linux (Ubuntu)
sudo apt-get install mysql-server
```

### 2. Import Chinook Database

```bash
# เข้าสู่ MySQL
mysql -u root -p

# สร้างฐานข้อมูล
CREATE DATABASE chinook;
USE chinook;

# Import ไฟล์ SQL
SOURCE /path/to/Chinook_MySql.sql;
```

### 3. ตรวจสอบตารางที่มี

```sql
SHOW TABLES;

-- ตารางที่สำคัญ:
-- - Album (อัลบั้มเพลง)
-- - Artist (ศิลปิน)
-- - Track (เพลง)
-- - Customer (ลูกค้า)
-- - Invoice (ใบแจ้งหนี้)
-- - Employee (พนักงาน)
```

## 🔑 การตั้งค่า

### 1. OpenAI Assistant Setup

สร้าง Assistant ที่มี **Code Interpreter** หรือ **Function Calling**:

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

# สร้าง Assistant with Code Interpreter
assistant = client.beta.assistants.create(
    name="Database Query Assistant",
    instructions="""
คุณคือผู้ช่วยที่เชี่ยวชาญในการแปลงคำถามเป็น SQL Query
Database Schema:
- Album: AlbumId, Title, ArtistId
- Artist: ArtistId, Name
- Track: TrackId, Name, AlbumId, GenreId, Composer, Milliseconds, Bytes, UnitPrice
- Customer: CustomerId, FirstName, LastName, Country, Email
- Invoice: InvoiceId, CustomerId, InvoiceDate, Total

เมื่อได้รับคำถาม ให้:
1. แปลงเป็น SQL Query
2. อธิบายว่า Query ทำอะไร
3. ตอบคำถามด้วยภาษาไทยที่เข้าใจง่าย
    """,
    model="gpt-4o-mini",
    tools=[{"type": "code_interpreter"}]
)

print(f"Assistant ID: {assistant.id}")
```

### 2. Configuration

```python
# OpenAI Configuration
assistant_id = "asst_xxxxxxxxxxxxx"
api_key = "your-openai-api-key"

# LINE Configuration
channel_secret = "your-channel-secret"
channel_access_token = "your-channel-access-token"

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your-password',
    'database': 'chinook'
}
```

## 🚀 การใช้งาน

### โครงสร้างโค้ดพื้นฐาน

```python
import mysql.connector
from openai import OpenAI
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
import time

# Initialize
client = OpenAI(api_key=api_key)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
app = Flask(__name__)

# Database Connection
def execute_query(sql_query):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return f"Error: {str(e)}"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # สร้าง Thread
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": f"คำถาม: {user_message}\nกรุณาสร้าง SQL Query สำหรับคำถามนี้"
            }
        ]
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
    
    # ดึง SQL Query จากคำตอบ
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response_text = messages.data[0].content[0].text.value
    
    # Extract SQL Query (ใช้ regex หรือ parsing)
    # สมมติว่า SQL Query อยู่ระหว่าง ```sql ... ```
    import re
    sql_match = re.search(r'```sql\n(.*?)\n```', response_text, re.DOTALL)
    
    if sql_match:
        sql_query = sql_match.group(1)
        
        # Execute Query
        results = execute_query(sql_query)
        
        # Format ผลลัพธ์
        if isinstance(results, list) and len(results) > 0:
            output = f"พบข้อมูล {len(results)} รายการ:\n\n"
            for i, row in enumerate(results[:5], 1):  # แสดง 5 รายการแรก
                output += f"{i}. " + ", ".join([f"{k}: {v}" for k, v in row.items()]) + "\n"
            
            if len(results) > 5:
                output += f"\n... และอีก {len(results)-5} รายการ"
        else:
            output = "ไม่พบข้อมูล"
    else:
        output = response_text
    
    # ส่งกลับไปยัง LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=output)
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

## 📊 ตัวอย่างคำถามและ SQL

### 1. คำถามเกี่ยวกับศิลปิน
```
คำถาม: "มีศิลปินทั้งหมดกี่คน?"
SQL: SELECT COUNT(*) as total FROM Artist;
คำตอบ: มีศิลปินทั้งหมด 275 คน
```

### 2. คำถามเกี่ยวกับเพลง
```
คำถาม: "เพลงของ AC/DC มีอะไรบ้าง?"
SQL: SELECT t.Name 
     FROM Track t 
     JOIN Album a ON t.AlbumId = a.AlbumId 
     JOIN Artist ar ON a.ArtistId = ar.ArtistId 
     WHERE ar.Name = 'AC/DC';
คำตอบ: เพลงของ AC/DC ที่พบ: For Those About To Rock, Put The Finger On You, ...
```

### 3. คำถามเกี่ยวกับยอดขาย
```
คำถาม: "ลูกค้าคนไหนซื้อมากที่สุด?"
SQL: SELECT c.FirstName, c.LastName, SUM(i.Total) as TotalSpent
     FROM Customer c
     JOIN Invoice i ON c.CustomerId = i.CustomerId
     GROUP BY c.CustomerId
     ORDER BY TotalSpent DESC
     LIMIT 1;
คำตอบ: ลูกค้าที่ซื้อมากที่สุดคือ Helena Holy ซื้อไปทั้งหมด $49.62
```

### 4. คำถามซับซ้อน
```
คำถาม: "ประเทศไหนมีลูกค้ามากที่สุด 5 อันดับแรก?"
SQL: SELECT Country, COUNT(*) as CustomerCount
     FROM Customer
     GROUP BY Country
     ORDER BY CustomerCount DESC
     LIMIT 5;
คำตอบ: ประเทศที่มีลูกค้ามากที่สุด 5 อันดับ: USA (13), Canada (8), France (5), ...
```

## 🎯 Use Cases

1. **E-commerce Analytics** - วิเคราะห์ยอดขายและพฤติกรรมลูกค้า
2. **Customer Service** - ตอบคำถามเกี่ยวกับสินค้า/คำสั่งซื้อ
3. **Business Intelligence** - รายงานข้อมูลธุรกิจ
4. **Inventory Management** - ตรวจสอบสต็อกสินค้า
5. **HR System** - query ข้อมูลพนักงาน

## ⚙️ Advanced Features

### 1. Function Calling (แนะนำ)

```python
# กำหนด Function สำหรับ query database
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Execute SQL query on the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["sql_query"]
            }
        }
    }
]

# สร้าง Assistant with Function
assistant = client.beta.assistants.create(
    name="Database Query Assistant",
    instructions="...",
    model="gpt-4o-mini",
    tools=tools
)
```

### 2. เพิ่มความปลอดภัย

```python
def is_safe_query(sql_query):
    # ตรวจสอบว่าเป็น SELECT เท่านั้น
    if not sql_query.strip().upper().startswith('SELECT'):
        return False
    
    # ห้ามคำสั่งอันตราย
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
    for keyword in dangerous_keywords:
        if keyword in sql_query.upper():
            return False
    
    return True

# ใช้งาน
if is_safe_query(sql_query):
    results = execute_query(sql_query)
else:
    results = "ไม่สามารถ execute คำสั่งนี้ได้ เพื่อความปลอดภัย"
```

### 3. แคชผลลัพธ์

```python
import hashlib
import pickle

query_cache = {}

def execute_query_with_cache(sql_query):
    # สร้าง hash key
    query_hash = hashlib.md5(sql_query.encode()).hexdigest()
    
    # ตรวจสอบ cache
    if query_hash in query_cache:
        return query_cache[query_hash]
    
    # Execute และเก็บใน cache
    results = execute_query(sql_query)
    query_cache[query_hash] = results
    
    return results
```

## 💰 ราคา

### OpenAI Assistant API
- **gpt-4o-mini**: $0.150 / 1M input tokens, $0.600 / 1M output tokens
- **Function Calling**: ไม่มีค่าใช้จ่ายเพิ่มเติม

### MySQL
- **Local**: ฟรี
- **Cloud (AWS RDS)**: เริ่มต้น $15-30/เดือน
- **Cloud (PlanetScale)**: Free tier มี

### LINE Messaging API
- **Free Tier**: 500 messages/month
- **Paid**: 0.30-0.50 บาท/message

## ⚠️ ข้อควรระวัง

1. **SQL Injection**
   - ✅ ใช้ Parameterized Queries
   - ✅ Validate SQL ก่อน execute
   - ✅ จำกัดเฉพาะ SELECT

2. **Performance**
   - ใช้ LIMIT สำหรับผลลัพธ์ที่มาก
   - สร้าง Index บนคอลัมน์ที่ query บ่อย
   - ใช้ Connection Pooling

3. **Security**
   - ❌ ห้าม expose database credentials
   - ✅ ใช้ Read-only user สำหรับ query
   - ✅ ตั้ง timeout สำหรับ query

4. **Timeout**
   - LINE webhook timeout 30 วินาที
   - Query ที่ซับซ้อนอาจเกินเวลา
   - ควรมี fallback message

## 🐛 การแก้ปัญหา

### Query ช้าเกินไป
```python
# ตั้ง timeout
cursor.execute(sql_query, timeout=10)

# หรือใช้ asyncio
import asyncio
result = await asyncio.wait_for(execute_query(sql_query), timeout=10)
```

### AI สร้าง SQL ผิด
- ✅ ปรับ Instructions ให้ละเอียด
- ✅ ให้ตัวอย่าง SQL ที่ถูกต้อง
- ✅ ระบุ Schema ชัดเจน

### Database Connection Error
```python
# ใช้ Connection Pool
from mysql.connector import pooling

db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)

def execute_query(sql_query):
    conn = db_pool.get_connection()
    # ... execute query ...
    conn.close()
```

## 📚 Chinook Database Schema

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Artist    │────>│   Album     │────>│   Track     │
│             │     │             │     │             │
│ ArtistId PK │     │ AlbumId  PK │     │ TrackId  PK │
│ Name        │     │ Title       │     │ Name        │
└─────────────┘     │ ArtistId FK │     │ AlbumId  FK │
                    └─────────────┘     │ GenreId  FK │
                                       │ UnitPrice   │
                                       └─────────────┘
┌─────────────┐     ┌─────────────┐
│  Customer   │────>│  Invoice    │
│             │     │             │
│ CustomerId  │     │ InvoiceId   │
│ FirstName   │     │ CustomerId  │
│ LastName    │     │ Total       │
│ Country     │     └─────────────┘
└─────────────┘
```

## 📚 เอกสารเพิ่มเติม

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [MySQL Connector Python](https://dev.mysql.com/doc/connector-python/en/)
- [Chinook Database](https://github.com/lerocha/chinook-database)
- [SQL Tutorial](https://www.w3schools.com/sql/)

## 🔒 Best Practices

1. **ใช้ Read-only Database User** เพื่อความปลอดภัย
2. **Validate SQL ทุกครั้ง** ก่อน execute
3. **จำกัดจำนวนผลลัพธ์** ด้วย LIMIT
4. **ใช้ Connection Pooling** เพื่อประสิทธิภาพ
5. **Log SQL Queries** สำหรับ debugging
6. **Cache ผลลัพธ์** สำหรับ query ที่ซ้ำ
7. **Monitor Performance** ตรวจสอบ slow queries

## 🚀 การพัฒนาต่อ

### 1. เพิ่ม Visualization
```python
# สร้างกราฟจากข้อมูล
import matplotlib.pyplot as plt
# ... generate chart ...
# ส่งกลับเป็นรูปภาพใน LINE
```

### 2. Multi-Database Support
```python
# รองรับหลาย database
databases = {
    'chinook': db_config_chinook,
    'sales': db_config_sales
}
```

### 3. Export ผลลัพธ์
```python
# Export เป็น CSV, Excel
import pandas as pd
df = pd.DataFrame(results)
df.to_excel('output.xlsx')
```

---

💡 **Pro Tip**: สร้าง database view สำหรับ query ที่ใช้บ่อยเพื่อเพิ่มความเร็วและความปลอดภัย

---

## 📝 หมายเหตุ

โปรเจคนี้อยู่ระหว่างการพัฒนา ปัจจุบันมีเพียงไฟล์ `Chinook_MySql.sql` สำหรับ setup ฐานข้อมูล โค้ด Python สำหรับ LINE Bot จะถูกเพิ่มในอนาคต
