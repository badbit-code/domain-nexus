FROM python:3.9.4-slim as base

FROM base as builder

COPY ./requirements.txt .
COPY ./requirements-test.txt .

RUN pip install -r requirements.txt
RUN pip install -r requirements-test.txt

FROM base as final
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/

# Add the application
COPY . .

#ENTRYPOINT [ "python", "-c", "import ssl; print(ssl.OPENSSL_VERSION)" ]
ENTRYPOINT [ "python", "src/godaddy_collector.py"]