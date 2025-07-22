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
    return render(request, 'accounts/home.html')

@login_required
def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'accounts/list.html', {'medicines': medicines})

@login_required
def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
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
            form.save()
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'accounts/edit.html', {'form': form})

@login_required
def delete_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        medicine.delete()
        return redirect('medicine_list')
    return render(request, 'accounts/delete.html', {'medicine': medicine})

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
        print(result)
        return JsonResponse(result, safe=False)
    return JsonResponse({'error': '无效的请求'}, status=400)
