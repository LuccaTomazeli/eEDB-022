FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/usr/lib/jvm/default-java \
    HOME=/tmp \
    IVY_HOME=/tmp/.ivy2 \
    SPARK_USER=spark \
    HADOOP_USER_NAME=spark

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && for uid in $(seq 1000 1010); do echo "spark${uid}:x:${uid}:${uid}:Spark User:/tmp:/bin/sh" >> /etc/passwd ; done

WORKDIR /workspace/atividade_03

COPY requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt
