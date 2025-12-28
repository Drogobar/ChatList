"""
Скрипт для обновления названий моделей в базе данных.
"""

from db import Database
from models import ModelManager

# Список моделей для обновления
MODELS_TO_UPDATE = [
    "xiaomi/mimo-v2-flash",
    "nvidia/nemotron-3-nano-30b-a3b",
    "mistralai/devstral-2512",
    "nex-agi/deepseek-v3.1-nex-n1",
    "kwaipilot/kat-coder-pro",
    "tngtech/deepseek-r1t2-chimera"
]

# Новые названия с :free
NEW_NAMES = {
    "xiaomi/mimo-v2-flash": "xiaomi/mimo-v2-flash:free",
    "nvidia/nemotron-3-nano-30b-a3b": "nvidia/nemotron-3-nano-30b-a3b:free",
    "mistralai/devstral-2512": "mistralai/devstral-2512:free",
    "nex-agi/deepseek-v3.1-nex-n1": "nex-agi/deepseek-v3.1-nex-n1:free",
    "kwaipilot/kat-coder-pro": "kwaipilot/kat-coder-pro:free",
    "tngtech/deepseek-r1t2-chimera": "tngtech/deepseek-r1t2-chimera:free"
}


def update_models():
    """Обновить названия моделей в базе данных."""
    db = Database()
    model_manager = ModelManager(db)
    
    updated_count = 0
    not_found_count = 0
    error_count = 0
    
    print("Обновление названий моделей в базе данных...\n")
    
    # Получаем все модели
    all_models = model_manager.get_all_models()
    
    for old_name, new_name in NEW_NAMES.items():
        try:
            # Ищем модель по старому названию
            model = next((m for m in all_models if m['name'] == old_name), None)
            
            if model:
                # Обновляем название
                model_manager.update_model(model['id'], name=new_name)
                print(f"[+] Модель '{old_name}' обновлена на '{new_name}' (ID: {model['id']})")
                updated_count += 1
            else:
                print(f"[!] Модель '{old_name}' не найдена в базе данных")
                not_found_count += 1
        except Exception as e:
            print(f"[-] Ошибка при обновлении модели '{old_name}': {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"Итого:")
    print(f"  Обновлено: {updated_count}")
    print(f"  Не найдено: {not_found_count}")
    print(f"  Ошибок: {error_count}")
    print(f"{'='*50}")
    
    # Показываем список всех активных моделей
    print("\nАктивные модели в базе данных:")
    active_models = model_manager.get_active_models()
    if active_models:
        for model in active_models:
            print(f"  - {model['name']} ({model['model_type']})")
    else:
        print("  Нет активных моделей")
    
    db.close()


if __name__ == "__main__":
    try:
        update_models()
    except KeyboardInterrupt:
        print("\n\nОперация прервана пользователем")
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()

