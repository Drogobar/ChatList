"""
Диалог для отображения результатов улучшения промта.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel,
    QTabWidget, QWidget, QMessageBox, QDialogButtonBox, QScrollArea,
    QGroupBox, QButtonGroup, QRadioButton
)
from PyQt5.QtCore import Qt
from typing import Dict, List, Optional


class PromptImproverDialog(QDialog):
    """Диалог для отображения результатов улучшения промта."""
    
    def __init__(self, original_prompt: str, improved_result: Dict, 
                 adaptations: Optional[Dict[str, str]] = None, parent=None):
        """
        Инициализация диалога.
        
        Args:
            original_prompt: Исходный промт
            improved_result: Результат улучшения {'improved': str, 'alternatives': List[str]}
            adaptations: Адаптации под разные типы задач (опционально)
            parent: Родительское окно
        """
        super().__init__(parent)
        self.original_prompt = original_prompt
        self.improved_result = improved_result
        self.adaptations = adaptations or {}
        self.selected_text = None  # Выбранный текст для подстановки
        
        self.setWindowTitle("Улучшение промта")
        self.setMinimumSize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Исходный промт
        original_group = QGroupBox("Исходный промт")
        original_layout = QVBoxLayout()
        self.original_text = QTextEdit()
        self.original_text.setPlainText(self.original_prompt)
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(100)
        original_layout.addWidget(self.original_text)
        original_group.setLayout(original_layout)
        layout.addWidget(original_group)
        
        # Вкладки для разных вариантов
        self.tabs = QTabWidget()
        
        # Вкладка: Улучшенная версия
        improved_tab = self.create_improved_tab()
        self.tabs.addTab(improved_tab, "Улучшенная версия")
        
        # Вкладки для альтернативных вариантов
        alternatives = self.improved_result.get('alternatives', [])
        for i, alt in enumerate(alternatives, 1):
            alt_tab = self.create_alternative_tab(alt, i)
            self.tabs.addTab(alt_tab, f"Вариант {i}")
        
        # Вкладки для адаптаций (если есть)
        if self.adaptations.get('code'):
            code_tab = self.create_adaptation_tab(self.adaptations['code'], "Код")
            self.tabs.addTab(code_tab, "Адаптация: Код")
        
        if self.adaptations.get('analysis'):
            analysis_tab = self.create_adaptation_tab(self.adaptations['analysis'], "Анализ")
            self.tabs.addTab(analysis_tab, "Адаптация: Анализ")
        
        if self.adaptations.get('creative'):
            creative_tab = self.create_adaptation_tab(self.adaptations['creative'], "Креатив")
            self.tabs.addTab(creative_tab, "Адаптация: Креатив")
        
        layout.addWidget(self.tabs)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        self.use_button = QPushButton("Подставить в поле ввода")
        self.use_button.clicked.connect(self.on_use_selected)
        buttons_layout.addWidget(self.use_button)
        
        self.save_button = QPushButton("Сохранить как новый промт")
        self.save_button.clicked.connect(self.on_save_prompt)
        buttons_layout.addWidget(self.save_button)
        
        buttons_layout.addStretch()
        
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(button_box)
        
        layout.addLayout(buttons_layout)
    
    def create_improved_tab(self) -> QWidget:
        """Создать вкладку с улучшенной версией."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        improved_text = self.improved_result.get('improved', '')
        
        text_edit = QTextEdit()
        text_edit.setPlainText(improved_text)
        text_edit.setReadOnly(True)
        text_edit.setMinimumHeight(200)
        layout.addWidget(text_edit)
        
        # Радио-кнопка для выбора
        radio = QRadioButton("Использовать этот вариант")
        radio.setChecked(True)  # По умолчанию выбран улучшенный вариант
        radio.toggled.connect(lambda checked: self.on_variant_selected(improved_text) if checked else None)
        layout.addWidget(radio)
        
        # Устанавливаем выбранный текст по умолчанию
        self.selected_text = improved_text
        
        return widget
    
    def create_alternative_tab(self, text: str, variant_num: int) -> QWidget:
        """Создать вкладку с альтернативным вариантом."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        text_edit.setMinimumHeight(200)
        layout.addWidget(text_edit)
        
        # Радио-кнопка для выбора
        radio = QRadioButton("Использовать этот вариант")
        radio.toggled.connect(lambda checked: self.on_variant_selected(text) if checked else None)
        layout.addWidget(radio)
        
        return widget
    
    def create_adaptation_tab(self, text: str, adaptation_type: str) -> QWidget:
        """Создать вкладку с адаптацией."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Проверяем, не является ли текст ошибкой
        if text.startswith("Ошибка:"):
            label = QLabel(text)
            label.setStyleSheet("color: red;")
            layout.addWidget(label)
        else:
            text_edit = QTextEdit()
            text_edit.setPlainText(text)
            text_edit.setReadOnly(True)
            text_edit.setMinimumHeight(200)
            layout.addWidget(text_edit)
            
            # Радио-кнопка для выбора
            radio = QRadioButton("Использовать этот вариант")
            radio.toggled.connect(lambda checked: self.on_variant_selected(text) if checked else None)
            layout.addWidget(radio)
        
        return widget
    
    def on_variant_selected(self, text: str):
        """Обработчик выбора варианта."""
        self.selected_text = text
    
    def on_use_selected(self):
        """Подставить выбранный вариант в поле ввода."""
        if not self.selected_text:
            # Если ничего не выбрано, берем текущую вкладку
            current_widget = self.tabs.currentWidget()
            text_edits = current_widget.findChildren(QTextEdit)
            if text_edits:
                self.selected_text = text_edits[0].toPlainText()
        
        if not self.selected_text or not self.selected_text.strip():
            QMessageBox.warning(self, "Предупреждение", "Выберите вариант для подстановки")
            return
        
        self.accept()
    
    def on_save_prompt(self):
        """Сохранить выбранный вариант как новый промт."""
        if not self.selected_text:
            # Если ничего не выбрано, берем текущую вкладку
            current_widget = self.tabs.currentWidget()
            text_edits = current_widget.findChildren(QTextEdit)
            if text_edits:
                self.selected_text = text_edits[0].toPlainText()
        
        if not self.selected_text or not self.selected_text.strip():
            QMessageBox.warning(self, "Предупреждение", "Выберите вариант для сохранения")
            return
        
        # Сохраняем выбранный текст и закрываем диалог с кодом сохранения
        self.selected_text = self.selected_text.strip()
        self.done(2)  # Специальный код для сохранения
    
    def get_selected_text(self) -> Optional[str]:
        """Получить выбранный текст."""
        return self.selected_text

