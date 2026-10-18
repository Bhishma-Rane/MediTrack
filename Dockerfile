FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --requirement requirements.txt
COPY . .
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "meditrack.main:app", "--host", "0.0.0.0", "--port", "8000"]
