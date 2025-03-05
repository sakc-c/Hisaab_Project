from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect

from django.contrib.auth import get_user_model
User = get_user_model()

from hisaab.forms import CategoryForm, ProductForm
from hisaab.models import Category, Product


def user_login(request):
    if request.method == 'POST':
        users = User.objects.all()
        for user in users:
            print(user.username)
            print(user.password)
        # print("POST")
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            # print("User found")
            if user.is_active:
                # print("User active")
                login(request, user)
                return redirect(reverse('dashboard'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            # print("Wrong details")
            # print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        # print("no POST")
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


def inventory(request):
    if request.user.is_authenticated:
        categories = Category.objects.all()
        return render(request, 'hisaab/inventoryMain.html', {'categories': categories})  # Pass inventory items
    else:
       return render(request, 'hisaab/login.html') 


def bills(request):
    if request.user.is_authenticated:
        return render(request, 'hisaab/bills.html', {'bills': []})  # Pass bills data
    else:
       return render(request, 'hisaab/login.html') 


def reports(request):
    if request.user.is_authenticated:
        return render(request, 'hisaab/reports.html', {'report': []})  # Pass reports data
    else:
       return render(request, 'hisaab/login.html') 


def user_management(request):
    if request.user.is_authenticated:
        return render(request, 'hisaab/user_management.html')
    else:
       return render(request, 'hisaab/login.html') 


def add_category(request):
    if request.user.is_authenticated:
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
        product = get_object_or_404(Product, id=product_id)
        category_id = product.categoryID.id
        product.delete()
        return redirect('category', category_id=category_id)  # Redirect after deleting
    else:
       return render(request, 'hisaab/login.html') 
