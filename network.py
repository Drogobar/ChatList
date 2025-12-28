"""
Модуль для работы с API нейросетей.
Отправляет запросы к различным API и обрабатывает ответы.
"""

import os
import json
import time
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import requests

# Загружаем переменные окружения из .env и .env.local
load_dotenv()  # Загружает .env
load_dotenv('.env.local')  # Загружает .env.local (если существует)


class APIError(Exception):
    """Исключение для ошибок API."""
    pass


class NetworkClient:
    """Базовый класс для работы с API нейросетей."""
    
    def __init__(self, timeout: int = 60):
        """
        Инициализация клиента.
        
        Args:
            timeout: Таймаут запроса в секундах
        """
        self.timeout = timeout
    
    def get_api_key(self, api_id: str) -> Optional[str]:
        """
        Получить API-ключ из переменных окружения.
        
        Args:
            api_id: Имя переменной окружения с API-ключом
        
        Returns:
            API-ключ или None
        """
        return os.getenv(api_id)
    
    def send_request(self, model_info: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """
        Отправить промт в модель и получить ответ.
        
        Args:
            model_info: Информация о модели из БД (словарь с полями: name, api_url, api_id, model_type)
            prompt: Текст промта
        
        Returns:
            Словарь с результатом: {'response': str, 'metadata': dict}
        
        Raises:
            APIError: При ошибке запроса
        """
        model_type = model_info.get('model_type', '').lower()
        
        if model_type == 'openrouter':
            return self._send_openrouter_request(model_info, prompt)
        elif model_type == 'openai':
            return self._send_openai_request(model_info, prompt)
        elif model_type == 'deepseek':
            return self._send_deepseek_request(model_info, prompt)
        elif model_type == 'groq':
            return self._send_groq_request(model_info, prompt)
        else:
            # Попытка универсального запроса (OpenAI-совместимый формат)
            return self._send_universal_request(model_info, prompt)
    
    def _send_openrouter_request(self, model_info: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Отправить запрос через OpenRouter API."""
        api_key = self.get_api_key(model_info['api_id'])
        if not api_key:
            raise APIError(f"API-ключ {model_info['api_id']} не найден в переменных окружения")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Опционально
            "X-Title": "ChatList"  # Опционально
        }
        
        # Извлекаем имя модели из model_info
        # Для OpenRouter имя модели должно быть в формате "provider/model-name"
        # Например: "openai/gpt-4", "anthropic/claude-3-opus", "google/gemini-pro"
        model_name = model_info.get('name', '')
        
        # Если имя модели не указано или не в правильном формате, используем дефолт
        if not model_name or '/' not in model_name:
            model_name = "openai/gpt-3.5-turbo"
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            metadata = {
                'model': data.get('model', model_name),
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'response_time': round(elapsed_time, 2),
                'api_type': 'openrouter'
            }
            
            return {
                'response': content,
                'metadata': metadata
            }
        except requests.exceptions.RequestException as e:
            raise APIError(f"Ошибка запроса к OpenRouter: {str(e)}")
    
    def _send_openai_request(self, model_info: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Отправить запрос через OpenAI API."""
        api_key = self.get_api_key(model_info['api_id'])
        if not api_key:
            raise APIError(f"API-ключ {model_info['api_id']} не найден в переменных окружения")
        
        url = model_info.get('api_url', 'https://api.openai.com/v1/chat/completions')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Извлекаем имя модели из name или используем дефолт
        model_name = model_info.get('name', 'gpt-3.5-turbo')
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            metadata = {
                'model': data.get('model', model_name),
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'response_time': round(elapsed_time, 2),
                'api_type': 'openai'
            }
            
            return {
                'response': content,
                'metadata': metadata
            }
        except requests.exceptions.RequestException as e:
            raise APIError(f"Ошибка запроса к OpenAI: {str(e)}")
    
    def _send_deepseek_request(self, model_info: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Отправить запрос через DeepSeek API."""
        api_key = self.get_api_key(model_info['api_id'])
        if not api_key:
            raise APIError(f"API-ключ {model_info['api_id']} не найден в переменных окружения")
        
        url = model_info.get('api_url', 'https://api.deepseek.com/v1/chat/completions')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        model_name = model_info.get('name', 'deepseek-chat')
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            metadata = {
                'model': data.get('model', model_name),
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'response_time': round(elapsed_time, 2),
                'api_type': 'deepseek'
            }
            
            return {
                'response': content,
                'metadata': metadata
            }
        except requests.exceptions.RequestException as e:
            raise APIError(f"Ошибка запроса к DeepSeek: {str(e)}")
    
    def _send_groq_request(self, model_info: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Отправить запрос через Groq API."""
        api_key = self.get_api_key(model_info['api_id'])
        if not api_key:
            raise APIError(f"API-ключ {model_info['api_id']} не найден в переменных окружения")
        
        url = model_info.get('api_url', 'https://api.groq.com/openai/v1/chat/completions')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        model_name = model_info.get('name', 'mixtral-8x7b-32768')
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            metadata = {
                'model': data.get('model', model_name),
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'response_time': round(elapsed_time, 2),
                'api_type': 'groq'
            }
            
            return {
                'response': content,
                'metadata': metadata
            }
        except requests.exceptions.RequestException as e:
            raise APIError(f"Ошибка запроса к Groq: {str(e)}")
    
    def _send_universal_request(self, model_info: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Универсальный запрос для OpenAI-совместимых API."""
        api_key = self.get_api_key(model_info['api_id'])
        if not api_key:
            raise APIError(f"API-ключ {model_info['api_id']} не найден в переменных окружения")
        
        url = model_info.get('api_url')
        if not url:
            raise APIError("URL API не указан для модели")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        model_name = model_info.get('name', 'unknown')
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            metadata = {
                'model': data.get('model', model_name),
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'response_time': round(elapsed_time, 2),
                'api_type': model_info.get('model_type', 'unknown')
            }
            
            return {
                'response': content,
                'metadata': metadata
            }
        except requests.exceptions.RequestException as e:
            raise APIError(f"Ошибка запроса к API: {str(e)}")

