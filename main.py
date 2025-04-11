from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Enable CORS for all origins (frontend allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        with open("admins.json") as f:
            admins = json.load(f)
    except:
        return {"error": "admin file not found"}

    for admin in admins:
        if admin["username"] == username and admin["password"] == password:
            return {"access_token": "mocked-token", "token_type": "bearer"}
    return {"error": "invalid credentials"}

@app.get("/")
def home():
    return {"message": "API running"}