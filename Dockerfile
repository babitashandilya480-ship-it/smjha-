FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend/samjha /app/backend/samjha
ENV PYTHONPATH=/app/backend
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn samjha.api:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
