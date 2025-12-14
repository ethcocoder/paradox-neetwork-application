# Lightweight base
FROM python:3.9-slim

# Prevent python from writing pyc
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (if needed for basic image ops)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Core Package
COPY . /app

# Install Paradox with Server deps
RUN pip install --no-cache-dir .[server,ai]

# Default Port
EXPOSE 8000

# Entrypoint: Start a Shard Server
# Override with CMD ["--id", "shard_1", "--port", "8000"]
ENTRYPOINT ["python", "-m", "paradox.distributed.server"]
