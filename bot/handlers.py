import logging
from telegram import Update
from telegram.ext import ContextTypes
from models import User
from app import db, app
from content.lessons import LESSONS
from content.quizzes import QUIZZES
from bot.keyboard import get_main_keyboard, get_lesson_keyboard
from utils.db_utils import get_or_create_user, update_progress, get_user_progress
from bot.ai_helper import get_ml_explanation, analyze_ml_question

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
        "/ask <вопрос> - задать вопрос по ML\n"
        "/explain <тема> - получить объяснение темы"
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
        "/ask <вопрос> - задать вопрос по ML\n"
        "/explain <тема> - получить объяснение темы\n"
        "/help - показать это сообщение"
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
        await update.message.reply_text("Поздравляем! Вы прошли все уроки! 🎉")

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
        await update.message.reply_text("Нет доступных тестов.")

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

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(telegram_id=update.effective_user.id)
    if not user:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    quiz = context.user_data.get('current_quiz')

    if quiz and update.message.text.lower() == quiz['correct_answer'].lower():
        if update_progress(user.id, user.current_lesson, 100):
            with app.app_context():
                user = User.query.get(user.id)  # Refresh user from database
                user.current_lesson += 1
                db.session.commit()

            await update.message.reply_text(
                "✅ Правильно! Можете переходить к следующему уроку.",
                reply_markup=get_main_keyboard()
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

async def handle_explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите тему после команды /explain"
        )
        return

    topic = " ".join(context.args)
    explanation = get_ml_explanation(topic)
    await update.message.reply_text(explanation)