FROM python:3.9.4-slim as base

FROM base as final

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .

RUN python -m pip install -r requirements.txt

# RUN ["pytest", "-s"]



# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1


COPY ./src /app
COPY . /app

WORKDIR /app

ENTRYPOINT [ "python", "./app.py"]