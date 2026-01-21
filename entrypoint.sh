#!/bin/bash
set -e

echo "Starting application setup..."

mkdir -p logs

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Running tests..."
python manage.py test conversations.tests.conversation_service_tests conversations.tests.message_service_tests conversations.tests --noinput

if [ $? -eq 0 ]; then
    echo "All tests passed successfully!"
else
    echo "Tests failed. Exiting."
    exit 1
fi

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
