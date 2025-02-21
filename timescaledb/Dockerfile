# FROM python:3.9
FROM python:3.11-slim-buster


WORKDIR /app

ENV DOCKER_RUNNING True

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tk

RUN pip install --upgrade pip
RUN pip install pipenv

# Install dependencies
COPY ./Pipfile Pipfile
RUN pipenv install --skip-lock --system --dev

COPY . .