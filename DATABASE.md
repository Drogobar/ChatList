# Схема базы данных ChatList

## Общая информация

База данных использует SQLite и состоит из четырёх основных таблиц:
- `prompts` - хранение промтов (запросов)
- `models` - хранение информации о нейросетях
- `results` - хранение сохранённых результатов
- `settings` - хранение настроек программы

## Таблица: prompts

Хранит промты (запросы), которые пользователь отправляет в нейросети.

### Структура таблицы

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор промта |
| date | TEXT | NOT NULL | Дата и время создания промта (формат ISO: YYYY-MM-DD HH:MM:SS) |
| prompt | TEXT | NOT NULL | Текст промта |
| tags | TEXT | NULL | Теги для категоризации промтов (разделитель: запятая или JSON) |

### Индексы
- `idx_prompts_date` на поле `date` для быстрой сортировки по дате
- `idx_prompts_tags` на поле `tags` для поиска по тегам

### Пример данных
```
id: 1
date: "2024-01-15 10:30:00"
prompt: "Объясни квантовую физику простыми словами"
tags: "наука,физика,обучение"
```

## Таблица: models

Хранит информацию о нейросетях (моделях), к которым можно отправлять запросы.

### Структура таблицы

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор модели |
| name | TEXT | NOT NULL UNIQUE | Название модели (например, "GPT-4", "DeepSeek Chat") |
| api_url | TEXT | NOT NULL | URL API для отправки запросов |
| api_id | TEXT | NOT NULL | Идентификатор переменной окружения с API-ключом (например, "OPENAI_API_KEY") |
| model_type | TEXT | NOT NULL | Тип модели/API (например, "openai", "deepseek", "groq") |
| is_active | INTEGER | NOT NULL DEFAULT 1 | Флаг активности модели (1 - активна, 0 - неактивна) |
| created_at | TEXT | NOT NULL | Дата и время добавления модели |

### Индексы
- `idx_models_is_active` на поле `is_active` для быстрого получения активных моделей
- `idx_models_name` на поле `name` для поиска по названию

### Пример данных
```
id: 1
name: "GPT-4"
api_url: "https://api.openai.com/v1/chat/completions"
api_id: "OPENAI_API_KEY"
model_type: "openai"
is_active: 1
created_at: "2024-01-10 09:00:00"
```

**Важно**: API-ключи хранятся в файле `.env` в переменных окружения, а не в базе данных. В таблице хранится только имя переменной окружения (`api_id`).

## Таблица: results

Хранит сохранённые результаты ответов нейросетей на промты.

### Структура таблицы

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор результата |
| prompt_id | INTEGER | NOT NULL | Ссылка на промт из таблицы prompts |
| model_id | INTEGER | NOT NULL | Ссылка на модель из таблицы models |
| response | TEXT | NOT NULL | Текст ответа от нейросети |
| saved_at | TEXT | NOT NULL | Дата и время сохранения результата |
| metadata | TEXT | NULL | Дополнительные метаданные (JSON) - токены, время ответа и т.д. |

### Индексы
- `idx_results_prompt_id` на поле `prompt_id` для быстрого поиска результатов по промту
- `idx_results_model_id` на поле `model_id` для быстрого поиска результатов по модели
- `idx_results_saved_at` на поле `saved_at` для сортировки по дате сохранения

### Внешние ключи
- `prompt_id` → `prompts(id)` (ON DELETE CASCADE)
- `model_id` → `models(id)` (ON DELETE RESTRICT)

### Пример данных
```
id: 1
prompt_id: 1
model_id: 1
response: "Квантовая физика изучает поведение частиц на атомном уровне..."
saved_at: "2024-01-15 10:35:00"
metadata: '{"tokens": 150, "response_time": 2.3}'
```

## Таблица: settings

Хранит настройки программы.

### Структура таблицы

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| key | TEXT | PRIMARY KEY | Ключ настройки |
| value | TEXT | NOT NULL | Значение настройки (может быть JSON) |
| updated_at | TEXT | NOT NULL | Дата и время последнего обновления |

### Пример данных
```
key: "default_timeout"
value: "30"

key: "export_format"
value: "markdown"

key: "theme"
value: "light"
```

## Диаграмма связей

```
prompts (1) ──< (N) results
models  (1) ──< (N) results
settings (независимая таблица)
```

## SQL для создания таблиц

```sql
-- Таблица промтов
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    prompt TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date);
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags);

-- Таблица моделей
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT NOT NULL,
    api_id TEXT NOT NULL,
    model_type TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active);
CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);

-- Таблица результатов
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    response TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id);
CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id);
CREATE INDEX IF NOT EXISTS idx_results_saved_at ON results(saved_at);

-- Таблица настроек
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## Примечания

1. **API-ключи**: Все API-ключи должны храниться в файле `.env` в корне проекта. В таблице `models` хранится только имя переменной окружения, которая содержит ключ.

2. **Форматы дат**: Все даты хранятся в формате ISO 8601: `YYYY-MM-DD HH:MM:SS`.

3. **Метаданные**: Поле `metadata` в таблице `results` может содержать JSON с дополнительной информацией (количество токенов, время ответа, модель и т.д.).

4. **Теги**: Поле `tags` в таблице `prompts` может хранить теги в виде строки с разделителями (запятая) или в формате JSON массива.

5. **Каскадное удаление**: При удалении промта все связанные результаты также удаляются (ON DELETE CASCADE). Удаление модели запрещено, если есть связанные результаты (ON DELETE RESTRICT).

