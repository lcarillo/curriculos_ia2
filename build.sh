#!/usr/bin/env bash
set -o errexit

echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "🗃️ Applying database migrations..."
python manage.py migrate --no-input

echo "👤 Creating superuser..."
python create_superuser.py

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "📥 Downloading spaCy models..."
python -m spacy download pt_core_news_sm
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm

echo "✅ Build completed successfully!"
