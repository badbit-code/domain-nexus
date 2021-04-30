FROM python:3.9.4-slim as base

FROM base as builder

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# COPY ./requirements-test.txt .
#RUN pip install -r requirements-test.txt

FROM base as final
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

# ENV FLASK_APP=app

 # RUN apt-get -qq update \
 # && apt-get install -y --no-install-recommends \
 # openssl \
 # && rm -rf /var/lib/apt/lists/*



# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY ./ca-certificate.crt root.crt
COPY ./src/* .

ENTRYPOINT [ "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8050"]
