
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Telegram Userbot Backend API is running"}
