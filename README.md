# -------------------------------
# Stage 1: Build dependencies
# -------------------------------
FROM python:3.12-alpine AS builder

# Install build dependencies required for compiling Python wheels
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

WORKDIR /app

# Copy requirement file first to leverage Docker layer caching
COPY requirements.txt .

# Build wheels inside /wheels directory
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# -------------------------------
# Stage 2: Lightweight runtime image
# -------------------------------
FROM python:3.12-alpine

# Install only runtime dependencies (no compilers)
RUN apk add --no-cache libffi openssl

WORKDIR /app

# Copy built wheels from builder image
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY app.py .

# ------------------------------------------------------------------
# 🔐 Create NON-ROOT user (Security Best Practice)
# ------------------------------------------------------------------
# WHY THIS IS IMPORTANT:
# -----------------------
# - Running containers as root is dangerous because:
#     • If app is compromised → attacker gets root inside the container.
#     • Root inside container can affect mounted volumes.
#     • Reduces impact of RCE attacks.
# - CIS Benchmarks, OWASP, Docker Bench all require non-root.
# - Kubernetes runAsNonRoot requires a non-root UID.
# - UID 1000 is the standard Linux unprivileged user → safest choice.
# ------------------------------------------------------------------

RUN addgroup --gid 1000 appgroup \
    && adduser --uid 1000 --ingroup appgroup --disabled-password --gecos "" appuser

# Switch to non-root user
USER 1000:1000

EXPOSE 5000

# Start application
CMD ["python", "app.py"]
