FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for C compilation (ChromaDB/numpy dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and setup requirements
COPY pyproject.toml .
# Create dummy module to install dependencies first and utilize Docker cache layer
RUN mkdir paper_scout && touch paper_scout/__init__.py
RUN pip install --no-cache-dir -e .

# Copy the rest of the backend files
COPY . .

EXPOSE 8001

CMD ["uvicorn", "paper_scout.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8001"]
