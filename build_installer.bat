@echo off
chcp 65001 >nul
echo ========================================
echo Сборка установщика ChatList
echo ========================================
echo.

echo Шаг 1: Проверка наличия исполняемого файла...
if not exist "dist\ChatList-1.0.0.exe" (
    echo ОШИБКА: Файл dist\ChatList-1.0.0.exe не найден!
    echo Сначала выполните сборку приложения: build.bat
    pause
    exit /b 1
)

echo Шаг 2: Поиск Inno Setup...
REM Попытка найти iscc.exe в стандартных местах
set "ISCC_PATH="
set "ISCC_FOUND=0"
set "INNO_PATH1=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set "INNO_PATH2=C:\Program Files\Inno Setup 6\ISCC.exe"

if exist "%INNO_PATH1%" (
    set "ISCC_PATH=%INNO_PATH1%"
    set "ISCC_FOUND=1"
    goto found_iscc
)

if exist "%INNO_PATH2%" (
    set "ISCC_PATH=%INNO_PATH2%"
    set "ISCC_FOUND=1"
    goto found_iscc
)

:found_iscc
if "%ISCC_FOUND%"=="0" (
    echo ОШИБКА: Inno Setup не найден!
    echo Установите Inno Setup из https://jrsoftware.org/isdl.php
    echo Обычно Inno Setup находится в: C:\Program Files (x86)\Inno Setup 6\ISCC.exe
    pause
    exit /b 1
)

echo Найден: %ISCC_PATH%

echo Шаг 3: Создание папки для установщика...
if not exist "installer" mkdir installer

echo Шаг 4: Компиляция установщика...
echo.

"%ISCC_PATH%" ChatList.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Установщик успешно создан!
    echo Файл: installer\ChatList-Setup-1.0.0.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ОШИБКА при создании установщика!
    echo ========================================
)

echo.
pause
