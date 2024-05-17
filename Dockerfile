FROM python:3.12-slim as builder

WORKDIR /usr/src/app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt


# Production
FROM python:3.12-slim as base

WORKDIR /usr/src/app

RUN groupadd app \
  && useradd --create-home -g app app

COPY --from=builder /opt/venv /opt/venv
COPY . .

USER app

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]


#Development
FROM base as dev

USER root

RUN pip install -r requirements.dev.txt

USER app