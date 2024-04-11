捏人  使用 [PIL库（现在称为Pillow）](https://github.com/python-pillow/Pillow)

使用的是 python 3.10 版本

### 安装依赖
```
pip install --upgrade Pillow

pip install fastapi

pip install jinja2

pip install "uvicorn[standard]"
```

### 开发阶段 调试运行： 
```bash
uvicorn main:app --reload
```


# ubuntu 生产部署
#### 安装
```
pip install Gunicorn

sudo apt install nginx
```

#### 编辑 nginx.conf配置文件
`nginx.conf`配置文件的地址可以用 `sudo nginx -t` 查看
```
user root;
worker_processes  2;
events {
    worker_connections  1024;
}

http {
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

  server {
                listen 80;
                server_name res.ouj.com; # 这里的domain_name是域名地址。
                location / {
                        proxy_pass http://127.0.0.1:8000; # 注意这里的端口跟配置脚本的端口一致。
                        proxy_set_header Host $host;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                }
        }
}
```
> server_name res.ouj.com; # 这里的域名地址，要根据实际修改 

#### 查看nginx的配置文件是否正常、配置文件目录
```
sudo nginx -t     
```

#### 运行
```
gunicorn main:app -c ./gunicorn.py             # 这个命令要进入merge_man目录，在运行

sudo nginx
```

#### 停止
```
sudo nginx -s stop

gunicorn没有对应的停止命令， 只能通过 ps aux | grep gun 找到进程ID再手动 kill掉
```


