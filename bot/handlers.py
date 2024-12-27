import logging
import json
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from content.lessons import LESSONS
from content.quizzes import QUIZZES
from bot.keyboard import get_main_keyboard, get_lesson_keyboard, get_history_keyboard
from utils.db_utils import (
    get_or_create_user, update_progress, get_user_progress,
    update_user_lesson, get_user_statistics, get_all_users_statistics
)
from bot.ai_helper import get_ml_explanation, analyze_ml_question, generate_ml_meme, get_random_ml_history
import time
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

# Add this at the top of the file
_LESSONS_CACHE = {}
_QUIZZES_CACHE = {}

def _init_caches():
    """Initialize caches for lessons and quizzes"""
    global _LESSONS_CACHE, _QUIZZES_CACHE
    _LESSONS_CACHE.clear()
    _QUIZZES_CACHE.clear()
    _LESSONS_CACHE.update(LESSONS)
    _QUIZZES_CACHE.update(QUIZZES)
    logger.info(f"Caches initialized: {len(_LESSONS_CACHE)} lessons, {len(_QUIZZES_CACHE)} quizzes")

# Initialize caches
_init_caches()

@lru_cache(maxsize=100)
def get_cached_lesson(lesson_id: int):
    """Get lesson from cache with improved error handling"""
    try:
        lesson = _LESSONS_CACHE.get(lesson_id)
        if lesson:
            logger.debug(f"Cache hit for lesson {lesson_id}")
            return lesson
        logger.warning(f"Lesson {lesson_id} not found in cache")
        return None
    except Exception as e:
        logger.error(f"Error getting cached lesson {lesson_id}: {str(e)}")
        return None

@lru_cache(maxsize=100)
def get_cached_quiz(quiz_id: int):
    """Get quiz from cache with improved error handling"""
    try:
        quiz = _QUIZZES_CACHE.get(quiz_id)
        if quiz:
            logger.debug(f"Cache hit for quiz {quiz_id}")
            return quiz
        logger.warning(f"Quiz {quiz_id} not found in cache")
        return None
    except Exception as e:
        logger.error(f"Error getting cached quiz {quiz_id}: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оптимизированный обработчик команды start."""
    logger.info(f"Received /start command from user {update.effective_user.id}")
    start_time = time.time()

    try:
        # Асинхронно получаем или создаем пользователя
        user = await asyncio.to_thread(
            get_or_create_user,
            telegram_id=update.effective_user.id,
            username=update.effective_user.username
        )
        logger.debug(f"get_or_create_user result: {user}")
        logger.info(f"User creation/fetch took {time.time() - start_time:.2f} seconds")

        if not user:
            logger.error(f"Failed to create/get user for telegram_id {update.effective_user.id}")
            await update.message.reply_text(
                "Извините, произошла ошибка при создании профиля. Попробуйте позже."
            )
            return

        # Создаем клавиатуру заранее
        keyboard = get_main_keyboard()
        logger.debug("Created main keyboard")

        welcome_message = (
            "👋 Добро пожаловать в бот для изучения машинного обучения!\n\n"
            "🎓 Здесь вы изучите основы ML:\n"
            "- Базовые концепции\n"
            "- Популярные алгоритмы\n"
            "- Практические примеры\n\n"
            "Используйте меню для навигации"
        )

        try:
            logger.info(f"Attempting to send welcome message to user {update.effective_user.id}")
            # Отправляем сообщение с клавиатурой
            result = await update.message.reply_text(
                text=welcome_message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            logger.info(f"Successfully sent welcome message. Message ID: {result.message_id}")
        except Exception as e:
            logger.error(f"Failed to send welcome message: {str(e)}", exc_info=True)
            # Пробуем отправить упрощенное сообщение без клавиатуры
            try:
                await update.message.reply_text(
                    "👋 Добро пожаловать в бот! Если меню не отображается, попробуйте перезапустить бот командой /start",
                    parse_mode='HTML'
                )
            except Exception as simple_e:
                logger.error(f"Failed to send simplified message: {str(simple_e)}", exc_info=True)

    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}", exc_info=True)
        try:
            await update.message.reply_text(
                "Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже.",
                parse_mode='HTML'
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {str(send_error)}", exc_info=True)

    logger.info(f"Total start command processing took {time.time() - start_time:.2f} seconds")

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
    await update.message.reply_text(help_text, parse_mode='HTML')

async def handle_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оптимизированный обработчик уроков."""
    start_time = time.time()
    logger.info(f"Starting handle_lesson for user {update.effective_user.id}")

    try:
        user = await asyncio.to_thread(
            get_or_create_user,
            telegram_id=update.effective_user.id
        )
        if not user:
            logger.error(f"Failed to get/create user for telegram_id {update.effective_user.id}")
            await update.message.reply_text(
                "Произошла ошибка при получении данных пользователя. Попробуйте позже.",
                parse_mode='HTML'
            )
            return

        lesson = get_cached_lesson(user.current_lesson)
        logger.debug(f"Retrieved lesson data for lesson_id {user.current_lesson}: {bool(lesson)}")

        if not lesson:
            if user.current_lesson > len(_LESSONS_CACHE):
                await update.message.reply_text(
                    "🎉 Поздравляем! Вы прошли все уроки!",
                    parse_mode='HTML'
                )
            else:
                logger.error(f"Failed to retrieve lesson {user.current_lesson}")
                await update.message.reply_text(
                    "Произошла ошибка при загрузке урока. Попробуйте позже.",
                    parse_mode='HTML'
                )
            return

        try:
            lesson_message = (
                f"📖 Урок {user.current_lesson}: {lesson['title']}\n\n"
                f"{lesson['content']}\n\n"
                f"❓ Проверочный вопрос:\n"
                f"{lesson['check_question']}\n\n"
            )

            # Добавляем варианты ответов
            for option in lesson['check_options']:
                lesson_message += f"{option}\n"

            lesson_message += "\n📚 Дополнительные материалы:\n"
            for material in lesson['materials']:
                lesson_message += f"{material}\n"

            # Сохраняем информацию о текущем вопросе в контексте
            context.user_data['current_check'] = {
                'lesson_id': user.current_lesson,
                'correct_answer': lesson['check_correct']
            }

            keyboard = get_lesson_keyboard()
            await update.message.reply_text(
                lesson_message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            logger.info(f"Successfully sent lesson {user.current_lesson} to user {update.effective_user.id}")

        except KeyError as ke:
            logger.error(f"Missing key in lesson data: {ke}")
            await update.message.reply_text(
                "Извините, в данных урока обнаружена ошибка. Мы уже работаем над её исправлением.",
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error formatting lesson message: {str(e)}")
            await update.message.reply_text(
                "Произошла ошибка при подготовке урока. Попробуйте позже.",
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Error in handle_lesson: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при загрузке урока. Пожалуйста, попробуйте позже.",
            parse_mode='HTML'
        )

    finally:
        logger.info(f"Lesson handling took {time.time() - start_time:.2f} seconds")

async def handle_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оптимизированный обработчик тестов."""
    start_time = time.time()

    user = await asyncio.to_thread(
        get_or_create_user,
        telegram_id=update.effective_user.id
    )
    if not user:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    quiz = get_cached_quiz(user.current_lesson)
    if not quiz:
        await update.message.reply_text("Нет доступных тестов.")
        return

    # Сохраняем текущий тест в контексте пользователя
    context.user_data['current_quiz'] = {
        'quiz_id': user.current_lesson,
        'correct_answer': quiz['correct_answer'],
        'title': quiz['title']
    }

    logger.info(f"Setting quiz for user {user.id}, lesson {user.current_lesson}")

    await update.message.reply_text(
        f"❓ Тест по теме {quiz['title']}\n\n{quiz['question']}",
        parse_mode='HTML'
    )
    logger.info(f"Quiz handling took {time.time() - start_time:.2f} seconds")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оптимизированный обработчик ответов и кнопок."""
    start_time = time.time()
    logger.info(f"Starting handle_answer for user {update.effective_user.id}")

    try:
        # Обработка кнопок меню
        text = update.message.text
        logger.debug(f"Received button text: '{text}'")  # Добавляем логирование для отладки

        # Нормализуем текст для сравнения
        normalized_text = text.strip() if text else ""

        # Словарь соответствия текста кнопок и действий
        button_actions = {
            "📚 Урок": handle_lesson,
            "📚 К списку уроков": handle_lesson,
            "📚 К урокам": handle_lesson,
            "❓ Тест": handle_quiz,
            "📝 Пройти тест": handle_quiz,
            "📊 Прогресс": handle_progress,
            "📜 История": handle_history,
            "🔄 Другая история": handle_history,
            "🎨 Мем": handle_meme,
            "❓ Помощь": help_command
        }

        # Проверяем, есть ли текст кнопки в словаре действий
        if normalized_text in button_actions:
            logger.info(f"Handling button press: {normalized_text}")
            await button_actions[normalized_text](update, context)
            return

        # Если не кнопка, обрабатываем как ответ на вопрос
        user = await asyncio.to_thread(
            get_or_create_user,
            telegram_id=update.effective_user.id
        )
        if not user:
            logger.error(f"Failed to get/create user for telegram_id {update.effective_user.id}")
            await update.message.reply_text(
                "Произошла ошибка при получении данных пользователя. Попробуйте позже.",
                reply_markup=get_main_keyboard(),
                parse_mode='HTML'
            )
            return

        answer = update.message.text.upper()
        logger.debug(f"Received answer: {answer} from user {update.effective_user.id}")

        # Проверяем, есть ли текущий тест или проверочный вопрос
        current_quiz = context.user_data.get('current_quiz')
        current_check = context.user_data.get('current_check')
        current_history_test = context.user_data.get('current_history_test')

        if current_history_test:
            # Обработка ответа на исторический тест
            if answer == current_history_test.get('correct_answer', ''):
                await update.message.reply_text(
                    f"✅ Правильно!\n\n{current_history_test.get('explanation', '')}",
                    reply_markup=get_history_keyboard(),
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    "❌ Неправильно. Попробуйте еще раз или запросите новую историческую справку.",
                    reply_markup=get_history_keyboard(),
                    parse_mode='HTML'
                )
            context.user_data.pop('current_history_test', None)
            return

        if not current_quiz and not current_check:
            logger.warning(f"No active quiz or check for user {update.effective_user.id}")
            await update.message.reply_text(
                "Используйте команду /lesson чтобы начать урок или /help для списка команд.",
                reply_markup=get_main_keyboard(),
                parse_mode='HTML'
            )
            return

        if current_check:
            logger.info(f"Processing check question answer for lesson {current_check['lesson_id']}")
            # Обработка ответа на проверочный вопрос
            if answer == current_check['correct_answer']:
                await update.message.reply_text(
                    "✅ Правильно! Теперь вы можете пройти тест к этому уроку.\n"
                    "Используйте команду /quiz для начала тестирования.",
                    reply_markup=get_main_keyboard(),
                    parse_mode='HTML'
                )
                logger.info(f"Correct answer for check question, lesson {current_check['lesson_id']}")
                context.user_data.pop('current_check', None)
            else:
                lesson = get_cached_lesson(current_check['lesson_id'])
                if lesson:
                    hint_message = (
                        "❌ Неправильно. Попробуйте еще раз.\n"
                        "Подсказка: внимательно прочитайте материал урока\n\n"
                        f"Вопрос: {lesson['check_question']}\n"
                    )
                    for option in lesson['check_options']:
                        hint_message += f"{option}\n"

                    await update.message.reply_text(
                        hint_message,
                        reply_markup=get_lesson_keyboard(),
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text(
                        "❌ Неправильно. Попробуйте еще раз.",
                        reply_markup=get_lesson_keyboard(),
                        parse_mode='HTML'
                    )
                logger.info(f"Incorrect answer for check question from user {user.id}")
            return

        if current_quiz:
            logger.info(f"Processing quiz answer for quiz {current_quiz['quiz_id']}")
            if answer == current_quiz['correct_answer']:
                # Асинхронно обновляем прогресс
                success = await asyncio.to_thread(
                    update_progress,
                    user.id,
                    current_quiz['quiz_id'],
                    100
                )

                if success:
                    logger.info(f"Progress updated for user {user.id}, lesson {current_quiz['quiz_id']}")
                    next_lesson = current_quiz['quiz_id'] + 1

                    # Обновляем урок пользователя
                    lesson_updated = await asyncio.to_thread(
                        update_user_lesson,
                        user.id,
                        next_lesson
                    )

                    if lesson_updated:
                        context.user_data.pop('current_quiz', None)
                        await update.message.reply_text(
                            "✅ Правильно! Можете переходить к следующему уроку.\n"
                            "Используйте /lesson для просмотра следующего урока.",
                            reply_markup=get_main_keyboard(),
                            parse_mode='HTML'
                        )
                        logger.info(f"User {user.id} moved to next lesson {next_lesson}")
                        return
                    else:
                        logger.error(f"Failed to update user {user.id} to lesson {next_lesson}")
                else:
                    logger.error(f"Failed to update progress for user {user.id}")

                await update.message.reply_text(
                    "Произошла ошибка при сохранении прогресса. Попробуйте позже.",
                    reply_markup=get_main_keyboard(),
                    parse_mode='HTML'
                )
            else:
                quiz = get_cached_quiz(current_quiz['quiz_id'])
                if quiz:
                    await update.message.reply_text(
                        f"❌ Неправильно. Попробуйте еще раз.\n\n"
                        f"Вопрос: {quiz['question']}\n"
                        "Подсказка: правильный ответ должен быть одной буквой (A, B или C)",
                        reply_markup=get_main_keyboard(),
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text(
                        "❌ Неправильно. Попробуйте еще раз.\n"
                        "Подсказка: правильный ответ должен быть одной буквой (A, B или C)",
                        reply_markup=get_main_keyboard(),
                        parse_mode='HTML'
                    )
                logger.info(f"Incorrect quiz answer from user {user.id}")

    except Exception as e:
        logger.error(f"Error in handle_answer: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при обработке ответа. Попробуйте позже.",
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )

    finally:
        logger.info(f"Answer handling took {time.time() - start_time:.2f} seconds")

async def handle_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оптимизированный обработчик прогресса с улучшенным отображением."""
    start_time = time.time()
    logger.info(f"Starting handle_progress for user {update.effective_user.id}")

    try:
        user = await asyncio.to_thread(
            get_or_create_user,
            telegram_id=update.effective_user.id
        )
        if not user:
            logger.error(f"Failed to get/create user for telegram_id {update.effective_user.id}")
            await update.message.reply_text(
                "Произошла ошибка при получении данных пользователя.\nПопробуйте позже.",
                parse_mode='HTML'
            )
            return

        progress = await asyncio.to_thread(get_user_progress, user.id)
        logger.debug(f"Retrieved progress data for user {user.id}: {bool(progress)}")

        # Получаем общее количество уроков из кэша
        total_lessons = len(_LESSONS_CACHE)
        completed_lessons = len([p for p in progress if p.completed]) if progress else 0
        completion_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0

        # Создаем визуальный индикатор прогресса
        progress_bar = "▓" * int(completion_percentage / 10) + "░" * (10 - int(completion_percentage / 10))

        if progress:
            avg_score = sum(p.quiz_score for p in progress) / len(progress)
            progress_text = (
                f"📊 Ваш прогресс:\n\n"
                f"Прогресс курса: [{progress_bar}] {completion_percentage:.1f}%\n\n"
                f"📚 Текущий урок: {user.current_lesson}/{total_lessons}\n"
                f"✅ Завершено уроков: {completed_lessons}\n"
                f"📝 Средний балл: {avg_score:.1f}/100\n\n"
                f"🎯 Осталось уроков: {total_lessons - completed_lessons}\n\n"
                f"Продолжайте обучение! Используйте /lesson для перехода к следующему уроку."
            )
        else:
            progress_text = (
                f"📊 Ваш прогресс:\n\n"
                f"Прогресс курса: [░░░░░░░░░░] 0%\n\n"
                f"📚 Текущий урок: 1/{total_lessons}\n"
                f"✅ Завершено уроков: 0\n"
                f"📝 Средний балл: 0.0/100\n\n"
                f"🎯 Осталось уроков: {total_lessons}\n\n"
                f"Начните обучение! Используйте /lesson для перехода к первому уроку."
            )

        await update.message.reply_text(
            progress_text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Successfully sent progress to user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Error in handle_progress: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при получении прогресса.\nПопробуйте позже.",
            parse_mode='HTML'
        )

    finally:
        logger.info(f"Progress handling took {time.time() - start_time:.2f} seconds")

async def handle_explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оптимизированный обработчик объяснений."""
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите тему после команды /explain",
            parse_mode='HTML'
        )
        return

    topic = " ".join(context.args)
    explanation = get_ml_explanation(topic)
    await update.message.reply_text(explanation, parse_mode='HTML')

    if "❓" in explanation:
        context.user_data['last_explanation'] = topic
        context.user_data['last_question'] = explanation.split("❓")[-1].strip()

async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /history command to show random ML history facts."""
    logger.info(f"Starting handle_history for user {update.effective_user.id}")
    try:
        await update.message.reply_text(
            "🕒 Генерирую историческую справку...",
            parse_mode='HTML'
        )

        history_data = get_random_ml_history()
        logger.debug(f"Got history data: {bool(history_data)}")

        try:
            data = history_data if isinstance(history_data, dict) else json.loads(history_data)

            if not all(key in data for key in ['history', 'question', 'correct_answer', 'explanation']):
                raise ValueError("Missing required fields in history data")

            context.user_data['current_history_test'] = {
                'correct_answer': data['correct_answer'],
                'explanation': data['explanation']
            }

            keyboard = get_history_keyboard()

            message = (
                f"📚 {data['history']}\n\n"
                f"❓ Тест на понимание:\n{data['question']}\n\n"
                "Выберите ответ (A, B или C):"
            )

            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            logger.info(f"Successfully sent history to user {update.effective_user.id}")

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Error processing history data: {str(e)}")
            await update.message.reply_text(
                "😔 Извините, произошла ошибка при обработке исторической справки.\n"
                "Попробуйте еще раз, используя команду /history",
                reply_markup=get_main_keyboard(),
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Error in handle_history: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте позже.",
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )

async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите ваш вопрос после команды /ask",
            parse_mode='HTML'
        )
        return

    question = " ".join(context.args)
    answer = analyze_ml_question(question)
    await update.message.reply_text(answer, parse_mode='HTML')


async def handle_meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /meme command to generate ML-related memes."""
    concept = " ".join(context.args) if context.args else None

    # Validate concept if provided
    if concept:
        if len(concept) > 100:
            await update.message.reply_text(
                "😅 Тема слишком длинная. Пожалуйста, сократите её до 100 символов.\n\n"
                "❓ Если нужна помощь, обращайтесь к @raddayurieva",
                parse_mode='HTML'
            )
            return

        # Check for potentially problematic characters
        if any(char in concept for char in ['@', '#', '$', '%', '&', '*', '<', '>', '/']):
            await update.message.reply_text(
                "😅 Пожалуйста, используйте только буквы, цифры и простые знаки препинания в теме.\n\n"
                "❓ Если нужна помощь, обращайтесь к @raddayurieva",
                parse_mode='HTML'
            )
            return

    await update.message.reply_text(
        "🎨 Генерирую мем" + (f" про {concept}" if concept else "") + "...\n"
        "Это может занять несколько секунд.",
        parse_mode='HTML'
    )

    try:
        meme_url = generate_ml_meme(concept)
        if meme_url:
            await update.message.reply_photo(
                photo=meme_url,
                caption="🤖 Ваш мем о машинном обучении!" + 
                       (f"\nТема: {concept}" if concept else "") +
                       "\n\n💡 Используйте команду /meme [тема] для генерации мема на конкретную тему" +
                       "\n❓ Есть вопросы? Обращайтесь к @raddayurieva",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "😔 Извините, не удалось сгенерировать мем. " +
                ("Возможно, стоит попробовать другую тему или " if concept else "") +
                "повторить попытку позже.\n\n"
                "❓ Есть вопросы или нужна помощь?\n"
                "Обращайтесь к @raddayurieva",
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error in handle_meme: {str(e)}")
        await update.message.reply_text(
            "😔 Произошла ошибка при генерации мема. "
            "Пожалуйста, попробуйте позже.\n\n"
            "❓ Если проблема повторяется, обращайтесь к @raddayurieva",
            parse_mode='HTML'
        )


async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику для админа."""
    # Проверяем, является ли пользователь админом
    ADMIN_ID = int(os.environ.get("ADMIN_TELEGRAM_ID", "0"))
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ У вас нет доступа к этой команде.",
            parse_mode='HTML'
        )
        return

    all_stats = await asyncio.to_thread(get_all_users_statistics)

    if not all_stats:
        await update.message.reply_text(
            "📊 Статистика пока недоступна.",
            parse_mode='HTML'
        )
        return

    # Формируем сообщение со статистикой
    stats_message = "📊 Статистика пользователей:\n\n"

    for user_stat in all_stats:
        stats_message += (
            f"👤 Пользователь: {user_stat['username']}\n"
            f"📚 Текущий урок: {user_stat['current_lesson']}\n"
            f"✅ Завершено уроков: {user_stat['completed_lessons']}\n"
            f"📝 Средний балл: {user_stat['average_score']:.1f}\n"
            f"🔄 Всего попыток: {user_stat['total_attempts']}\n"
            f"⏰ Последняя активность: {user_stat['last_activity'].strftime('%Y-%m-%d %H:%M')}\n"
            "-------------------\n"
        )

    # Разбиваем на части, если сообщение слишком длинное
    MAX_MESSAGE_LENGTH = 4096
    for i in range(0, len(stats_message), MAX_MESSAGE_LENGTH):
        await update.message.reply_text(
            stats_message[i:i + MAX_MESSAGE_LENGTH],
            parse_mode='HTML'
        )

async def handle_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику для конкретного пользователя."""
    # Проверяем, является ли пользователь админом
    ADMIN_ID = int(os.environ.get("ADMIN_TELEGRAM_ID", "0"))

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ У вас нет доступа к этой команде.",
            parse_mode='HTML'
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Укажите ID пользователя после команды.\n"
            "Пример: /user_stats 123456789",
            parse_mode='HTML'
        )
        return

    try:
        user_id = int(context.args[0])
        stats = await asyncio.to_thread(get_user_statistics, user_id)

        if not stats:
            await update.message.reply_text(
                "❌ Пользователь не найден или статистика недоступна.",
                parse_mode='HTML'
            )
            return

        stats_message = (
            f"📊 Подробная статистика пользователя {user_id}:\n\n"
            f"⏰ Общее время: {stats['total_time_spent']} минут\n"
            f"📝 Средний балл: {stats['average_score']:.1f}\n"
            f"✅ Завершено уроков: {stats['completed_lessons']}\n"
            f"🔄 Всего попыток: {stats['total_attempts']}\n"
            f"👍 Успешных попыток: {stats['successful_attempts']}\n"
            f"📈 Процент успеха: {stats['success_rate']:.1f}%\n"
            f"🕒 Последняя активность: {stats['last_activity'].strftime('%Y-%m-%d %H:%M')}"
        )

        await update.message.reply_text(stats_message, parse_mode='HTML')

    except ValueError:
        await update.message.message.reply_text(
            "❌ Некорректный ID пользователя.\n"
            "Используйте только цифры.",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in handle_user_stats: {str(e)}")
        await update.message.reply_text(
            "❌ Произошла ошибка при получении статистики.",
            parse_mode='HTML'
        )