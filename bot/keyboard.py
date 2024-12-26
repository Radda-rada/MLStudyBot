from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    keyboard = [
        ['📚 Урок', '❓ Тест'],
        ['📊 Прогресс', '📜 История'],
        ['🎨 Мем', '❓ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_lesson_keyboard():
    keyboard = [
        ['📝 Пройти тест'],
        ['📚 К списку уроков']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)