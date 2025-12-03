#!/bin/bash

echo "[Start] Wait for DB"
sleed 3
echo "[Complete] Wait for DB"

cd backend
alembic upgrade head
cd ..
uvicorn backend.app.main:app

