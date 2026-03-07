FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy project files
COPY pyproject.toml /app/
COPY crisis_inbox/ /app/crisis_inbox/

# Install dependencies
RUN uv pip install --system -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "crisis_inbox.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
