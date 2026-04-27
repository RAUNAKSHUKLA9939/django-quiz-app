from django.contrib import admin
from django.urls import path
from core import views   # ✅ correct import

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
]