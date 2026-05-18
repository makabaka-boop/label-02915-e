#!/bin/sh
echo "Waiting for MySQL to be ready..."
sleep 5

echo "Downloading product images..."
python generate_images.py || echo "Warning: image generation had issues, continuing..."

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 9999
