FROM python:3.9.4-slim as base

FROM base as builder

COPY ./requirements.txt .

RUN pip install -r requirements.txt

FROM builder as tester

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

COPY . /data_collector
WORKDIR /app

RUN pytest