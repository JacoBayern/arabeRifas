from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('sorteos/', views.sorteo_list, name='sorteo_list'),  
    path('pagos/', views.payment_list, name='payment_list'),
    path('logout', views.logout_view, name='logout'),
    path('sorteo/create/', views.sorteo_edit, name='sorteo_create'),
    path('sorteo/<int:sorteo_id>/edit/', views.sorteo_edit, name='sorteo_edit'),
    path('sorteo/<int:sorteo_id>/tickets', views.ticket_list, name='ticket_list'),
    path('sorteo/<slug:sorteo_slug>/process-payment/', views.process_payment, name='process_payment'),
    path('payment/success/<str:payment_serial>/', views.payment_success, name='payment_success'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/cancel/', views.cancel_payment, name='cancel_payment'),
    path('verify-tickets/', views.verify_tickets, name='verify_tickets'),
]