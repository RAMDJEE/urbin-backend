# Utilise une image officielle Python avec Debian
FROM python:3.12-slim

# Installe les dpendances systme dont libGL
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Cre un rpertoire app
WORKDIR /app

# Copie le code
COPY . .

# Installe les dpendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collecte les fichiers statiques
RUN python manage.py collectstatic --noinput

# Expose le port
EXPOSE 8080

# Lance Gunicorn
CMD ["gunicorn", "urbin.wsgi:application", "--bind", "0.0.0.0:8080"]
