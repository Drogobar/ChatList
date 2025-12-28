"""
Модуль для работы с базой данных SQLite.
Инкапсулирует всю логику работы с базой данных приложения ChatList.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple


class Database:
    """Класс для работы с базой данных SQLite."""
    
    def __init__(self, db_path: str = "chatlist.db"):
        """
        Инициализация подключения к базе данных.
        
        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._initialize_db()
    
    def _connect(self):
        """Установка подключения к базе данных."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Возвращает результаты как словари
        except sqlite3.Error as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")
    
    def _initialize_db(self):
        """Инициализация базы данных - создание таблиц и индексов."""
        cursor = self.conn.cursor()
        
        try:
            # Таблица промтов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    tags TEXT
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags)
            """)
            
            # Таблица моделей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    api_url TEXT NOT NULL,
                    api_id TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_models_name ON models(name)
            """)
            
            # Таблица результатов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    model_id INTEGER NOT NULL,
                    response TEXT NOT NULL,
                    saved_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
                    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_results_saved_at ON results(saved_at)
            """)
            
            # Таблица настроек
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка инициализации базы данных: {e}")
        finally:
            cursor.close()
    
    def _get_current_datetime(self) -> str:
        """Получить текущую дату и время в формате ISO 8601."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ========== Методы для работы с таблицей prompts ==========
    
    def add_prompt(self, prompt: str, tags: Optional[str] = None) -> int:
        """
        Добавить новый промт в базу данных.
        
        Args:
            prompt: Текст промта
            tags: Теги для категоризации (строка с разделителями или None)
        
        Returns:
            ID добавленного промта
        """
        cursor = self.conn.cursor()
        try:
            date = self._get_current_datetime()
            cursor.execute("""
                INSERT INTO prompts (date, prompt, tags)
                VALUES (?, ?, ?)
            """, (date, prompt, tags))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка добавления промта: {e}")
        finally:
            cursor.close()
    
    def get_prompts(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получить список промтов.
        
        Args:
            limit: Максимальное количество записей (None = все)
            offset: Смещение для пагинации
        
        Returns:
            Список словарей с данными промтов
        """
        cursor = self.conn.cursor()
        try:
            if limit:
                cursor.execute("""
                    SELECT * FROM prompts
                    ORDER BY date DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM prompts
                    ORDER BY date DESC
                """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения промтов: {e}")
        finally:
            cursor.close()
    
    def search_prompts(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Поиск промтов по тексту или тегам.
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
        
        Returns:
            Список найденных промтов
        """
        cursor = self.conn.cursor()
        try:
            search_pattern = f"%{query}%"
            sql = """
                SELECT * FROM prompts
                WHERE prompt LIKE ? OR tags LIKE ?
                ORDER BY date DESC
            """
            
            if limit:
                sql += " LIMIT ?"
                cursor.execute(sql, (search_pattern, search_pattern, limit))
            else:
                cursor.execute(sql, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка поиска промтов: {e}")
        finally:
            cursor.close()
    
    def get_prompt_by_id(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить промт по ID.
        
        Args:
            prompt_id: ID промта
        
        Returns:
            Словарь с данными промта или None
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения промта: {e}")
        finally:
            cursor.close()
    
    def sort_prompts(self, sort_by: str = "date", order: str = "DESC") -> List[Dict[str, Any]]:
        """
        Получить отсортированный список промтов.
        
        Args:
            sort_by: Поле для сортировки (date, prompt, tags)
            order: Порядок сортировки (ASC, DESC)
        
        Returns:
            Отсортированный список промтов
        """
        cursor = self.conn.cursor()
        try:
            valid_fields = ["date", "prompt", "tags"]
            if sort_by not in valid_fields:
                sort_by = "date"
            
            valid_orders = ["ASC", "DESC"]
            if order not in valid_orders:
                order = "DESC"
            
            cursor.execute(f"""
                SELECT * FROM prompts
                ORDER BY {sort_by} {order}
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка сортировки промтов: {e}")
        finally:
            cursor.close()
    
    # ========== Методы для работы с таблицей models ==========
    
    def add_model(self, name: str, api_url: str, api_id: str, model_type: str, 
                  is_active: int = 1) -> int:
        """
        Добавить новую модель в базу данных.
        
        Args:
            name: Название модели
            api_url: URL API для отправки запросов
            api_id: Имя переменной окружения с API-ключом
            model_type: Тип модели/API (openai, deepseek, groq и т.д.)
            is_active: Флаг активности (1 - активна, 0 - неактивна)
        
        Returns:
            ID добавленной модели
        """
        cursor = self.conn.cursor()
        try:
            created_at = self._get_current_datetime()
            cursor.execute("""
                INSERT INTO models (name, api_url, api_id, model_type, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, api_url, api_id, model_type, is_active, created_at))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise Exception(f"Модель с таким именем уже существует: {e}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка добавления модели: {e}")
        finally:
            cursor.close()
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Получить список всех моделей.
        
        Returns:
            Список словарей с данными моделей
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM models ORDER BY name")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения моделей: {e}")
        finally:
            cursor.close()
    
    def get_active_models(self) -> List[Dict[str, Any]]:
        """
        Получить список активных моделей (is_active=1).
        
        Returns:
            Список активных моделей
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM models
                WHERE is_active = 1
                ORDER BY name
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения активных моделей: {e}")
        finally:
            cursor.close()
    
    def update_model_status(self, model_id: int, is_active: int) -> bool:
        """
        Обновить статус активности модели.
        
        Args:
            model_id: ID модели
            is_active: Новый статус (1 - активна, 0 - неактивна)
        
        Returns:
            True если обновление успешно
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE models
                SET is_active = ?
                WHERE id = ?
            """, (is_active, model_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка обновления статуса модели: {e}")
        finally:
            cursor.close()
    
    def get_model_by_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить модель по ID.
        
        Args:
            model_id: ID модели
        
        Returns:
            Словарь с данными модели или None
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM models WHERE id = ?", (model_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения модели: {e}")
        finally:
            cursor.close()
    
    def update_model(self, model_id: int, name: Optional[str] = None,
                     api_url: Optional[str] = None, api_id: Optional[str] = None,
                     model_type: Optional[str] = None, is_active: Optional[int] = None) -> bool:
        """
        Обновить данные модели.
        
        Args:
            model_id: ID модели
            name: Новое название (опционально)
            api_url: Новый URL API (опционально)
            api_id: Новый api_id (опционально)
            model_type: Новый тип модели (опционально)
            is_active: Новый статус активности (опционально)
        
        Returns:
            True если обновление успешно
        """
        cursor = self.conn.cursor()
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if api_url is not None:
                updates.append("api_url = ?")
                params.append(api_url)
            if api_id is not None:
                updates.append("api_id = ?")
                params.append(api_id)
            if model_type is not None:
                updates.append("model_type = ?")
                params.append(model_type)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            
            if not updates:
                return False
            
            params.append(model_id)
            sql = f"UPDATE models SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, params)
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка обновления модели: {e}")
        finally:
            cursor.close()
    
    def delete_model(self, model_id: int) -> bool:
        """
        Удалить модель из базы данных.
        
        Args:
            model_id: ID модели
        
        Returns:
            True если удаление успешно
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise Exception("Невозможно удалить модель: существуют связанные результаты")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка удаления модели: {e}")
        finally:
            cursor.close()
    
    def search_models(self, query: str) -> List[Dict[str, Any]]:
        """
        Поиск моделей по названию или типу.
        
        Args:
            query: Поисковый запрос
        
        Returns:
            Список найденных моделей
        """
        cursor = self.conn.cursor()
        try:
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM models
                WHERE name LIKE ? OR model_type LIKE ?
                ORDER BY name
            """, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка поиска моделей: {e}")
        finally:
            cursor.close()
    
    def sort_models(self, sort_by: str = "name", order: str = "ASC") -> List[Dict[str, Any]]:
        """
        Получить отсортированный список моделей.
        
        Args:
            sort_by: Поле для сортировки (name, model_type, created_at, is_active)
            order: Порядок сортировки (ASC, DESC)
        
        Returns:
            Отсортированный список моделей
        """
        cursor = self.conn.cursor()
        try:
            valid_fields = ["name", "model_type", "created_at", "is_active"]
            if sort_by not in valid_fields:
                sort_by = "name"
            
            valid_orders = ["ASC", "DESC"]
            if order not in valid_orders:
                order = "ASC"
            
            cursor.execute(f"""
                SELECT * FROM models
                ORDER BY {sort_by} {order}
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка сортировки моделей: {e}")
        finally:
            cursor.close()
    
    # ========== Методы для работы с таблицей results ==========
    
    def save_result(self, prompt_id: int, model_id: int, response: str,
                    metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Сохранить результат ответа нейросети.
        
        Args:
            prompt_id: ID промта
            model_id: ID модели
            response: Текст ответа
            metadata: Дополнительные метаданные (словарь, будет сохранён как JSON)
        
        Returns:
            ID сохранённого результата
        """
        cursor = self.conn.cursor()
        try:
            saved_at = self._get_current_datetime()
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO results (prompt_id, model_id, response, saved_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (prompt_id, model_id, response, saved_at, metadata_json))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка сохранения результата: {e}")
        finally:
            cursor.close()
    
    def get_results(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получить список сохранённых результатов.
        
        Args:
            limit: Максимальное количество записей (None = все)
            offset: Смещение для пагинации
        
        Returns:
            Список словарей с данными результатов
        """
        cursor = self.conn.cursor()
        try:
            if limit:
                cursor.execute("""
                    SELECT r.*, p.prompt, m.name as model_name
                    FROM results r
                    JOIN prompts p ON r.prompt_id = p.id
                    JOIN models m ON r.model_id = m.id
                    ORDER BY r.saved_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            else:
                cursor.execute("""
                    SELECT r.*, p.prompt, m.name as model_name
                    FROM results r
                    JOIN prompts p ON r.prompt_id = p.id
                    JOIN models m ON r.model_id = m.id
                    ORDER BY r.saved_at DESC
                """)
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                # Парсим metadata если она есть
                if result.get('metadata'):
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except json.JSONDecodeError:
                        pass
                results.append(result)
            return results
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения результатов: {e}")
        finally:
            cursor.close()
    
    def get_results_by_prompt(self, prompt_id: int) -> List[Dict[str, Any]]:
        """
        Получить все результаты для конкретного промта.
        
        Args:
            prompt_id: ID промта
        
        Returns:
            Список результатов для промта
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT r.*, m.name as model_name
                FROM results r
                JOIN models m ON r.model_id = m.id
                WHERE r.prompt_id = ?
                ORDER BY r.saved_at DESC
            """, (prompt_id,))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result.get('metadata'):
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except json.JSONDecodeError:
                        pass
                results.append(result)
            return results
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения результатов по промту: {e}")
        finally:
            cursor.close()
    
    def get_results_by_model(self, model_id: int) -> List[Dict[str, Any]]:
        """
        Получить все результаты для конкретной модели.
        
        Args:
            model_id: ID модели
        
        Returns:
            Список результатов для модели
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT r.*, p.prompt
                FROM results r
                JOIN prompts p ON r.prompt_id = p.id
                WHERE r.model_id = ?
                ORDER BY r.saved_at DESC
            """, (model_id,))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result.get('metadata'):
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except json.JSONDecodeError:
                        pass
                results.append(result)
            return results
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения результатов по модели: {e}")
        finally:
            cursor.close()
    
    def search_results(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Поиск результатов по тексту ответа или промта.
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
        
        Returns:
            Список найденных результатов
        """
        cursor = self.conn.cursor()
        try:
            search_pattern = f"%{query}%"
            sql = """
                SELECT r.*, p.prompt, m.name as model_name
                FROM results r
                JOIN prompts p ON r.prompt_id = p.id
                JOIN models m ON r.model_id = m.id
                WHERE r.response LIKE ? OR p.prompt LIKE ?
                ORDER BY r.saved_at DESC
            """
            
            if limit:
                sql += " LIMIT ?"
                cursor.execute(sql, (search_pattern, search_pattern, limit))
            else:
                cursor.execute(sql, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result.get('metadata'):
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except json.JSONDecodeError:
                        pass
                results.append(result)
            return results
        except sqlite3.Error as e:
            raise Exception(f"Ошибка поиска результатов: {e}")
        finally:
            cursor.close()
    
    def sort_results(self, sort_by: str = "saved_at", order: str = "DESC") -> List[Dict[str, Any]]:
        """
        Получить отсортированный список результатов.
        
        Args:
            sort_by: Поле для сортировки (saved_at, response, model_name, prompt)
            order: Порядок сортировки (ASC, DESC)
        
        Returns:
            Отсортированный список результатов
        """
        cursor = self.conn.cursor()
        try:
            valid_fields = ["saved_at", "response"]
            if sort_by not in valid_fields:
                sort_by = "saved_at"
            
            valid_orders = ["ASC", "DESC"]
            if order not in valid_orders:
                order = "DESC"
            
            cursor.execute(f"""
                SELECT r.*, p.prompt, m.name as model_name
                FROM results r
                JOIN prompts p ON r.prompt_id = p.id
                JOIN models m ON r.model_id = m.id
                ORDER BY r.{sort_by} {order}
            """)
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result.get('metadata'):
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except json.JSONDecodeError:
                        pass
                results.append(result)
            return results
        except sqlite3.Error as e:
            raise Exception(f"Ошибка сортировки результатов: {e}")
        finally:
            cursor.close()
    
    def delete_result(self, result_id: int) -> bool:
        """
        Удалить результат из базы данных.
        
        Args:
            result_id: ID результата
        
        Returns:
            True если удаление успешно
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка удаления результата: {e}")
        finally:
            cursor.close()
    
    # ========== Методы для работы с таблицей settings ==========
    
    def save_setting(self, key: str, value: str) -> bool:
        """
        Сохранить настройку.
        
        Args:
            key: Ключ настройки
            value: Значение настройки
        
        Returns:
            True если сохранение успешно
        """
        cursor = self.conn.cursor()
        try:
            updated_at = self._get_current_datetime()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, updated_at))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка сохранения настройки: {e}")
        finally:
            cursor.close()
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Получить значение настройки.
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию, если настройка не найдена
        
        Returns:
            Значение настройки или default
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения настройки: {e}")
        finally:
            cursor.close()
    
    def get_all_settings(self) -> Dict[str, str]:
        """
        Получить все настройки.
        
        Returns:
            Словарь всех настроек (ключ -> значение)
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
            return {row['key']: row['value'] for row in rows}
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения всех настроек: {e}")
        finally:
            cursor.close()
    
    def delete_setting(self, key: str) -> bool:
        """
        Удалить настройку.
        
        Args:
            key: Ключ настройки
        
        Returns:
            True если удаление успешно
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка удаления настройки: {e}")
        finally:
            cursor.close()
    
    # ========== Общие методы ==========
    
    def close(self):
        """Закрыть подключение к базе данных."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера."""
        self.close()

