"""
Диалог настроек приложения.
Позволяет выбрать тему и размер шрифта.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QGroupBox, QFormLayout, QDialogButtonBox,
    QMessageBox
)
from PyQt5.QtCore import Qt
from db import Database


class SettingsDialog(QDialog):
    """Диалог настроек приложения."""
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Настройки")
        self.setMinimumSize(400, 300)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Группа настроек темы
        theme_group = QGroupBox("Тема оформления")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Светлая", "light")
        self.theme_combo.addItem("Темная", "dark")
        self.theme_combo.addItem("Системная", "system")
        theme_layout.addRow("Тема:", self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Группа настроек шрифта
        font_group = QGroupBox("Размер шрифта")
        font_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setSuffix(" pt")
        font_layout.addRow("Размер шрифта панелей:", self.font_size_spin)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        layout.addWidget(button_box)
    
    def load_settings(self):
        """Загрузить настройки из БД."""
        # Загружаем тему
        theme = self.db.get_setting('theme', 'system')
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        else:
            self.theme_combo.setCurrentIndex(2)  # Системная по умолчанию
        
        # Загружаем размер шрифта
        font_size_str = self.db.get_setting('font_size', '10')
        try:
            font_size = int(font_size_str)
            self.font_size_spin.setValue(font_size)
        except (ValueError, TypeError):
            self.font_size_spin.setValue(10)  # По умолчанию 10
    
    def restore_defaults(self):
        """Восстановить настройки по умолчанию."""
        self.theme_combo.setCurrentIndex(2)  # Системная тема
        self.font_size_spin.setValue(10)  # Размер шрифта 10
    
    def get_settings(self) -> dict:
        """Получить текущие настройки."""
        return {
            'theme': self.theme_combo.currentData(),
            'font_size': self.font_size_spin.value()
        }
    
    def accept(self):
        """Сохранить настройки."""
        settings = self.get_settings()
        
        try:
            # Сохраняем настройки в БД
            self.db.save_setting('theme', settings['theme'])
            self.db.save_setting('font_size', str(settings['font_size']))
            
            QMessageBox.information(
                self, "Успех",
                "Настройки сохранены.\n"
                "Для применения изменений перезапустите приложение."
            )
            
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки:\n{str(e)}")

