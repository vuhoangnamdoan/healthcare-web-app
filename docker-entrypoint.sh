#!/bin/bash
# docker-entrypoint.sh

set -e

echo "Running database migrations..."
python manage.py migrate --settings=health_system.settings_production

echo "Creating initial doctors..."
python manage.py create_doctors --settings=health_system.settings_production

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=health_system.settings_production

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

echo "🚀 Starting Django server..."
exec "$@"