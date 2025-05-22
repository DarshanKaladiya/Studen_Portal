from django.contrib import admin
from django.urls import path, include
from . import views
from .views import mentor_home, approve_file, reject_file, update_file_status

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('delete_file/<int:file_id>/', views.delete_file, name="delete_file"),
    path("student/home/", views.student_home, name="student_home"),
    path('mentor_home/', views.mentor_home, name='mentor_home'),
    path('approve-file/<int:file_id>/', views.approve_file, name='approve_file'),
    path('reject-file/<int:file_id>/', views.reject_file, name='reject_file'),
    path("update_file/<int:file_id>/<str:action>/", views.update_file_status, name="update_file_status"),
] 
