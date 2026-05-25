import os
import requests
from dotenv import load_dotenv

# Memuat isi file .env
load_dotenv()

def tanya_ai(pertanyaan):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": pertanyaan}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"