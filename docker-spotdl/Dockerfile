FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy requirements files
COPY poetry.lock pyproject.toml /

# Install spotdl requirements
RUN poetry install --no-root

# Add source code files to WORKDIR
ADD . .

# Install spotdl itself
RUN poetry install

# Create music directory
RUN mkdir /music

# Change CWD to /music
WORKDIR /music

ENV SPOTIPY_CLIENT_ID=""
ENV SPOTIPY_CLIENT_SECRET=""

# Entrypoint command
ENTRYPOINT ["poetry", "run", "spotdl"]