# Быстрый старт - Публикация на GitHub

## 🚀 Быстрая публикация (5 минут)

### 1. Создание репозитория (2 минуты)

```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Drogobar/ChatList.git
git branch -M main
git push -u origin main
```

### 3. Настройка GitHub Actions (1 минута)

1. GitHub → Settings → Developer settings → Personal access tokens
2. Создайте токен с правами `repo` и `workflow`
3. Репозиторий → Settings → Secrets → New secret
4. Name: `GITHUB_TOKEN`, Value: ваш токен

### 4. Включение GitHub Pages (30 секунд)

1. Репозиторий → Settings → Pages
2. Source: **GitHub Actions**
3. Сохраните

### 5. Создание первого релиза (30 секунд)

```powershell
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

GitHub Actions автоматически:
- ✅ Соберет приложение
- ✅ Создаст установщик
- ✅ Опубликует релиз
- ✅ Опубликует сайт на GitHub Pages

## 📚 Подробные инструкции

- **Полное руководство**: `PUBLISH_GUIDE.md`
- **GitHub Release**: `GITHUB_RELEASE.md`
- **GitHub Pages**: `GITHUB_PAGES.md`
- **Шаблон релиза**: `RELEASE_NOTES_TEMPLATE.md`

## ✅ Проверка

После выполнения шагов:

1. **Релиз**: https://github.com/Drogobar/ChatList/releases
2. **Сайт**: https://Drogobar.github.io/ChatList/
3. **Actions**: https://github.com/Drogobar/ChatList/actions

## 🆘 Проблемы?

Смотрите раздел "Troubleshooting" в `PUBLISH_GUIDE.md`
