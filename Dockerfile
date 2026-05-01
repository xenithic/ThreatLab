FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    nmap \
    hydra \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start.sh .
RUN chmod +x start.sh

EXPOSE 5000
EXPOSE 5001

CMD ["bash", "start.sh"]
