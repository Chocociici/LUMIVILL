#!/bin/bash
set -e

echo "🔄 Building ARMOR project for Render..."

# Create virtual environment and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run migrations
cd app0
python manage.py migrate
python manage.py collectstatic --noinput

echo "✅ Build complete!"
