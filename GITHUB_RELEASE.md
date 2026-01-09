# Инструкция по публикации на GitHub Release

## Подготовка

### 1. Создание репозитория на GitHub

1. Перейдите на https://github.com/new
2. Создайте новый репозиторий с именем `ChatList`
3. Выберите публичный или приватный репозиторий
4. **НЕ** добавляйте README, .gitignore или лицензию (они уже есть в проекте)

### 2. Инициализация Git (если еще не сделано)

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Drogobar/ChatList.git
git push -u origin main
```

## Автоматическая публикация через GitHub Actions

### Шаг 1: Создание токена доступа

1. Перейдите в GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Нажмите "Generate new token (classic)"
3. Выберите права:
   - `repo` (полный доступ к репозиториям)
   - `workflow` (обновление GitHub Actions workflows)
4. Скопируйте токен (он показывается только один раз!)

### Шаг 2: Добавление секрета в репозиторий

1. Перейдите в ваш репозиторий → Settings → Secrets and variables → Actions
2. Нажмите "New repository secret"
3. Имя: `GITHUB_TOKEN`
4. Значение: вставьте токен из шага 1
5. Нажмите "Add secret"

### Шаг 3: Настройка workflow

Файл `.github/workflows/release.yml` уже создан и настроен. Он автоматически:
- Собирает приложение при создании тега версии
- Создает установщик через Inno Setup
- Публикует релиз на GitHub Release

### Шаг 4: Создание релиза

#### Вариант A: Через GitHub веб-интерфейс

1. Перейдите в ваш репозиторий → Releases → "Create a new release"
2. Выберите "Choose a tag" → "Create new tag"
3. Введите версию: `v1.0.0`
4. Заголовок: `ChatList v1.0.0`
5. Описание (можно использовать шаблон из `RELEASE_NOTES_TEMPLATE.md`):
   ```markdown
   ## Что нового в v1.0.0
   
   - Первый релиз ChatList
   - Поддержка отправки промтов в несколько нейросетей
   - AI-ассистент для улучшения промтов
   - Настройки темы и размера шрифта
   ```
6. Нажмите "Publish release"
7. GitHub Actions автоматически соберет и прикрепит файлы

#### Вариант B: Через Git команды

```powershell
# Обновите версию в version.py если нужно
# Создайте тег
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Затем создайте релиз через веб-интерфейс GitHub
```

## Ручная публикация (без GitHub Actions)

Если вы хотите опубликовать релиз вручную:

1. Соберите приложение:
   ```powershell
   .\build.bat
   ```

2. Создайте установщик:
   ```powershell
   .\build_installer.ps1
   ```

3. Перейдите в GitHub → Releases → "Draft a new release"

4. Заполните информацию:
   - Tag: `v1.0.0`
   - Title: `ChatList v1.0.0`
   - Description: используйте шаблон из `RELEASE_NOTES_TEMPLATE.md`

5. Прикрепите файлы:
   - `dist\ChatList-1.0.0.exe` (портативная версия)
   - `installer\ChatList-Setup-1.0.0.exe` (установщик)

6. Нажмите "Publish release"

## Структура релиза

Каждый релиз должен содержать:

- **ChatList-Setup-X.X.X.exe** - установщик (основной файл)
- **ChatList-X.X.X.exe** - портативная версия (опционально)
- **Source code (zip)** - автоматически создается GitHub
- **Source code (tar.gz)** - автоматически создается GitHub

## Обновление версии

При обновлении версии:

1. Обновите `version.py`:
   ```python
   __version__ = "1.0.1"
   ```

2. Обновите `ChatList.iss` (если нужно):
   ```iss
   #define MyAppVersion "1.0.1"
   #define MyAppExeName "ChatList-1.0.1.exe"
   ```

3. Создайте новый тег и релиз:
   ```powershell
   git add .
   git commit -m "Bump version to 1.0.1"
   git tag -a v1.0.1 -m "Release version 1.0.1"
   git push origin main
   git push origin v1.0.1
   ```

## Проверка релиза

После публикации проверьте:

1. ✅ Файлы загружены и доступны для скачивания
2. ✅ Версия в описании соответствует версии файлов
3. ✅ Установщик работает на чистой системе
4. ✅ Все ссылки работают
