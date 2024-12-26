import os
from openai import OpenAI
import logging
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
                    "content": "Вы - опытный преподаватель ML. Объясняйте кратко и по делу. Ответ на русском."
                },
                {
                    "role": "user",
                    "content": f"Объясните концепцию: {topic}"
                }
            ],
            max_tokens=500,  # Уменьшаем размер ответа для скорости
            temperature=0.7
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
                    "content": "Вы - эксперт ML. Отвечайте кратко и по делу. Ответ на русском."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=300,  # Уменьшаем размер ответа для скорости
            temperature=0.7
        )
        logger.info(f"OpenAI question analysis request took {time.time() - start_time:.2f} seconds")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error analyzing ML question: {e}")
        return "Извините, произошла ошибка. Попробуйте позже."

def generate_ml_meme(concept: str = None) -> str:
    """Generate a meme about machine learning using DALL-E."""
    start_time = time.time()
    try:
        prompt = (
            "Create a simple educational meme about machine learning"
            if not concept else
            f"Create a simple educational meme about {concept} in machine learning"
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"  # Используем standard вместо hd для скорости
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
                    "content": "Создайте короткую историческую справку о ML с тестом."
                },
                {
                    "role": "user",
                    "content": "Сгенерируйте историческую справку и тестовый вопрос"
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=400,  # Уменьшаем размер ответа для скорости
            temperature=0.7
        )
        logger.info(f"OpenAI history request took {time.time() - start_time:.2f} seconds")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting ML history: {str(e)}")
        return {
            "history": "Извините, произошла ошибка.",
            "question": None,
            "correct_answer": None,
            "explanation": None
        }