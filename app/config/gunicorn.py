import os
import json

DEFAULT_GUNICORN_CONFIG = {
    "bind": "0.0.0.0:8000",
    "workers": 1,
    "timeout": 30,
    "graceful_timeout": 30,
    "keepalive": 2,
    "loglevel": "info",
    "accesslog": "-",
    "errorlog": "-",
    "worker_tmp_dir": "/dev/shm",
}

# Logging
# https://docs.gunicorn.org/en/stable/settings.html#logging
loglevel = os.getenv("LOG_LEVEL", DEFAULT_GUNICORN_CONFIG["loglevel"])
accesslog = os.getenv("ACCESS_LOG", DEFAULT_GUNICORN_CONFIG["accesslog"])
errorlog = os.getenv("ERROR_LOG", DEFAULT_GUNICORN_CONFIG["errorlog"])

# Worker processes
# https://docs.gunicorn.org/en/stable/settings.html#worker-processes
workers = int(os.getenv("WORKERS", DEFAULT_GUNICORN_CONFIG["workers"]))
timeout = int(os.getenv("TIMEOUT", DEFAULT_GUNICORN_CONFIG["timeout"]))
graceful_timeout = int(
    os.getenv("GRACEFUL_TIMEOUT", DEFAULT_GUNICORN_CONFIG["graceful_timeout"])
)
keepalive = int(os.getenv("KEEP_ALIVE", DEFAULT_GUNICORN_CONFIG["keepalive"]))

# Server machanics
# https://docs.gunicorn.org/en/stable/settings.html?highlight=worker_tmp_dir#worker-tmp-dir
# This is set to /dev/shm to speed up the startup of workers by using a in memory file system
worker_tmp_dir = str(
    os.getenv("WORKER_TMP_DIR", DEFAULT_GUNICORN_CONFIG["worker_tmp_dir"])
)

# Server socket
# https://docs.gunicorn.org/en/stable/settings.html?highlight=bind#bind
bind = os.getenv("BIND", DEFAULT_GUNICORN_CONFIG["bind"])

log_data = {
    "bind": bind,
    "workers": workers,
    "timeout": timeout,
    "graceful_timeout": graceful_timeout,
    "keepalive": keepalive,
    "loglevel": loglevel,
    "errorlog": errorlog,
    "accesslog": accesslog,
    "worker_tmp_dir": worker_tmp_dir,
}
print(json.dumps(log_data))
