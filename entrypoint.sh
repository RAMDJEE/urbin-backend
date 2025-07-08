#!/bin/bash

echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

echo "🚀 Starting server..."
exec gunicorn urbin.wsgi:application --bind 0.0.0.0:8080
