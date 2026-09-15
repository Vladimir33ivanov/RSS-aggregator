#!/usr/bin/env bash
# Резервное копирование PostgreSQL-бэкенда RSS-агрегатора.
#
# Запуск вручную (из WSL, из корня проекта):
#   ./scripts/backup_postgres.sh
#
# Планирование через cron (пример — каждый день в 3:00 ночи):
#   crontab -e
#   0 3 * * * cd /путь/к/проекту && ./scripts/backup_postgres.sh
# (сам скрипт уже пишет и в консоль, и в лог-файл — отдельно
# перенаправлять вывод в cron не обязательно)

set -euo pipefail

CONTAINER_NAME="rss-aggregator-db"
DB_NAME="rss_aggregator"
DB_USER="rss_user"
RETENTION_DAYS=7

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/../backups"
LOG_FILE="$SCRIPT_DIR/../logs/backup.log"

mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
BACKUP_FILE="$BACKUP_DIR/rss_aggregator_${TIMESTAMP}.sql.gz"

log "Старт бэкапа: $BACKUP_FILE"

if ! docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    log "ОШИБКА: pg_dump завершился с ошибкой, удаляю неполный файл"
    rm -f "$BACKUP_FILE"
    exit 1
fi

log "Бэкап успешно создан: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"

log "Поиск бэкапов старше $RETENTION_DAYS дней для удаления"
DELETED_COUNT=0
while IFS= read -r old_file; do
    rm -f "$old_file"
    log "Удалён старый бэкап: $old_file"
    DELETED_COUNT=$((DELETED_COUNT + 1))
done < <(find "$BACKUP_DIR" -name "rss_aggregator_*.sql.gz" -mtime "+$RETENTION_DAYS")

log "Удалено старых бэкапов: $DELETED_COUNT"
log "Готово"
