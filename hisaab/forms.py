from django import forms
from hisaab.models import Category, Product


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

