"""
Окно для управления промтами.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QLineEdit, QTextEdit, QLabel,
                             QDialogButtonBox, QFormLayout, QWidget)
from PyQt5.QtCore import Qt
from db import Database


class PromptsDialog(QDialog):
    """Диалог для управления промтами."""
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Управление промтами")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_prompts()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        
        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search_prompts)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить промт")
        self.add_button.clicked.connect(self.add_prompt)
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_prompt)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_prompt)
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_prompts)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Таблица промтов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Дата", "Промт", "Теги", "Действия"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Кнопки закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_prompts(self):
        """Загрузить список промтов в таблицу."""
        prompts = self.db.get_prompts()
        self.table.setRowCount(len(prompts))
        
        for row, prompt in enumerate(prompts):
            self.table.setItem(row, 0, QTableWidgetItem(str(prompt['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(prompt['date']))
            
            prompt_text = prompt['prompt'][:100] + "..." if len(prompt['prompt']) > 100 else prompt['prompt']
            self.table.setItem(row, 2, QTableWidgetItem(prompt_text))
            
            tags = prompt.get('tags', '') or ''
            self.table.setItem(row, 3, QTableWidgetItem(tags))
            
            # Кнопки CRUD
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout()
            buttons_layout.setContentsMargins(2, 2, 2, 2)
            buttons_widget.setLayout(buttons_layout)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_prompt_by_row(r))
            buttons_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_prompt_by_row(r))
            buttons_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 4, buttons_widget)
        
        self.table.resizeColumnsToContents()
    
    def search_prompts(self, query: str):
        """Поиск промтов."""
        if not query.strip():
            self.load_prompts()
            return
        
        prompts = self.db.search_prompts(query)
        self.table.setRowCount(len(prompts))
        
        for row, prompt in enumerate(prompts):
            self.table.setItem(row, 0, QTableWidgetItem(str(prompt['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(prompt['date']))
            
            prompt_text = prompt['prompt'][:100] + "..." if len(prompt['prompt']) > 100 else prompt['prompt']
            self.table.setItem(row, 2, QTableWidgetItem(prompt_text))
            
            tags = prompt.get('tags', '') or ''
            self.table.setItem(row, 3, QTableWidgetItem(tags))
            
            # Кнопки CRUD
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout()
            buttons_layout.setContentsMargins(2, 2, 2, 2)
            buttons_widget.setLayout(buttons_layout)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_prompt_by_row(r))
            buttons_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_prompt_by_row(r))
            buttons_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 4, buttons_widget)
        
        self.table.resizeColumnsToContents()
    
    def get_selected_prompt_id(self) -> int:
        """Получить ID выбранного промта."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        return int(self.table.item(current_row, 0).text())
    
    def add_prompt(self):
        """Добавить новый промт."""
        dialog = PromptEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.db.add_prompt(
                    dialog.prompt_edit.toPlainText(),
                    dialog.tags_edit.text() if dialog.tags_edit.text().strip() else None
                )
                self.load_prompts()
                QMessageBox.information(self, "Успех", "Промт успешно добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить промт:\n{str(e)}")
    
    def edit_prompt(self):
        """Редактировать выбранный промт."""
        prompt_id = self.get_selected_prompt_id()
        if not prompt_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите промт для редактирования")
            return
        
        self.edit_prompt_by_id(prompt_id)
    
    def edit_prompt_by_row(self, row: int):
        """Редактировать промт по номеру строки."""
        if row < 0 or row >= self.table.rowCount():
            return
        
        prompt_id = int(self.table.item(row, 0).text())
        self.edit_prompt_by_id(prompt_id)
    
    def edit_prompt_by_id(self, prompt_id: int):
        """Редактировать промт по ID."""
        prompt = self.db.get_prompt_by_id(prompt_id)
        if not prompt:
            QMessageBox.critical(self, "Ошибка", "Промт не найден")
            return
        
        dialog = PromptEditDialog(self, prompt)
        if dialog.exec_() == QDialog.Accepted:
            try:
                prompt_text = dialog.prompt_edit.toPlainText().strip()
                tags_text = dialog.tags_edit.text().strip() if dialog.tags_edit.text().strip() else None
                
                if not prompt_text:
                    QMessageBox.warning(self, "Предупреждение", "Промт не может быть пустым")
                    return
                
                self.db.update_prompt(prompt_id, prompt_text, tags_text)
                self.load_prompts()
                QMessageBox.information(self, "Успех", "Промт успешно обновлён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить промт:\n{str(e)}")
    
    def delete_prompt(self):
        """Удалить выбранный промт."""
        prompt_id = self.get_selected_prompt_id()
        if not prompt_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите промт для удаления")
            return
        
        self.delete_prompt_by_id(prompt_id)
    
    def delete_prompt_by_row(self, row: int):
        """Удалить промт по номеру строки."""
        if row < 0 or row >= self.table.rowCount():
            return
        
        prompt_id = int(self.table.item(row, 0).text())
        self.delete_prompt_by_id(prompt_id)
    
    def delete_prompt_by_id(self, prompt_id: int):
        """Удалить промт по ID."""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить этот промт?\nВсе связанные результаты также будут удалены.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_prompt(prompt_id)
                self.load_prompts()
                QMessageBox.information(self, "Успех", "Промт успешно удалён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить промт:\n{str(e)}")


class PromptEditDialog(QDialog):
    """Диалог для добавления/редактирования промта."""
    
    def __init__(self, parent=None, prompt=None):
        super().__init__(parent)
        self.prompt = prompt
        self.setWindowTitle("Редактировать промт" if prompt else "Добавить промт")
        self.setMinimumSize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QFormLayout()
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Введите промт...")
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Теги через запятую (опционально)")
        
        layout.addRow("Промт:", self.prompt_edit)
        layout.addRow("Теги:", self.tags_edit)
        
        if self.prompt:
            self.prompt_edit.setText(self.prompt['prompt'])
            self.tags_edit.setText(self.prompt.get('tags', '') or '')
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)

