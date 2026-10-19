#!/usr/bin/env bash
# Проверка и восстановление PostgreSQL-бэкенда RSS-агрегатора из архива,
# созданного scripts/backup_postgres.sh.
#
# Два режима:
#
#   ./scripts/restore_postgres.sh [архив.sql.gz]
#       Режим проверки (по умолчанию, безопасный). Разворачивает архив во
#       ВРЕМЕННУЮ базу rss_aggregator_restore_check, считает строки в
#       таблицах и удаляет временную базу. Рабочая база не затрагивается.
#       Так проверяется, что бэкап реально восстанавливается.
#
#   ./scripts/restore_postgres.sh --replace [архив.sql.gz]
#       Восстановление поверх рабочей базы. Спрашивает подтверждение,
#       перед заменой делает свежий бэкап текущего состояния, затем
#       пересоздаёт базу из архива. После этого приложение (uvicorn)
#       нужно перезапустить — у него остались старые соединения.
#
# Если архив не указан — берётся самый свежий из backups/.
# Каждый шаг пишется в консоль и в logs/restore.log.

set -euo pipefail

CONTAINER_NAME="rss-aggregator-db"
DB_NAME="rss_aggregator"
DB_USER="rss_user"
CHECK_DB="rss_aggregator_restore_check"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/../backups"
LOG_FILE="$SCRIPT_DIR/../logs/restore.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

MODE="verify"
BACKUP_FILE=""
for arg in "$@"; do
    case "$arg" in
        --replace) MODE="replace" ;;
        *) BACKUP_FILE="$arg" ;;
    esac
done

if [ -z "$BACKUP_FILE" ]; then
    BACKUP_FILE="$(ls -1t "$BACKUP_DIR"/rss_aggregator_*.sql.gz 2>/dev/null | head -n 1 || true)"
fi

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    log "ОШИБКА: архив для восстановления не найден (искал в $BACKUP_DIR)"
    exit 1
fi

# Выполнить SQL-команду от имени администратора в служебной базе postgres.
psql_admin() {
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -v ON_ERROR_STOP=1 -q -c "$1"
}

# Развернуть архив в указанную (уже созданную пустую) базу.
load_dump() {
    gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$1" -v ON_ERROR_STOP=1 -q
}

# Посчитать строки в таблице указанной базы.
count_rows() {
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$1" -t -A -c "SELECT count(*) FROM $2"
}

log "Режим: $MODE, архив: $BACKUP_FILE"

if [ "$MODE" = "verify" ]; then
    # Временная база удаляется при любом выходе из скрипта, в том числе
    # по ошибке — чтобы не оставлять за собой мусор.
    cleanup() {
        psql_admin "DROP DATABASE IF EXISTS $CHECK_DB WITH (FORCE)" >/dev/null 2>&1 || true
    }
    trap cleanup EXIT

    log "Создаю временную базу $CHECK_DB"
    psql_admin "DROP DATABASE IF EXISTS $CHECK_DB WITH (FORCE)"
    psql_admin "CREATE DATABASE $CHECK_DB"

    log "Разворачиваю архив во временную базу"
    if ! load_dump "$CHECK_DB"; then
        log "ОШИБКА: архив не развернулся — бэкап повреждён или несовместим"
        exit 1
    fi

    SOURCES_COUNT="$(count_rows "$CHECK_DB" sources)"
    ARTICLES_COUNT="$(count_rows "$CHECK_DB" articles)"
    log "Проверка пройдена: sources=$SOURCES_COUNT, articles=$ARTICLES_COUNT"
    log "Временная база будет удалена. Рабочая база не затронута."
    exit 0
fi

# --- режим replace ---

log "ВНИМАНИЕ: рабочая база $DB_NAME будет полностью заменена содержимым архива"
read -r -p "Продолжить? Введите yes: " ANSWER
if [ "$ANSWER" != "yes" ]; then
    log "Отменено пользователем, ничего не изменено"
    exit 1
fi

log "Делаю страховочный бэкап текущего состояния перед заменой"
"$SCRIPT_DIR/backup_postgres.sh"

log "Пересоздаю базу $DB_NAME"
psql_admin "DROP DATABASE IF EXISTS $DB_NAME WITH (FORCE)"
psql_admin "CREATE DATABASE $DB_NAME"

log "Разворачиваю архив в $DB_NAME"
if ! load_dump "$DB_NAME"; then
    log "ОШИБКА: архив не развернулся. Состояние до замены сохранено в страховочном бэкапе (backups/)"
    exit 1
fi

SOURCES_COUNT="$(count_rows "$DB_NAME" sources)"
ARTICLES_COUNT="$(count_rows "$DB_NAME" articles)"
log "Восстановление завершено: sources=$SOURCES_COUNT, articles=$ARTICLES_COUNT"
log "Перезапустите приложение (uvicorn), чтобы оно переподключилось к базе"
