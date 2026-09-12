#!/bin/bash
# Log memory every 15 minutes for OOM diagnosis
LOG=/var/log/malitinne-memory.log
DATE=$(date '+%Y-%m-%d %H:%M:%S')
FREE=$(free -m | grep Mem | awk '{print "total:"$2" used:"$3" free:"$4" available:"$7}')
GUNICORN=$(ps aux | grep gunicorn | grep -v grep | awk '{sum+=$6} END {print "gunicorn_mb:"sum/1024}')
CELERY=$(ps aux | grep celery | grep -v grep | awk '{sum+=$6} END {print "celery_mb:"sum/1024}')
echo "$DATE $FREE $GUNICORN $CELERY" >> $LOG