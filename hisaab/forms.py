from django import forms
from hisaab.models import Category, Product, Bill
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


class CustomPasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        required=True
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        if new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match")
        if len(new_password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', new_password1):
            raise forms.ValidationError("Password must contain at least one number.")
        if not re.search(r'[a-zA-Z]', new_password1):
            raise forms.ValidationError("Password must contain at least one letter.")
        if not re.search(r'[@#$%^&+=!~*()_]', new_password1):
            raise forms.ValidationError("Password must contain at least one special character.")
        return cleaned_data


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


class BillForm(forms.Form):
    customer_name = forms.CharField(max_length=255, required=True, label='Customer Name')
    discount = forms.ChoiceField(choices=Bill.DISCOUNT_CHOICES, required=False, label='Discount')

    # Dynamic fields for up to 20 products
    for i in range(1, 21):
        locals()[f'product_{i}'] = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label=f'Product {i}')
        locals()[f'quantity_{i}'] = forms.IntegerField(min_value=1, required=False, label=f'Quantity {i}')

    def clean(self):
        cleaned_data = super().clean()

        # Ensure at least one product and quantity is selected
        products = [cleaned_data.get(f'product_{i}') for i in range(1, 21)]
        quantities = [cleaned_data.get(f'quantity_{i}') for i in range(1, 21)]

        if not any(products) or not any(quantities):
            raise forms.ValidationError("Please add at least one product with quantity.")

        return cleaned_data
