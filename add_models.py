"""
Скрипт для добавления языковых моделей в базу данных.
"""

from db import Database
from models import ModelManager

# Список моделей для добавления
MODELS_TO_ADD = [
    {
        "name": "xiaomi/mimo-v2-flash",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "nvidia/nemotron-3-nano-30b-a3b",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "mistralai/devstral-2512",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "nex-agi/deepseek-v3.1-nex-n1",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "kwaipilot/kat-coder-pro",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "tngtech/deepseek-r1t2-chimera",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    }
]


def add_models():
    """Добавить модели в базу данных."""
    db = Database()
    model_manager = ModelManager(db)
    
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    print("Добавление моделей в базу данных...\n")
    
    for model_data in MODELS_TO_ADD:
        try:
            # Проверяем, существует ли модель с таким именем
            existing_models = model_manager.get_all_models()
            model_exists = any(m['name'] == model_data['name'] for m in existing_models)
            
            if model_exists:
                print(f"[!] Модель '{model_data['name']}' уже существует, пропускаем")
                skipped_count += 1
            else:
                model_id = model_manager.add_model(
                    name=model_data['name'],
                    api_url=model_data['api_url'],
                    api_id=model_data['api_id'],
                    model_type=model_data['model_type'],
                    is_active=model_data['is_active']
                )
                print(f"[+] Модель '{model_data['name']}' успешно добавлена (ID: {model_id})")
                added_count += 1
        except Exception as e:
            print(f"[-] Ошибка при добавлении модели '{model_data['name']}': {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"Итого:")
    print(f"  Добавлено: {added_count}")
    print(f"  Пропущено: {skipped_count}")
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
        add_models()
    except KeyboardInterrupt:
        print("\n\nОперация прервана пользователем")
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()

