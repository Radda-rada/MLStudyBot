from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    """
    Создает основную клавиатуру бота с улучшенной обработкой ошибок
    """
    keyboard = [
        ['📚 Урок', '❓ Тест'],
        ['📊 Прогресс', '📜 История'],
        ['🎨 Мем', '❓ Помощь']
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )

def get_lesson_keyboard():
    """
    Создает клавиатуру для урока с улучшенной обработкой ошибок
    """
    keyboard = [
        ['📝 Пройти тест'],
        ['📚 К списку уроков'],
        ['📜 История', '❓ Помощь']
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )

def get_history_keyboard():
    """
    Создает клавиатуру для исторической справки
    """
    keyboard = [
        ['📚 К урокам'],
        ['🔄 Другая история']
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )