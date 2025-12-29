"""Проверка списка моделей в базе данных."""
from db import Database
from models import ModelManager

db = Database()
mm = ModelManager(db)

models = mm.get_active_models()
print(f"Всего активных моделей: {len(models)}\n")
for m in models:
    print(f"  - {m['name']} ({m['model_type']})")

db.close()


