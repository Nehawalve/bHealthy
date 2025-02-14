from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('appointment/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    
    # -- Patient Management --
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    
    # -- Auth --
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='healthcare_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
