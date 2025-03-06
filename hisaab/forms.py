from django import forms
from hisaab.models import Category, Product
from django.contrib.auth.models import Group
from .models import User
from django.contrib.auth import get_user_model
import re

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'password')

class CreateUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'groups')

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple,
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose a different username.")
        if not username[0].isalpha():
            raise forms.ValidationError("Username must begin with a letter. Please choose a different username.")
        if len(username) < 7:
            raise forms.ValidationError("Username too short. Please choose a different username.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")
        if not re.search(r'[a-zA-Z]', password):
            raise forms.ValidationError("Password must contain at least one letter.")
        if not re.search(r'[@#$%^&+=!~*()_]', password):
            raise forms.ValidationError("Password must contain at least one special character.")
        return password

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image_url']

    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Category description'}))
    image_url = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'Image URL (optional)'}), required=False)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unitPrice', 'stockLevel', 'categoryID']  # Include all fields you want to be editable

