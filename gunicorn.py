daemon=True #是守护进程

bind='0.0.0.0:8000'#绑定

pidfile='gunicorn.pid'#pid文件地址
chdir='.' # 项目地址
worker_class='uvicorn.workers.UvicornWorker'
workers=1   # 推荐 CPU数 * 2  + 1
threads=2
loglevel='debug' # 日志级别
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = "gunicorn_access.log"
errorlog = "gunicorn_error.log"