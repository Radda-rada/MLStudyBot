import logging
import json
from telegram import Update
from telegram.ext import ContextTypes
from models import User
from content.lessons import LESSONS, HISTORY
from content.quizzes import QUIZZES
from bot.keyboard import get_main_keyboard, get_lesson_keyboard
from utils.db_utils import (
    get_or_create_user, update_progress, get_user_progress,
    update_user_lesson
)
from bot.ai_helper import get_ml_explanation, analyze_ml_question, generate_ml_meme, get_random_ml_history

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(
        telegram_id=update.effective_user.id,
        username=update.effective_user.username
    )

    if not user:
        await update.message.reply_text(
            "Извините, произошла ошибка при создании профиля. Попробуйте позже."
        )
        return

    welcome_message = (
        "👋 Добро пожаловать в бот для изучения машинного обучения!\n\n"
        "🎓 Здесь вы изучите основы ML:\n"
        "- Базовые концепции\n"
        "- Популярные алгоритмы\n"
        "- Практические примеры\n\n"
        "Используйте команды:\n"
        "/lesson - начать урок\n"
        "/quiz - пройти тест\n"
        "/progress - посмотреть прогресс\n"
        "/history - историческая справка\n"
        "/ask <вопрос> - задать вопрос по ML\n"
        "/explain <тема> - получить объяснение темы\n"
        "/meme [тема] - получить мем про ML\n\n"
        "❓ Есть вопросы или нужна помощь?\n"
        "Обращайтесь к @raddayurieva"
    )

    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 Доступные команды:\n\n"
        "/start - начать обучение\n"
        "/lesson - перейти к урокам\n"
        "/quiz - пройти тест\n"
        "/progress - ваш прогресс\n"
        "/history - историческая справка\n"
        "/ask <вопрос> - задать вопрос по ML\n"
        "/explain <тема> - получить объяснение темы\n"
        "/meme [тема] - получить мем про ML\n"
        "/help - показать это сообщение\n\n"
        "❓ Есть вопросы или нужна помощь?\n"
        "Обращайтесь к @raddayurieva"
    )
    await update.message.reply_text(help_text)

async def handle_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(telegram_id=update.effective_user.id)
    if not user:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    lesson = LESSONS.get(user.current_lesson)

    if lesson:
        await update.message.reply_text(
            f"📖 Урок {user.current_lesson}: {lesson['title']}\n\n{lesson['content']}",
            reply_markup=get_lesson_keyboard()
        )
    else:
        await update.message.reply_text(
            "Поздравляем! Вы прошли все уроки! 🎉\n\n"
            "❓ Есть вопросы или нужна помощь?\n"
            "Обращайтесь к @raddayurieva"
        )

async def handle_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(telegram_id=update.effective_user.id)
    if not user:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    quiz = QUIZZES.get(user.current_lesson)

    if quiz:
        context.user_data['current_quiz'] = quiz
        await update.message.reply_text(
            f"❓ Тест по теме {quiz['title']}\n\n{quiz['question']}"
        )
    else:
        await update.message.reply_text(
            "Нет доступных тестов.\n\n"
            "❓ Есть вопросы или нужна помощь?\n"
            "Обращайтесь к @raddayurieva"
        )

async def handle_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(telegram_id=update.effective_user.id)
    if not user:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    progress = get_user_progress(user.id)

    if progress:
        progress_text = (
            f"📊 Ваш прогресс:\n"
            f"Текущий урок: {user.current_lesson}\n"
            f"Пройдено уроков: {len(progress)}\n"
            f"Средний балл: {sum([p.quiz_score for p in progress])/len(progress):.1f}"
        )
    else:
        progress_text = (
            f"📊 Ваш прогресс:\n"
            f"Текущий урок: {user.current_lesson}\n"
            f"Пройдено уроков: 0\n"
            f"Средний балл: 0.0"
        )

    await update.message.reply_text(progress_text)

async def handle_explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите тему после команды /explain"
        )
        return

    topic = " ".join(context.args)
    explanation = get_ml_explanation(topic)
    await update.message.reply_text(explanation)

    # Add the test question to context for later verification
    if "❓" in explanation:
        question_part = explanation.split("❓")[-1].strip()
        context.user_data['last_explanation'] = topic
        context.user_data['last_question'] = question_part

async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /history command to show random ML history facts."""
    history_data = get_random_ml_history()

    try:
        data = json.loads(history_data)
        context.user_data['current_history_test'] = data

        await update.message.reply_text(
            f"📚 {data['history']}\n\n"
            f"❓ Тест на понимание:\n{data['question']}\n\n"
            "Выберите ответ (A, B или C):"
        )
    except Exception as e:
        logger.error(f"Error parsing history data: {str(e)}")
        await update.message.reply_text(
            "😔 Извините, произошла ошибка при получении исторической справки.\n"
            "Попробуйте позже.\n\n"
            "❓ Если проблема повторяется, обращайтесь к @raddayurieva"
        )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(telegram_id=update.effective_user.id)
    if not user:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    answer = update.message.text.upper()

    # Handle history test answers
    if 'current_history_test' in context.user_data:
        test_data = context.user_data['current_history_test']
        if answer == test_data['correct_answer']:
            await update.message.reply_text(
                "✅ Правильно! Вы хорошо усвоили материал."
            )
        else:
            await update.message.reply_text(
                f"❌ Неправильно. Вот объяснение:\n\n{test_data['explanation']}\n\n"
                "Попробуйте ещё раз с новой исторической справкой: /history"
            )
        context.user_data.pop('current_history_test')
        return

    # Handle quiz answers
    quiz = context.user_data.get('current_quiz')
    if quiz and answer == quiz['correct_answer']:
        if update_progress(user.id, user.current_lesson, 100):
            if update_user_lesson(user.id, user.current_lesson + 1):
                await update.message.reply_text(
                    "✅ Правильно! Можете переходить к следующему уроку.",
                    reply_markup=get_main_keyboard()
                )
            else:
                await update.message.reply_text(
                    "Произошла ошибка при обновлении урока. Попробуйте позже."
                )
        else:
            await update.message.reply_text(
                "Произошла ошибка при сохранении прогресса. Попробуйте позже."
            )
    elif quiz:
        await update.message.reply_text(
            "❌ Неправильно. Попробуйте еще раз."
        )

async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите ваш вопрос после команды /ask"
        )
        return

    question = " ".join(context.args)
    answer = analyze_ml_question(question)
    await update.message.reply_text(answer)


async def handle_meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /meme command to generate ML-related memes."""
    concept = " ".join(context.args) if context.args else None

    # Validate concept if provided
    if concept:
        if len(concept) > 100:
            await update.message.reply_text(
                "😅 Тема слишком длинная. Пожалуйста, сократите её до 100 символов.\n\n"
                "❓ Если нужна помощь, обращайтесь к @raddayurieva"
            )
            return

        # Check for potentially problematic characters
        if any(char in concept for char in ['@', '#', '$', '%', '&', '*', '<', '>', '/']):
            await update.message.reply_text(
                "😅 Пожалуйста, используйте только буквы, цифры и простые знаки препинания в теме.\n\n"
                "❓ Если нужна помощь, обращайтесь к @raddayurieva"
            )
            return

    await update.message.reply_text(
        "🎨 Генерирую мем" + (f" про {concept}" if concept else "") + "...\n"
        "Это может занять несколько секунд."
    )

    try:
        meme_url = generate_ml_meme(concept)
        if meme_url:
            await update.message.reply_photo(
                photo=meme_url,
                caption="🤖 Ваш мем о машинном обучении!" + 
                       (f"\nТема: {concept}" if concept else "") +
                       "\n\n💡 Используйте команду /meme [тема] для генерации мема на конкретную тему" +
                       "\n❓ Есть вопросы? Обращайтесь к @raddayurieva"
            )
        else:
            await update.message.reply_text(
                "😔 Извините, не удалось сгенерировать мем. " +
                ("Возможно, стоит попробовать другую тему или " if concept else "") +
                "повторить попытку позже.\n\n"
                "❓ Есть вопросы или нужна помощь?\n"
                "Обращайтесь к @raddayurieva"
            )
    except Exception as e:
        logger.error(f"Error in handle_meme: {str(e)}")
        await update.message.reply_text(
            "😔 Произошла ошибка при генерации мема. "
            "Пожалуйста, попробуйте позже.\n\n"
            "❓ Если проблема повторяется, обращайтесь к @raddayurieva"
        )