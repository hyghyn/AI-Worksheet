from openai import OpenAI
import os

# ใช้ Environment Variable แทนการใส่ API Key ตรงๆ
# Windows: set OPENAI_API_KEY=your-api-key
# Linux/Mac: export OPENAI_API_KEY=your-api-key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # หรือใส่ API Key ของคุณที่นี่
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "คุณคือนักปรัญญา"},
        {"role": "user", "content": "ไก่ย่างห้าดาวคืออะไร?"}
    ],
    n=1, #number of responses expected from the Chat GPT
    stop=None
)

message = response.choices[0].message.content
print(message)