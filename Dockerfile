FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn telethon apscheduler python-jose

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
