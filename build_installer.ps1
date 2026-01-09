# Скрипт для сборки установщика ChatList
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Сборка установщика ChatList" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Шаг 1: Проверка наличия исполняемого файла
Write-Host "Шаг 1: Проверка наличия исполняемого файла..." -ForegroundColor Yellow
if (-not (Test-Path "dist\ChatList-1.0.0.exe")) {
    Write-Host "ОШИБКА: Файл dist\ChatList-1.0.0.exe не найден!" -ForegroundColor Red
    Write-Host "Сначала выполните сборку приложения: .\build.bat" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "Файл найден: dist\ChatList-1.0.0.exe" -ForegroundColor Green

# Шаг 2: Поиск Inno Setup
Write-Host "Шаг 2: Поиск Inno Setup..." -ForegroundColor Yellow
$isccPath = $null

$paths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        $isccPath = $path
        break
    }
}

if ($null -eq $isccPath) {
    Write-Host "ОШИБКА: Inno Setup не найден!" -ForegroundColor Red
    Write-Host "Установите Inno Setup из https://jrsoftware.org/isdl.php" -ForegroundColor Red
    Write-Host "Обычно Inno Setup находится в: C:\Program Files (x86)\Inno Setup 6\ISCC.exe" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "Найден: $isccPath" -ForegroundColor Green

# Шаг 3: Создание папки для установщика
Write-Host "Шаг 3: Создание папки для установщика..." -ForegroundColor Yellow
if (-not (Test-Path "installer")) {
    New-Item -ItemType Directory -Path "installer" | Out-Null
}

# Шаг 4: Компиляция установщика
Write-Host "Шаг 4: Компиляция установщика..." -ForegroundColor Yellow
Write-Host ""

$process = Start-Process -FilePath $isccPath -ArgumentList "ChatList.iss" -Wait -PassThru -NoNewWindow
$exitCode = $process.ExitCode

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Установщик успешно создан!" -ForegroundColor Green
    Write-Host "Файл: installer\ChatList-Setup-1.0.0.exe" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ОШИБКА при создании установщика!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "Нажмите Enter для выхода"
