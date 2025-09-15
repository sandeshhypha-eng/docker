# Use official Python image
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt requirements.txt
COPY app.py app.py

# Install dependencies
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-alpine

# RUN sudo useradd -m appuser
RUN chmod -R 700 /var

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /app/app.py /app/app.py

# Expose port 5000
EXPOSE 5000

RUN chown -R appuser:appgroup /app

USER appuser

# Run the app
CMD ["python", "app.py"]
