FROM python:3.9-slim

WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Exposer les ports
EXPOSE 5000 8000 8001 8002

# Commande par défaut
CMD ["python", "app/app.py"]