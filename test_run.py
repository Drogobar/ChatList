"""Тестовый скрипт для проверки запуска приложения."""
import sys
import traceback

try:
    print("Импорт модулей...")
    from PyQt5.QtWidgets import QApplication
    from db import Database
    from models import ModelManager
    from network import NetworkClient
    print("Все модули импортированы успешно")
    
    print("Инициализация БД...")
    db = Database()
    print("БД инициализирована")
    
    print("Инициализация менеджера моделей...")
    model_manager = ModelManager(db)
    print("Менеджер моделей инициализирован")
    
    print("Инициализация сетевого клиента...")
    network_client = NetworkClient()
    print("Сетевой клиент инициализирован")
    
    print("Создание QApplication...")
    app = QApplication(sys.argv)
    print("QApplication создан")
    
    print("Импорт MainWindow...")
    from main import MainWindow
    print("MainWindow импортирован")
    
    print("Создание главного окна...")
    window = MainWindow()
    print("Главное окно создано")
    
    print("Показ окна...")
    window.show()
    print("Окно показано. Приложение должно быть видно.")
    print("Нажмите Ctrl+C для выхода или закройте окно.")
    
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"ОШИБКА: {e}")
    traceback.print_exc()
    input("Нажмите Enter для выхода...")
    sys.exit(1)

