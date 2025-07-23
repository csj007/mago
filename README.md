sudo apt update
sudo apt install python3 python3-pip

pip3 install django

django-admin startproject mysite
cd mysite
python3 manage.py startapp accounts

python manage.py makemigrations
python manage.py migrate

python manage.py shell


from django.contrib.auth.models import User, Group

user = User.objects.create_user(username='new_user', password='your_password', email='new_user@example.com')
user.save()
print("用户新增成功：", user.username)

user = User.objects.create_superuser(username='admin2', email='admin2@example.com', password='your_password')
user.save()
print("管理员用户新增成功：", user.username)

Group.objects.get_or_create(name='管理员')
Group.objects.get_or_create(name='普通用户')

user = User.objects.get(username='zhangsan')
group = Group.objects.get(name='管理员')
user.groups.add(group)

user = User.objects.get(username='zhangsan')
group = Group.objects.get(name='普通用户')
user.groups.add(group)


home.html
home.js
views.py
urls.py
list.html
settings.py
login.html
register.html
forms.py


pip install gunicorn
apt update
apt install nginx
gunicorn --bind 0.0.0.0:8000 mysite.wsgi:application
测试是否可以访问：curl http://127.0.0.1:8000

sudo nano /etc/nginx/sites-available/myproject
添加以下内容（请根据你的 Gunicorn 端口修改）：
server {
    listen 80;
    server_name 172.114.131.112;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/static/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }
}
然后启用这个配置：
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
测试 Nginx 配置并重启服务：
sudo nginx -t
sudo systemctl restart ngin

你可以在后台直接运行 Gunicorn，但最好使用 systemd 来管理进程，确保它在服务器重启后自动运行。
创建一个 systemd 服务文件：
sudo nano /etc/systemd/system/gunicorn.service
添加以下内容（根据你自己的项目路径修改）：
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/virtualenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/your/project/gunicorn.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target

启动并启用服务：
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn


设置静态文件（static files）
python manage.py collectstatic --noinput
mkdir accounts/media

使用 Let's Encrypt 免费为你的网站添加 HTTPS：

安装 Certbot：
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d 172.114.131.112
sudo certbot renew --dry-run

最终访问方式
通过 IP 访问：http://172.114.131.112
通过域名访问（如果你有）：http://yourdomain.com
建议使用 HTTPS：https://yourdomain.com
