"""
Gunicorn configuration for Funda Malitinne LMS
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "funda_malitinne_lms"

# Server mechanics
daemon = False
pidfile = None
tmp_upload_dir = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (use with nginx)
keyfile = None
certfile = None
ssl_version = None
cert_reqs = 0
ca_certs = None
suppress_ragged_eof = True

# Application
wsgi_app = "lms.wsgi:application"
preload_app = True
