# Stage 1: Build dependencies
FROM python:3.10-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc libffi-dev && \
    pip install --user --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Runtime environment
FROM python:3.10-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /home/appuser/app

# Copy installed packages and code
COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /app /home/appuser/app

ENV PATH="/home/appuser/.local/bin:$PATH"
RUN chown -R appuser:appgroup /home/appuser && chmod -R 755 /home/appuser

USER appuser
EXPOSE 8080
CMD ["python", "app.py"]
