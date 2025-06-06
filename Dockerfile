# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Install system dependencies and build essentials
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    sqlite3 \
    ffmpeg \
    ca-certificates \
    imagemagick \
    build-essential \
    libpq-dev \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install Node.js and Prettier with cleanup
RUN curl -sL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh && \
    bash nodesource_setup.sh && \
    apt-get install -y nodejs && \
    rm nodesource_setup.sh && \
    npm install -g prettier@3.4.2

# Set working directory
WORKDIR /app

COPY requirements.txt /app/

# Create and activate virtual environment
RUN python3 -m venv /app/venv

# Set venv as default Python environment
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies into the venv using uv
RUN uv pip install --upgrade pip setuptools wheel && \
    uv pip install --no-cache-dir -r /app/requirements.txt


# Install Python dependencies
#RUN uv pip install --system --no-cache-dir --upgrade pip setuptools wheel && \
#uv pip install --system --no-cache-dir \
#fastapi \
#uvicorn[standard] \
#requests \
#httpx \
#pandas \
#numpy \
#duckdb \
#scipy \
#sqlalchemy \
#psycopg2-binary \
#asyncpg \
#torch \
#pillow \
#scikit-learn \
#markdown \
#markdown2 \
#python-dateutil \
#bs4 \
#beautifulsoup4 

# Copy application code
COPY main.py /app/
COPY static /app/static

# Create data directory
RUN mkdir -p /data


## Run the application
CMD ["uv", "run", "main.py"]

# Run the application with proper uvicorn command
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]