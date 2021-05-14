FROM python:3.9.4-slim as base

FROM base as final

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./

COPY ./common/requirements.txt .
RUN python -m pip install -r requirements.txt
WORKDIR /app

#FROM builder as tester

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB

# RUN ["pytest", "-s"]

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

COPY ./data_collector/src /app
COPY ./common /app
COPY ./certificate /app

WORKDIR /app

ENTRYPOINT [ "/bin/bash" ]
