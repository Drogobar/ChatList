@echo off
echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Создание исполняемого файла...
pyinstaller MinimalPyQtApp.spec

echo.
echo Готово! Исполняемый файл находится в папке dist\ChatList-*.exe
pause

