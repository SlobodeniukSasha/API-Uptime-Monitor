import uvicorn
from fastapi import FastAPI
from app.api.router import router as monitor_router

app = FastAPI(title="API Uptime Monitor")

# app.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/auth",
#     tags=["Auth"],
# )
#
# app.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix="/auth",
#     tags=["Auth"],
# )

app.include_router(monitor_router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
