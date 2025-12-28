"""
Главный модуль приложения ChatList.
Реализует пользовательский интерфейс для отправки промтов в нейросети.
"""

import sys
import json
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QCheckBox, QMessageBox, QFileDialog, QMenuBar, QMenu,
    QStatusBar, QHeaderView, QProgressBar, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from db import Database
from models import ModelManager
from network import NetworkClient, APIError
from ui_models_dialog import ModelsDialog
from ui_prompts_dialog import PromptsDialog
from ui_results_dialog import ResultsDialog


class RequestThread(QThread):
    """Поток для выполнения запросов к API без блокировки UI."""
    
    finished = pyqtSignal(int, dict)  # model_id, result
    error = pyqtSignal(int, str)  # model_id, error_message
    all_finished = pyqtSignal()
    
    def __init__(self, model_info: Dict, prompt: str, network_client: NetworkClient):
        super().__init__()
        self.model_info = model_info
        self.prompt = prompt
        self.network_client = network_client
    
    def run(self):
        """Выполнить запрос к API."""
        try:
            result = self.network_client.send_request(self.model_info, self.prompt)
            self.finished.emit(self.model_info['id'], result)
        except APIError as e:
            self.error.emit(self.model_info['id'], str(e))
        except Exception as e:
            self.error.emit(self.model_info['id'], f"Неожиданная ошибка: {str(e)}")


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.model_manager = ModelManager(self.db)
        self.network_client = NetworkClient()
        
        # Временная таблица результатов (в памяти)
        self.temp_results: List[Dict] = []
        self.request_threads: List[RequestThread] = []
        self.pending_requests = 0
        
        self.init_ui()
        self.load_saved_prompts()
        self.load_active_models()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("ChatList - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем меню
        self.create_menu()
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Разделитель для разделения на области
        splitter = QSplitter(Qt.Vertical)
        
        # Верхняя область: ввод промта
        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_widget.setLayout(top_layout)
        
        # Выбор сохранённого промта
        prompt_select_layout = QHBoxLayout()
        prompt_select_layout.addWidget(QLabel("Выбрать сохранённый промт:"))
        self.prompt_combo = QComboBox()
        self.prompt_combo.currentTextChanged.connect(self.on_prompt_selected)
        prompt_select_layout.addWidget(self.prompt_combo)
        prompt_select_layout.addStretch()
        top_layout.addLayout(prompt_select_layout)
        
        # Ввод нового промта
        top_layout.addWidget(QLabel("Или введите новый промт:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Введите ваш запрос здесь...")
        self.prompt_input.setMaximumHeight(150)
        top_layout.addWidget(self.prompt_input)
        
        # Кнопки управления промтом
        prompt_buttons_layout = QHBoxLayout()
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_requests)
        self.save_prompt_button = QPushButton("Сохранить промт")
        self.save_prompt_button.clicked.connect(self.save_prompt)
        prompt_buttons_layout.addWidget(self.send_button)
        prompt_buttons_layout.addWidget(self.save_prompt_button)
        prompt_buttons_layout.addStretch()
        top_layout.addLayout(prompt_buttons_layout)
        
        splitter.addWidget(top_widget)
        
        # Средняя область: выбор моделей
        models_widget = QWidget()
        models_layout = QVBoxLayout()
        models_widget.setLayout(models_layout)
        
        models_header_layout = QHBoxLayout()
        models_header_layout.addWidget(QLabel("Активные модели:"))
        self.manage_models_button = QPushButton("Настроить модели")
        self.manage_models_button.clicked.connect(self.manage_models)
        models_header_layout.addWidget(self.manage_models_button)
        models_header_layout.addStretch()
        models_layout.addLayout(models_header_layout)
        
        # Список моделей с чекбоксами
        self.models_list_widget = QWidget()
        self.models_list_layout = QVBoxLayout()
        self.models_list_widget.setLayout(self.models_list_layout)
        models_layout.addWidget(self.models_list_widget)
        
        splitter.addWidget(models_widget)
        
        # Нижняя область: результаты
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_widget.setLayout(results_layout)
        
        results_header_layout = QHBoxLayout()
        results_header_layout.addWidget(QLabel("Результаты:"))
        self.save_results_button = QPushButton("Сохранить выбранные")
        self.save_results_button.clicked.connect(self.save_selected_results)
        self.clear_results_button = QPushButton("Очистить")
        self.clear_results_button.clicked.connect(self.clear_results)
        results_header_layout.addWidget(self.save_results_button)
        results_header_layout.addWidget(self.clear_results_button)
        results_header_layout.addStretch()
        results_layout.addLayout(results_header_layout)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Модель", "Ответ", "Выбрать"])
        self.results_table.horizontalHeader().setStretchLastSection(False)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)
        
        splitter.addWidget(results_widget)
        
        # Устанавливаем пропорции разделителя
        splitter.setSizes([200, 150, 450])
        
        main_layout.addWidget(splitter)
        
        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_bar.showMessage("Готово")
    
    def create_menu(self):
        """Создать меню приложения."""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        export_md_action = file_menu.addAction("Экспорт в Markdown...")
        export_md_action.triggered.connect(lambda: self.export_results('markdown'))
        
        export_json_action = file_menu.addAction("Экспорт в JSON...")
        export_json_action.triggered.connect(lambda: self.export_results('json'))
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)
        
        # Меню Управление
        manage_menu = menubar.addMenu("Управление")
        
        models_action = manage_menu.addAction("Модели...")
        models_action.triggered.connect(self.manage_models)
        
        prompts_action = manage_menu.addAction("Промты...")
        prompts_action.triggered.connect(self.manage_prompts)
        
        results_action = manage_menu.addAction("Сохранённые результаты...")
        results_action.triggered.connect(self.view_saved_results)
        
        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)
    
    def load_saved_prompts(self):
        """Загрузить сохранённые промты в выпадающий список."""
        self.prompt_combo.clear()
        self.prompt_combo.addItem("-- Новый промт --")
        
        prompts = self.db.get_prompts(limit=50)
        for prompt in prompts:
            preview = prompt['prompt'][:50] + "..." if len(prompt['prompt']) > 50 else prompt['prompt']
            self.prompt_combo.addItem(f"{prompt['id']}: {preview}", prompt['id'])
    
    def load_active_models(self):
        """Загрузить активные модели и создать чекбоксы."""
        # Очищаем предыдущие чекбоксы
        for i in reversed(range(self.models_list_layout.count())):
            self.models_list_layout.itemAt(i).widget().setParent(None)
        
        models = self.model_manager.get_active_models()
        self.model_checkboxes = {}
        
        if not models:
            label = QLabel("Нет активных моделей. Нажмите 'Настроить модели' для добавления.")
            self.models_list_layout.addWidget(label)
        else:
            for model in models:
                checkbox = QCheckBox(model['name'])
                checkbox.setChecked(True)
                checkbox.setData(model['id'])
                self.model_checkboxes[model['id']] = checkbox
                self.models_list_layout.addWidget(checkbox)
        
        self.models_list_layout.addStretch()
    
    def on_prompt_selected(self, text):
        """Обработчик выбора промта из списка."""
        if text == "-- Новый промт --":
            self.prompt_input.clear()
            return
        
        prompt_id = self.prompt_combo.currentData()
        if prompt_id:
            prompt = self.db.get_prompt_by_id(prompt_id)
            if prompt:
                self.prompt_input.setText(prompt['prompt'])
    
    def save_prompt(self):
        """Сохранить текущий промт в БД."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Промт не может быть пустым")
            return
        
        try:
            self.db.add_prompt(prompt_text)
            self.load_saved_prompts()
            QMessageBox.information(self, "Успех", "Промт сохранён")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промт:\n{str(e)}")
    
    def send_requests(self):
        """Отправить промт во все выбранные модели."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите промт")
            return
        
        # Получаем выбранные модели
        selected_models = []
        for model_id, checkbox in self.model_checkboxes.items():
            if checkbox.isChecked():
                model = self.model_manager.get_model_by_id(model_id)
                if model:
                    selected_models.append(model)
        
        if not selected_models:
            QMessageBox.warning(self, "Предупреждение", "Выберите хотя бы одну модель")
            return
        
        # Очищаем предыдущие результаты
        self.clear_results()
        
        # Сохраняем промт если его нет в БД
        prompt_id = self.prompt_combo.currentData()
        if not prompt_id:
            try:
                prompt_id = self.db.add_prompt(prompt_text)
                self.load_saved_prompts()
            except Exception as e:
                QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить промт:\n{str(e)}")
                prompt_id = None
        
        # Отправляем запросы
        self.pending_requests = len(selected_models)
        self.progress_bar.setMaximum(self.pending_requests)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.send_button.setEnabled(False)
        self.status_bar.showMessage(f"Отправка запросов... (0/{self.pending_requests})")
        
        self.request_threads = []
        for model in selected_models:
            thread = RequestThread(model, prompt_text, self.network_client)
            thread.finished.connect(self.on_request_finished)
            thread.error.connect(self.on_request_error)
            thread.all_finished.connect(self.on_all_requests_finished)
            self.request_threads.append(thread)
            thread.start()
    
    def on_request_finished(self, model_id: int, result: Dict):
        """Обработчик успешного завершения запроса."""
        model = self.model_manager.get_model_by_id(model_id)
        model_name = model['name'] if model else f"Модель {model_id}"
        
        # Добавляем результат во временную таблицу
        self.temp_results.append({
            'model_id': model_id,
            'model_name': model_name,
            'response': result['response'],
            'metadata': result.get('metadata', {}),
            'selected': True
        })
        
        self.update_results_table()
        self.pending_requests -= 1
        self.progress_bar.setValue(self.progress_bar.maximum() - self.pending_requests)
        self.status_bar.showMessage(
            f"Отправка запросов... ({self.progress_bar.maximum() - self.pending_requests}/{self.progress_bar.maximum()})"
        )
        
        if self.pending_requests == 0:
            self.on_all_requests_finished()
    
    def on_request_error(self, model_id: int, error_message: str):
        """Обработчик ошибки запроса."""
        model = self.model_manager.get_model_by_id(model_id)
        model_name = model['name'] if model else f"Модель {model_id}"
        
        # Добавляем ошибку во временную таблицу
        self.temp_results.append({
            'model_id': model_id,
            'model_name': model_name,
            'response': f"ОШИБКА: {error_message}",
            'metadata': {},
            'selected': False
        })
        
        self.update_results_table()
        self.pending_requests -= 1
        self.progress_bar.setValue(self.progress_bar.maximum() - self.pending_requests)
        self.status_bar.showMessage(
            f"Отправка запросов... ({self.progress_bar.maximum() - self.pending_requests}/{self.progress_bar.maximum()})"
        )
        
        if self.pending_requests == 0:
            self.on_all_requests_finished()
    
    def on_all_requests_finished(self):
        """Обработчик завершения всех запросов."""
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Готово. Получено ответов: {len(self.temp_results)}")
    
    def update_results_table(self):
        """Обновить таблицу результатов."""
        self.results_table.setRowCount(len(self.temp_results))
        
        for row, result in enumerate(self.temp_results):
            # Название модели
            self.results_table.setItem(row, 0, QTableWidgetItem(result['model_name']))
            
            # Текст ответа
            response_item = QTableWidgetItem(result['response'])
            response_item.setFlags(response_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 1, response_item)
            
            # Чекбокс выбора
            checkbox = QCheckBox()
            checkbox.setChecked(result.get('selected', True))
            checkbox.stateChanged.connect(
                lambda state, r=row: self.on_result_selection_changed(r, state == Qt.Checked)
            )
            self.results_table.setCellWidget(row, 2, checkbox)
    
    def on_result_selection_changed(self, row: int, selected: bool):
        """Обработчик изменения выбора результата."""
        if 0 <= row < len(self.temp_results):
            self.temp_results[row]['selected'] = selected
    
    def save_selected_results(self):
        """Сохранить выбранные результаты в БД."""
        if not self.temp_results:
            QMessageBox.warning(self, "Предупреждение", "Нет результатов для сохранения")
            return
        
        selected_results = [r for r in self.temp_results if r.get('selected', False)]
        if not selected_results:
            QMessageBox.warning(self, "Предупреждение", "Выберите результаты для сохранения")
            return
        
        # Получаем ID промта
        prompt_id = self.prompt_combo.currentData()
        if not prompt_id:
            prompt_text = self.prompt_input.toPlainText().strip()
            if prompt_text:
                try:
                    prompt_id = self.db.add_prompt(prompt_text)
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промт:\n{str(e)}")
                    return
        
        if not prompt_id:
            QMessageBox.warning(self, "Предупреждение", "Не удалось определить промт")
            return
        
        # Сохраняем результаты
        saved_count = 0
        for result in selected_results:
            try:
                self.db.save_result(
                    prompt_id,
                    result['model_id'],
                    result['response'],
                    result.get('metadata', {})
                )
                saved_count += 1
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить результат:\n{str(e)}")
        
        if saved_count > 0:
            QMessageBox.information(self, "Успех", f"Сохранено результатов: {saved_count}")
            # Удаляем сохранённые результаты из временной таблицы
            self.temp_results = [r for r in self.temp_results if not r.get('selected', False)]
            self.update_results_table()
    
    def clear_results(self):
        """Очистить временную таблицу результатов."""
        self.temp_results = []
        self.results_table.setRowCount(0)
        self.status_bar.showMessage("Результаты очищены")
    
    def manage_models(self):
        """Открыть окно управления моделями."""
        dialog = ModelsDialog(self.model_manager, self)
        dialog.exec_()
        self.load_active_models()
    
    def manage_prompts(self):
        """Открыть окно управления промтами."""
        dialog = PromptsDialog(self.db, self)
        dialog.exec_()
        self.load_saved_prompts()
    
    def view_saved_results(self):
        """Открыть окно просмотра сохранённых результатов."""
        dialog = ResultsDialog(self.db, self)
        dialog.exec_()
    
    def export_results(self, format_type: str):
        """Экспортировать результаты в файл."""
        if not self.temp_results:
            QMessageBox.warning(self, "Предупреждение", "Нет результатов для экспорта")
            return
        
        selected_results = [r for r in self.temp_results if r.get('selected', False)]
        if not selected_results:
            selected_results = self.temp_results
        
        if format_type == 'markdown':
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как Markdown", "", "Markdown Files (*.md)"
            )
            if filename:
                self.export_to_markdown(filename, selected_results)
        elif format_type == 'json':
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как JSON", "", "JSON Files (*.json)"
            )
            if filename:
                self.export_to_json(filename, selected_results)
    
    def export_to_markdown(self, filename: str, results: List[Dict]):
        """Экспортировать результаты в Markdown."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Результаты сравнения нейросетей\n\n")
                
                prompt_text = self.prompt_input.toPlainText().strip()
                if prompt_text:
                    f.write(f"## Промт\n\n{prompt_text}\n\n")
                
                f.write("## Ответы\n\n")
                for i, result in enumerate(results, 1):
                    f.write(f"### {i}. {result['model_name']}\n\n")
                    f.write(f"{result['response']}\n\n")
                    if result.get('metadata'):
                        f.write("**Метаданные:**\n")
                        for key, value in result['metadata'].items():
                            f.write(f"- {key}: {value}\n")
                        f.write("\n")
            
            QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{str(e)}")
    
    def export_to_json(self, filename: str, results: List[Dict]):
        """Экспортировать результаты в JSON."""
        try:
            data = {
                'prompt': self.prompt_input.toPlainText().strip(),
                'results': results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{str(e)}")
    
    def show_about(self):
        """Показать информацию о программе."""
        QMessageBox.about(
            self, "О программе ChatList",
            "ChatList - Приложение для сравнения ответов нейросетей\n\n"
            "Позволяет отправлять один промт в несколько нейросетей\n"
            "и сравнивать их ответы.\n\n"
            "Версия 1.0"
        )
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        # Останавливаем все потоки
        for thread in self.request_threads:
            if thread.isRunning():
                thread.terminate()
                thread.wait()
        
        # Закрываем БД
        self.db.close()
        event.accept()


def main():
    """Главная функция приложения."""
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        print(f"Ошибка при запуске приложения: {e}")
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
        sys.exit(1)


if __name__ == "__main__":
    main()
