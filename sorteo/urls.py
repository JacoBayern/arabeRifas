from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('sorteos/', views.sorteo_list, name='sorteo_list'),  
    path('pagos/', views.payment_list, name='payment_list'),
    path('logout', views.logout_view, name='logout'),
    path('sorteo/create/', views.sorteo_edit, name='sorteo_create'),
    path('sorteo/<int:sorteo_id>/edit/', views.sorteo_edit, name='sorteo_edit')
]