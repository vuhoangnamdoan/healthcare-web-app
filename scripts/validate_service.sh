#!/bin/bash
# Wait up to 30 seconds for the backend service to respond on port 8000
for i in {1..30}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$STATUS" -eq 200 ]; then
        echo "Application started successfully."
        exit 0
    fi
    echo "Waiting for application to start..."
    sleep 1
done

echo "Application failed to start within 30 seconds."
exit 1
