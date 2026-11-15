FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/

WORKDIR /app
