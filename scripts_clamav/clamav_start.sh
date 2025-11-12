#!/bin/bash

set -e

echo "🚀 Starting ClamAV services..."

# Скачивание начальных баз
echo "📥 Downloading initial databases..."
sudo -u clamav freshclam --verbose

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск служб
sudo systemctl enable clamav-daemon
sudo systemctl enable clamav-freshclam

sudo systemctl start clamav-daemon
sudo systemctl start clamav-freshclam

# Небольшая пауза для инициализации
sleep 5

# Проверка статуса
echo "📊 Checking services status..."
sudo systemctl status clamav-daemon --no-pager -l | head -10
sudo systemctl status clamav-freshclam --no-pager -l | head -10

# Создание символической ссылки если нужно
if [ ! -L "/run/clamav/clamd.sock" ]; then
    sudo ln -sf /run/clamav/clamd.ctl /run/clamav/clamd.sock
fi

echo "✅ ClamAV services started successfully!"
