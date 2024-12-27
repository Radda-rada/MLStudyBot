# Образовательный Telegram Бот для Изучения ML 🤖

Телеграм бот для интерактивного изучения основ машинного обучения. Бот предоставляет структурированные уроки, тесты, исторические справки и возможность задавать вопросы по ML с использованием GPT-4.

## Основные функции 🎯

- 📚 Интерактивные уроки по основам ML
- ❓ Тесты для проверки знаний
- 📊 Отслеживание прогресса обучения
- 📜 Исторические справки о развитии ML
- 🤖 Ответы на вопросы с помощью GPT-4
- 🎨 Генерация тематических мемов
- 📈 Статистика обучения

## Технический стек 🛠

- Python 3.11
- python-telegram-bot 20.6
- SQLAlchemy + PostgreSQL
- OpenAI GPT-4 и DALL-E 3
- Flask + Flask-SQLAlchemy
- asyncio для асинхронной обработки

## Установка и запуск 🚀

1. Клонируйте репозиторий:
```bash
git clone [repository-url]
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` со следующими переменными:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_postgresql_database_url
ADMIN_TELEGRAM_ID=your_admin_telegram_id
```

4. Запустите бота:
```bash
python main.py
```

## Структура проекта 📁

```
├── app.py              # Конфигурация приложения и базы данных
├── main.py            # Точка входа и инициализация бота
├── models.py          # Модели базы данных
├── bot/
│   ├── handlers.py    # Обработчики команд бота
│   ├── keyboard.py    # Клавиатуры и кнопки
│   └── ai_helper.py   # Интеграция с OpenAI
├── content/
│   ├── lessons.py     # Контент уроков
│   └── quizzes.py     # Тестовые задания
└── utils/
    └── db_utils.py    # Утилиты для работы с БД
```

## Команды бота 🎮

- `/start` - Начать обучение
- `/lesson` - Перейти к урокам
- `/quiz` - Пройти тест
- `/progress` - Просмотр прогресса
- `/history` - Историческая справка
- `/ask <вопрос>` - Задать вопрос по ML
- `/explain <тема>` - Получить объяснение темы
- `/meme [тема]` - Получить мем про ML
- `/help` - Справка по командам

## База данных 💾

### Таблицы

1. **users**
   - Информация о пользователях
   - Текущий прогресс
   - Дата регистрации

2. **progress**
   - Прогресс по урокам
   - Результаты тестов
   - Статистика попыток

3. **user_statistics**
   - Общая статистика обучения
   - Время изучения
   - Средние показатели

4. **lesson_attempts**
   - История попыток прохождения уроков
   - Результаты
   - Временные метки

5. **lessons**
   - Контент уроков
   - Проверочные вопросы
   - Дополнительные материалы

6. **quizzes**
   - Тестовые задания
   - Правильные ответы
   - Объяснения

## Особенности реализации ⚙️

- Асинхронная обработка сообщений
- Кэширование запросов к API
- Оптимизированные запросы к БД
- Логирование всех действий
- Обработка ошибок с fallback
- Масштабируемая архитектура

## Администрирование 👨‍💻

Для администраторов доступна команда `/stats`, которая показывает:
- Общую статистику использования
- Активность пользователей
- Прогресс обучения
- Эффективность тестирования

## Лицензия 📄

MIT License - свободное использование и модификация

## Контакты 📧

По всем вопросам обращайтесь:
@raddayurieva