#!/usr/bin/env bash
# Postgres that lives entirely inside this project: the server programs come from the pgserver
# package in .venv (installed by `uv sync`), the data lives in db/pgdata. No Docker, no system install.
#   scripts/db.sh init    create the cluster + ukon user/database (first time only)
#   scripts/db.sh start   start the server on port $PGPORT (default 5433)
#   scripts/db.sh stop    stop it
#   scripts/db.sh status  is it running?
#   scripts/db.sh psql    open a psql shell on the ukon database
#   scripts/db.sh wipe    stop and move db/pgdata aside (recreate with init)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PGDATA="$ROOT/db/pgdata"
PGLOG="$ROOT/db/postgres.log"
PGPORT="${PGPORT:-5433}"

project_bin() {
  # Postgres bundled inside this project's .venv (the pgserver package, installed by `uv sync`)
  for p in "$ROOT"/.venv/lib/python*/site-packages/pgserver/pginstall/bin; do
    if [ -f "$p/pg_ctl" ]; then chmod +x "$p"/* 2>/dev/null || true; echo "$p"; return 0; fi
  done
  return 1
}

find_bin() {
  # 1. Explicit override:  PG_BIN=/path/to/postgres/bin scripts/db.sh init
  if [ -n "${PG_BIN:-}" ] && [ -x "$PG_BIN/pg_ctl" ]; then echo "$PG_BIN"; return; fi
  # 2. Bundled in the project (default). Run `uv sync` first if it's missing.
  if project_bin; then return; fi
  if command -v uv >/dev/null 2>&1; then
    echo "Installing the project's bundled Postgres (uv sync)..." >&2
    (cd "$ROOT" && uv sync -q) >&2 && project_bin && return
  fi
  # 3. A Postgres already on this machine (PATH, Postgres.app, postgresql.org installer, Homebrew)
  if command -v pg_ctl >/dev/null 2>&1; then dirname "$(command -v pg_ctl)"; return; fi
  for p in /Applications/Postgres.app/Contents/Versions/latest/bin \
           $(ls -d /Applications/Postgres.app/Contents/Versions/*/bin 2>/dev/null | sort -rV) \
           $(ls -d /Library/PostgreSQL/*/bin 2>/dev/null | sort -rV); do
    [ -x "$p/pg_ctl" ] && { echo "$p"; return; }
  done
  if command -v brew >/dev/null 2>&1; then
    for f in postgresql@16 postgresql@17 postgresql; do
      p="$(brew --prefix "$f" 2>/dev/null)/bin"
      [ -x "$p/pg_ctl" ] && { echo "$p"; return; }
    done
  fi
  for p in /opt/homebrew/opt/postgresql@16/bin /usr/local/opt/postgresql@16/bin /usr/lib/postgresql/*/bin; do
    [ -x "$p/pg_ctl" ] && { echo "$p"; return; }
  done
  echo "Postgres not found. Point to it with  PG_BIN=/path/to/bin scripts/db.sh init" >&2
  echo "(the folder that contains pg_ctl), or install Postgres.app / brew install postgresql@16." >&2
  exit 1
}
BIN="$(find_bin)"

running() { "$BIN/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1; }

start() {
  if running; then echo "Postgres already running on port $PGPORT"; return; fi
  # Socket lives in db/pgdata so nothing is written outside the project.
  "$BIN/pg_ctl" -D "$PGDATA" -l "$PGLOG" -w \
    -o "-p $PGPORT -k '$PGDATA' -c listen_addresses=localhost" start
  echo "Postgres running on localhost:$PGPORT (data: db/pgdata)"
}

case "${1:-}" in
  init)
    if [ -f "$PGDATA/PG_VERSION" ]; then echo "db/pgdata already initialised"; else
      mkdir -p "$PGDATA"
      "$BIN/initdb" -D "$PGDATA" -U postgres --auth=trust --encoding=UTF8 >/dev/null
      echo "Initialised cluster in db/pgdata"
    fi
    start
    "$BIN/psql" -h localhost -p "$PGPORT" -U postgres -v ON_ERROR_STOP=1 -q <<'SQL'
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ukon') THEN
    CREATE ROLE ukon LOGIN PASSWORD 'ukon';
  END IF;
END $$;
SQL
    "$BIN/psql" -h localhost -p "$PGPORT" -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='ukon'" | grep -q 1 \
      || "$BIN/createdb" -h localhost -p "$PGPORT" -U postgres -O ukon ukon
    echo "Database 'ukon' ready. Next: uv run python -m pipeline.run_all"
    ;;
  start) start ;;
  stop) running && "$BIN/pg_ctl" -D "$PGDATA" -m fast stop || echo "not running" ;;
  status) running && echo "running on port $PGPORT" || echo "stopped" ;;
  psql) exec "$BIN/psql" -h localhost -p "$PGPORT" -U ukon ukon ;;
  wipe)
    running && "$BIN/pg_ctl" -D "$PGDATA" -m fast stop || true
    mv "$PGDATA" "$PGDATA.old.$(date +%s)" && echo "Moved db/pgdata aside; run: scripts/db.sh init"
    ;;
  *) sed -n '2,9p' "$0"; exit 1 ;;
esac
