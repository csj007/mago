你好！部署 Django 项目到京东云主机并对外开放访问是一个很常见的流程。既然你已经完成了本地调试，并且拥有公网 IP（172.144.130.133），下面我会为你提供一个详细的部署步骤，保证你的 Django 项目可以被所有人访问。

---

## 🗂️ 一、准备工作

### 1.1 确保云主机环境
- 操作系统：推荐使用 **Ubuntu 20.04 LTS** 或 **CentOS 7+**
- Python 版本：建议使用 Python 3.8+
- 用户权限：使用非 root 用户，并添加 `sudo` 权限

### 1.2 安装必要的软件
确保你已经安装了以下工具：

```bash
sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-venv nginx -y
```

---

## 🛠️ 二、部署 Django 项目

### 2.1 创建项目目录结构

```bash
mkdir -p /var/www/myproject
cd /var/www/myproject
```

你可以将本地的 Django 项目目录上传到该位置，比如使用 `scp`、`rsync` 或 `git clone`。

---

### 2.2 创建并激活虚拟环境

```bash
python3 -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
```

---

### 2.3 修改 Django 设置

在 `settings.py` 中修改以下内容：

```python
ALLOWED_HOSTS = ['172.144.130.133', 'yourdomain.com']  # 替换为你自己的域名或 IP
```

---

### 2.4 收集静态文件

```bash
python manage.py collectstatic --noinput
```

---

## 🔄 三、配置 WSGI 和 Gunicorn

### 3.1 安装 Gunicorn

```bash
pip install gunicorn
```

### 3.2 测试 Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 myproject.wsgi
```

访问 `http://172.144.130.133:8000` 查看是否能访问。

---

## 🚪 四、配置 Nginx 作为反向代理

### 4.1 创建 Nginx 配置文件

```bash
sudo nano /etc/nginx/sites-available/myproject
```

粘贴下列内容（根据你的实际路径修改）：

```nginx
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
```

### 4.2 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔁 五、使用 systemd 管理 Gunicorn

### 5.1 创建 service 文件

```bash
sudo nano /etc/systemd/system/myproject.service
```

粘贴以下内容（根据你的路径修改）：

```ini
[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=yourusername
Group=www-data
WorkingDirectory=/var/www/myproject
Environment="PATH=/var/www/myproject/myvenv/bin"
ExecStart=/var/www/myproject/myvenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/myproject/myproject.sock -m 007 myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 5.2 启动服务

```bash
sudo systemctl start myproject
sudo systemctl enable myproject
```

---

## 🔐 六、安全设置（可选但推荐）

### 6.1 安装 Let's Encrypt 证书（HTTPS）

如果你有域名，可以使用 `certbot` 安装免费的 SSL 证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

> 如果你没有域名，可以暂时跳过这一步。

---

## ✅ 七、验证部署是否成功

访问：

```
http://172.144.130.133
```

你应该能看到你的 Django 项目页面。

---

## 📌 常见问题排查

| 问题 | 可能原因 |
|------|----------|
| 无法访问网页 | 检查防火墙是否开放 80 端口 |
| 502 Bad Gateway | 检查 Gunicorn 是否启动，socket 是否正确 |
| 403 Forbidden | 检查静态文件权限 |
| 500 Internal Server Error | 检查日志 `gunicorn logs` 和 Django 的 `DEBUG` 设置 |

---

## 🧾 后续优化建议

1. **使用域名访问**：尽量绑定域名，支持 HTTPS。
2. **添加数据库**（如 MySQL/PostgreSQL）。
3. **配置定时任务**（使用 `django-cron` 或 `celery`）。
4. **设置日志监控和报警**。
5. **部署多个项目**：可以使用 `gunicorn + supervisor + nginx` 多项目部署。

---

如果你希望我帮你生成某个步骤的完整脚本（比如一键部署脚本），也可以告诉我，我可以为你定制脚本。

祝你部署顺利！如果在过程中遇到问题，欢迎随时继续提问。🌟
