LESSONS = {
    1: {
        "title": "Введение в машинное обучение",
        "content": """
🎯 Что такое машинное обучение?

Машинное обучение (ML) - это подраздел искусственного интеллекта, который позволяет компьютерам учиться на основе данных без явного программирования.

🔑 Основные компоненты ML:

1️⃣ Данные - фундамент ML
• Структурированные данные:
  - Таблицы (Excel, CSV)
  - Базы данных (SQL)
  - Временные ряды
• Неструктурированные данные:
  - Текст (статьи, комментарии)
  - Изображения (фото, рисунки)
  - Звук (речь, музыка)
  - Видео
• Важность качества данных:
  - Полнота
  - Точность
  - Актуальность
  - Репрезентативность

2️⃣ Алгоритмы - методы обучения
• Классические алгоритмы:
  - Линейная регрессия
  - Логистическая регрессия
  - Деревья решений
  - Случайный лес
• Современные подходы:
  - Нейронные сети
  - Глубокое обучение
  - Трансформеры
• Выбор алгоритма:
  - Тип задачи
  - Объем данных
  - Вычислительные ресурсы
  - Интерпретируемость

3️⃣ Модели - результат обучения
• Процесс создания модели:
  - Подготовка данных
  - Выбор архитектуры
  - Обучение и валидация
  - Тестирование
• Оценка качества:
  - Метрики эффективности
  - Кросс-валидация
  - A/B тестирование
• Внедрение:
  - Оптимизация
  - Мониторинг
  - Обновление

🔄 Типы машинного обучения:

👨‍🏫 Обучение с учителем (Supervised Learning)
• Принцип работы:
  - Размеченные данные
  - Пары "вход-выход"
  - Обучение на примерах
• Задачи:
  - Классификация
  - Регрессия
  - Прогнозирование
• Примеры:
  - Спам-фильтры
  - Прогноз цен
  - Распознавание объектов

🤖 Обучение без учителя (Unsupervised Learning)
• Особенности:
  - Работа с неразмеченными данными
  - Поиск скрытых паттернов
  - Автоматическое выделение признаков
• Задачи:
  - Кластеризация
  - Уменьшение размерности
  - Поиск аномалий
• Примеры:
  - Сегментация клиентов
  - Рекомендательные системы
  - Обнаружение мошенничества

🎮 Обучение с подкреплением (Reinforcement Learning)
• Компоненты:
  - Агент
  - Среда
  - Действия
  - Награды
• Принцип работы:
  - Исследование среды
  - Получение обратной связи
  - Оптимизация стратегии
• Применения:
  - Игровые AI
  - Робототехника
  - Автономные системы

💡 Практическое применение:

1. Медицина
   • Диагностика:
     - Анализ медицинских изображений
     - Предсказание заболеваний
     - Персонализированное лечение
   • Разработка лекарств:
     - Моделирование молекул
     - Прогнозирование эффективности
     - Оптимизация испытаний

2. Финансы
   • Управление рисками:
     - Оценка кредитоспособности
     - Предсказание дефолтов
     - Портфельный анализ
   • Трейдинг:
     - Алгоритмическая торговля
     - Анализ рынка
     - Прогноз цен активов

3. Технологии
   • Компьютерное зрение:
     - Распознавание лиц
     - Автономное вождение
     - Контроль качества
   • Обработка языка:
     - Перевод текста
     - Чат-боты
     - Анализ тональности
   • Рекомендации:
     - Персонализированный контент
     - Таргетированная реклама
     - Подбор товаров""",
        "check_question": "Какие основные компоненты необходимы для построения системы машинного обучения?",
        "check_options": [
            "A) Данные, алгоритмы и модели",
            "B) Только большой набор данных",
            "C) Только мощный компьютер"
        ],
        "check_correct": "A",
        "materials": [
            "📖 Курс ML на Coursera от Andrew Ng: https://www.coursera.org/learn/machine-learning",
            "📚 Книга «Hands-On Machine Learning with Scikit-Learn & TensorFlow»",
            "🌐 Документация scikit-learn: https://scikit-learn.org/stable/",
            "📺 MIT OpenCourseWare: Introduction to Machine Learning",
            "🎓 Stanford CS229: Machine Learning",
            "📱 Google AI Education"
        ]
    },
    2: {
        "title": "Обучение с учителем",
        "content": """
👨‍🏫 Supervised Learning
        
В обучении с учителем:
1. У нас есть размеченные данные
2. Модель учится на примерах
3. Цель - предсказать результат
        
Примеры задач:
• Классификация
• Регрессия
• Прогнозирование
        
Популярные алгоритмы:
- Linear Regression
- Decision Trees
- Random Forest""",
        "check_question": "Какой алгоритм лучше всего подходит для предсказания числовых значений?",
        "check_options": ["A) K-means", "B) Linear Regression", "C) Random Forest"],
        "check_correct": "B",
        "materials": [
            "📖 Stanford CS229: https://cs229.stanford.edu/",
            "📚 Книга «Hands-On Machine Learning with Scikit-Learn»",
            "🌐 Туториал по Linear Regression: https://scikit-learn.org/stable/modules/linear_model.html"
        ]
    },
    3: {
        "title": "Обучение без учителя",
        "content": """
🤖 Unsupervised Learning
        
Особенности:
1. Данные без меток
2. Поиск скрытых паттернов
3. Группировка похожих объектов
        
Основные задачи:
• Кластеризация
• Уменьшение размерности
• Поиск аномалий
        
Алгоритмы:
- K-means
- DBSCAN
- PCA""",
        "check_question": "Какой алгоритм используется для группировки похожих объектов?",
        "check_options": ["A) Linear Regression", "B) Decision Trees", "C) K-means"],
        "check_correct": "C",
        "materials": [
            "📖 Tutorial по кластеризации: https://scikit-learn.org/stable/modules/clustering.html",
            "📚 Книга «Pattern Recognition and Machine Learning» by Christopher Bishop",
            "🌐 Визуализация K-means: https://www.naftaliharris.com/blog/visualizing-k-means-clustering/"
        ]
    },
    4: {
        "title": "Обучение с подкреплением",
        "content": """
🎮 Reinforcement Learning
        
Ключевые компоненты:
1. Агент - принимает решения
2. Среда - реагирует на действия
3. Награда - оценка действий
        
Примеры применения:
• Игровые AI
• Робототехника
• Оптимизация систем
        
Основные концепции:
- Состояния и действия
- Политика принятия решений
- Q-learning и DQN""",
        "check_question": "Что является ключевым элементом в обучении с подкреплением?",
        "check_options": ["A) Метки классов", "B) Система наград", "C) Кластеризация"],
        "check_correct": "B",
        "materials": [
            "📖 Deep RL Course: https://www.deeplearning.ai/courses/reinforcement-learning-explained/",
            "📚 Книга «Reinforcement Learning: An Introduction» by Sutton & Barto",
            "🌐 OpenAI Gym: https://gymnasium.farama.org/"
        ]
    },
    5: {
        "title": "Нейронные сети",
        "content": """
🧠 Neural Networks
        
Структура нейронной сети:
1. Входной слой
2. Скрытые слои
3. Выходной слой
        
Типы нейронных сетей:
• Feedforward Networks
• Convolutional Networks (CNN)
• Recurrent Networks (RNN)
        
Применения:
- Компьютерное зрение
- Обработка языка
- Генерация контента""",
        "check_question": "Какой тип нейронных сетей лучше всего подходит для обработки изображений?",
        "check_options": ["A) RNN", "B) CNN", "C) Feedforward"],
        "check_correct": "B",
        "materials": [
            "📖 Deep Learning Specialization: https://www.coursera.org/specializations/deep-learning",
            "📚 Книга «Deep Learning» by Ian Goodfellow",
            "🌐 TensorFlow Tutorials: https://www.tensorflow.org/tutorials"
        ]
    },
    6: {
        "title": "Подготовка данных",
        "content": """
📊 Data Preprocessing
        
Этапы подготовки:
1. Сбор данных
2. Очистка данных
3. Трансформация
        
Основные техники:
• Нормализация
• Кодирование категорий
• Обработка пропусков
        
Важные аспекты:
- Качество данных
- Баланс классов
- Размер выборки""",
        "check_question": "Какой процесс преобразует категориальные переменные в числовые?",
        "check_options": ["A) Нормализация", "B) Кодирование", "C) Агрегация"],
        "check_correct": "B",
        "materials": [
            "📖 Data Cleaning Course: https://www.kaggle.com/learn/data-cleaning",
            "📚 Книга «Feature Engineering for Machine Learning»",
            "🌐 Pandas Documentation: https://pandas.pydata.org/docs/"
        ]
    },
    7: {
        "title": "Оценка моделей",
        "content": """
📈 Model Evaluation
        
Метрики оценки:
1. Accuracy (точность)
2. Precision (прецизионность)
3. Recall (полнота)
4. F1-score
        
Методы валидации:
• Cross-validation
• Hold-out
• Time series split
        
Важные концепты:
- Overfitting
- Underfitting
- Bias-Variance trade-off""",
        "check_question": "Какая метрика лучше всего подходит для несбалансированных классов?",
        "check_options": ["A) Accuracy", "B) F1-score", "C) Mean Squared Error"],
        "check_correct": "B",
        "materials": [
            "📖 Model Validation: https://scikit-learn.org/stable/modules/cross_validation.html",
            "📚 Книга «Applied Predictive Modeling»",
            "🌐 ML Metrics Guide: https://neptune.ai/blog/performance-metrics-in-machine-learning-complete-guide"
        ]
    },
    8: {
        "title": "Оптимизация гиперпараметров",
        "content": """
⚙️ Hyperparameter Tuning
        
Методы оптимизации:
1. Grid Search
2. Random Search
3. Bayesian Optimization
        
Важные гиперпараметры:
• Learning rate
• Batch size
• Model architecture
        
Стратегии:
- Cross-validation
- Early stopping
- Learning rate scheduling""",
        "check_question": "Какой метод оптимизации гиперпараметров наиболее эффективен для большого пространства параметров?",
        "check_options": ["A) Grid Search", "B) Random Search", "C) Bayesian Optimization"],
        "check_correct": "C",
        "materials": [
            "📖 Hyperparameter Tuning Guide: https://neptune.ai/blog/hyperparameter-tuning-in-python-complete-guide",
            "📚 Книга «Automated Machine Learning»",
            "🌐 Optuna Documentation: https://optuna.org/"
        ]
    },
    9: {
        "title": "Глубокое обучение",
        "content": """
🔥 Deep Learning
        
Особенности:
1. Многослойные сети
2. Автоматическое извлечение признаков
3. Большие наборы данных
        
Архитектуры:
• Transformers
• GANs
• Autoencoders
        
Применения:
- NLP
- Computer Vision
- Speech Recognition""",
        "check_question": "Какая архитектура произвела революцию в обработке естественного языка?",
        "check_options": ["A) CNN", "B) Transformers", "C) GAN"],
        "check_correct": "B",
        "materials": [
            "📖 Deep Learning Book: https://www.deeplearningbook.org/",
            "📚 Книга «Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow»",
            "🌐 PyTorch Tutorials: https://pytorch.org/tutorials/"
        ]
    },
    10: {
        "title": "MLOps",
        "content": """
⚡️ MLOps
        
Основные компоненты:
1. Версионирование данных
2. Автоматизация пайплайнов
3. Мониторинг моделей
        
Инструменты:
• MLflow
• DVC
• Kubeflow
        
Практики:
- CI/CD для ML
- A/B тестирование
- Feature Store""",
        "check_question": "Что является ключевым аспектом MLOps?",
        "check_options": ["A) Ручное обучение моделей", "B) Автоматизация процессов", "C) Единоразовое развертывание"],
        "check_correct": "B",
        "materials": [
            "📖 MLOps Course: https://madewithml.com/",
            "📚 Книга «Introducing MLOps»",
            "🌐 MLflow Documentation: https://mlflow.org/"
        ]
    },
    11: {
        "title": "Этика в ML",
        "content": """
🤝 Ethics in ML
        
Ключевые аспекты:
1. Справедливость моделей
2. Прозрачность решений
3. Конфиденциальность данных
        
Проблемы:
• Предвзятость
• Интерпретируемость
• Безопасность
        
Решения:
- Аудит моделей
- Explainable AI
- Differential Privacy""",
        "check_question": "Какой аспект этики ML связан с пониманием решений модели?",
        "check_options": ["A) Конфиденциальность", "B) Интерпретируемость", "C) Масштабируемость"],
        "check_correct": "B",
        "materials": [
            "📖 Ethics in AI: https://www.coursera.org/learn/ai-ethics",
            "📚 Книга «Weapons of Math Destruction»",
            "🌐 AI Ethics Guidelines: https://www.microsoft.com/en-us/ai/responsible-ai"
        ]
    }
}

HISTORY = """
📚 История машинного обучения:

1. Зарождение (1940-1950-е):
- 1943: Маккалох и Питтс создают первую математическую модель нейрона
- 1949: Дональд Хебб описывает основной принцип обучения нейронных сетей

2. Первые шаги (1950-1960-е):
- 1957: Фрэнк Розенблатт создает персептрон
- 1959: Артур Самуэль вводит термин "машинное обучение"
- 1965: Алексей Ивахненко разрабатывает метод группового учета аргументов

3. Первая зима ИИ (1970-е):
- Критика персептрона Минским и Папертом
- Сокращение финансирования исследований

4. Возрождение (1980-е):
- 1982: Джон Хопфилд представляет рекуррентные нейронные сети
- 1986: Метод обратного распространения ошибки

5. Современная эра (1990-2010):
- Развитие методов опорных векторов
- Появление глубокого обучения
- Создание сверточных нейронных сетей

6. Эра больших данных (2010-2020):
- Развитие глубокого обучения
- Появление трансформеров
- Создание GANs

7. Настоящее время (2020+):
- Развитие больших языковых моделей
- Мультимодальные модели
- Этичный ИИ

❓ Остались вопросы или нужна помощь?
Обращайтесь к @raddayurieva
"""