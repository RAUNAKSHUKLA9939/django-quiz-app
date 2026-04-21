from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Category, Quiz, Option


def home(request):
    categories = Category.objects.all()
    return render(request, 'core/home.html', {'categories': categories})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'core/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def category_quizzes(request, category_id):
    quizzes = Quiz.objects.filter(category_id=category_id)
    return render(request, 'core/quizzes_by_category.html', {'quizzes': quizzes})


# ===================== DAY 5 START =====================

@login_required
def start_quiz(request, quiz_id):
    request.session['quiz_id'] = quiz_id
    request.session['question_index'] = 0
    request.session['score'] = 0
    request.session['answers'] = {}
    return redirect('attempt_quiz')


@login_required
def attempt_quiz(request):
    quiz_id = request.session.get('quiz_id')
    question_index = request.session.get('question_index', 0)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.question_set.all())

    if question_index >= len(questions):
        return redirect('quiz_result')

    question = questions[question_index]
    options = question.options.all()

    if request.method == 'POST':
        selected_option_id = request.POST.get('option')

        if selected_option_id:
            selected_option = Option.objects.get(id=selected_option_id)

            answers = request.session.get('answers', {})
            answers[str(question.id)] = selected_option.id
            request.session['answers'] = answers

            if selected_option.is_correct:
                request.session['score'] = request.session.get('score', 0) + 1

        request.session['question_index'] = question_index + 1
        return redirect('attempt_quiz')

    return render(request, 'core/quiz_attempt.html', {
        'question': question,
        'options': options,
        'question_number': question_index + 1,
        'total_questions': len(questions),
    })


@login_required
def quiz_result(request):
    score = request.session.get('score', 0)
    quiz_id = request.session.get('quiz_id')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    total_questions = quiz.question_set.count()

    for key in ['quiz_id', 'question_index', 'score', 'answers']:
        request.session.pop(key, None)

    return render(request, 'core/quiz_result.html', {
        'score': score,
        'total_questions': total_questions,
        'quiz': quiz,
    })