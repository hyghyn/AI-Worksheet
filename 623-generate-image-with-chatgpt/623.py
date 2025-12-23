from openai import OpenAI
import urllib.request
import os

# ใช้ Environment Variable แทนการใส่ API Key ตรงๆ
# Windows: set OPENAI_API_KEY=your-api-key
# Linux/Mac: export OPENAI_API_KEY=your-api-key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # หรือใส่ API Key ของคุณที่นี่
)

response = client.images.generate(
    model="dall-e-3",
    prompt="a cute dog and a cat playing together in a garden, digital art",
    size="1024x1024",
    quality="standard",
    n=1,)

image_url = response.data[0].url
urllib.request.urlretrieve(image_url, "output_image.png")