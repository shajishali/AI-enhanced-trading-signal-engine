@echo off
echo Starting Celery Beat Scheduler...
celery -A ai_trading_engine beat -l info
pause
