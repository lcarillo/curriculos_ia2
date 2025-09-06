#!/usr/bin/env bash
# build.sh

set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗃️ Applying database migrations..."
python manage.py migrate --no-input

echo "👤 Creating superuser..."
python create_superuser.py

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"