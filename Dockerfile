FROM python:3.12.2-slim

WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*


COPY api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /code/api
