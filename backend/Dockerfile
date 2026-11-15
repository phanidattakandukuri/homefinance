FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
