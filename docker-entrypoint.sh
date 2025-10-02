#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate

echo "Collecting static files (including admin)..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser if needed..."
if [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
"
fi

echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000
