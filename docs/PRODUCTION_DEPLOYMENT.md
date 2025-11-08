# BSEE Production Deployment Guide

## Overview

This guide covers deploying the BSEE (Binary Structure Enhancement Engine) to production environments with AI-powered homogeneity optimization capabilities.

## 🚀 Quick Deployment

### Using Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd bsee

# Start the production environment
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BSEE_ENV=production
export BSEE_LOG_LEVEL=INFO

# Run the application
python main.py
```

## 🐳 Docker Configuration

### Production Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 bseeuser && chown -R bseeuser:bseeuser /app
USER bseeuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "main.py"]
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  bsee-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BSEE_ENV=production
      - BSEE_LOG_LEVEL=INFO
      - BSEE_DB_HOST=postgres
      - BSEE_REDIS_HOST=redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - bsee_models:/app/models
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=bsee
      - POSTGRES_USER=bsee
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - bsee-app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  bsee_models:
```

## 🔧 Environment Configuration

### Environment Variables

Create a `.env` file for production:

```bash
# Application Settings
BSEE_ENV=production
BSEE_DEBUG=false
BSEE_LOG_LEVEL=INFO
BSEE_PORT=8000

# Database Configuration
BSEE_DB_HOST=localhost
BSEE_DB_PORT=5432
BSEE_DB_NAME=bsee
BSEE_DB_USER=bsee
BSEE_DB_PASSWORD=secure_password

# Redis Configuration
BSEE_REDIS_HOST=localhost
BSEE_REDIS_PORT=6379
BSEE_REDIS_PASSWORD=redis_password

# AI Configuration
BSEE_AI_MODEL_PATH=/app/models
BSEE_AI_LEARNING_ENABLED=true
BSEE_AI_SAVE_INTERVAL=300

# Security
BSEE_SECRET_KEY=your-secret-key-here
BSEE_API_KEY_REQUIRED=false

# Performance
BSEE_MAX_WORKERS=4
BSEE_MEMORY_LIMIT=1GB
BSEE_TIMEOUT=30
```

### Configuration Files

#### `config/production.yaml`

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 30

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/app/logs/bsee.log"
  max_size: "100MB"
  backup_count: 5

database:
  host: "${BSEE_DB_HOST}"
  port: "${BSEE_DB_PORT}"
  name: "${BSEE_DB_NAME}"
  user: "${BSEE_DB_USER}"
  password: "${BSEE_DB_PASSWORD}"
  pool_size: 20
  max_overflow: 30

ai:
  enabled: true
  model_path: "${BSEE_AI_MODEL_PATH}"
  learning_enabled: true
  save_interval: 300
  cache_size: 1000

security:
  secret_key: "${BSEE_SECRET_KEY}"
  cors_origins: ["https://yourdomain.com"]
  rate_limiting:
    enabled: true
    requests_per_minute: 100

monitoring:
  metrics_enabled: true
  health_check_interval: 30
  performance_tracking: true
```

## 🔄 Deployment Process

### Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Database schema created
- [ ] SSL certificates installed
- [ ] Backup procedures in place
- [ ] Monitoring configured
- [ ] Log rotation setup
- [ ] Security settings reviewed
- [ ] Performance testing completed

### Deployment Steps

1. **Prepare Environment**
```bash
# Set production environment
export BSEE_ENV=production

# Create necessary directories
mkdir -p data logs models ssl
```

2. **Database Setup**
```bash
# Run database migrations
python scripts/migrate.py

# Create initial admin user
python scripts/create_admin.py
```

3. **Deploy Application**
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or manual deployment
pip install -r requirements.txt
python main.py
```

4. **Verify Deployment**
```bash
# Health check
curl http://localhost:8000/health

# Check AI system
curl http://localhost:8000/api/ai/status

# Test functionality
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"data": "SGVsbG8gV29ybGQ="}'
```

## 📊 Monitoring and Logging

### Application Monitoring

Configure monitoring with Prometheus:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bsee'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Log Management

Configure centralized logging:

```python
# config/logging.yaml
version: 1
disable_existing_loggers: false

formatters:
  production:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'

handlers:
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /app/logs/bsee.log
    maxBytes: 104857600  # 100MB
    backupCount: 5
    formatter: production

  json_file:
    class: logging.handlers.RotatingFileHandler
    filename: /app/logs/bsee.json
    maxBytes: 104857600  # 100MB
    backupCount: 5
    formatter: json

  syslog:
    class: logging.handlers.SysLogHandler
    address: /dev/log
    formatter: production

loggers:
  bsee:
    level: INFO
    handlers: [file, json_file, syslog]
    propagate: false

root:
  level: INFO
  handlers: [file]
```

### Health Checks

Implement comprehensive health checks:

```python
# health_check.py
from flask import Flask, jsonify
import psutil
import os

app = Flask(__name__)

@app.route('/health')
def health_check():
    checks = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': os.environ.get('BSEE_VERSION', 'unknown'),
        'checks': {}
    }

    # Check disk space
    disk_usage = psutil.disk_usage('/')
    checks['checks']['disk_space'] = {
        'status': 'healthy' if disk_usage.percent < 80 else 'warning',
        'usage_percent': disk_usage.percent
    }

    # Check memory
    memory = psutil.virtual_memory()
    checks['checks']['memory'] = {
        'status': 'healthy' if memory.percent < 80 else 'warning',
        'usage_percent': memory.percent
    }

    # Check AI system
    try:
        from bsee_ai import SimpleHomogeneityScorer
        scorer = SimpleHomogeneityScorer()
        test_score = scorer.calculate_score(b"test")
        checks['checks']['ai_system'] = {
            'status': 'healthy' if test_score >= 0 else 'error'
        }
    except Exception as e:
        checks['checks']['ai_system'] = {
            'status': 'error',
            'error': str(e)
        }

    overall_status = 'healthy'
    if any(check['status'] == 'error' for check in checks['checks'].values()):
        overall_status = 'unhealthy'
    elif any(check['status'] == 'warning' for check in checks['checks'].values()):
        overall_status = 'warning'

    checks['status'] = overall_status
    return jsonify(checks), 200 if overall_status == 'healthy' else 503
```

## 🔒 Security Configuration

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream bsee_backend {
        server bsee-app:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://bsee_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health {
            proxy_pass http://bsee_backend;
            access_log off;
        }
    }
}
```

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 🔄 Backup and Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/bsee"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/bsee_backup_$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application data
tar -czf $BACKUP_FILE \
    /app/data \
    /app/models \
    /app/logs \
    /app/config

# Backup database
pg_dump -h localhost -U bsee bsee > $BACKUP_DIR/database_$DATE.sql

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

### Recovery Procedure

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_BACKUP_FILE=$2

if [ -z "$BACKUP_FILE" ] || [ -z "$DB_BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file> <db_backup_file>"
    exit 1
fi

# Stop application
docker-compose down

# Restore application data
tar -xzf $BACKUP_FILE -C /

# Restore database
psql -h localhost -U bsee -d bsee < $DB_BACKUP_FILE

# Start application
docker-compose up -d

echo "Restore completed"
```

## 📈 Performance Optimization

### Production Tuning

```python
# config/production_tuning.py
import os

# Worker configuration
WORKERS = int(os.environ.get('BSEE_MAX_WORKERS', '4'))
THREADS = int(os.environ.get('BSEE_MAX_THREADS', '2'))

# Memory limits
MEMORY_LIMIT = os.environ.get('BSEE_MEMORY_LIMIT', '1GB')

# AI system optimization
AI_CACHE_SIZE = int(os.environ.get('BSEE_AI_CACHE_SIZE', '1000'))
AI_BATCH_SIZE = int(os.environ.get('BSEE_AI_BATCH_SIZE', '100'))

# Database optimization
DB_POOL_SIZE = int(os.environ.get('BSEE_DB_POOL_SIZE', '20'))
DB_MAX_OVERFLOW = int(os.environ.get('BSEE_DB_MAX_OVERFLOW', '30'))
```

### Load Balancing

```yaml
# docker-compose.lb.yml
version: '3.8'

services:
  bsee-app-1:
    build: .
    environment:
      - BSEE_WORKER_ID=1
    # ... other configuration

  bsee-app-2:
    build: .
    environment:
      - BSEE_WORKER_ID=2
    # ... other configuration

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.lb.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - bsee-app-1
      - bsee-app-2
```

## 🚨 Troubleshooting

### Common Issues

**High Memory Usage:**
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart

# Clear cache
redis-cli FLUSHALL
```

**Database Connection Issues:**
```bash
# Check database status
docker-compose exec postgres pg_isready

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**AI System Errors:**
```bash
# Check AI models
ls -la /app/models/

# Reset AI system
curl -X POST http://localhost:8000/api/ai/reset

# View AI logs
docker-compose logs bsee-app | grep AI
```

### Performance Debugging

```bash
# Monitor system resources
htop
iotop
nethogs

# Check application logs
docker-compose logs -f bsee-app

# Profile application
python -m cProfile -o profile.stats main.py
```

## 📋 Maintenance Tasks

### Daily Tasks

- Check application health
- Review error logs
- Monitor system resources
- Verify backup completion

### Weekly Tasks

- Update security patches
- Review performance metrics
- Clean old log files
- Update AI models

### Monthly Tasks

- Security audit
- Performance optimization review
- Capacity planning
- Disaster recovery testing

## 📞 Support

For production support:

1. Check health endpoints: `GET /health`
2. Review application logs
3. Monitor system metrics
4. Consult troubleshooting guide
5. Contact support team

---

This deployment guide ensures a robust, secure, and scalable production deployment of the BSEE system with AI-powered homogeneity optimization.