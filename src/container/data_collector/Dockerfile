FROM python:3.9.4-slim as base

FROM base as builder

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .

RUN pip install -r requirements.txt

FROM builder as tester

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

COPY . /app
WORKDIR /app

RUN pytest

FROM base as final

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

COPY --from=tester /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY --from=tester /app /app

WORKDIR /app