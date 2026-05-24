from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser, LostFoundItem, Claim


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
        if not email.endswith('@ostimteknik.edu.tr'):
            raise forms.ValidationError('Email must end with @ostimteknik.edu.tr')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            # Remove spaces, dashes, parentheses
            cleaned = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^(\+90|0)?5\d{9}$', cleaned):
                raise forms.ValidationError('Please enter a valid Turkish phone number (e.g., +905xx xxx xx xx).')
            return cleaned
        return phone

class ItemPostForm(forms.ModelForm):
    class Meta:
        model = LostFoundItem
        fields = ['title', 'description', 'item_type', 'category', 'location', 'dropoff_location', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'item_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_item_type'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'dropoff_location': forms.Select(attrs={'class': 'form-select', 'id': 'id_dropoff_location'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
        if not CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')

        if password1:
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(password1)
            except forms.ValidationError as e:
                self.add_error('password1', e)

        return cleaned_data


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['proof_description', 'preferred_contact_method']
        widgets = {
            'proof_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide specific details (color, serial numbers, stickers, passwords, brand, contents, etc.) that prove ownership.'
            }),
            'preferred_contact_method': forms.Select(attrs={'class': 'form-select'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+90 5xx xxx xx xx'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            # Remove spaces, dashes, parentheses
            cleaned = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^(\+90|0)?5\d{9}$', cleaned):
                raise forms.ValidationError('Please enter a valid Turkish phone number (e.g., +905xx xxx xx xx).')
            return cleaned
        return phone


class AccountPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
