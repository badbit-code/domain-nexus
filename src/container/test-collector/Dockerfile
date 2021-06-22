FROM python:3.9.4-slim as base


# Directories -------------------------

ENV COLLECTOR_DIR=./test-collector

# BUILD LAYER -------------------------

FROM base as builder

WORKDIR /app

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./common/requirements.txt ./requirements.txt

RUN python -m pip install -r requirements.txt

# Uncomment to install packages from collector specific requirements
# list.
#COPY ${COLLECTOR_DIR}/requirements.txt ./requirements.txt
#
#RUN python -m pip install -r requirements.txt

COPY ./common ./

# TEST LAYER -------------------------

# Test Container Env Variables
# This needs to run with t  
FROM builder as unit-tests

WORKDIR /app

#Bridge network
ENV POSTGRES_HOST=172.17.0.1 
ENV POSTGRES_USER=unicorn_user
ENV POSTGRES_PASSWORD=magical_password
ENV POSTGRES_DB=rainbow_database
ENV POSTGRES_PORT=65056
ENV PYTHONPATH=/app/:/app/common


RUN pip install pytest

COPY ${COLLECTOR_DIR}/tests/ ./tests/
RUN ["python", "-m", "pytest", "./tests/"]

# FINAL LAYER -------------------------

FROM base as final

ENV PYTHONPATH=/app/:/app/common

WORKDIR /app

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

COPY ${COLLECTOR_DIR}/app.py ./

ENTRYPOINT [ "python", "./app.py"]