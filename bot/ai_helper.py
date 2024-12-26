import os
from openai import OpenAI
import logging
from functools import lru_cache
import time
from typing import Optional

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Уменьшаем размеры ответов и добавляем таймауты
TIMEOUT = 10  # seconds
MAX_TOKENS = {
    'explanation': 300,  # было 500
    'question': 200,    # было 300
    'history': 300      # было 400
}

@lru_cache(maxsize=50)
def get_ml_explanation(topic: str) -> str:
    """Get an explanation of a machine learning concept using GPT."""
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Кратко объясните ML концепцию. Максимум 2-3 предложения."
                },
                {
                    "role": "user",
                    "content": f"Объясните: {topic}"
                }
            ],
            max_tokens=MAX_TOKENS['explanation'],
            temperature=0.5,  # Уменьшаем для более четких ответов
            timeout=TIMEOUT
        )
        logger.info(f"OpenAI explanation request took {time.time() - start_time:.2f} seconds")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting ML explanation: {e}")
        return "Извините, произошла ошибка. Попробуйте позже."

@lru_cache(maxsize=50)
def analyze_ml_question(question: str) -> str:
    """Analyze and answer a question about machine learning."""
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Отвечайте кратко, максимум 2 предложения."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=MAX_TOKENS['question'],
            temperature=0.5,
            timeout=TIMEOUT
        )
        logger.info(f"OpenAI question analysis request took {time.time() - start_time:.2f} seconds")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error analyzing ML question: {e}")
        return "Извините, произошла ошибка. Попробуйте позже."

def generate_ml_meme(concept: Optional[str] = None) -> Optional[str]:
    """Generate a meme about machine learning using DALL-E."""
    start_time = time.time()
    try:
        prompt = (
            "Create a simple, minimalist meme about machine learning"
            if not concept else
            f"Create a simple, minimalist meme about {concept} in machine learning"
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            timeout=TIMEOUT
        )
        logger.info(f"OpenAI meme generation request took {time.time() - start_time:.2f} seconds")
        return response.data[0].url if response.data else None
    except Exception as e:
        logger.error(f"Error generating ML meme: {str(e)}")
        return None

@lru_cache(maxsize=20)
def get_random_ml_history() -> dict:
    """Get a random historical fact about machine learning with a test question."""
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Создайте краткую историческую справку о ML с тестом."
                },
                {
                    "role": "user",
                    "content": "Сгенерируйте короткую историческую справку и тестовый вопрос"
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=MAX_TOKENS['history'],
            temperature=0.5,
            timeout=TIMEOUT
        )
        logger.info(f"OpenAI history request took {time.time() - start_time:.2f} seconds")
        content = response.choices[0].message.content
        return content if isinstance(content, dict) else {
            "history": "Извините, произошла ошибка.",
            "question": None,
            "correct_answer": None,
            "explanation": None
        }
    except Exception as e:
        logger.error(f"Error getting ML history: {str(e)}")
        return {
            "history": "Извините, произошла ошибка.",
            "question": None,
            "correct_answer": None,
            "explanation": None
        }