# core/ai_helper.py
import json
import logging
from groq import Groq
from django.conf import settings

logger = logging.getLogger(__name__)
_client = None


def get_groq_client():
    global _client
    if _client is None:
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError('GROQ_API_KEY is not configured')
        _client = Groq(api_key=api_key)
    return _client


def _safe_json_loads(text, fallback):
    try:
        cleaned = text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned)
    except Exception:
        return fallback


def ai_conversation(user_message, topic='Daily Conversation', history=None):
    history = history or []
    messages = [
        {
            'role': 'system',
            'content': f'''
You are Grammify, a friendly English conversation tutor.
Conversation topic/scope: {topic}.
Rules:
1. Keep the conversation focused on this topic.
2. Reply in simple English.
3. Ask one follow-up question so the user keeps practicing.
4. Correct grammar gently only when needed.
5. If explaining a correction, use simple Indonesian.
'''
        }
    ]

    for item in history[-8:]:
        role = 'assistant' if item['sender'] == 'ai' else 'user'
        messages.append({'role': role, 'content': item['text']})

    messages.append({'role': 'user', 'content': user_message})

    try:
        response = get_groq_client().chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return {'success': True, 'message': response.choices[0].message.content}
    except Exception as e:
        logger.exception('Groq AI conversation failed')
        return {
            'success': False,
            'message': 'Maaf, layanan AI sedang tidak tersedia. Coba lagi ya! 🙏',
            'error': str(e) if settings.DEBUG else None,
        }


def check_grammar(text):
    fallback = {
        'corrected': text,
        'errors': [],
        'vocabulary_mistakes': [],
        'score': 0,
        'feedback': 'AI belum berhasil memberi hasil dalam format yang benar.',
    }
    try:
        response = get_groq_client().chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    'role': 'system',
                    'content': '''
You are an English grammar checker.
Respond ONLY in valid JSON with this structure:
{
  "corrected": "corrected sentence",
  "errors": [
    {
      "type": "Verb Tense / Subject Verb Agreement / Preposition / Article / Word Order / Vocabulary / Spelling / Other",
      "original": "wrong part",
      "correction": "correct part",
      "explanation": "short explanation in Indonesian"
    }
  ],
  "vocabulary_mistakes": ["wrong vocabulary word 1", "wrong vocabulary word 2"],
  "score": 85,
  "feedback": "overall feedback in Indonesian"
}
If there is no mistake, return errors as [] and score 100.
'''
                },
                {'role': 'user', 'content': f'Check this English text: {text}'},
            ],
            max_tokens=900,
            temperature=0.2,
        )
        content = response.choices[0].message.content
        return {'success': True, 'data': _safe_json_loads(content, fallback)}
    except Exception as e:
        logger.exception('Grammar checker failed')
        return {'success': False, 'message': 'Gagal mengecek grammar. Coba lagi!', 'error': str(e)}


def analyze_conversation(topic, messages):
    conversation_text = '\n'.join([f"{m.sender}: {m.text}" for m in messages])
    fallback = {
        'summary': 'Percakapan selesai.',
        'grammar_score': 0,
        'vocabulary_score': 0,
        'fluency_score': 0,
        'recommendation': 'Lanjutkan latihan percakapan secara rutin.',
    }
    try:
        response = get_groq_client().chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    'role': 'system',
                    'content': '''
You are an English learning evaluator.
Analyze the conversation and respond ONLY in valid JSON:
{
  "summary": "short summary in Indonesian",
  "grammar_score": 80,
  "vocabulary_score": 75,
  "fluency_score": 85,
  "recommendation": "specific learning recommendation in Indonesian"
}
'''
                },
                {'role': 'user', 'content': f'Topic: {topic}\nConversation:\n{conversation_text}'},
            ],
            max_tokens=700,
            temperature=0.2,
        )
        content = response.choices[0].message.content
        return _safe_json_loads(content, fallback)
    except Exception as e:
        logger.exception('Conversation analysis failed')
        return fallback
