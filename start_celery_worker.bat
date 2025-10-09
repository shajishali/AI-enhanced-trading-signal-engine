@echo off
echo Starting Celery Worker...
celery -A ai_trading_engine worker -l info --pool=solo
pause
