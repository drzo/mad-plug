# Deployment Guide
## AI Chatbot Management Platform - Production Deployment

**Version**: 2.0.0  
**Last Updated**: January 30, 2026  
**Target Environment**: Production

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Application Deployment](#application-deployment)
5. [Storage Configuration](#storage-configuration)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Logging](#monitoring--logging)
8. [Performance Optimization](#performance-optimization)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### System Requirements

#### Hardware (Minimum)
- **CPU**: 2 cores (4 cores recommended)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 20GB SSD (50GB+ recommended)
- **Network**: 100 Mbps connection

#### Hardware (Production)
- **CPU**: 4+ cores
- **RAM**: 16GB+
- **Storage**: 100GB+ SSD with RAID
- **Network**: 1 Gbps connection

#### Software
- **Node.js**: v18.x or v20.x LTS
- **pnpm**: v10.4.1 or higher
- **MySQL**: v8.0+
- **Redis**: v7.x (optional, for caching)
- **nginx**: v1.24+ (for reverse proxy)

### Cloud Provider Options

#### AWS
- **EC2**: t3.medium or larger
- **RDS**: MySQL 8.0 (db.t3.small or larger)
- **S3**: For file storage
- **CloudFront**: For CDN
- **ElastiCache**: For Redis (optional)

#### Google Cloud Platform
- **Compute Engine**: n2-standard-2 or larger
- **Cloud SQL**: MySQL 8.0
- **Cloud Storage**: For file storage
- **Cloud CDN**: For content delivery

#### Azure
- **Virtual Machines**: B2s or larger
- **Azure Database for MySQL**: Flexible Server
- **Blob Storage**: For file storage
- **Azure CDN**: For content delivery

#### Self-Hosted
- **Docker**: v24.0+
- **Docker Compose**: v2.20+
- **Linux**: Ubuntu 22.04 LTS or similar

---

## 🔧 Environment Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/o9nn/cbase.git
cd cbase

# Checkout specific version (recommended for production)
git checkout tags/v2.0.0
```

### 2. Install Dependencies

```bash
# Install pnpm if not already installed
npm install -g pnpm@10.4.1

# Install project dependencies
pnpm install --frozen-lockfile
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```bash
# Application
NODE_ENV=production
PORT=3000
BASE_URL=https://yourdomain.com

# Database
DATABASE_URL=mysql://username:password@host:3306/database_name

# Authentication
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
SESSION_SECRET=your-super-secret-session-key-min-32-chars
COOKIE_DOMAIN=yourdomain.com

# OpenAI / LLM API
FORGE_API_KEY=your-api-key-here
FORGE_API_URL=https://api.openai.com/v1  # or custom endpoint

# Embeddings API (if different from LLM API)
EMBEDDING_API_KEY=your-embedding-api-key
EMBEDDING_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

# AWS S3 Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
S3_PUBLIC_URL=https://your-bucket.s3.amazonaws.com

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Monitoring (optional)
SENTRY_DSN=https://your-sentry-dsn
DATADOG_API_KEY=your-datadog-api-key

# Rate Limiting
RATE_LIMIT_WINDOW=60000  # 1 minute in ms
RATE_LIMIT_MAX=100  # max requests per window

# Security
CORS_ORIGIN=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. Generate Secrets

```bash
# Generate secure random strings for secrets
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Use this output for JWT_SECRET and SESSION_SECRET
```

---

## 🗄️ Database Configuration

### 1. Create Database

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE cbase_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'cbase_user'@'%' IDENTIFIED BY 'secure_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON cbase_production.* TO 'cbase_user'@'%';
FLUSH PRIVILEGES;
```

### 2. Run Migrations

```bash
# Generate migrations (if schema changed)
pnpm run db:push

# Or run existing migrations
npx drizzle-kit migrate
```

### 3. Verify Database

```bash
# Connect and verify tables
mysql -u cbase_user -p cbase_production

SHOW TABLES;
# Should show: agents, chatSessions, chatMessages, knowledgeSources, 
#              knowledgeEmbeddings, trainingJobs, users, etc.

# Check indexes
SHOW INDEXES FROM agents;
```

### 4. Database Optimization

```sql
-- For production, set optimal configuration
-- Note: These settings should be added to my.cnf or my.ini for persistence
-- Temporary session settings:
SET GLOBAL innodb_buffer_pool_size = 2147483648;  -- 2GB
SET GLOBAL max_connections = 200;

-- Enable slow query log for monitoring
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- For permanent settings, add to my.cnf (Linux) or my.ini (Windows):
-- [mysqld]
-- innodb_buffer_pool_size = 2G
-- max_connections = 200
-- slow_query_log = 1
-- long_query_time = 2
```

---

## 🚀 Application Deployment

### Method 1: Direct Deployment (PM2)

#### 1. Build Application

```bash
# Build frontend and backend
pnpm run build

# Output:
# - dist/index.js (backend)
# - client/dist/* (frontend static files)
```

#### 2. Install PM2

```bash
npm install -g pm2
```

#### 3. Create PM2 Ecosystem File

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'cbase-app',
    script: './dist/index.js',
    instances: 'max',  // Use all CPU cores
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    max_memory_restart: '1G'
  }]
};
```

#### 4. Start Application

```bash
# Start with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 startup script
pm2 startup
# Follow the instructions printed
```

#### 5. Manage Application

```bash
# Status
pm2 status

# Logs
pm2 logs cbase-app

# Restart
pm2 restart cbase-app

# Stop
pm2 stop cbase-app

# Monitor
pm2 monit
```

### Method 2: Docker Deployment

#### 1. Create Dockerfile

Create `Dockerfile`:

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@10.4.1

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN pnpm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@10.4.1

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install production dependencies only
RUN pnpm install --prod --frozen-lockfile

# Copy built application
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/client/dist ./client/dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start application
CMD ["node", "dist/index.js"]
```

#### 2. Create Docker Compose File

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      DATABASE_URL: mysql://cbase_user:password@db:3306/cbase_production
      REDIS_URL: redis://redis:6379
    env_file:
      - .env
    depends_on:
      - db
      - redis
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: CHANGE_THIS_ROOT_PASSWORD
      MYSQL_DATABASE: cbase_production
      MYSQL_USER: cbase_user
      MYSQL_PASSWORD: CHANGE_THIS_USER_PASSWORD
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
    command: --default-authentication-plugin=mysql_native_password

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

#### 3. Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Method 3: Kubernetes Deployment

#### 1. Create Kubernetes Manifests

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cbase-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cbase-app
  template:
    metadata:
      labels:
        app: cbase-app
    spec:
      containers:
      - name: cbase-app
        image: your-registry/cbase:2.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: cbase-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: cbase-service
spec:
  selector:
    app: cbase-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

#### 2. Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace cbase-prod

# Create secrets
kubectl create secret generic cbase-secrets \
  --from-literal=database-url='mysql://...' \
  --namespace=cbase-prod

# Apply manifests
kubectl apply -f k8s/ --namespace=cbase-prod

# Check status
kubectl get pods --namespace=cbase-prod
kubectl get services --namespace=cbase-prod
```

---

## 📦 Storage Configuration

### AWS S3 Setup

#### 1. Create S3 Bucket

```bash
aws s3 mb s3://your-cbase-bucket --region us-east-1
```

#### 2. Configure Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-cbase-bucket/public/*"
    }
  ]
}
```

#### 3. Enable CORS

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["https://yourdomain.com"],
    "ExposeHeaders": ["ETag"]
  }
]
```

#### 4. Configure Lifecycle Rules

```json
{
  "Rules": [
    {
      "Id": "Delete-temp-files",
      "Status": "Enabled",
      "Prefix": "temp/",
      "Expiration": {
        "Days": 7
      }
    },
    {
      "Id": "Archive-old-exports",
      "Status": "Enabled",
      "Prefix": "exports/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

### Alternative: Local Storage

For self-hosted deployments without S3:

```typescript
// server/storage.ts
// Configure local file storage
export const storageConfig = {
  type: 'local',
  basePath: '/var/app/storage',
  publicUrl: 'https://yourdomain.com/files'
};
```

---

## 🔒 Security Hardening

### 1. nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    upstream backend {
        server app:3000;
        keepalive 32;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API rate limiting
        location /api {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location / {
            limit_req zone=general_limit burst=50 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Health check
        location /health {
            access_log off;
            proxy_pass http://backend;
        }
    }
}
```

### 2. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

### 3. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Or iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### 4. Database Security

```sql
-- Remove default test database
DROP DATABASE IF EXISTS test;

-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Disallow root login remotely
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Reload privileges
FLUSH PRIVILEGES;
```

---

## 📊 Monitoring & Logging

### 1. Application Logging

```typescript
// server/_core/logger.ts
import winston from 'winston';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});
```

### 2. PM2 Monitoring

```bash
# Install PM2 monitoring
pm2 install pm2-logrotate

# Configure log rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
```

### 3. Health Check Endpoint

```typescript
// server/_core/health.ts
export async function healthCheck() {
  try {
    // Check database
    await db.select().from(agents).limit(1);
    
    // Check Redis (if used)
    if (redis) {
      await redis.ping();
    }
    
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error.message
    };
  }
}
```

### 4. External Monitoring

#### Uptime Monitoring
- **UptimeRobot**: https://uptimerobot.com
- **Pingdom**: https://www.pingdom.com
- **StatusCake**: https://www.statuscake.com

#### APM (Application Performance Monitoring)
- **Datadog**: https://www.datadoghq.com
- **New Relic**: https://newrelic.com
- **AppDynamics**: https://www.appdynamics.com

#### Error Tracking
- **Sentry**: https://sentry.io
- **Rollbar**: https://rollbar.com
- **Bugsnag**: https://www.bugsnag.com

---

## ⚡ Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_chat_sessions_agent ON chatSessions(agentId);
CREATE INDEX idx_chat_messages_session ON chatMessages(sessionId);
CREATE INDEX idx_knowledge_sources_agent ON knowledgeSources(agentId, status);
CREATE INDEX idx_knowledge_embeddings_agent ON knowledgeEmbeddings(agentId);

-- Optimize tables
OPTIMIZE TABLE agents;
OPTIMIZE TABLE chatMessages;
OPTIMIZE TABLE knowledgeEmbeddings;
```

### 2. Enable Caching

```typescript
// server/_core/cache.ts
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export async function getCached<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 3600
): Promise<T> {
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }
  
  const data = await fetcher();
  await redis.setex(key, ttl, JSON.stringify(data));
  return data;
}
```

### 3. CDN Configuration

#### CloudFlare
1. Add your domain to CloudFlare
2. Enable CDN caching
3. Configure cache rules
4. Enable Brotli compression
5. Enable HTTP/3

#### AWS CloudFront
1. Create CloudFront distribution
2. Set origin to your domain
3. Configure cache behaviors
4. Enable compression
5. Configure SSL certificate

### 4. Code Optimization

```bash
# Production build optimizations are already configured in vite.config.ts
# - Minification
# - Tree shaking
# - Code splitting
# - Asset optimization

# Verify build size
pnpm run build
du -sh client/dist
```

---

## 💾 Backup & Recovery

### 1. Database Backup

#### Automated Daily Backups

Create `backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="cbase_production"
DB_USER="cbase_user"

# ⚠️ SECURITY: Store password in .my.cnf instead of hardcoding
# Create ~/.my.cnf with:
# [client]
# user=cbase_user
# password=your_secure_password

mkdir -p $BACKUP_DIR

# Create backup (reads credentials from ~/.my.cnf)
mysqldump --defaults-extra-file=~/.my.cnf $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Or use environment variable
# mysqldump -u $DB_USER -p"${MYSQL_PASSWORD}" $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-bucket/backups/
```

#### Schedule with cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup-db.sh
```

### 2. Application Backup

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/app"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/var/www/cbase"

mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C $APP_DIR .

# Backup environment variables
cp $APP_DIR/.env $BACKUP_DIR/env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -name "app_*.tar.gz" -mtime +7 -delete
```

### 3. Disaster Recovery Plan

#### Recovery Steps
1. **Restore Database**
   ```bash
   gunzip < backup_20260130.sql.gz | mysql -u cbase_user -p cbase_production
   ```

2. **Restore Application**
   ```bash
   tar -xzf app_20260130.tar.gz -C /var/www/cbase
   ```

3. **Restore Environment**
   ```bash
   cp env_20260130 /var/www/cbase/.env
   ```

4. **Restart Services**
   ```bash
   pm2 restart all
   # or
   docker-compose restart
   ```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue: Application Won't Start

```bash
# Check logs
pm2 logs cbase-app
# or
docker-compose logs app

# Common causes:
# - Port already in use
# - Database connection failed
# - Missing environment variables
# - Permission issues
```

#### Issue: Database Connection Failed

```bash
# Test database connection
mysql -u cbase_user -p -h localhost cbase_production

# Check if MySQL is running
sudo systemctl status mysql

# Check connection from app server
telnet db-host 3306
```

#### Issue: High Memory Usage

```bash
# Check memory usage
free -h
pm2 monit

# Restart application
pm2 restart cbase-app --update-env

# Check for memory leaks in logs
pm2 logs cbase-app | grep "memory"
```

#### Issue: Slow Performance

```bash
# Check database slow queries
mysql -u root -p -e "SELECT * FROM mysql.slow_log LIMIT 10;"

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "https://yourdomain.com/api/health"

# Check system load
top
htop
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
pm2 restart cbase-app --update-env

# View debug logs
pm2 logs cbase-app --lines 100
```

---

## 📝 Post-Deployment Checklist

- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Backup scripts scheduled
- [ ] Monitoring enabled
- [ ] Health checks passing
- [ ] DNS configured
- [ ] CDN configured (if using)
- [ ] Load testing completed
- [ ] Security scan completed
- [ ] Error tracking configured
- [ ] Documentation updated
- [ ] Team notified
- [ ] Rollback plan documented

---

## 📞 Support

### Getting Help
- **Documentation**: https://github.com/o9nn/cbase/tree/main/docs
- **Issues**: https://github.com/o9nn/cbase/issues
- **Email**: support@example.com

---

*Deployment Guide v2.0.0 - Last Updated: January 30, 2026*
