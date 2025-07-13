FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget ca-certificates netbase \
      build-essential python2.7 python2.7-dev \
      libssl-dev libffi-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://bootstrap.pypa.io/pip/2.7/get-pip.py && \
    python2.7 get-pip.py && \
    rm get-pip.py

RUN pip install --upgrade "pip<21.0" setuptools wheel

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
CMD ["python2.7", "app.py"]
