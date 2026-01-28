from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.medicine_list, name='medicine_list'),
    path('add/', views.add_medicine, name='add_medicine'),
    path('edit/<int:medicine_id>/', views.edit_medicine, name='edit_medicine'),
    path('delete/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),
    path('export/', views.export_medicine, name='export_medicine'),
    path('home/', views.home, name='home'),
    path('api/get-medicine-codes/', views.get_medicine_codes, name='get_medicine_codes'),
    path('api/find_medicine_codes/', views.find_medicine_codes, name='find_medicine_codes'),
    path('register/', views.register, name='register'),
    path('api/save_recipe/', views.save_recipe, name='save_recipe'),
    path('api/load_recipe/<int:recipe_id>/', views.load_recipe, name='load_recipe'),
    path('api/list_recipes/', views.list_recipes, name='list_recipes'),
    path('api/search_recipes/', views.search_recipes, name='search_recipes'),
    path('api/delete_recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    path('api/rename_recipe/<int:recipe_id>/', views.rename_recipe, name='rename_recipe'),
    path('activity/', views.user_activity_report, name='user_activity'),
]
