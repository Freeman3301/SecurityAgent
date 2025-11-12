#!/bin/bash

# Скрипт для сбора ошибок из dmesg и journalctl
# Автор: System Agent

# Директория для логов
LOG_DIR="./error_collector"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Создаем директорию если не существует
mkdir -p "$LOG_DIR"

# Файлы для вывода
DMESG_FILE="$LOG_DIR/dmesg_errors_$TIMESTAMP.log"
JOURNAL_FILE="$LOG_DIR/journal_errors_$TIMESTAMP.log"

# Сбор ошибок из dmesg (только ошибки и критические сообщения)
dmesg -T -l err,crit 2>/dev/null > "$DMESG_FILE"

# Сбор ошибок из journalctl (только ошибки за последние 24 часа)
journalctl --since="24 hours ago" -p err..emerg 2>/dev/null > "$JOURNAL_FILE"

exit 0
