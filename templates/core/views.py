from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Option
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'core/home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        confirm  = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')

    return render(request, 'core/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
@login_required
def attempt_quiz(request):
    quiz_id = request.session.get('quiz_id')
    question_index = request.session.get('question_index', 0)

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

            # store answers properly
            answers = request.session.get('answers', {})
            answers[str(current_question.id)] = selected_option.id
            request.session['answers'] = answers

            if selected_option.is_correct:
                request.session['score'] += 1

        request.session['question_index'] += 1
        return redirect('attempt_quiz')

    return render(request, 'core/quiz_attempt.html', {
        'question': current_question,
        'options': options,
        'question_number': question_index + 1,
        'total_questions': len(questions),
    })