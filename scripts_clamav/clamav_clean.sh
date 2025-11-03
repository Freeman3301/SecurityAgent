#!/bin/bash

echo "🧹 Starting ClamAV complete cleanup..."

# Остановка служб
sudo systemctl stop clamav-daemon 2>/dev/null
sudo systemctl stop clamav-freshclam 2>/dev/null

# Отключение служб
sudo systemctl disable clamav-daemon 2>/dev/null
sudo systemctl disable clamav-freshclam 2>/dev/null

# Удаление служб systemd
sudo rm -f /etc/systemd/system/clamav-daemon.service
sudo rm -f /etc/systemd/system/clamav-freshclam.service

# Перезагрузка systemd
sudo systemctl daemon-reload
sudo systemctl reset-failed

# Удаление конфигурационных файлов
sudo rm -rf /etc/clamav/

# Удаление баз данных и логов
sudo rm -rf /var/lib/clamav/
sudo rm -rf /var/log/clamav/

# Удаление runtime файлов
sudo rm -rf /run/clamav/

# Удаление пакетов
sudo pacman -Rns clamav clamav-unofficial-sigs --noconfirm 2>/dev/null

# Очистка кэша pacman
sudo pacman -Sc --noconfirm

echo "✅ ClamAV completely removed!"
