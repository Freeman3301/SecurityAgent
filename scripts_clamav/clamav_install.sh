#!/bin/bash

set -e

echo "🛠️ Installing ClamAV..."

# Обновление системы
sudo pacman -Syu --noconfirm

# Установка ClamAV
sudo pacman -S clamav --noconfirm

# Попытка установки неофициальных сигнатур
sudo pacman -S clamav-unofficial-sigs --noconfirm 2>/dev/null || echo "⚠️ clamav-unofficial-sigs not available"

# Создание директорий
sudo mkdir -p /etc/clamav
sudo mkdir -p /var/lib/clamav
sudo mkdir -p /var/log/clamav
sudo mkdir -p /run/clamav

# Настройка прав
sudo chown -R clamav:clamav /var/lib/clamav /var/log/clamav /run/clamav
sudo chmod -R 755 /var/lib/clamav

echo "✅ ClamAV installed successfully!"
