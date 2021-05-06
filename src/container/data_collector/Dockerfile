FROM python:3.9.4-slim as base

FROM base as final


RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./

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

ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

COPY . /app
WORKDIR /app

RUN ["pytest", "-s"]

FROM base as final

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

COPY --from=tester /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY --from=tester /app /app

WORKDIR /app

ENTRYPOINT [ "/bin/bash" ]
