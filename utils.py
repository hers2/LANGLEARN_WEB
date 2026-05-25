import os
import requests
from dotenv import load_dotenv

# Ambil data dari file .env
load_dotenv()

def panggil_ai_deepseek(teks_user):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": teks_user}],
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        # Mengambil jawaban teks dari AI
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Waduh, ada masalah: {str(e)}"