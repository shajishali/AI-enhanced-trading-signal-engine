# AI Trading Engine - Production Deployment Guide

This guide provides comprehensive instructions for deploying the AI Trading Engine to a production environment.

## Overview

The production deployment includes:
- **WSGI Server**: Gunicorn with multiple workers
- **Web Server**: Nginx with SSL/TLS and load balancing
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis for sessions and caching
- **Process Management**: Supervisor for service orchestration
- **Monitoring**: Health checks and performance monitoring
- **Security**: Firewall, fail2ban, and SSL certificates

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04 LTS or later
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB, Recommended 50GB+
- **CPU**: 2+ cores recommended
- **Network**: Stable internet connection

### Software Requirements
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Nginx 1.18+
- Supervisor 4.0+

## Installation Steps

### 1. System Preparation

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install essential packages
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    libssl-dev \
    libffi-dev
```

### 2. Project Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-trading-engine.git
cd ai-trading-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE ai_trading_engine_prod;"
sudo -u postgres psql -c "CREATE USER trading_user WITH PASSWORD 'your-secure-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_trading_engine_prod TO trading_user;"
sudo -u postgres psql -c "ALTER USER trading_user CREATEDB;"
```

### 4. Redis Setup

```bash
# Install Redis
sudo apt-get install -y redis-server

# Configure Redis
sudo cp redis.conf /etc/redis/redis.conf
sudo systemctl enable redis-server
sudo systemctl restart redis-server
```

### 5. Environment Configuration

```bash
# Copy production environment file
cp env.production .env.production

# Edit environment variables
nano .env.production

# Key variables to update:
# - SECRET_KEY
# - DB_PASSWORD
# - REDIS_PASSWORD
# - ALLOWED_HOSTS
# - CORS_ALLOWED_ORIGINS
```

### 6. Django Configuration

```bash
# Set production settings
export DJANGO_SETTINGS_MODULE=ai_trading_engine.settings_production

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Deployment

### 1. Automated Deployment

```bash
# Make deployment script executable
chmod +x deploy_production.sh

# Run deployment script
./deploy_production.sh
```

### 2. Manual Deployment

#### Gunicorn Configuration
```bash
# Copy Gunicorn config
sudo cp gunicorn.conf.py /etc/gunicorn/

# Test configuration
gunicorn --config gunicorn.conf.py ai_trading_engine.wsgi:application
```

#### Nginx Configuration
```bash
# Copy Nginx config
sudo cp nginx.conf /etc/nginx/sites-available/ai_trading_engine

# Enable site
sudo ln -s /etc/nginx/sites-available/ai_trading_engine /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Supervisor Configuration
```bash
# Copy Supervisor config
sudo cp supervisor.conf /etc/supervisor/conf.d/ai_trading_engine.conf

# Update Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 3. SSL Certificate Setup

#### Self-Signed Certificate (Development)
```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/ai_trading_engine.key \
    -out /etc/ssl/certs/ai_trading_engine.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# Set permissions
sudo chmod 600 /etc/ssl/private/ai_trading_engine.key
sudo chmod 644 /etc/ssl/certs/ai_trading_engine.crt
```

#### Let's Encrypt Certificate (Production)
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Health Checks

### 1. Health Check Command

```bash
# Run comprehensive health checks
python manage.py health_check

# JSON format output
python manage.py health_check --format json

# Critical issues only
python manage.py health_check --critical-only
```

### 2. Service Status

```bash
# Check all services
sudo supervisorctl status

# Check specific service
sudo supervisorctl status ai_trading_gunicorn

# View logs
sudo tail -f /var/log/supervisor/gunicorn.log
```

### 3. Performance Monitoring

```bash
# System resources
htop
iotop
nethogs

# Application logs
tail -f logs/trading_engine_prod.log
tail -f logs/errors_prod.log
```

## Security Configuration

### 1. Firewall Setup

```bash
# Enable UFW
sudo ufw --force enable

# Configure rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000:8002

# Check status
sudo ufw status
```

### 2. Fail2ban Configuration

```bash
# Install fail2ban
sudo apt-get install -y fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
```

### 3. Security Headers

The Nginx configuration includes:
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Content Security Policy
- Referrer Policy

## Performance Optimization

### 1. Database Optimization

```bash
# PostgreSQL tuning
sudo nano /etc/postgresql/*/main/postgresql.conf

# Key settings:
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 4MB
# maintenance_work_mem = 64MB
```

### 2. Redis Optimization

```bash
# Redis tuning
sudo nano /etc/redis/redis.conf

# Key settings:
# maxmemory 256mb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# save 60 10000
```

### 3. Nginx Optimization

```bash
# Nginx tuning
sudo nano /etc/nginx/nginx.conf

# Key settings:
# worker_processes auto;
# worker_connections 1024;
# keepalive_timeout 65;
# gzip on;
# gzip_comp_level 6;
```

## Maintenance & Updates

### 1. Application Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo supervisorctl restart all
```

### 2. Database Backups

```bash
# Create backup
pg_dump ai_trading_engine_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql ai_trading_engine_prod < backup_file.sql
```

### 3. Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/ai_trading_engine

# Configuration:
/var/log/ai_trading_engine/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
sudo tail -f /var/log/supervisor/*.log

# Check configuration
sudo supervisorctl reread
sudo supervisorctl update

# Restart supervisor
sudo systemctl restart supervisor
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
sudo -u postgres psql -c "SELECT version();"

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 3. Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Check access logs
sudo tail -f /var/log/nginx/access.log
```

#### 4. SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in /etc/ssl/certs/ai_trading_engine.crt -text -noout

# Check certificate expiration
openssl x509 -in /etc/ssl/certs/ai_trading_engine.crt -noout -dates

# Renew Let's Encrypt certificate
sudo certbot renew
```

### Performance Issues

#### 1. High CPU Usage
```bash
# Check process usage
top
htop

# Check specific processes
ps aux | grep gunicorn
ps aux | grep celery
```

#### 2. High Memory Usage
```bash
# Check memory usage
free -h
vmstat 1 10

# Check for memory leaks
sudo journalctl -u supervisor -f
```

#### 3. Slow Response Times
```bash
# Check database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check Redis performance
redis-cli info memory
redis-cli info stats
```

## Scaling Considerations

### 1. Horizontal Scaling

- **Load Balancer**: Use HAProxy or Nginx Plus
- **Multiple Servers**: Deploy across multiple instances
- **Database Clustering**: PostgreSQL read replicas
- **Redis Cluster**: Multiple Redis instances

### 2. Vertical Scaling

- **CPU**: Increase CPU cores
- **Memory**: Add more RAM
- **Storage**: Use SSD storage
- **Network**: Optimize network configuration

### 3. Monitoring & Alerting

- **Application Monitoring**: New Relic, Datadog
- **Infrastructure Monitoring**: Prometheus, Grafana
- **Log Aggregation**: ELK Stack, Fluentd
- **Alerting**: PagerDuty, Slack, Email

## Security Best Practices

### 1. Regular Updates
- Keep system packages updated
- Monitor security advisories
- Regular security audits
- Penetration testing

### 2. Access Control
- Use SSH keys instead of passwords
- Implement two-factor authentication
- Regular user access reviews
- Principle of least privilege

### 3. Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Regular backup encryption
- Data retention policies

## Additional Resources

### Documentation
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tools
- [Certbot](https://certbot.eff.org/) - SSL certificates
- [Supervisor](http://supervisord.org/) - Process management
- [Fail2ban](https://www.fail2ban.org/) - Intrusion prevention
- [UFW](https://help.ubuntu.com/community/UFW) - Firewall

### Support
- [GitHub Issues](https://github.com/yourusername/ai-trading-engine/issues)
- [Community Forum](https://community.yourdomain.com)
- [Documentation Wiki](https://wiki.yourdomain.com)

---

## Deployment Checklist

- [ ] System packages updated
- [ ] Python dependencies installed
- [ ] Database configured and migrated
- [ ] Redis configured and running
- [ ] Environment variables set
- [ ] Static files collected
- [ ] Gunicorn configured and tested
- [ ] Nginx configured and tested
- [ ] SSL certificates installed
- [ ] Supervisor configured
- [ ] Firewall configured
- [ ] Fail2ban configured
- [ ] Health checks passing
- [ ] Performance tests completed
- [ ] Monitoring configured
- [ ] Backup system configured
- [ ] Documentation updated
- [ ] Team trained on deployment

---

**Last Updated**: August 21, 2025  
**Version**: 1.0.0  
**Author**: AI Trading Engine Team
