# 🚀 Quick Start Guide - Signal Generation System

## ✅ **SYSTEM STATUS: FULLY OPERATIONAL**

All issues have been fixed! Your signal generation system is ready to use.

---

## 📋 **TO START AUTOMATIC SIGNAL GENERATION:**

### **Step 1: Verify Celery Worker is Running**
The Celery worker is already running in the background. To verify:
```bash
python -m celery -A ai_trading_engine inspect active
```

### **Step 2: Start Celery Beat Scheduler (REQUIRED)**
Open a new terminal and run:
```bash
.\start_celery_beat.bat
```
**Keep this window open** - it must run continuously for automatic signal generation.

---

## 🎯 **HOW IT WORKS**

Once Celery Beat is running:
- **Every 5 minutes:** Fresh market data is fetched
- **Every hour (at XX:00):** New trading signals are generated
- **Every 10 minutes:** Sentiment analysis updates
- **Daily at 2 AM:** Old data is cleaned up

---

## 🔍 **QUICK CHECKS**

### **Check Active Signals:**
```bash
python manage.py shell -c "from apps.signals.models import TradingSignal; print(f'Active signals: {TradingSignal.objects.filter(is_valid=True).count()}')"
```

### **Check System Status:**
```bash
python manage.py system_status
```

### **Test Signal Generation Manually:**
```bash
python manage.py shell -c "from apps.signals.services import SignalGenerationService; from apps.trading.models import Symbol; service = SignalGenerationService(); symbol = Symbol.objects.get(symbol='BTC'); signals = service.generate_signals_for_symbol(symbol); print(f'Generated {len(signals)} signals')"
```

---

## 📊 **CURRENT STATUS**

✅ **Celery Worker:** Running in background  
✅ **Market Data:** Fresh (229 symbols updated)  
✅ **Technical Indicators:** Calculated (3,947 indicators)  
✅ **Signal Generation:** Verified working (BTC test passed)  
⚠️ **Celery Beat:** Needs manual start (see Step 2 above)

---

## 🎯 **EXPECTED BEHAVIOR**

Once Celery Beat starts:
1. Wait until the top of the next hour (e.g., 15:00, 16:00)
2. Celery will automatically run `generate_signals_for_all_symbols`
3. Top 5 best signals will be saved to database
4. Old signals will be archived
5. Check active signals to see the results

---

## ⚡ **TROUBLESHOOTING**

### **If No Signals Generate:**
1. Check Celery worker is running: `python -m celery -A ai_trading_engine inspect active`
2. Check Celery beat is running (should see beat scheduler output)
3. Check market data is fresh: `python manage.py system_status`
4. Check logs for errors

### **If Celery Worker Stops:**
Restart it:
```bash
python -m celery -A ai_trading_engine worker -l info --pool=solo --detach
```

### **If Market Data is Stale:**
Update manually:
```bash
python manage.py shell -c "from apps.data.tasks import update_crypto_prices; update_crypto_prices()"
```

---

## 📝 **IMPORTANT NOTES**

- **Symbols:** Use base symbols like `BTC`, `ETH` (not `BTCUSDT`, `ETHUSDT`)
- **Signal Limit:** System keeps only TOP 5 best signals at any time
- **Automatic:** Everything runs automatically once Celery Beat is started
- **Monitoring:** Check `python manage.py system_status` regularly

---

## 🎉 **YOU'RE READY!**

Your AI Trading Engine is fully operational. Just start Celery Beat and watch the signals generate automatically!

**Start Now:**
```bash
.\start_celery_beat.bat
```

---

**For detailed information, read:** `SIGNAL_GENERATION_COMPLETE_FIX_SUMMARY.md`



































































