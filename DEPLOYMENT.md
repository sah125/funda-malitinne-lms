# Deployment Guide - Funda Malitinne LMS

## 📋 Pre-Deployment Checklist

- [ ] All environment variables configured in `.env`
- [ ] Database credentials set correctly
- [ ] Redis configured for caching
- [ ] Email settings configured
- [ ] SSL certificates obtained
- [ ] Domain name configured
- [ ] All secrets changed from defaults
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS updated
- [ ] CORS origins configured

## 🚀 Docker Deployment (Recommended)

### Step 1: Prepare Server

```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### Step 2: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/yourusername/funda_malitinne_system.git
cd funda_malitinne_system
```

### Step 3: Configure Environment

```bash
# Copy environment template
sudo cp .env.example .env

# Edit with production values
sudo nano .env
```

**Critical settings to update:**
```
DEBUG=False
SECRET_KEY=your-secure-random-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=strong-database-password
REDIS_URL=redis://redis:6379/0
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SECURE_SSL_REDIRECT=True
```

### Step 4: Start Services

```bash
# Build and start all services
sudo docker-compose up -d

# Check status
sudo docker-compose ps

# View logs
sudo docker-compose logs -f web
```

### Step 5: Run Migrations

```bash
sudo docker-compose exec web python manage.py migrate --settings=lms.settings_production
```

### Step 6: Create Admin User

```bash
sudo docker-compose exec web python manage.py createsuperuser --settings=lms.settings_production
```

### Step 7: Collect Static Files

```bash
sudo docker-compose exec web python manage.py collectstatic --noinput --settings=lms.settings_production
```

## 🔒 SSL/TLS Certificate Setup

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Create SSL directory
sudo mkdir -p /opt/funda_malitinne_system/ssl

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/funda_malitinne_system/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/funda_malitinne_system/ssl/key.pem

# Renew certificates automatically
sudo certbot renew --dry-run
```

## 🛡️ Firewall Configuration

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check rules
sudo ufw status
```

## 📦 Database Backup & Restore

### Automated Backups

```bash
# Create backup script
sudo nano /opt/funda_malitinne_system/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/opt/funda_malitinne_system/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose -f /opt/funda_malitinne_system/docker-compose.yml exec -T db \
  pg_dump -U lms_user funda_malitinne_lms > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 backups
find $BACKUP_DIR -type f -name "backup_*.sql" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql"
```

```bash
# Make executable
sudo chmod +x /opt/funda_malitinne_system/backup.sh

# Schedule daily backup at 2 AM
sudo crontab -e
# Add: 0 2 * * * /opt/funda_malitinne_system/backup.sh
```

### Manual Restore

```bash
# Restore from backup
docker-compose exec db psql -U lms_user funda_malitinne_lms < backup_20260519_120000.sql
```

## 🔄 Continuous Deployment

### GitHub Actions Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: SSH and Deploy
        env:
          SSH_KEY: ${{ secrets.SSH_KEY }}
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USER: ${{ secrets.SERVER_USER }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H $SERVER_HOST >> ~/.ssh/known_hosts
          
          ssh $SERVER_USER@$SERVER_HOST << 'EOF'
          cd /opt/funda_malitinne_system
          git pull origin main
          docker-compose down
          docker-compose up -d
          docker-compose exec web python manage.py migrate --settings=lms.settings_production
          EOF
```

## 📊 Monitoring & Logging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f nginx
```

### Monitor Resources

```bash
# Check container stats
docker stats

# Check disk usage
df -h
du -sh /opt/funda_malitinne_system/media

# Check database size
docker-compose exec db psql -U lms_user funda_malitinne_lms -c "SELECT pg_size_pretty(pg_database_size('funda_malitinne_lms'));"
```

## 🔧 Maintenance Commands

### Update Application

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --settings=lms.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=lms.settings_production

# Restart services
docker-compose restart web celery
```

### Clear Cache

```bash
docker-compose exec redis redis-cli FLUSHALL
```

### Clean Up Docker

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

## 🆘 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Restart specific service
docker-compose restart web

# Rebuild service
docker-compose up -d --build web
```

### Database Connection Error

```bash
# Check database service
docker-compose ps db

# Test connection
docker-compose exec db psql -U lms_user -c "\l"
```

### Static Files Not Loading

```bash
# Rebuild static files
docker-compose exec web python manage.py collectstatic --noinput --settings=lms.settings_production

# Check nginx config
docker-compose exec nginx nginx -t
```

### High Memory Usage

```bash
# Restart all services
docker-compose restart

# Check Docker system usage
docker system df
```

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Check system resources: `docker stats`
3. Verify configuration: `cat .env`
4. Contact: support@fundamalitinne.com

---

**Last Updated**: May 2026
