import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routers.monitor_router import router as monitor_router
from backend.app.api.routers.auth_router import router as auth_router

app = FastAPI(title="API Health Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # FastAPI itself
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)


app.include_router(monitor_router)
app.include_router(auth_router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
