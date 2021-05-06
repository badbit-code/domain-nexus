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

COPY . ./

# COPY ./src ./

ENTRYPOINT [ "python", "./app.py"]