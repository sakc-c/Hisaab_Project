from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

from hisaab.forms import CategoryForm, ProductForm
from hisaab.models import Category, Product
from django.contrib.auth.models import Group

from hisaab.forms import CreateUserForm


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('dashboard'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'hisaab/login.html')

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'hisaab/login.html')

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'hisaab/dashboard.html')
    else:
       return render(request, 'hisaab/login.html') 

def create_user(request):
    registered = False
    errors = ""
    user_form = CreateUserForm()
    # print("Entered user creation")
    groups = Group.objects.all()
    if request.method == 'POST':
        # print("POST")
        user_form = CreateUserForm(request.POST)
        if user_form.is_valid():
            # print("form valid")
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            user.groups.set(user_form.cleaned_data['groups']) # workaround this?
            registered = True
        else:
            errors = user_form.errors
            # print(errors)
    return render(request, 'hisaab/user_management.html', context={'user_form': user_form, 'registered': registered, 'groups': groups, 'errors': errors})

def inventory(request):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')
        categories = Category.objects.all()
        return render(request, 'hisaab/inventoryMain.html', {'categories': categories})  # Pass inventory items
    else:
       return render(request, 'hisaab/login.html') 


def bills(request):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'cashier']).exists():
            return render(request, 'hisaab/unauthorised.html')
        return render(request, 'hisaab/bills.html', {'bills': []})  # Pass bills data
    else:
       return render(request, 'hisaab/login.html') 


def reports(request):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='h_admin').exists():
            return render(request, 'hisaab/unauthorised.html')
        return render(request, 'hisaab/reports.html', {'report': []})  # Pass reports data
    else:
       return render(request, 'hisaab/login.html') 


def user_management(request):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='h_admin').exists():
            return render(request, 'hisaab/unauthorised.html')
        return render(request, 'hisaab/user_management.html')
    else:
       return render(request, 'hisaab/login.html') 


def add_category(request):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='h_admin').exists():
            return render(request, 'hisaab/unauthorised.html')
        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()  # Saves the category
                return redirect('inventory')  # Redirect back to the inventory page after adding a category
            else:
                return redirect('inventory')
        else:
            form = CategoryForm()

        return render(request, 'hisaab/InventoryMain.html', {'form': form})
    else:
       return render(request, 'hisaab/login.html') 


def category_detail(request, category_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')
        category = get_object_or_404(Category, id=category_id)
        inventory_items = Product.objects.filter(categoryID=category_id)  # Ensure filtering correctly

        return render(request, 'hisaab/category.html', {
            'category': category,
            'inventory_items': inventory_items  # Pass products properly
        })
    else:
       return render(request, 'hisaab/login.html') 

def edit_product(request, product_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')
        product = get_object_or_404(Product, id=product_id)

        if request.method == 'POST':
            # Bind the form with the POST data and the current product instance
            form = ProductForm(request.POST, instance=product)

            if form.is_valid():
                form.save()
                return redirect('category',
                                category_id=product.categoryID.id)  # Redirect back to the category page after saving
            else:
                print(form.errors)
                return redirect('category',
                                category_id=product.categoryID.id)

        else:
            # If GET request, initialize the form with the current product's data
            form = ProductForm(instance=product)

        category = product.categoryID
        inventory_items = Product.objects.filter(categoryID=category)
        return render(request, 'hisaab/category.html', {'category': category,'inventory_items': inventory_items, })
    else:
       return render(request, 'hisaab/login.html') 


def delete_product(request, product_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')
        product = get_object_or_404(Product, id=product_id)
        category_id = product.categoryID.id
        product.delete()
        return redirect('category', category_id=category_id)  # Redirect after deleting
    else:
       return render(request, 'hisaab/login.html') 
