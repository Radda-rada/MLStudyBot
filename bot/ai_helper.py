import os
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_ml_explanation(topic: str) -> str:
    """Get an explanation of a machine learning concept using GPT."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better ML explanations
            messages=[
                {
                    "role": "system",
                    "content": "Вы - опытный преподаватель машинного обучения. "
                    "Объясняйте концепции просто и понятно, с примерами из реальной жизни. "
                    "Используйте эмодзи для лучшего восприятия. "
                    "Ответ должен быть на русском языке."
                },
                {
                    "role": "user",
                    "content": f"Объясните концепцию: {topic}"
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting ML explanation: {e}")
        return "Извините, произошла ошибка при получении объяснения. Попробуйте позже."

def analyze_ml_question(question: str) -> str:
    """Analyze and answer a question about machine learning."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Вы - эксперт по машинному обучению. "
                    "Отвечайте на вопросы детально, но доступно. "
                    "Если вопрос не связан с ML, вежливо укажите на это. "
                    "Используйте эмодзи для лучшего восприятия. "
                    "Ответ должен быть на русском языке."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error analyzing ML question: {e}")
        return "Извините, произошла ошибка при анализе вопроса. Попробуйте позже."
