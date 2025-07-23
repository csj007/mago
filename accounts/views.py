from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from .models import Medicine
from .forms import MedicineForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from urllib.parse import urlencode
import datetime
import csv
from django.http import HttpResponse
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'medicine_logs.txt')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser or user.groups.filter(name='管理员').exists():
                    return redirect('medicine_list')
                else:
                    return redirect('home')
            else:
                messages.error(request, '用户名或密码错误')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    medicines = Medicine.objects.all()
    context = {
        'medicines': medicines,
    }
    return render(request, 'accounts/home.html', context)

@login_required
def medicine_list(request):
    order_by = request.GET.get('order_by', 'name')  # 默认按名称排序
    is_desc = request.GET.get('dir', 'asc') == 'desc'

    # 根据字段排序
    if is_desc:
        order_by = f'-{order_by}'

    medicines = Medicine.objects.all().order_by(order_by)
    data = [
        {
            'name': m.name,
            'code': m.code,
            'type': m.type,
        } for m in medicines
    ]
    # 构建排序图标和链接
    sort_dir = 'desc' if is_desc else 'asc'
    sort_icon = '-up' if is_desc else '-down'
    sort_arrow = f'&dir={sort_dir}'

    context = {
        'medicines': medicines,
        'order_by': order_by.lstrip('-'),  # 移除排序方向符号
        'sort_icon': sort_icon,
        'sort_arrow': sort_arrow,
    }

    file_path = os.path.join(os.path.dirname(__file__), 'medicine_data.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return render(request, 'accounts/list.html', context)


@login_required
def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save() 
            log_operation(
                user=request.user,
                action='新增',
                medicine_info=f"{medicine.name} - {medicine.code} - {medicine.get_type_display()}"
            )
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'accounts/add.html', {'form': form})

@login_required
def edit_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, pk=medicine_id)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            old_name = medicine.name
            old_code = medicine.code
            form.save()
            new_name = form.cleaned_data['name']
            new_code = form.cleaned_data['code']
            log_operation(
                user=request.user,
                action='编辑',
                medicine_info=f"原: {old_name} - {old_code}, 现: {new_name} - {new_code}"
            )
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'accounts/edit.html', {'form': form})

@login_required
def delete_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        deleted_name = medicine.name
        deleted_code = medicine.code
        medicine.delete()
        log_operation(
            user=request.user,
            action='删除',
            medicine_info=f"{deleted_name} - {deleted_code}"
        )
        return redirect('medicine_list')
    return render(request, 'accounts/delete.html', {'medicine': medicine})

@login_required
def export_medicine(request):
    medicines = Medicine.objects.all()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"material_list_{timestamp}.csv"

    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',  # 注意这里的 charset=utf-8-sig
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )

    writer = csv.writer(response)
    writer.writerow(['种类', '名称', '编号'])

    for medicine in medicines:
        writer.writerow([
            medicine.get_type_display(),
            medicine.name,
            medicine.code,
        ])

    return response

@csrf_exempt
def get_medicine_codes(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        materials = data.get('materials', [])

        result = []
        for item in materials:
            name = item.get('name', '').strip()
            amount = item.get('amount', 0)

            try:
                medicine = Medicine.objects.get(name__iexact=name)
                code = medicine.code  # 获取数据库中的编号
            except Medicine.DoesNotExist:
                code = name  # 如果找不到，就用用户输入的名称代替编号

            result.append({
                'name': name,
                'code': code,
                'amount': amount
            })
        return JsonResponse(result, safe=False)
    return JsonResponse({'error': '无效的请求'}, status=400)


def log_operation(user, action, medicine_info):
    now = datetime.datetime.now()
    log_entry = f"[{now}] 用户 {user} 执行了 [{action}] 操作，药品信息：{medicine_info}\n"
    
    with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(log_entry)
