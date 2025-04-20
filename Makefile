api:
	@echo "🚀 Starting FastAPI..."
	PYTHONPATH=. uvicorn services.main:app --reload --host 0.0.0.0 --port=8000

worker:
	@echo "👷 Starting Celery..."
	PYTHONPATH=. celery -A services.main.celery_app worker --loglevel=info

gradio:
	@echo "💬 Launching Gradio UI..."
	cd demo && python demo.py

flush:
	@echo "🧹 Flushing Redis cache..."
	redis-cli flushall

dev: api worker gradio


menu:
	@bash ./start.sh
