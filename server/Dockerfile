FROM python:3.11-slim

# Install PortAudio system library
RUN apt-get update && apt-get install -y alsa-utils && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y portaudio19-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# EXPOSE 8000

CMD ["python", "-m", "services.interview"]