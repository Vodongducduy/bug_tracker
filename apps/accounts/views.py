from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import User
from .forms import LoginForm

def login_view(request):
    if hasattr(request, 'logged_user') and request.logged_user:
        return redirect('dashboard')
        
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            try:
                user = User.objects.get(username=username, is_active=True)
                if check_password(password, user.password):
                    # Login successful: set signed cookie
                    response = redirect('dashboard')
                    response.set_signed_cookie(
                        'auth_session', 
                        str(user.id), 
                        salt='manual_auth',
                        max_age=3600*24 # 1 day
                    )
                    return response
                else:
                    form.add_error(None, "Tên đăng nhập hoặc mật khẩu không đúng.")
            except User.DoesNotExist:
                form.add_error(None, "Tên đăng nhập hoặc mật khẩu không đúng.")
                
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    response = redirect('login')
    response.delete_cookie('auth_session')
    return response

from django.contrib.auth.hashers import make_password
from .forms import RegisterForm

def register_view(request):
    if hasattr(request, 'logged_user') and request.logged_user:
        return redirect('dashboard')
        
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            raw_password = form.cleaned_data.get('password')
            
            # Hash password securely
            hashed_password = make_password(raw_password)
            
            # Create the user directly
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=hashed_password,
                is_active=True,
                is_staff=False,
                is_superuser=False
            )
            
            # Auto-login after registration
            response = redirect('dashboard')
            response.set_signed_cookie(
                'auth_session', 
                str(user.id), 
                salt='manual_auth',
                max_age=3600*24 # 1 day
            )
            return response
            
    return render(request, 'accounts/register.html', {'form': form})
