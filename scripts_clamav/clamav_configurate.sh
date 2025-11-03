#!/bin/bash

set -e

echo "⚙️ Configuring ClamAV..."

# Бэкап существующих конфигов
sudo cp /etc/clamav/freshclam.conf /etc/clamav/freshclam.conf.backup 2>/dev/null || true
sudo cp /etc/clamav/clamd.conf /etc/clamav/clamd.conf.backup 2>/dev/null || true

# Настройка freshclam
sudo tee /etc/clamav/freshclam.conf > /dev/null << 'EOF'
DatabaseDirectory /var/lib/clamav
UpdateLogFile /var/log/clamav/freshclam.log
LogFileMaxSize 2M
LogRotate yes
LogTime yes
Checks 4
PrivateMirror https://clamav-mirror.ru/
PrivateMirror https://mirror.truenetwork.ru/clamav/
DatabaseMirror database.clamav.net
MaxAttempts 3
ScriptedUpdates no
ConnectTimeout 30
ReceiveTimeout 60
LogVerbose yes
EOF

# Настройка clamd
sudo tee /etc/clamav/clamd.conf > /dev/null << 'EOF'
LogFile /var/log/clamav/clamd.log
LogTime yes
LogClean yes
LogRotate yes
PidFile /run/clamav/clamd.pid
TemporaryDirectory /tmp
DatabaseDirectory /var/lib/clamav
LocalSocket /run/clamav/clamd.ctl
FixStaleSocket yes
MaxConnectionQueueLength 30
MaxThreads 10
ReadTimeout 300
SelfCheck 3600
ScanPE yes
ScanELF yes
ScanArchive yes
LogVerbose yes
EOF

# Настройка прав конфигов
sudo chown clamav:clamav /etc/clamav/freshclam.conf
sudo chown clamav:clamav /etc/clamav/clamd.conf
sudo chmod 644 /etc/clamav/freshclam.conf
sudo chmod 644 /etc/clamav/clamd.conf

# Создание лог файлов
sudo touch /var/log/clamav/freshclam.log
sudo touch /var/log/clamav/clamd.log
sudo chown clamav:clamav /var/log/clamav/*.log
sudo chmod 644 /var/log/clamav/*.log

# Настройка logrotate
sudo tee /etc/logrotate.d/clamav > /dev/null << 'EOF'
/var/log/clamav/*.log {
    weekly
    missingok
    rotate 12
    compress
    delaycompress
    notifempty
    create 640 clamav clamav
}
EOF

# Создание символической ссылки для сокета
sudo ln -sf /run/clamav/clamd.ctl /run/clamav/clamd.sock

echo "✅ ClamAV configured successfully!"
