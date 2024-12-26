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
                    "Ответ должен быть на русском языке. "
                    "После объяснения добавьте один вопрос для проверки понимания материала."
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

def generate_ml_meme(concept: str = None) -> str:
    """Generate a meme about machine learning using DALL-E."""
    try:
        prompt = (
            "Create a funny educational meme about machine learning" if not concept
            else f"Create a funny educational meme about {concept} in machine learning"
        )
        prompt += ", with text overlays in English, in the style of modern internet memes, use simple but humorous tech explanations, keep it educational and witty"

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            style="vivid"
        )

        if not response.data:
            logger.error("DALL-E response contains no data")
            return None

        return response.data[0].url
    except Exception as e:
        logger.error(f"Error generating ML meme: {str(e)}")
        return None

def get_random_ml_history() -> dict:
    """Get a random historical fact about machine learning with a test question."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better historical context
            messages=[
                {
                    "role": "system",
                    "content": "Создайте случайную историческую справку о машинном обучении. "
                    "Включите конкретный год, значимое событие и его влияние на развитие ML. "
                    "После справки добавьте тестовый вопрос с вариантами ответа (A, B, C) и объяснение правильного ответа. "
                    "Верните ответ в формате JSON со следующими полями: "
                    "history (текст справки), question (текст вопроса), "
                    "correct_answer (A, B или C), explanation (объяснение правильного ответа). "
                    "Ответ должен быть на русском языке."
                },
                {
                    "role": "user",
                    "content": "Сгенерируйте историческую справку и тестовый вопрос"
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting ML history: {str(e)}")
        return {
            "history": "Извините, произошла ошибка при получении исторической справки.",
            "question": None,
            "correct_answer": None,
            "explanation": None
        }