# Pre-Deployment Checklist - Funda Malitinne LMS

## 🔍 Configuration Checklist

### Environment & Secrets
- [ ] `.env` file created with all required variables
- [ ] `SECRET_KEY` is strong and unique (not default)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured with your domain
- [ ] All credentials changed from example values
- [ ] Email settings configured
- [ ] Database credentials secured
- [ ] Redis URL configured
- [ ] AWS credentials configured (if using S3)

### Database Setup
- [ ] PostgreSQL 13+ installed
- [ ] Database created: `funda_malitinne_lms`
- [ ] Database user created: `lms_user`
- [ ] Database user has proper permissions
- [ ] Migrations run successfully
- [ ] Database backup strategy in place
- [ ] Backup automation configured

### Security
- [ ] SSL certificate obtained and configured
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT=True`)
- [ ] Security headers configured
- [ ] CORS origins configured correctly
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Firewall rules configured
- [ ] SSH key-based authentication enabled
- [ ] Weak passwords removed from codebase

### Static & Media Files
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Media directory permissions set correctly
- [ ] S3 bucket configured (if using cloud storage)
- [ ] CDN configured (if using)
- [ ] File upload size limits configured
- [ ] File type restrictions configured

### Docker & Containers
- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] `.env` file updated for Docker
- [ ] Docker images building successfully
- [ ] All services starting without errors
- [ ] Health checks passing
- [ ] Volumes properly configured
- [ ] Container restart policies set

### Services & Dependencies
- [ ] PostgreSQL service running
- [ ] Redis service running
- [ ] Nginx service running
- [ ] Gunicorn service running
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] All service logs checked for errors

### Monitoring & Logging
- [ ] Logging configured
- [ ] Log files writable and accessible
- [ ] Log rotation configured
- [ ] Error notifications set up
- [ ] Monitoring dashboard accessible
- [ ] Health check endpoint working (`/health/`)
- [ ] Monitoring alerts configured

### Email Configuration
- [ ] Email backend configured
- [ ] SMTP credentials verified
- [ ] Test email sent successfully
- [ ] Email templates reviewed
- [ ] Bounce handling configured
- [ ] Unsubscribe functionality working

### DNS & Domain
- [ ] Domain registered and active
- [ ] DNS records updated
- [ ] A records pointing to server
- [ ] MX records configured (for email)
- [ ] DNS propagation verified
- [ ] Domain SSL certificate valid

### API & Performance
- [ ] API endpoints tested
- [ ] Rate limiting tested
- [ ] Response times acceptable
- [ ] Database queries optimized
- [ ] Caching strategy configured
- [ ] CDN cache headers set
- [ ] Load testing completed

### Testing & QA
- [ ] Unit tests passing: `python manage.py test`
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] User acceptance testing done
- [ ] Performance testing completed
- [ ] Security testing completed
- [ ] Accessibility testing done

### Backups & Recovery
- [ ] Database backup script created
- [ ] Automated daily backups configured
- [ ] Backup retention policy set (30 days minimum)
- [ ] Backup restore tested successfully
- [ ] Media files backup strategy in place
- [ ] Disaster recovery plan documented

### Documentation
- [ ] README.md complete
- [ ] DEPLOYMENT.md complete
- [ ] API documentation updated
- [ ] Setup instructions clear
- [ ] Troubleshooting guide created
- [ ] Database schema documented
- [ ] Runbook for common operations created

### Monitoring & Alerts
- [ ] Uptime monitoring configured
- [ ] Performance monitoring active
- [ ] Error tracking enabled
- [ ] Alert notifications configured
- [ ] Dashboard accessible
- [ ] Metrics being collected

### Deployment Process
- [ ] Deployment script tested
- [ ] Rollback procedure documented
- [ ] Maintenance window planned
- [ ] Team trained on deployment
- [ ] Communication plan for downtime
- [ ] Post-deployment validation plan

### Post-Deployment
- [ ] All services verified running
- [ ] Application accessible via domain
- [ ] SSL certificate valid
- [ ] Admin panel working
- [ ] User login working
- [ ] File uploads working
- [ ] Email sending working
- [ ] API endpoints responding
- [ ] Database queries working
- [ ] No critical errors in logs

---

## 🚀 Pre-Launch Sign-Off

- [ ] Technical team: _________________ (Name/Date)
- [ ] Operations team: ________________ (Name/Date)
- [ ] Management approval: ___________ (Name/Date)

---

## 📞 Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| System Admin | | | |
| Database Admin | | | |
| Security Lead | | | |
| Manager | | | |

---

## 📋 Quick Reference Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate --settings=lms.settings_production

# Create superuser
docker-compose exec web python manage.py createsuperuser --settings=lms.settings_production

# Collect static
docker-compose exec web python manage.py collectstatic --noinput --settings=lms.settings_production

# Database backup
docker-compose exec db pg_dump -U lms_user funda_malitinne_lms > backup.sql

# Restart services
docker-compose restart web celery nginx
```

---

**Created**: May 2026
**Last Updated**: May 2026
