from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from hisaab.forms import CategoryForm, ProductForm
from hisaab.models import Category, Product


def sign_in(request):
    return render(request, 'hisaab/sign_in.html')


def dashboard(request):
    return render(request, 'hisaab/dashboard.html')


def inventory(request):
    categories = Category.objects.all()
    return render(request, 'hisaab/inventoryMain.html', {'categories': categories})  # Pass inventory items


def bills(request):
    return render(request, 'hisaab/bills.html', {'bills': []})  # Pass bills data


def reports(request):
    return render(request, 'hisaab/reports.html', {'report': []})  # Pass reports data


def user_management(request):
    return render(request, 'hisaab/user_management.html')


def add_category(request):
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


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    inventory_items = Product.objects.filter(categoryID=category_id)  # Ensure filtering correctly

    return render(request, 'hisaab/category.html', {
        'category': category,
        'inventory_items': inventory_items  # Pass products properly
    })


def edit_product(request, product_id):
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


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category_id = product.categoryID.id
    product.delete()
    return redirect('category', category_id=category_id)  # Redirect after deleting
