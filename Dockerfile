FROM python:3.12

WORKDIR /code

COPY api/requirements.txt .

RUN pip install -r requirements.txt

COPY api/ /code/api
