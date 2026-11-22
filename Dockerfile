FROM python:3.11-slim


# 2. Prevent Python from writing .pyc files & enable unbuffered logging for GCP Cloud Logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080


# 3. Set work directory
WORKDIR /app


# 5. Install Python dependencies first (leveraging Docker layer caching)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Expose default Cloud Run port
EXPOSE 8080

# 8. Start Uvicorn bound to 0.0.0.0 and dynamic $PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]