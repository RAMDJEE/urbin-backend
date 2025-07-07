FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# RENDRE LE SCRIPT EXECUTABLE
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
