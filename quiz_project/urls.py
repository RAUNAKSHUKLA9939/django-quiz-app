from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # HOME
    path('', views.home, name='home'),

    # AUTH
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # QUIZ FLOW
    path('category/<int:category_id>/', views.category_quizzes, name='category_quizzes'),
    path('start-quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('attempt/', views.attempt_quiz, name='attempt_quiz'),
    path('result/', views.quiz_result, name='quiz_result'),

    # USER
    path('my-attempts/', views.my_attempts, name='my_attempts'),

    # 🔥 DAY 9 - ADMIN USER MANAGEMENT
    path('admin/users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin/users/add/', views.admin_add_user, name='admin_add_user'),
    path('admin/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/users/upload_csv/', views.upload_users_csv, name='upload_users_csv'),
]