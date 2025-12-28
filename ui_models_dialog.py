"""
Окно для управления моделями нейросетей.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QCheckBox, QLineEdit, QLabel, 
                             QComboBox, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt
from models import ModelManager


class ModelsDialog(QDialog):
    """Диалог для управления моделями."""
    
    def __init__(self, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.model_manager = model_manager
        self.setWindowTitle("Управление моделями")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_models()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить модель")
        self.add_button.clicked.connect(self.add_model)
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_model)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_model)
        self.toggle_button = QPushButton("Активировать/Деактивировать")
        self.toggle_button.clicked.connect(self.toggle_model)
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_models)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Таблица моделей
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "API URL", "API ID", "Тип", "Активна"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Кнопки закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_models(self):
        """Загрузить список моделей в таблицу."""
        models = self.model_manager.get_all_models()
        self.table.setRowCount(len(models))
        
        for row, model in enumerate(models):
            self.table.setItem(row, 0, QTableWidgetItem(str(model['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(model['name']))
            self.table.setItem(row, 2, QTableWidgetItem(model['api_url']))
            self.table.setItem(row, 3, QTableWidgetItem(model['api_id']))
            self.table.setItem(row, 4, QTableWidgetItem(model['model_type']))
            
            active_item = QTableWidgetItem("Да" if model['is_active'] == 1 else "Нет")
            active_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, active_item)
        
        self.table.resizeColumnsToContents()
    
    def get_selected_model_id(self) -> int:
        """Получить ID выбранной модели."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        return int(self.table.item(current_row, 0).text())
    
    def add_model(self):
        """Добавить новую модель."""
        dialog = ModelEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.model_manager.add_model(
                    dialog.name_edit.text(),
                    dialog.api_url_edit.text(),
                    dialog.api_id_edit.text(),
                    dialog.model_type_combo.currentText(),
                    1 if dialog.is_active_check.isChecked() else 0
                )
                self.load_models()
                QMessageBox.information(self, "Успех", "Модель успешно добавлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить модель:\n{str(e)}")
    
    def edit_model(self):
        """Редактировать выбранную модель."""
        model_id = self.get_selected_model_id()
        if not model_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для редактирования")
            return
        
        model = self.model_manager.get_model_by_id(model_id)
        if not model:
            QMessageBox.critical(self, "Ошибка", "Модель не найдена")
            return
        
        dialog = ModelEditDialog(self, model)
        if dialog.exec_() == QDialog.Accepted:
            try:
                updates = {}
                if dialog.name_edit.text() != model['name']:
                    updates['name'] = dialog.name_edit.text()
                if dialog.api_url_edit.text() != model['api_url']:
                    updates['api_url'] = dialog.api_url_edit.text()
                if dialog.api_id_edit.text() != model['api_id']:
                    updates['api_id'] = dialog.api_id_edit.text()
                if dialog.model_type_combo.currentText() != model['model_type']:
                    updates['model_type'] = dialog.model_type_combo.currentText()
                if (dialog.is_active_check.isChecked() and model['is_active'] == 0) or \
                   (not dialog.is_active_check.isChecked() and model['is_active'] == 1):
                    updates['is_active'] = 1 if dialog.is_active_check.isChecked() else 0
                
                if updates:
                    self.model_manager.update_model(model_id, **updates)
                    self.load_models()
                    QMessageBox.information(self, "Успех", "Модель успешно обновлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить модель:\n{str(e)}")
    
    def delete_model(self):
        """Удалить выбранную модель."""
        model_id = self.get_selected_model_id()
        if not model_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить эту модель?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.model_manager.delete_model(model_id)
                self.load_models()
                QMessageBox.information(self, "Успех", "Модель успешно удалена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить модель:\n{str(e)}")
    
    def toggle_model(self):
        """Переключить статус активности модели."""
        model_id = self.get_selected_model_id()
        if not model_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель")
            return
        
        try:
            self.model_manager.toggle_model_status(model_id)
            self.load_models()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус:\n{str(e)}")


class ModelEditDialog(QDialog):
    """Диалог для добавления/редактирования модели."""
    
    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Редактировать модель" if model else "Добавить модель")
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.api_url_edit = QLineEdit()
        self.api_id_edit = QLineEdit()
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(['openrouter', 'openai', 'deepseek', 'groq', 'universal'])
        self.is_active_check = QCheckBox()
        self.is_active_check.setChecked(True)
        
        layout.addRow("Название:", self.name_edit)
        layout.addRow("API URL:", self.api_url_edit)
        layout.addRow("API ID (переменная .env):", self.api_id_edit)
        layout.addRow("Тип модели:", self.model_type_combo)
        layout.addRow("Активна:", self.is_active_check)
        
        if self.model:
            self.name_edit.setText(self.model['name'])
            self.api_url_edit.setText(self.model['api_url'])
            self.api_id_edit.setText(self.model['api_id'])
            index = self.model_type_combo.findText(self.model['model_type'])
            if index >= 0:
                self.model_type_combo.setCurrentIndex(index)
            self.is_active_check.setChecked(self.model['is_active'] == 1)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)

