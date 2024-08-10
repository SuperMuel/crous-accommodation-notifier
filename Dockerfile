# Utilisation d'une image Python de base
FROM python:3.12-slim

# Configuration de l'environnement
ENV POETRY_VERSION=1.8.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation de Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
COPY pyproject.toml poetry.lock /app/

# Installation des dépendances via Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copier le reste du code du projet dans le conteneur
COPY . /app

# Commande pour exécuter le script principal
CMD ["poetry", "run", "python", "main.py"]
