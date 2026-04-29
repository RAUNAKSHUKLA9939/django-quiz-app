from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category, Quiz, Question, Option, Attempt, Answer


# HOME
def home(request):
    categories = Category.objects.all()
    return render(request, 'core/home.html', {'categories': categories})


# SIGNUP
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # validations
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        login(request, user)
        return redirect('home')

    return render(request, 'core/register.html')   # ✅ use register.html


# LOGIN
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'core/login.html')


# LOGOUT
def user_logout(request):
    logout(request)
    return redirect('home')


# CATEGORY QUIZZES
def category_quizzes(request, category_id):
    quizzes = Quiz.objects.filter(category_id=category_id)
    return render(request, 'core/quizzes_by_category.html', {'quizzes': quizzes})


# QUIZ START
@login_required
def start_quiz(request, quiz_id):
    request.session['quiz_id'] = quiz_id
    request.session['question_index'] = 0
    request.session['score'] = 0
    request.session['answers'] = {}
    return redirect('attempt_quiz')


# QUIZ ATTEMPT
@login_required
def attempt_quiz(request):
    quiz_id = request.session.get('quiz_id')
    question_index = request.session.get('question_index', 0)

    if not quiz_id:
        return redirect('home')

    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = list(quiz.question_set.all())

    if question_index >= len(questions):
        return redirect('quiz_result')

    current_question = questions[question_index]
    options = current_question.options.all()

    if request.method == 'POST':
        selected_option_id = request.POST.get('option')

        if selected_option_id:
            selected_option = Option.objects.get(id=selected_option_id)

            answers = request.session.get('answers', {})
            answers[str(current_question.id)] = selected_option.id
            request.session['answers'] = answers

            if selected_option.is_correct:
                request.session['score'] = request.session.get('score', 0) + 1

        request.session['question_index'] = question_index + 1
        return redirect('attempt_quiz')

    return render(request, 'core/quiz_attempt.html', {
        'question': current_question,
        'options': options,
        'question_number': question_index + 1,
        'total_questions': len(questions),
    })


# QUIZ RESULT + SAVE ATTEMPT
@login_required
def quiz_result(request):
    score = request.session.get('score', 0)
    quiz_id = request.session.get('quiz_id')
    answers = request.session.get('answers', {})

    if not quiz_id:
        return redirect('home')

    quiz = get_object_or_404(Quiz, pk=quiz_id)
    total_questions = quiz.question_set.count()

    # SAVE ATTEMPT
    attempt = Attempt.objects.create(
        user=request.user,
        quiz=quiz,
        score=score,
        total=total_questions
    )

    for qid, oid in answers.items():
        question = Question.objects.get(pk=qid)
        option = Option.objects.get(pk=oid)

        Answer.objects.create(
            attempt=attempt,
            question=question,
            selected_option=option
        )

    # CLEAR SESSION
    for key in ['score', 'quiz_id', 'question_index', 'answers']:
        request.session.pop(key, None)

    return render(request, 'core/quiz_result.html', {
        'score': score,
        'total_questions': total_questions,
        'quiz': quiz
    })


# MY ATTEMPTS
@login_required
def my_attempts(request):
    attempts = Attempt.objects.filter(user=request.user).order_by('-completed_at')
    return render(request, 'core/my_attempts.html', {'attempts': attempts})
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import csv
from io import TextIOWrapper


@staff_member_required
def admin_manage_users(request):
    users = User.objects.all()
    return render(request, 'core/admin_users.html', {'users': users})


@staff_member_required
def admin_add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "User created successfully.")

        return redirect('admin_manage_users')

    return render(request, 'core/admin_add_user.html')


@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect('admin_manage_users')


@staff_member_required
def upload_users_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
        reader = csv.DictReader(file_data)

        for row in reader:
            username = row['username']
            email = row['email']
            password = row['password']

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, email=email, password=password)

        messages.success(request, "Users uploaded successfully.")
        return redirect('admin_manage_users')

    return render(request, 'core/admin_upload_users.html')


@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        password = request.POST.get('password')

        if password:
            user.set_password(password)

        user.save()
        messages.success(request, "User updated successfully.")
        return redirect('admin_manage_users')

    return render(request, 'core/admin_edit_user.html', {'user': user})