#!/bin/bash
set -e

echo "------[Start] Wait for DB"
sleep 10
echo "------[Complete] Wait for DB"

echo "------Current directory:"

pwd

ls -la

#echo "------Running Alembic migrations"
#alembic upgrade head

echo "------Starting Uvicorn"
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
