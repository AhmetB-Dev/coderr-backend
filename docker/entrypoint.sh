#!/bin/sh
set -eu

wait_for_postgres() {
  [ -n "${DB_HOST:-}" ] || return 0

  echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT:-5432}..."
  until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -q; do
    sleep 1
  done
  echo "PostgreSQL is ready."
}

prepare_writable_directories() {
  if [ "$(id -u)" != "0" ]; then
    return
  fi

  mkdir -p /app/media /app/staticfiles
  chown -R app:app /app/media /app/staticfiles
}

run_as_app_user() {
  if [ "$(id -u)" = "0" ]; then
    exec gosu app "$@"
  fi
  exec "$@"
}

wait_for_postgres
prepare_writable_directories
run_as_app_user "$@"
