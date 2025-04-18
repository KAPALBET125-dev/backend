from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta
import json
import os

app = FastAPI()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth functions
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({ "exp": expire })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        with open("admins.json") as f:
            admins = json.load(f)
    except:
        return {"error": "admin file not found"}

    for admin in admins:
        if admin["username"] == username and admin["password"] == password:
            token = create_token({ "sub": username, "role": admin.get("role", "user") })
            return {"access_token": token, "token_type": "bearer"}
    return {"error": "invalid credentials"}

@app.get("/accounts")
def get_accounts(user=Depends(get_current_user)):
    if not os.path.exists("accounts.json"):
        return []
    with open("accounts.json") as f:
        return json.load(f)

@app.post("/accounts")
def add_account(phone: str = Form(...), user=Depends(get_current_user)):
    new_acc = { "phone": phone, "active": True }
    accs = []
    if os.path.exists("accounts.json"):
        with open("accounts.json") as f:
            accs = json.load(f)
    accs.append(new_acc)
    with open("accounts.json", "w") as f:
        json.dump(accs, f)
    return {"message": "added"}

@app.get("/schedules")
def get_schedules(user=Depends(get_current_user)):
    if not os.path.exists("schedules.json"):
        return []
    with open("schedules.json") as f:
        return json.load(f)

@app.post("/schedules")
def add_schedule(phone: str = Form(...), target: str = Form(...), interval: int = Form(...), user=Depends(get_current_user)):
    new_job = { "phone": phone, "target": target, "interval": interval }
    jobs = []
    if os.path.exists("schedules.json"):
        with open("schedules.json") as f:
            jobs = json.load(f)
    jobs.append(new_job)
    with open("schedules.json", "w") as f:
        json.dump(jobs, f)
    return {"message": "scheduled"}

@app.get("/admins")
def get_admins(user=Depends(get_current_user)):
    if user.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Forbidden")
    with open("admins.json") as f:
        return json.load(f)

@app.post("/admins")
def add_admin(username: str = Form(...), password: str = Form(...), role: str = Form(...), user=Depends(get_current_user)):
    if user.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Forbidden")
    with open("admins.json") as f:
        admins = json.load(f)
    admins.append({ "username": username, "password": password, "role": role })
    with open("admins.json", "w") as f:
        json.dump(admins, f)
    return {"message": "admin added"}

@app.get("/logs")
def get_logs(user=Depends(get_current_user)):
    if not os.path.exists("logs/forward.log"):
        return []
    with open("logs/forward.log") as f:
        return f.read()