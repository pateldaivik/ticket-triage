FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/

RUN useradd --create-home appuser

WORKDIR /app

COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY --chown=appuser:appuser README.md ./
COPY --chown=appuser:appuser src/ src/
RUN uv sync --locked --no-dev

USER appuser

ENTRYPOINT ["uv", "run", "--no-sync", "ticket-triage"]
