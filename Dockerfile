FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080

CMD bash -c "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python import_csv.py && gunicorn urbin.wsgi:application --bind 0.0.0.0:8080"