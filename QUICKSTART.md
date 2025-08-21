# 🚀 AI Trading Engine - Quick Start Guide

## ⚡ **Get Started in 3 Simple Steps**

---

## **Step 1: Start Your Project** 🚀

```bash
# 1. Open PowerShell in your project directory
cd "D:\Research Development"

# 2. Activate the virtual environment
venv\Scripts\Activate.ps1

# 3. Start the Django server
python manage.py runserver 0.0.0.0:8000
```

**✅ Success!** Your server is now running at: **http://localhost:8000/**

---

## **Step 2: Access Your Application** 🌐

### **Main Pages:**
- **🏠 Homepage**: http://localhost:8000/
- **📊 Dashboard**: http://localhost:8000/dashboard/
- **📈 Trading Signals**: http://localhost:8000/signals/
- **🔍 Analytics**: http://localhost:8000/analytics/
- **💼 Portfolio**: http://localhost:8000/dashboard/portfolio/
- **⚙️ Admin Panel**: http://localhost:8000/admin/

---

## **Step 3: Use Your Trading Platform** 💹

### **🎯 What You Can Do Right Now:**

1. **View Trading Signals** - AI-generated buy/sell recommendations
2. **Analyze Markets** - Real-time market data and trends
3. **Manage Portfolio** - Track your trading positions
4. **Monitor Performance** - View your trading results
5. **Access ML Insights** - Machine learning predictions
6. **Use Risk Tools** - Advanced risk management features

---

## 🔧 **API Endpoints (For Developers)**

```bash
# Get all trading signals
GET /signals/api/signals/

# Get signal statistics
GET /signals/api/statistics/

# Execute a trading signal
POST /signals/api/signals/{id}/execute/

# Get performance metrics
GET /core/api/performance/
```

---

## 📱 **Quick Commands Reference**

```bash
# Check project status
python manage.py check

# View database migrations
python manage.py showmigrations

# Create admin user (if needed)
python manage.py createsuperuser

# Stop server
# Press Ctrl+C in the terminal
```

---

## 🎉 **You're All Set!**

Your AI Trading Engine is now **fully operational** with:

- ✅ **Complete trading platform**
- ✅ **AI-powered signals**
- ✅ **Real-time analytics**
- ✅ **Professional dashboard**
- ✅ **Production-ready performance**

---

## 🆘 **Need Help?**

- **Server won't start?** Check if port 8000 is free
- **Can't access pages?** Make sure server is running
- **Database issues?** Run `python manage.py check`
- **Performance slow?** Check the performance API at `/core/api/performance/`

---

**🚀 Your AI Trading Engine is ready to trade! Open http://localhost:8000/ and start exploring!**
