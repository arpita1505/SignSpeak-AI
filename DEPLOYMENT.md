# Deployment Guide

## Production Deployment

SignSpeak AI is designed as a single containerized service suitable for deployment on any Docker-compatible hosting platform.

The production image includes the verified model artifact and built frontend. Do not mount raw
training images into the runtime container. Remote camera access requires HTTPS. A public deployment
is not claimed until the service has been created and verified in the owner's authenticated account.

## Prerequisites

- Docker and Docker Compose
- Trained ML model (`artifacts/signspeak_model.joblib`)
- GitHub repository with code pushed

## Local Docker Testing

### Build Image

```bash
docker build -t signspeak-ai:latest .
```

### Run Container

```bash
docker run \
  -p 8000:8000 \
  -e PORT=8000 \
  -e APP_ENV=production \
  signspeak-ai:latest
```

### Test with Docker Compose

```bash
docker compose up --build
```

Access: http://localhost:8000

### Smoke Test

```bash
./scripts/smoke_test.sh
```

Expected output:
```
✅ Application is ready!
✅ Health check passed
✅ Labels endpoint works
✅ Model info endpoint works
🎉 All smoke tests passed!
```

## Render Deployment

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial SignSpeak AI implementation"
git branch -M main
git push -u origin main
```

### 2. Create Render Web Service

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Click **New** → **Web Service**
4. Select **GitHub**
5. Authorize GitHub access
6. Select `signspeak-ai` repository
7. Click **Create Web Service**

### 3. Configure Service

**Build Configuration:**

| Setting | Value |
|---------|-------|
| Build Command | (leave default) |
| Start Command | (leave default) |
| Runtime | Docker |

**Environment Variables:**

```env
APP_ENV=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./signspeak.db
MODEL_PATH=/app/artifacts/signspeak_model.joblib
MODEL_METADATA_PATH=/app/artifacts/model_metadata.json
CONFIDENCE_THRESHOLD=0.75
STABILITY_WINDOW=5
STABILITY_MIN_COUNT=4
SIGN_COOLDOWN_MS=800
LOG_LEVEL=INFO
```

**Instance:**
- Type: Standard
- Size: Medium (sufficient for inference-only workload)

**Health Check:**
- Health Check Path: `/api/health`
- Health Check Protocol: HTTP

### 4. Deploy

1. Click **Deploy** button
2. Wait for build (~5-10 minutes)
3. Check deployment logs for errors

### 5. Verify Deployment

Once deployment completes:

```bash
# Get your Render URL (e.g., signspeak-ai.onrender.com)
curl https://signspeak-ai.onrender.com/api/health

# Should return:
# {"status":"ok","model_loaded":true,"model_version":"1.0.0","database":"ok"}
```

## Production Configuration

### Environment Variables

**Required:**
```env
APP_ENV=production
```

**Recommended:**
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db  # For production
LOG_LEVEL=WARNING

# ML Model
CONFIDENCE_THRESHOLD=0.75
STABILITY_WINDOW=5
STABILITY_MIN_COUNT=4
SIGN_COOLDOWN_MS=800
```

### Database Setup

#### SQLite (Development/Testing)
- No setup required
- File: `signspeak.db` in app directory
- Suitable for single-instance deployments

#### PostgreSQL (Production)

```bash
# Create database
createdb signspeak

# Set environment
export DATABASE_URL="postgresql://user:password@localhost:5432/signspeak"

# Run migrations (when available)
alembic upgrade head
```

### SSL/TLS

**Important:** Webcam APIs require secure context (HTTPS)

Render provides free SSL certificates automatically.

**Configuration:**
- Render auto-generates: `https://your-service.onrender.com`
- Certificate renewal: Automatic
- HSTS: Already enabled by default

### Health Check

Render will monitor your application health:

```bash
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "1.0.0",
  "database": "ok"
}
```

If unhealthy 3 times in a row, Render will restart the service.

### Logging

Logs appear in Render dashboard:

```
2024-01-01T12:00:00Z - Application starting up...
2024-01-01T12:00:01Z - Database initialized: sqlite:///./signspeak.db
2024-01-01T12:00:02Z - Model loaded: version 1.0.0
2024-01-01T12:00:03Z - Uvicorn running at 0.0.0.0:8000
```

## AWS EC2 Deployment (Alternative)

### 1. Launch EC2 Instance

```bash
# Create instance
AWS Console → EC2 → Launch Instance
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium
- Storage: 20 GB
- Security Group: Allow ports 22, 80, 443
```

### 2. Connect and Setup

```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Deploy Application

```bash
# Clone repository
git clone <your-repository-url> CGMS
cd CGMS

# Create production env file
cp .env.example .env.prod
# Edit .env.prod with production settings

# Start application
docker compose up -d

# View logs
docker compose logs -f app
```

### 4. Setup Reverse Proxy (Nginx)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/signspeak-ai
```

```nginx
upstream signspeak_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://signspeak_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/signspeak-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Create certificate
sudo certbot certonly --standalone -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Troubleshooting Deployment

### Application fails to start

Check logs:
```bash
# Render
→ Dashboard → Logs (in browser)

# Docker
docker compose logs app
docker logs <container-id>
```

Common issues:
- Model file missing: Verify artifacts/ directory exists
- Port already in use: Change PORT environment variable
- Database connection: Check DATABASE_URL format

### WebSocket connection fails in production

Ensure:
- ✅ HTTPS enabled (not HTTP)
- ✅ Firewall allows WebSocket upgrade
- ✅ Reverse proxy configured for WebSocket:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  ```

### Slow inference

Check:
- CPU usage: `top` or CPU metrics
- Memory usage: `free -h`
- Model loaded: `curl https://your-domain/api/health`
- Network latency: Check from browser DevTools

### Memory leaks

Monitor:
```bash
docker stats  # Live memory usage
```

If memory grows unbounded:
- Check for unclosed connections
- Monitor WebSocket count
- Review for circular references

## Scaling

### Single Instance (Current)

Suitable for:
- Development/testing
- Demos and presentations
- <100 concurrent users
- Cost-minimal operation

### Multiple Instances (Future)

For higher load, consider:
- Load balancer (nginx, Render's built-in)
- Shared database (PostgreSQL)
- Session management
- Model serving service (optional)

## Monitoring & Maintenance

### Health Monitoring

Daily checks:
```bash
curl https://your-domain/api/health
```

### Backup Strategy

**Database Backup** (if using PostgreSQL):
```bash
# Daily automated backup
pg_dump signspeak > backup-$(date +%Y%m%d).sql
```

**Model Artifact Backup:**
- Backup `artifacts/` directory regularly
- Version control model metadata

### Security Updates

```bash
# Check for dependency vulnerabilities
npm audit     # Frontend
pip audit     # Backend (if implemented)

# Update base image
docker pull python:3.11-slim
docker build --no-cache -t signspeak-ai:latest .
```

### Metrics to Track

- ✅ Request latency (p50, p95, p99)
- ✅ Error rate
- ✅ Model accuracy (if possible)
- ✅ Uptime %
- ✅ Database size
- ✅ Active WebSocket connections

## Rollback Plan

If deployment fails:

### Render
1. Go to Dashboard
2. Select previous deployment
3. Click "Redeploy"

### Docker
```bash
# Revert to previous image
docker tag signspeak-ai:old signspeak-ai:latest
docker compose up -d
```

## Cost Estimation

### Render (Recommended for College Project)

- **Free Tier:** Limited compute (suitable for demos)
- **Standard:** ~$12/month per web service
- **Database:** Free tier available (5 GB PostgreSQL)

### AWS EC2

- **t3.medium:** ~$33/month
- **Elastic IP:** Free when in use
- **Data Transfer:** ~$0.1 GB (minimal for ISL app)
- **Total:** ~$35-40/month

### DigitalOcean

- **App Platform:** $12/month (recommended)
- **Database:** $15/month (optional)
- **Total:** $12-27/month

## Post-Deployment Validation

```bash
# 1. Health Check
curl https://your-domain/api/health

# 2. API Endpoints
curl https://your-domain/api/model/info
curl https://your-domain/api/labels

# 3. WebSocket Connection
wscat -c wss://your-domain/ws/predict

# 4. History Storage
curl -X POST https://your-domain/api/history \
  -d '{"text":"Hello"}'

# 5. Frontend Access
# Open in browser: https://your-domain/
# Check console for errors
# Test camera permission flow
# Test prediction flow
```

---

**Deployment Documentation Version:** 1.0  
**Last Updated:** 2024
