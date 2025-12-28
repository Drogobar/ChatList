"""
Модуль для работы с моделями нейросетей.
Управляет конфигурацией моделей и их валидацией.
"""

from typing import List, Dict, Optional, Any
from db import Database


class ModelManager:
    """Класс для управления моделями нейросетей."""
    
    def __init__(self, db: Database):
        """
        Инициализация менеджера моделей.
        
        Args:
            db: Экземпляр класса Database
        """
        self.db = db
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """
        Получить список всех моделей.
        
        Returns:
            Список всех моделей из БД
        """
        return self.db.get_models()
    
    def get_active_models(self) -> List[Dict[str, Any]]:
        """
        Получить список активных моделей.
        
        Returns:
            Список активных моделей (is_active=1)
        """
        return self.db.get_active_models()
    
    def add_model(self, name: str, api_url: str, api_id: str, model_type: str, 
                  is_active: int = 1) -> int:
        """
        Добавить новую модель.
        
        Args:
            name: Название модели
            api_url: URL API
            api_id: Имя переменной окружения с API-ключом
            model_type: Тип модели (openrouter, openai, deepseek, groq)
            is_active: Флаг активности (1 - активна, 0 - неактивна)
        
        Returns:
            ID добавленной модели
        
        Raises:
            ValueError: При невалидных данных
        """
        # Валидация
        self._validate_model_config(name, api_url, api_id, model_type)
        
        return self.db.add_model(name, api_url, api_id, model_type, is_active)
    
    def update_model(self, model_id: int, **kwargs) -> bool:
        """
        Обновить данные модели.
        
        Args:
            model_id: ID модели
            **kwargs: Поля для обновления (name, api_url, api_id, model_type, is_active)
        
        Returns:
            True если обновление успешно
        """
        # Валидация если переданы соответствующие поля
        if 'name' in kwargs or 'api_url' in kwargs or 'api_id' in kwargs or 'model_type' in kwargs:
            name = kwargs.get('name', '')
            api_url = kwargs.get('api_url', '')
            api_id = kwargs.get('api_id', '')
            model_type = kwargs.get('model_type', '')
            
            # Получаем текущие данные модели
            current_model = self.db.get_model_by_id(model_id)
            if not current_model:
                raise ValueError(f"Модель с ID {model_id} не найдена")
            
            # Используем новые значения или текущие
            final_name = name if name else current_model['name']
            final_api_url = api_url if api_url else current_model['api_url']
            final_api_id = api_id if api_id else current_model['api_id']
            final_model_type = model_type if model_type else current_model['model_type']
            
            self._validate_model_config(final_name, final_api_url, final_api_id, final_model_type)
        
        return self.db.update_model(model_id, **kwargs)
    
    def delete_model(self, model_id: int) -> bool:
        """
        Удалить модель.
        
        Args:
            model_id: ID модели
        
        Returns:
            True если удаление успешно
        
        Raises:
            ValueError: Если модель не найдена или есть связанные результаты
        """
        model = self.db.get_model_by_id(model_id)
        if not model:
            raise ValueError(f"Модель с ID {model_id} не найдена")
        
        try:
            return self.db.delete_model(model_id)
        except Exception as e:
            if "связанные результаты" in str(e):
                raise ValueError("Невозможно удалить модель: существуют сохранённые результаты")
            raise
    
    def toggle_model_status(self, model_id: int) -> bool:
        """
        Переключить статус активности модели.
        
        Args:
            model_id: ID модели
        
        Returns:
            True если обновление успешно
        """
        model = self.db.get_model_by_id(model_id)
        if not model:
            raise ValueError(f"Модель с ID {model_id} не найдена")
        
        new_status = 0 if model['is_active'] == 1 else 1
        return self.db.update_model_status(model_id, new_status)
    
    def get_model_by_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить модель по ID.
        
        Args:
            model_id: ID модели
        
        Returns:
            Словарь с данными модели или None
        """
        return self.db.get_model_by_id(model_id)
    
    def search_models(self, query: str) -> List[Dict[str, Any]]:
        """
        Поиск моделей.
        
        Args:
            query: Поисковый запрос
        
        Returns:
            Список найденных моделей
        """
        return self.db.search_models(query)
    
    def _validate_model_config(self, name: str, api_url: str, api_id: str, model_type: str):
        """
        Валидация конфигурации модели.
        
        Args:
            name: Название модели
            api_url: URL API
            api_id: Имя переменной окружения с API-ключом
            model_type: Тип модели
        
        Raises:
            ValueError: При невалидных данных
        """
        if not name or not name.strip():
            raise ValueError("Название модели не может быть пустым")
        
        if not api_url or not api_url.strip():
            raise ValueError("URL API не может быть пустым")
        
        if not api_url.startswith(('http://', 'https://')):
            raise ValueError("URL API должен начинаться с http:// или https://")
        
        if not api_id or not api_id.strip():
            raise ValueError("Имя переменной окружения с API-ключом не может быть пустым")
        
        valid_types = ['openrouter', 'openai', 'deepseek', 'groq', 'universal']
        if model_type.lower() not in valid_types:
            raise ValueError(f"Тип модели должен быть одним из: {', '.join(valid_types)}")

