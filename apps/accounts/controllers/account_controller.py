from django.shortcuts import render, redirect
from apps.accounts.decorators import custom_login_required
from apps.accounts.services.account_service import AccountService
from apps.accounts.repositories.user_repository import UserRepository
from apps.accounts.forms import RegisterForm

def _get_account_service():
    return AccountService(UserRepository())

@custom_login_required
def account_list(request):
    if not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    account_service = _get_account_service()
    users = account_service.get_all_accounts()
    return render(request, 'accounts/admin_list.html', {'users': users})

@custom_login_required
def create_account(request):
    if not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            account_service = _get_account_service()
            account_service.create_account(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                is_superuser=request.POST.get('is_superuser') == 'on'
            )
            return redirect('account_list')
            
    return render(request, 'accounts/admin_create.html', {'form': form})

@custom_login_required
def toggle_status(request, user_id):
    if not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    account_service = _get_account_service()
    account_service.toggle_account_status(user_id)
    return redirect('account_list')
