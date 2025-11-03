#!/bin/bash
echo "Установка зависимостей для агента мониторинга..."

# Обновление системы
pacman -Syu --noconfirm

# Основные зависимости
pacman -S --noconfirm \
    python \
    python-pip \
    python-psutil \
    procps-ng \
    net-tools \
    iproute2 \
    util-linux \
    grep \
    gzip \
    curl \
    jq \
    sysstat \
    lsof \
    systemd \
    logrotate

# Проверка установки
echo "Проверка установленных пакетов..."
which python && python --version
which pip && pip --version
pip list | grep psutil

echo "✅ Зависимости установлены!"
