from .models import Task
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        password_input2 = request.POST.get('password2')

        # 1. Check if username already exists
        if User.objects.filter(username=username_input).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        # 2. Check if email already exists
        if email_input and User.objects.filter(email=email_input).exists():
            return render(request, 'signup.html', {'error': 'Email already exists'})
        
        if password_input != password_input2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        try:
            # 3. Create and automatically save the user
            user = User.objects.create_user(
                username=username_input, 
                email=email_input, 
                password=password_input
            )
            
            # Optional: Log the user in immediately after signup
            login(request, user) 
            user.save()  # Save the user to the database
            
            return redirect('task_list')
            
        except Exception as e:
            return render(request, 'signup.html', {'error': f'Something went wrong: {e}'})

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        user = None
        try:
            user_obj = User.objects.get(email=email_input)
            user = authenticate(request, username=user_obj.username, password=password_input)
        except User.DoesNotExist:
            user = None
        if user is not None:
            login(request, user)
            return redirect('task_list')
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
        
    return render(request, 'task_list.html', {'tasks': tasks})


@login_required(login_url='login')
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        user = request.user
        tasks=Task.objects.create(title=title, description=description, user=user)
        tasks.save()
        task_list = Task.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'create_task.html', {'tasks_list': task_list})
    return render(request, 'create_task.html',)

def task_update(request, pk):
    task = Task.objects.get(pk=pk)
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.save()
        return redirect('task_list')
    return render(request, 'update_task.html', {'task': task})

def task_delete(request, pk):
    task = Task.objects.get(pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'delete_task.html', {'task': task})