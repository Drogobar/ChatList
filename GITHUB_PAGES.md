# Инструкция по настройке GitHub Pages

## Способ 1: Автоматическая публикация через GitHub Actions (Рекомендуется)

### Шаг 1: Включение GitHub Pages

1. Перейдите в ваш репозиторий → Settings → Pages
2. В разделе "Source" выберите:
   - Source: `GitHub Actions`
3. Сохраните изменения

### Шаг 2: Workflow уже настроен

Файл `.github/workflows/pages.yml` уже создан. Он автоматически:
- Собирает HTML-лендинг из папки `docs/`
- Публикует его на GitHub Pages при каждом push в main

### Шаг 3: Проверка

1. Сделайте commit и push:
   ```powershell
   git add .
   git commit -m "Add GitHub Pages"
   git push origin main
   ```

2. Подождите 1-2 минуты

3. Проверьте Actions:
   - Перейдите в репозиторий → Actions
   - Должен быть запущен workflow "Deploy GitHub Pages"
   - Дождитесь завершения (зеленая галочка)

4. Откройте ваш сайт:
   - URL: `https://Drogobar.github.io/ChatList/`
   - Или: `https://ВАШ_ORGANIZATION.github.io/ChatList/`

## Способ 2: Ручная публикация через ветку gh-pages

### Шаг 1: Создание ветки gh-pages

```powershell
git checkout -b gh-pages
git rm -rf .
git checkout main -- docs/
git mv docs/* .
git commit -m "Initial GitHub Pages"
git push origin gh-pages
```

### Шаг 2: Настройка в GitHub

1. Перейдите в Settings → Pages
2. Source: выберите `Deploy from a branch`
3. Branch: выберите `gh-pages` и папку `/ (root)`
4. Сохраните

### Шаг 3: Обновление сайта

При каждом обновлении:

```powershell
git checkout gh-pages
git checkout main -- docs/
git mv docs/* .
git add .
git commit -m "Update GitHub Pages"
git push origin gh-pages
git checkout main
```

## Настройка домена (опционально)

Если у вас есть собственный домен:

1. Создайте файл `CNAME` в корне репозитория (или в папке docs/):
   ```
   yourdomain.com
   ```

2. Настройте DNS записи у вашего регистратора:
   - Тип: `CNAME`
   - Имя: `www` (или `@`)
   - Значение: `Drogobar.github.io`

3. В GitHub → Settings → Pages добавьте домен

## Структура файлов

```
docs/
  ├── index.html          # Главная страница
  ├── assets/
  │   ├── css/
  │   │   └── style.css   # Стили
  │   └── images/         # Изображения
  └── README.md           # Описание (опционально)
```

## Обновление контента

1. Отредактируйте файлы в папке `docs/`
2. Сделайте commit и push:
   ```powershell
   git add docs/
   git commit -m "Update landing page"
   git push origin main
   ```
3. GitHub Actions автоматически обновит сайт

## Проверка локально

Для проверки сайта локально:

```powershell
# Установите простой HTTP сервер (если еще не установлен)
python -m http.server 8000

# Откройте в браузере
# http://localhost:8000/docs/
```

## Troubleshooting

### Сайт не обновляется

1. Проверьте Actions → должен быть успешный workflow
2. Подождите 1-2 минуты (кеширование)
3. Очистите кеш браузера (Ctrl+F5)

### 404 ошибка

1. Убедитесь, что файл `index.html` находится в папке `docs/`
2. Проверьте настройки Pages → Source должен быть `GitHub Actions`

### Стили не загружаются

1. Проверьте пути к CSS файлам (должны быть относительные)
2. Убедитесь, что файлы находятся в правильных папках
