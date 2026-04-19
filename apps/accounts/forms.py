from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tên đăng nhập'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Mật khẩu'})
    )

from .models import User

class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tên đăng nhập'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tên (Không bắt buộc)'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Họ (Không bắt buộc)'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Mật khẩu'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Nhập lại Mật khẩu'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập này đã được sử dụng.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Mật khẩu không khớp.")
            
        return cleaned_data
