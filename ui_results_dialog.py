"""
Окно для просмотра сохранённых результатов.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QLineEdit, QLabel, QTextEdit,
                             QDialogButtonBox, QSplitter)
from PyQt5.QtCore import Qt
from db import Database


class ResultsDialog(QDialog):
    """Диалог для просмотра сохранённых результатов."""
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Сохранённые результаты")
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.load_results()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        
        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search_results)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_results)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_result)
        self.view_button = QPushButton("Просмотр")
        self.view_button.clicked.connect(self.view_result)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.view_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Разделитель для таблицы и детального просмотра
        splitter = QSplitter(Qt.Horizontal)
        
        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Промт", "Модель", "Дата сохранения", "Ответ (превью)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        splitter.addWidget(self.table)
        
        # Область детального просмотра
        from PyQt5.QtWidgets import QWidget
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        detail_widget.setLayout(detail_layout)
        
        detail_layout.addWidget(QLabel("Детали результата:"))
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        
        splitter.addWidget(detail_widget)
        
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        # Кнопки закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_results(self):
        """Загрузить список результатов в таблицу."""
        results = self.db.get_results()
        self.table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(result['id'])))
            
            prompt_text = result.get('prompt', '')[:50] + "..." if len(result.get('prompt', '')) > 50 else result.get('prompt', '')
            self.table.setItem(row, 1, QTableWidgetItem(prompt_text))
            
            model_name = result.get('model_name', 'Неизвестно')
            self.table.setItem(row, 2, QTableWidgetItem(model_name))
            
            self.table.setItem(row, 3, QTableWidgetItem(result.get('saved_at', '')))
            
            response_preview = result.get('response', '')[:100] + "..." if len(result.get('response', '')) > 100 else result.get('response', '')
            self.table.setItem(row, 4, QTableWidgetItem(response_preview))
        
        self.table.resizeColumnsToContents()
    
    def search_results(self, query: str):
        """Поиск результатов."""
        if not query.strip():
            self.load_results()
            return
        
        results = self.db.search_results(query)
        self.table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(result['id'])))
            
            prompt_text = result.get('prompt', '')[:50] + "..." if len(result.get('prompt', '')) > 50 else result.get('prompt', '')
            self.table.setItem(row, 1, QTableWidgetItem(prompt_text))
            
            model_name = result.get('model_name', 'Неизвестно')
            self.table.setItem(row, 2, QTableWidgetItem(model_name))
            
            self.table.setItem(row, 3, QTableWidgetItem(result.get('saved_at', '')))
            
            response_preview = result.get('response', '')[:100] + "..." if len(result.get('response', '')) > 100 else result.get('response', '')
            self.table.setItem(row, 4, QTableWidgetItem(response_preview))
        
        self.table.resizeColumnsToContents()
    
    def on_selection_changed(self):
        """Обработчик изменения выбора в таблице."""
        result_id = self.get_selected_result_id()
        if result_id:
            # Получаем все результаты и находим нужный
            results = self.db.get_results()
            selected_result = next((r for r in results if r['id'] == result_id), None)
            if selected_result:
                detail_text = f"ID: {selected_result['id']}\n"
                detail_text += f"Промт: {selected_result.get('prompt', '')}\n\n"
                detail_text += f"Модель: {selected_result.get('model_name', 'Неизвестно')}\n"
                detail_text += f"Дата сохранения: {selected_result.get('saved_at', '')}\n\n"
                detail_text += f"Ответ:\n{selected_result.get('response', '')}\n\n"
                
                if selected_result.get('metadata'):
                    detail_text += "Метаданные:\n"
                    metadata = selected_result['metadata']
                    if isinstance(metadata, dict):
                        for key, value in metadata.items():
                            detail_text += f"  {key}: {value}\n"
                
                self.detail_text.setText(detail_text)
    
    def get_selected_result_id(self) -> int:
        """Получить ID выбранного результата."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        return int(self.table.item(current_row, 0).text())
    
    def view_result(self):
        """Просмотр выбранного результата."""
        result_id = self.get_selected_result_id()
        if not result_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите результат для просмотра")
            return
        
        # Детали уже отображаются в правой панели
        self.on_selection_changed()
    
    def delete_result(self):
        """Удалить выбранный результат."""
        result_id = self.get_selected_result_id()
        if not result_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите результат для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить этот результат?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_result(result_id)
                self.load_results()
                self.detail_text.clear()
                QMessageBox.information(self, "Успех", "Результат успешно удалён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить результат:\n{str(e)}")

