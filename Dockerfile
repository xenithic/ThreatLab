FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    nmap \
    hydra \
    netcat-traditional \
    netcat \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

EXPOSE 5000

CMD ["python", "app.py"]
