"""
Тестовая программа для работы с SQLite базами данных.
Позволяет просматривать таблицы, данные с пагинацией и выполнять CRUD операции.
"""

import sys
import sqlite3
from typing import List, Dict, Optional, Any
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QDialog, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QHeaderView, QAbstractItemView, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class DatabaseViewer:
    """Класс для работы с SQLite базой данных."""
    
    def __init__(self, db_path: str):
        """
        Инициализация подключения к базе данных.
        
        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Установка подключения к базе данных."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")
    
    def get_tables(self) -> List[str]:
        """Получить список всех таблиц в базе данных."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        return [row[0] for row in cursor.fetchall()]
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """Получить информацию о колонках таблицы."""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': row[3],
                'default_value': row[4],
                'pk': row[5]
            })
        return columns
    
    def get_table_data(self, table_name: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получить данные из таблицы с пагинацией."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_table_count(self, table_name: str) -> int:
        """Получить общее количество записей в таблице."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]
    
    def insert_row(self, table_name: str, data: Dict) -> int:
        """Вставить новую строку в таблицу."""
        cursor = self.conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())
        cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
        self.conn.commit()
        return cursor.lastrowid
    
    def update_row(self, table_name: str, row_id: int, primary_key: str, data: Dict):
        """Обновить строку в таблице."""
        cursor = self.conn.cursor()
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + [row_id]
        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?", values)
        self.conn.commit()
    
    def delete_row(self, table_name: str, primary_key: str, row_id: int):
        """Удалить строку из таблицы."""
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE {primary_key} = ?", (row_id,))
        self.conn.commit()
    
    def close(self):
        """Закрыть подключение к базе данных."""
        if self.conn:
            self.conn.close()


class EditRowDialog(QDialog):
    """Диалог для редактирования/создания строки."""
    
    def __init__(self, table_name: str, columns: List[Dict], row_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.row_data = row_data
        self.fields = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        title = f"Редактировать запись" if self.row_data else f"Создать запись"
        self.setWindowTitle(f"{title} - {self.table_name}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        form_layout = QFormLayout()
        
        for col in self.columns:
            label = QLabel(col['name'])
            if col['pk']:
                label.setText(f"{col['name']} (PK)")
            
            if col['type'].upper() in ('TEXT', 'VARCHAR', 'CHAR'):
                field = QTextEdit()
                field.setMaximumHeight(100)
                if self.row_data and col['name'] in self.row_data:
                    field.setPlainText(str(self.row_data[col['name']]))
            else:
                field = QLineEdit()
                if self.row_data and col['name'] in self.row_data:
                    field.setText(str(self.row_data[col['name']]))
                elif col['default_value'] is not None:
                    field.setText(str(col['default_value']))
            
            if col['pk'] and self.row_data:
                field.setReadOnly(True)
            
            self.fields[col['name']] = field
            form_layout.addRow(label, field)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_data(self) -> Dict:
        """Получить данные из формы."""
        data = {}
        for col_name, field in self.fields.items():
            if isinstance(field, QTextEdit):
                value = field.toPlainText()
            else:
                value = field.text()
            
            if value:
                data[col_name] = value
        return data


class TableViewWindow(QMainWindow):
    """Окно для просмотра и редактирования таблицы."""
    
    def __init__(self, db_viewer: DatabaseViewer, table_name: str, parent=None):
        super().__init__(parent)
        self.db_viewer = db_viewer
        self.table_name = table_name
        self.columns = db_viewer.get_table_info(table_name)
        self.primary_key = next((col['name'] for col in self.columns if col['pk']), None)
        self.current_page = 0
        self.rows_per_page = 50
        self.total_rows = 0
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle(f"Таблица: {self.table_name}")
        self.setGeometry(100, 100, 1200, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Панель управления
        control_panel = QHBoxLayout()
        
        # Кнопки CRUD
        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.create_row)
        control_panel.addWidget(self.create_button)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_row)
        control_panel.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_row)
        control_panel.addWidget(self.delete_button)
        
        control_panel.addStretch()
        
        # Информация о записях
        self.info_label = QLabel()
        control_panel.addWidget(self.info_label)
        
        layout.addLayout(control_panel)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Панель пагинации
        pagination_panel = QHBoxLayout()
        
        pagination_panel.addWidget(QLabel("Записей на странице:"))
        self.rows_per_page_spin = QSpinBox()
        self.rows_per_page_spin.setMinimum(10)
        self.rows_per_page_spin.setMaximum(1000)
        self.rows_per_page_spin.setValue(self.rows_per_page)
        self.rows_per_page_spin.valueChanged.connect(self.on_rows_per_page_changed)
        pagination_panel.addWidget(self.rows_per_page_spin)
        
        pagination_panel.addStretch()
        
        self.first_button = QPushButton("<<")
        self.first_button.clicked.connect(self.go_to_first_page)
        pagination_panel.addWidget(self.first_button)
        
        self.prev_button = QPushButton("<")
        self.prev_button.clicked.connect(self.go_to_prev_page)
        pagination_panel.addWidget(self.prev_button)
        
        self.page_label = QLabel()
        pagination_panel.addWidget(self.page_label)
        
        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(self.go_to_next_page)
        pagination_panel.addWidget(self.next_button)
        
        self.last_button = QPushButton(">>")
        self.last_button.clicked.connect(self.go_to_last_page)
        pagination_panel.addWidget(self.last_button)
        
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_data)
        pagination_panel.addWidget(self.refresh_button)
        
        layout.addLayout(pagination_panel)
    
    def load_data(self):
        """Загрузить данные в таблицу."""
        try:
            self.total_rows = self.db_viewer.get_table_count(self.table_name)
            offset = self.current_page * self.rows_per_page
            
            data = self.db_viewer.get_table_data(self.table_name, self.rows_per_page, offset)
            
            # Настройка таблицы
            self.table.setColumnCount(len(self.columns))
            self.table.setHorizontalHeaderLabels([col['name'] for col in self.columns])
            self.table.setRowCount(len(data))
            
            # Заполнение данными
            for row_idx, row_data in enumerate(data):
                for col_idx, col in enumerate(self.columns):
                    value = row_data.get(col['name'], '')
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    self.table.setItem(row_idx, col_idx, item)
            
            # Обновление информации о пагинации
            self.update_pagination_info()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def update_pagination_info(self):
        """Обновить информацию о пагинации."""
        total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page if self.total_rows > 0 else 1
        current_page_display = self.current_page + 1 if self.total_rows > 0 else 0
        
        self.page_label.setText(f"Страница {current_page_display} из {total_pages} (Всего записей: {self.total_rows})")
        
        self.first_button.setEnabled(self.current_page > 0)
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        self.last_button.setEnabled(self.current_page < total_pages - 1)
    
    def on_rows_per_page_changed(self, value: int):
        """Обработчик изменения количества строк на странице."""
        self.rows_per_page = value
        self.current_page = 0
        self.load_data()
    
    def go_to_first_page(self):
        """Перейти на первую страницу."""
        self.current_page = 0
        self.load_data()
    
    def go_to_prev_page(self):
        """Перейти на предыдущую страницу."""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()
    
    def go_to_next_page(self):
        """Перейти на следующую страницу."""
        total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page if self.total_rows > 0 else 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_data()
    
    def go_to_last_page(self):
        """Перейти на последнюю страницу."""
        total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page if self.total_rows > 0 else 1
        if total_pages > 0:
            self.current_page = total_pages - 1
            self.load_data()
    
    def get_selected_row_id(self) -> Optional[int]:
        """Получить ID выбранной строки."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if not self.primary_key:
            QMessageBox.warning(self, "Предупреждение", "Таблица не имеет первичного ключа")
            return None
        
        item = self.table.item(current_row, next(i for i, col in enumerate(self.columns) if col['name'] == self.primary_key))
        if item:
            try:
                return int(item.text())
            except ValueError:
                return None
        return None
    
    def get_selected_row_data(self) -> Optional[Dict]:
        """Получить данные выбранной строки."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        row_data = {}
        for col_idx, col in enumerate(self.columns):
            item = self.table.item(current_row, col_idx)
            if item:
                row_data[col['name']] = item.text()
        
        return row_data
    
    def create_row(self):
        """Создать новую строку."""
        dialog = EditRowDialog(self.table_name, self.columns, None, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                try:
                    self.db_viewer.insert_row(self.table_name, data)
                    QMessageBox.information(self, "Успех", "Запись создана")
                    self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось создать запись:\n{str(e)}")
    
    def edit_row(self):
        """Редактировать выбранную строку."""
        row_id = self.get_selected_row_id()
        if row_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите строку для редактирования")
            return
        
        row_data = self.get_selected_row_data()
        if not row_data:
            QMessageBox.warning(self, "Предупреждение", "Не удалось получить данные строки")
            return
        
        dialog = EditRowDialog(self.table_name, self.columns, row_data, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                try:
                    # Удаляем первичный ключ из данных для обновления
                    update_data = {k: v for k, v in data.items() if k != self.primary_key}
                    if update_data:
                        self.db_viewer.update_row(self.table_name, row_id, self.primary_key, update_data)
                        QMessageBox.information(self, "Успех", "Запись обновлена")
                        self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись:\n{str(e)}")
    
    def delete_row(self):
        """Удалить выбранную строку."""
        row_id = self.get_selected_row_id()
        if row_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите строку для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить запись с ID {row_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_viewer.delete_row(self.table_name, self.primary_key, row_id)
                QMessageBox.information(self, "Успех", "Запись удалена")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись:\n{str(e)}")


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        self.db_viewer: Optional[DatabaseViewer] = None
        self.table_windows = []
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("Просмотр SQLite базы данных")
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Кнопка выбора файла
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Файл не выбран")
        file_layout.addWidget(self.file_label)
        
        self.select_file_button = QPushButton("Выбрать файл SQLite")
        self.select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.select_file_button)
        
        layout.addLayout(file_layout)
        
        # Список таблиц
        layout.addWidget(QLabel("Таблицы в базе данных:"))
        
        self.tables_list = QTableWidget()
        self.tables_list.setColumnCount(2)
        self.tables_list.setHorizontalHeaderLabels(["Таблица", "Действие"])
        self.tables_list.horizontalHeader().setStretchLastSection(True)
        self.tables_list.setAlternatingRowColors(True)
        self.tables_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tables_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.tables_list)
    
    def select_file(self):
        """Выбрать файл базы данных."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выбрать файл SQLite", "", "SQLite Files (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if filename:
            try:
                if self.db_viewer:
                    self.db_viewer.close()
                
                self.db_viewer = DatabaseViewer(filename)
                self.file_label.setText(f"Файл: {filename}")
                self.load_tables()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть базу данных:\n{str(e)}")
                self.file_label.setText("Файл не выбран")
                self.db_viewer = None
    
    def load_tables(self):
        """Загрузить список таблиц."""
        if not self.db_viewer:
            return
        
        try:
            tables = self.db_viewer.get_tables()
            self.tables_list.setRowCount(len(tables))
            
            for row, table_name in enumerate(tables):
                # Название таблицы
                self.tables_list.setItem(row, 0, QTableWidgetItem(table_name))
                
                # Кнопка "Открыть"
                open_button = QPushButton("Открыть")
                open_button.clicked.connect(
                    lambda checked, name=table_name: self.open_table(name)
                )
                self.tables_list.setCellWidget(row, 1, open_button)
            
            self.tables_list.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список таблиц:\n{str(e)}")
    
    def open_table(self, table_name: str):
        """Открыть окно просмотра таблицы."""
        if not self.db_viewer:
            return
        
        window = TableViewWindow(self.db_viewer, table_name, self)
        window.show()
        self.table_windows.append(window)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        if self.db_viewer:
            self.db_viewer.close()
        event.accept()


def main():
    """Главная функция приложения."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

