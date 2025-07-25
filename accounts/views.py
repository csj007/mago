from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, MedicineForm
from .models import Medicine, Recipe, RecipeItem
from django.views.decorators.csrf import csrf_exempt
import json
import os
from urllib.parse import urlencode
import datetime
import csv
from django.contrib.auth.models import User, Group
from .forms import RegisterForm
from django.db.models import Q, CharField
from django.views.decorators.http import require_http_methods, require_GET
from django.http import HttpResponse, JsonResponse
from pypinyin import lazy_pinyin
from django.views.decorators.http import require_POST
from django.db.models.functions import Upper
from django.core.exceptions import ObjectDoesNotExist


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

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # 创建用户
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # 将用户加入“普通用户”组
            common_group, created = Group.objects.get_or_create(name='普通用户')
            user.groups.add(common_group)

            # 添加注册成功提示
            messages.success(request, '注册成功，请登录！')

            # 跳转到登录页面
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def home(request):
    medicines = Medicine.objects.all()
    context = {
        'medicines': medicines,
    }
    return render(request, 'accounts/home.html', context)

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
def medicine_list(request):
    order_by = request.GET.get('order_by', 'code')  # 默认按编号排序
    is_desc = request.GET.get('dir', 'asc') == 'desc'

    medicines = Medicine.objects.all()

    if order_by == 'name':
        # 使用 pypinyin 对 name 字段进行拼音排序
        medicines = sorted(medicines, key=lambda m: lazy_pinyin(m.name), reverse=is_desc)
    else:
        # 使用 Django 的默认排序
        if is_desc:
            order_by = f'-{order_by}'
        medicines = medicines.order_by(order_by)

    # 以下是你的原有逻辑保持不变
    data = [
        {
            'name': m.name,
            'code': m.code,
            'type': m.type,
            'cas_number': m.cas_number,
            'specification': m.specification,
            'unit': m.unit,
            'quantity': m.quantity,
            'manufacturer': m.manufacturer,
        } for m in medicines
    ]

    sort_dir = 'desc' if is_desc else 'asc'
    sort_icon = '-up' if is_desc else '-down'
    sort_arrow = f'&dir={sort_dir}'
    context = {
        'medicines': medicines,
        'order_by': order_by.lstrip('-'),
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

# ... edit, delete 等视图保持不变 ...

@login_required
def export_medicine(request):
    medicines = Medicine.objects.all()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"medicine_list_{timestamp}.csv"
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )
    writer = csv.writer(response)
    writer.writerow([
        '种类',
        '名称',
        '编号',
        'CAS号',
        '规格',
        '单位',
        '数量',
        '生产厂家'
    ])
    for medicine in medicines:
        writer.writerow([
            medicine.get_type_display(),
            medicine.name,
            medicine.code,
            medicine.cas_number or '',
            medicine.specification or '',
            medicine.unit or '',
            medicine.quantity or '',
            medicine.manufacturer or '',
        ])
    return response


def log_operation(user, action, medicine_info):
    now = datetime.datetime.now()
    log_entry = f"[{now}] 用户 {user} 执行了 [{action}] 操作，药品信息：{medicine_info}\n"
    
    with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(log_entry)

@csrf_exempt
@require_POST
def get_medicine_codes(request):
    search = request.POST.get('search', '').strip()

    unique_medicine_names = Medicine.objects.annotate(
        name_lower=Upper('name')
    ).filter(
        name_lower__icontains=search
    ).values_list('name', flat=True).distinct()

    data = []
    for name in unique_medicine_names:
        manufacturers = Medicine.objects.filter(name=name).values_list('manufacturer', flat=True).distinct()
        valid_manufacturers = [m for m in manufacturers if m and m.strip() != '']

        manufacturer_data = []
        for m in valid_manufacturers:
            cas_list = Medicine.objects.filter(name=name, manufacturer=m).values_list('cas_number', flat=True).distinct()
            valid_cas = [c for c in cas_list if c and c.strip() != '']
            manufacturer_data.append({
                'manufacturer': m,
                'cas_list': valid_cas
            })

        data.append({
            'name': name,
            'manufacturer_data': manufacturer_data
        })

    return JsonResponse(data, safe=False)


@require_GET
def find_medicine_codes(request):
    name = request.GET.get('name')
    manufacturer = request.GET.get('manufacturer')
    cas = request.GET.get('cas')

    # 第一步：只用 name 查询
    medicines = Medicine.objects.filter(name=name)

    if not medicines.exists():
        return JsonResponse({'code': None, 'error': '未找到药品'}, status=404)

    if len(medicines) == 1:
        return JsonResponse({'code': medicines[0].code})

    # 第二步：加上 manufacturer
    if manufacturer:
        medicines = medicines.filter(manufacturer=manufacturer)
        if len(medicines) == 1:
            return JsonResponse({'code': medicines[0].code})

    # 第三步：加上 cas
    if cas:
        medicines = medicines.filter(cas_number=cas)
        if len(medicines) == 1:
            return JsonResponse({'code': medicines[0].code})

    # 第四步：仍然不唯一
    return JsonResponse({'code': name})

@login_required
def save_recipe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        items = data.get('items')
        user = request.user

        # ✅ 检查用户是否已有同名配方
        if Recipe.objects.filter(user=user, name=name).exists():
            return JsonResponse({'status': 'error', 'message': '配方名称已存在'}, status=400)

        # 正常创建配方
        recipe = Recipe.objects.create(name=name, user=user)
        for item in items:
            RecipeItem.objects.create(
                recipe=recipe,
                name=item['name'],
                manufacturer=item['manufacturer'],
                cas=item['cas'],
                amount=item['amount']
            )
        return JsonResponse({'status': 'success', 'recipe_id': recipe.id})

@login_required
def load_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    items = [
        {
            'name': item.name,
            'manufacturer': item.manufacturer,
            'cas': item.cas,
            'amount': item.amount
        }
        for item in recipe.items.all()
    ]
    return JsonResponse({'items': items})

@login_required
def list_recipes(request):
    recipes = Recipe.objects.filter(user=request.user).prefetch_related('items')
    data = [
        {
            'id': recipe.id,
            'name': recipe.name,
            'items': [{
                'name': item.name,
                'amount': item.amount,
                'manufacturer': item.manufacturer or '',
                'cas': item.cas or ''
            } for item in recipe.items.all()]
        }
        for recipe in recipes
    ]
    return JsonResponse({'recipes': data})

@login_required
def search_recipes(request):
    query = request.GET.get('q', '')
    recipes = Recipe.objects.filter(name__icontains=query, user=request.user).values('id', 'name')
    return JsonResponse({'recipes': list(recipes)})

@login_required
def delete_recipe(request, recipe_id):
    if request.method == "DELETE":
        try:
            recipe = Recipe.objects.get(id=recipe_id, user=request.user)
            recipe.delete()
            return JsonResponse({"status": "success", "message": "配方已删除"})
        except ObjectDoesNotExist:
            return JsonResponse({"status": "error", "message": "配方不存在或无权操作"}, status=404)
    return JsonResponse({"status": "error", "message": "请求方法不支持"}, status=405)

@login_required
def rename_recipe(request, recipe_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_name = data.get('name')
        if not new_name:
            return JsonResponse({'status': 'error', 'message': '请提供配方名称'}, status=400)

        try:
            recipe = Recipe.objects.get(id=recipe_id, user=request.user)

            # 检查新名称是否已存在（排除当前配方）
            if Recipe.objects.filter(user=request.user, name=new_name).exclude(id=recipe.id).exists():
                return JsonResponse({'status': 'error', 'message': '该配方名称已存在，请换一个名称'}, status=400)

            # 重命名并保存
            recipe.name = new_name
            recipe.save()

            return JsonResponse({'status': 'success', 'message': '配方名称已更新'})
        except Recipe.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '配方不存在或无权操作'}, status=404)
    return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)
