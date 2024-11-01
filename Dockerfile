FROM python:3.12.2-slim as build

WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY /api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12.2-slim as prod

WORKDIR /code

COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY . .