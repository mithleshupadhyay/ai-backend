#!/bin/bash

echo "Select what to run:"
echo "1. Start FastAPI"
echo "2. Start Celery Worker"
echo "3. Start Gradio Demo"
echo "4. Flush Redis"
read -p "Choice: " choice

case $choice in
    1) PYTHONPATH=. uvicorn services.main:app --reload --host=0.0.0.0 --port=8000 ;;
    2) PYTHONPATH=. celery -A services.main.celery_app worker --loglevel=info ;;
    3) python demo/demo.py ;;
    4) redis-cli flushall ;;
    *) echo "Invalid choice" ;;
esac
