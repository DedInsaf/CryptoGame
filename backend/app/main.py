from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.user import Base
from utils.database import engine
from routes import auth, crypto

import sys
sys.path.append("C:/Users/damur/PycharmProjects/CryptoGame")

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="KidsCrypto Exchange")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(auth.router, prefix="/api/auth")
app.include_router(crypto.router, prefix="/api/crypto")

@app.get("/")
async def root():
    return {"message": "Welcome to KidsCrypto Exchange!"}