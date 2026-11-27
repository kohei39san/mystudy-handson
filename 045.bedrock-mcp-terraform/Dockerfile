FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-agent.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements-agent.txt

COPY agentcore_app ./agentcore_app

USER 10001

CMD ["python", "agentcore_app/main.py"]
