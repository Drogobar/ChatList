"""
Модуль для улучшения промтов с помощью AI.
Использует существующий NetworkClient для отправки запросов к моделям.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from network import NetworkClient, APIError


class PromptImprover:
    """Класс для улучшения промтов с помощью AI."""
    
    # Шаблоны промптов для разных типов улучшения
    IMPROVEMENT_TEMPLATE = """Ты эксперт по улучшению промптов для AI. Проанализируй следующий промпт и улучши его.

Исходный промпт:
{prompt}

Задача: Улучши этот промпт, сделав его более четким, конкретным и эффективным. Верни улучшенную версию промпта.

Формат ответа:
1. Улучшенная версия промпта (основной ответ)
2. Затем напиши "---ВАРИАНТЫ---" и после этого 2-3 альтернативных варианта переформулировки, каждый с новой строки, начинающийся с "Вариант N:"

Улучшенная версия:"""

    REFORMULATION_TEMPLATE = """Ты эксперт по переформулировке текста. Переформулируй следующий промпт, сохранив его смысл, но изменив формулировку.

Исходный промпт:
{prompt}

Верни 3 варианта переформулировки, каждый с новой строки, начинающийся с "Вариант N:"
Варианты:"""

    CODE_ADAPTATION_TEMPLATE = """Ты эксперт по написанию промптов для программирования и работы с кодом. Адаптируй следующий промпт для задач, связанных с программированием.

Исходный промпт:
{prompt}

Адаптируй промпт для работы с кодом, добавь конкретику, требования к формату ответа (код, объяснения, примеры). Верни улучшенную версию.

Улучшенная версия:"""

    ANALYSIS_ADAPTATION_TEMPLATE = """Ты эксперт по написанию промптов для аналитических задач. Адаптируй следующий промпт для задач анализа данных, текста или информации.

Исходный промпт:
{prompt}

Адаптируй промпт для аналитических задач, добавь требования к структуре ответа, глубине анализа, формату вывода. Верни улучшенную версию.

Улучшенная версия:"""

    CREATIVE_ADAPTATION_TEMPLATE = """Ты эксперт по написанию промптов для креативных задач. Адаптируй следующий промпт для творческих задач (написание текстов, генерация идей, креативные решения).

Исходный промпт:
{prompt}

Адаптируй промпт для креативных задач, добавь требования к стилю, тону, формату творческого ответа. Верни улучшенную версию.

Улучшенная версия:"""

    def __init__(self, network_client: NetworkClient):
        """
        Инициализация улучшателя промтов.
        
        Args:
            network_client: Экземпляр NetworkClient для отправки запросов
        """
        self.network_client = network_client
    
    def improve_prompt(self, original_prompt: str, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Улучшить промт и получить варианты переформулировки.
        
        Args:
            original_prompt: Исходный текст промта
            model_info: Информация о модели для улучшения
        
        Returns:
            Словарь с результатами:
            {
                'improved': str,  # Улучшенная версия
                'alternatives': List[str],  # 2-3 альтернативных варианта
                'metadata': dict  # Метаданные запроса
            }
        
        Raises:
            APIError: При ошибке запроса к API
        """
        if not original_prompt or not original_prompt.strip():
            raise ValueError("Промт не может быть пустым")
        
        # Формируем запрос для улучшения
        improvement_prompt = self.IMPROVEMENT_TEMPLATE.format(prompt=original_prompt)
        
        # Отправляем запрос
        try:
            result = self.network_client.send_request(model_info, improvement_prompt)
            response_text = result['response']
            
            # Парсим ответ
            improved, alternatives = self._parse_improvement_response(response_text)
            
            return {
                'improved': improved,
                'alternatives': alternatives,
                'metadata': result.get('metadata', {})
            }
        except APIError as e:
            raise APIError(f"Ошибка при улучшении промта: {str(e)}")
    
    def get_adaptations(self, original_prompt: str, model_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Получить адаптации промта под разные типы задач.
        
        Args:
            original_prompt: Исходный текст промта
            model_info: Информация о модели
        
        Returns:
            Словарь с адаптациями:
            {
                'code': str,  # Адаптация для кода
                'analysis': str,  # Адаптация для анализа
                'creative': str  # Адаптация для креатива
            }
        """
        adaptations = {}
        
        # Адаптация для кода
        try:
            code_prompt = self.CODE_ADAPTATION_TEMPLATE.format(prompt=original_prompt)
            code_result = self.network_client.send_request(model_info, code_prompt)
            adaptations['code'] = self._extract_main_response(code_result['response'])
        except Exception as e:
            adaptations['code'] = f"Ошибка: {str(e)}"
        
        # Адаптация для анализа
        try:
            analysis_prompt = self.ANALYSIS_ADAPTATION_TEMPLATE.format(prompt=original_prompt)
            analysis_result = self.network_client.send_request(model_info, analysis_prompt)
            adaptations['analysis'] = self._extract_main_response(analysis_result['response'])
        except Exception as e:
            adaptations['analysis'] = f"Ошибка: {str(e)}"
        
        # Адаптация для креатива
        try:
            creative_prompt = self.CREATIVE_ADAPTATION_TEMPLATE.format(prompt=original_prompt)
            creative_result = self.network_client.send_request(model_info, creative_prompt)
            adaptations['creative'] = self._extract_main_response(creative_result['response'])
        except Exception as e:
            adaptations['creative'] = f"Ошибка: {str(e)}"
        
        return adaptations
    
    def _parse_improvement_response(self, response: str) -> Tuple[str, List[str]]:
        """
        Распарсить ответ AI на улучшенную версию и альтернативы.
        
        Args:
            response: Текст ответа от AI
        
        Returns:
            Кортеж (улучшенная_версия, список_альтернатив)
        """
        response = response.strip()
        
        # Ищем разделитель "---ВАРИАНТЫ---"
        if "---ВАРИАНТЫ---" in response:
            parts = response.split("---ВАРИАНТЫ---", 1)
            improved = parts[0].strip()
            alternatives_text = parts[1].strip()
        else:
            # Если разделителя нет, пытаемся найти варианты по паттерну
            improved = response
            alternatives_text = ""
            
            # Ищем паттерны "Вариант N:" или "Вариант N."
            variant_pattern = r'Вариант\s+\d+[.:]\s*(.+?)(?=Вариант\s+\d+[.:]|$)'
            matches = re.findall(variant_pattern, response, re.IGNORECASE | re.DOTALL)
            if matches:
                # Если нашли варианты, берем первую часть как улучшенную версию
                first_variant_pos = re.search(r'Вариант\s+\d+[.:]', response, re.IGNORECASE)
                if first_variant_pos:
                    improved = response[:first_variant_pos.start()].strip()
                    alternatives_text = response[first_variant_pos.start():]
        
        # Извлекаем улучшенную версию (убираем префикс "Улучшенная версия:" если есть)
        improved = re.sub(r'^Улучшенная\s+версия[.:]?\s*', '', improved, flags=re.IGNORECASE).strip()
        
        # Извлекаем альтернативы
        alternatives = []
        if alternatives_text:
            # Ищем варианты по паттерну
            variant_pattern = r'Вариант\s+\d+[.:]\s*(.+?)(?=Вариант\s+\d+[.:]|$)'
            matches = re.findall(variant_pattern, alternatives_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                alt = match.strip()
                if alt:
                    alternatives.append(alt)
        
        # Если альтернатив не найдено, пытаемся разбить по строкам
        if not alternatives and alternatives_text:
            lines = [line.strip() for line in alternatives_text.split('\n') if line.strip()]
            for line in lines:
                # Убираем префикс "Вариант N:"
                cleaned = re.sub(r'^Вариант\s+\d+[.:]\s*', '', line, flags=re.IGNORECASE).strip()
                if cleaned and len(cleaned) > 10:  # Минимальная длина для валидного варианта
                    alternatives.append(cleaned)
        
        # Ограничиваем количество альтернатив до 3
        alternatives = alternatives[:3]
        
        return improved, alternatives
    
    def _extract_main_response(self, response: str) -> str:
        """
        Извлечь основной ответ из ответа AI (убрать префиксы и форматирование).
        
        Args:
            response: Текст ответа от AI
        
        Returns:
            Очищенный текст ответа
        """
        response = response.strip()
        
        # Убираем префиксы типа "Улучшенная версия:"
        response = re.sub(r'^Улучшенная\s+версия[.:]?\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^Ответ[.:]?\s*', '', response, flags=re.IGNORECASE)
        
        return response.strip()

