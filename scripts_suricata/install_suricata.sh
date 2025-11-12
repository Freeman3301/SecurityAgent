#!/bin/bash

# Скрипт для ручной установки Suricata из AUR
set -e

echo "=== Ручная установка Suricata из AUR ==="

# Проверка и установка зависимостей
echo "Устанавливаем зависимости..."
sudo pacman -S --needed --noconfirm git base-devel

# Создание временной директории
temp_dir=$(mktemp -d)
cd "$temp_dir"

echo "Клонируем пакет Suricata из AUR..."
git clone https://aur.archlinux.org/suricata.git
cd suricata



makepkg -si --noconfirm --skippgpcheck


# Очистка
cd /
rm -rf "$temp_dir"

# Проверка установки
echo "Проверяем установку..."
if command -v suricata &> /dev/null; then
    echo "Suricata успешно установлена!"
    echo "Версия: $(suricata --version 2>/dev/null | head -n1)"
else
    echo "Ошибка: Suricata не установлена корректно"
    exit 1
fi
echo "=== Установка завершена ==="
