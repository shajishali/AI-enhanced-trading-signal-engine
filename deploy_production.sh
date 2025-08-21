#!/bin/bash

# AI Trading Engine Production Deployment Script
# This script automates the production deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai_trading_engine"
PROJECT_DIR="/path/to/your/project"
VENV_DIR="/path/to/your/venv"
USER="www-data"
GROUP="www-data"

# Logging
LOG_FILE="/var/log/deployment.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${BLUE}=== AI Trading Engine Production Deployment ===${NC}"
echo "Deployment started at: $(date)"
echo "Project directory: $PROJECT_DIR"
echo "Virtual environment: $VENV_DIR"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if service is running
service_running() {
    systemctl is-active --quiet "$1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root"
    exit 1
fi

# Check if project directory exists
if [[ ! -d "$PROJECT_DIR" ]]; then
    print_error "Project directory $PROJECT_DIR does not exist"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "$VENV_DIR" ]]; then
    print_error "Virtual environment $VENV_DIR does not exist"
    exit 1
fi

print_status "Prerequisites check passed"

# Update system packages
print_status "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
print_status "Installing required system packages..."
sudo apt-get install -y \
    nginx \
    redis-server \
    postgresql \
    postgresql-contrib \
    supervisor \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    htop \
    iotop \
    nethogs

# Install Python packages
print_status "Installing Python packages..."
source "$VENV_DIR/bin/activate"
cd "$PROJECT_DIR"
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
print_status "Creating necessary directories..."
sudo mkdir -p /var/log/ai_trading_engine
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/log/supervisor
sudo mkdir -p /var/log/nginx
sudo mkdir -p /backups
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R $USER:$GROUP /var/log/ai_trading_engine
sudo chown -R $USER:$GROUP /var/log/gunicorn
sudo chown -R $USER:$GROUP /var/log/supervisor
sudo chown -R $USER:$GROUP /backups
sudo chmod 755 /var/log/ai_trading_engine
sudo chmod 755 /var/log/gunicorn
sudo chmod 755 /var/log/supervisor
sudo chmod 755 /backups

# Configure PostgreSQL
print_status "Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE ai_trading_engine_prod;"
sudo -u postgres psql -c "CREATE USER trading_user WITH PASSWORD 'your-secure-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_trading_engine_prod TO trading_user;"
sudo -u postgres psql -c "ALTER USER trading_user CREATEDB;"

# Configure Redis
print_status "Configuring Redis..."
sudo cp "$PROJECT_DIR/redis.conf" /etc/redis/redis.conf
sudo systemctl enable redis-server
sudo systemctl restart redis-server

# Configure Nginx
print_status "Configuring Nginx..."
sudo cp "$PROJECT_DIR/nginx.conf" /etc/nginx/sites-available/ai_trading_engine
sudo ln -sf /etc/nginx/sites-available/ai_trading_engine /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# Configure Supervisor
print_status "Configuring Supervisor..."
sudo cp "$PROJECT_DIR/supervisor.conf" /etc/supervisor/conf.d/ai_trading_engine.conf
sudo mkdir -p /var/log/supervisor
sudo systemctl enable supervisor
sudo systemctl restart supervisor

# Generate SSL certificate (self-signed for testing)
print_status "Generating SSL certificate..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/ai_trading_engine.key \
    -out /etc/ssl/certs/ai_trading_engine.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# Set SSL permissions
sudo chmod 600 /etc/ssl/private/ai_trading_engine.key
sudo chmod 644 /etc/ssl/certs/ai_trading_engine.crt

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000:8002
sudo ufw allow 5555  # Celery Flower
sudo ufw status

# Configure fail2ban
print_status "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# Collect static files
print_status "Collecting static files..."
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"
export DJANGO_SETTINGS_MODULE=ai_trading_engine.settings_production
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser (optional)
print_warning "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

# Start services
print_status "Starting services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# Health check
print_status "Performing health check..."
sleep 10

# Check if services are running
if sudo supervisorctl status | grep -q "RUNNING"; then
    print_status "All services are running successfully"
else
    print_error "Some services failed to start"
    sudo supervisorctl status
    exit 1
fi

# Test Nginx
if curl -k -s https://localhost/health/ | grep -q "healthy"; then
    print_status "Nginx is working correctly"
else
    print_error "Nginx health check failed"
    exit 1
fi

# Performance test
print_status "Running performance test..."
ab -n 100 -c 10 https://localhost/health/ > /tmp/performance_test.log 2>&1 || true

# Final status
print_status "Deployment completed successfully!"
echo "Services status:"
sudo supervisorctl status
echo ""
echo "Nginx status:"
sudo systemctl status nginx --no-pager -l
echo ""
echo "Redis status:"
sudo systemctl status redis-server --no-pager -l
echo ""
echo "PostgreSQL status:"
sudo systemctl status postgresql --no-pager -l
echo ""
echo "Firewall status:"
sudo ufw status
echo ""
echo "SSL certificate info:"
openssl x509 -in /etc/ssl/certs/ai_trading_engine.crt -text -noout | grep -E "(Subject:|Not Before:|Not After:)"
echo ""
echo "Deployment log: $LOG_FILE"
echo "Deployment completed at: $(date)"

# Optional: Open ports for external access
print_warning "Do you want to open ports for external access? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    print_status "Opening ports for external access..."
    sudo ufw allow from any to any port 80
    sudo ufw allow from any to any port 443
    sudo ufw reload
    print_status "External access enabled"
fi

print_status "Production deployment completed successfully!"
print_status "Your AI Trading Engine is now running in production mode"
print_status "Access your application at: https://yourdomain.com"
print_status "Monitor services with: sudo supervisorctl status"
print_status "View logs with: sudo tail -f /var/log/supervisor/*.log"
