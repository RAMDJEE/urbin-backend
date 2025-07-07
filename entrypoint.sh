set -e

#!/bin/bash
# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optional: import your CSV
echo "Importing CSV..."
python import_csv.py

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn urbin.wsgi:application --bind 0.0.0.0:8080
