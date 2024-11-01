# Stage 1: Build stage
FROM python:3.12.2-slim as build

WORKDIR /code

# Install necessary build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY /api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.12.2-slim as prod

WORKDIR /code

# Copy the installed packages from the build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .