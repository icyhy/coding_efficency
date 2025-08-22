# -*- coding: utf-8 -*-
"""
Gunicorn配置文件
用于生产环境部署Flask应用
"""

import os
import multiprocessing

# 服务器套接字
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# 工作进程
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 调试
reload = os.environ.get('GUNICORN_RELOAD', 'false').lower() == 'true'
reload_engine = 'auto'

# 日志
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'coding_efficiency_api'

# 用户和组
user = os.environ.get('GUNICORN_USER')
group = os.environ.get('GUNICORN_GROUP')

# 临时目录
tmp_upload_dir = None

# SSL（如果需要）
keyfile = os.environ.get('SSL_KEYFILE')
certfile = os.environ.get('SSL_CERTFILE')

# 钩子函数
def on_starting(server):
    """
    服务器启动时调用
    """
    server.log.info("Starting Coding Efficiency API Server")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Bind: {bind}")

def on_reload(server):
    """
    服务器重载时调用
    """
    server.log.info("Reloading Coding Efficiency API Server")

def when_ready(server):
    """
    服务器准备就绪时调用
    """
    server.log.info("Coding Efficiency API Server is ready. Listening on: %s", bind)

def worker_int(worker):
    """
    工作进程接收到SIGINT信号时调用
    """
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """
    工作进程fork之前调用
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """
    工作进程fork之后调用
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """
    工作进程初始化完成后调用
    """
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """
    工作进程异常退出时调用
    """
    worker.log.info("Worker aborted (pid: %s)", worker.pid)

def pre_exec(server):
    """
    执行新的主进程之前调用
    """
    server.log.info("Forked child, re-executing.")

def pre_request(worker, req):
    """
    处理请求之前调用
    """
    worker.log.debug("%s %s", req.method, req.path)

def post_request(worker, req, environ, resp):
    """
    处理请求之后调用
    """
    pass

def child_exit(server, worker):
    """
    子进程退出时调用
    """
    server.log.info("Worker exited (pid: %s)", worker.pid)

def worker_exit(server, worker):
    """
    工作进程退出时调用
    """
    server.log.info("Worker exited (pid: %s)", worker.pid)

def nworkers_changed(server, new_value, old_value):
    """
    工作进程数量改变时调用
    """
    server.log.info("Number of workers changed from %s to %s", old_value, new_value)

def on_exit(server):
    """
    服务器退出时调用
    """
    server.log.info("Shutting down Coding Efficiency API Server")