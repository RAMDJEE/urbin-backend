FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python manage.py migrate --noinput

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "urbin.wsgi:application", "--bind", "0.0.0.0:8080"]
