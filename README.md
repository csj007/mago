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
