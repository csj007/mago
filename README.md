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

pip install gunicorn
apt update
apt install nginx

vi /etc/nginx/sites-available/mysite
添加以下内容（请根据你的 Gunicorn 端口修改）：
server {
    listen 80;
    server_name 172.144.130.133;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/myproject;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
然后启用这个配置：
sudo ln -s /etc/nginx/sites-available/mysite /etc/nginx/sites-enabled
测试 Nginx 配置并重启服务：
sudo nginx -t
sudo systemctl restart ngin

sudo vi /etc/systemd/system/myproject.service

[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/mysite
Environment="PATH=/var/www/myproject/myvenv/bin"
ExecStart=/var/www/myproject/myvenv/bin/gunicorn --access-logfile - --workers 3 --bind 127.0.0.1:8000 mysite.wsgi


启动并启用服务：
sudo systemctl daemon-reload
sudo systemctl start mysite
sudo systemctl enable mysite


设置静态文件（static files）
python manage.py collectstatic --noinput
mkdir accounts/media


base.html  max-width:1500px
forms.py fields = '__all__'
settings.py把登录时间60s删掉

views.py修改
models.py修改
urls.py修改

list.html修改
home.html修改
home.js修改


pip install pypinyin
python manage.py makemigrations
python manage.py migrate

