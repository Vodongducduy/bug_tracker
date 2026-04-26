from django.shortcuts import render, redirect
from apps.accounts.forms import LoginForm, RegisterForm
from apps.accounts.services.auth_service import AuthService
from apps.accounts.repositories.user_repository import UserRepository

def login_view(request):
    if hasattr(request, 'logged_user') and request.logged_user:
        return redirect('dashboard')
        
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Injection
            user_repository = UserRepository()
            auth_service = AuthService(user_repository)
            
            user = auth_service.authenticate(username, password)
            if user == 'INACTIVE':
                form.add_error(None, "Tài khoản đã bị vô hiệu hóa.")
            elif user:
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
                
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    response = redirect('login')
    response.delete_cookie('auth_session')
    return response

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
            password = form.cleaned_data.get('password')
            
            # Injection
            user_repository = UserRepository()
            auth_service = AuthService(user_repository)
            
            # Create the user directly using service
            user = auth_service.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
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
