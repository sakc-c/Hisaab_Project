from decimal import Decimal

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password
from django.db.models import Count, Sum
from django.contrib.auth import get_user_model

User = get_user_model()

from hisaab.forms import CategoryForm, ProductForm, CreateUserForm, CustomPasswordChangeForm, BillForm
from hisaab.models import Category, Product, Bill, BillDetails

from django.contrib.auth.models import Group


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect(reverse('dashboard'))
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'hisaab/login.html')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'hisaab/login.html')


def dashboard(request):
    if request.user.is_authenticated:
        top_three_products_sold = (
            BillDetails.objects.values('productID', 'productID__name')
            .annotate(count=Count('productID'))
            .order_by('-count')[:3]
        )
        top_three_revenue_generating_products = (
           BillDetails.objects.values('productID', 'productID__name')
           .annotate(total_revenue=Sum('amount'))
           .order_by('-total_revenue')[:3]
        )
        sold_labels = [item['productID__name'] for item in top_three_products_sold]
        sold_data = [item['count'] for item in top_three_products_sold]
        revenue_labels = [item['productID__name'] for item in top_three_revenue_generating_products]
        revenue_data = [item['total_revenue'] for item in top_three_revenue_generating_products]

        low_stock_products = Product.objects.filter(stockLevel__lte=5)

        context = {
            'sold_labels': sold_labels,
            'sold_data': sold_data,
            'revenue_labels': revenue_labels,
            'revenue_data': revenue_data,
            'low_stock_products': low_stock_products
        }
        return render(request, 'hisaab/dashboard.html', context=context)
    else:
        return render(request, 'hisaab/login.html')


def create_user(request):
    registered = False
    errors = ""
    user_form = CreateUserForm()
    groups = Group.objects.all()
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            user.groups.set(user_form.cleaned_data['groups'])  # workaround this?
            registered = True
            return redirect('user_management')
        else:
            errors = user_form.errors
    return render(request, 'hisaab/create_user.html',
                  context={'user_form': user_form, 'registered': registered, 'groups': groups, 'errors': errors})


def change_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    form = CustomPasswordChangeForm(user=user)
    errors = {}
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password1')
            if check_password(new_password, user.password):
                errors['new_password1'] = ["New password cannot be the same as the current password."]
            else:
                user.set_password(new_password)
                user.save()
                return redirect('user_management')
        else:
            errors = form.errors
    return render(request, 'hisaab/change_password.html',
                  context={'username': user.get_username(), 'form': form, 'user_id': user.pk, 'errors': errors})


def delete_user_page(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'hisaab/delete_user.html', context={'user': user})


def delete_user(request, user_id):
    # print("deleting account...")
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    users = User.objects.exclude(groups__name='h_admin')
    return render(request, 'hisaab/user_management.html', context={'users': users})

def profile(request):
    if request.user.is_authenticated:
        return render(request, 'hisaab/profile.html', context={'user': request.user})
    else:
        return render(request, 'hisaab/unauthorised.html')


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
        users = User.objects.exclude(groups__name='h_admin')
        return render(request, 'hisaab/user_management.html', context={'users': users})
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
                return render(request, 'hisaab/InventoryMain.html',
                              {'form': form, 'errors': form.errors})  # display the errors later
        else:
            form = CategoryForm()

        return render(request, 'hisaab/InventoryMain.html', {'form': form})
    else:
        return render(request, 'hisaab/login.html')


def edit_category(request, category_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')

        category = get_object_or_404(Category, categoryID=category_id)

        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                return redirect('inventory')  # Redirect to the inventory page after saving
            else:
                print(form.errors)
                return render(request, 'hisaab/InventoryMain.html', {'form': form, 'errors': form.errors})
        else:
            form = CategoryForm(instance=category)

        return render(request, 'hisaab/InventoryMain.html', {'form': form})
    else:
        return render(request, 'hisaab/login.html')


def delete_category(request, category_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')

        category = get_object_or_404(Category, categoryID=category_id)
        category.delete()
        return redirect('inventory')  # Redirect to the inventory page after deletion
    else:
        return render(request, 'hisaab/login.html')


def category_detail(request, category_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')
        category = get_object_or_404(Category, categoryID=category_id)
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

        product = get_object_or_404(Product, productID=product_id)

        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
            category_id = request.POST.get('categoryID')
            if category_id:
                try:
                    form.instance.categoryID = Category.objects.get(categoryID=category_id)
                except (ValueError, Category.DoesNotExist) as e:
                    return redirect('category', category_id=product.categoryID.categoryID)

            if form.is_valid():
                form.save()  # Save the form with updated product and category
                return redirect('category', category_id=product.categoryID.categoryID)  # Redirect to category page
            else:
                print(form.errors)
                return redirect('category', category_id=product.categoryID.categoryID)

        else:
            form = ProductForm(instance=product)

        category = product.categoryID
        inventory_items = Product.objects.filter(categoryID=category)
        return render(request, 'hisaab/category.html', {'category': category, 'inventory_items': inventory_items})

    else:
        return render(request, 'hisaab/login.html')


def delete_product(request, product_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')

        # Use productID instead of id
        product = get_object_or_404(Product, productID=product_id)
        category_id = product.categoryID.categoryID  # Get the category ID before deleting the product
        product.delete()
        return redirect('category', category_id=category_id)
    else:
        return render(request, 'hisaab/login.html')


def add_product(request):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')

        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                product = form.save(commit=False)
                product.createdBy = request.user  # Automatically set createdBy to the current user
                product.save()
                return redirect('category', category_id=request.POST.get('categoryID'))
            else:
                return render(request, 'hisaab/InventoryMain.html', {'form': form, 'errors': form.errors})
        else:
            form = ProductForm()
        return render(request, 'hisaab/InventoryMain.html', {'form': form})
    else:
        return render(request, 'hisaab/login.html')


def bills(request):
    if request.user.is_authenticated:
        user_groups = list(request.user.groups.values_list('name', flat=True))
        bills = Bill.objects.all()
        products = Product.objects.all()
        return render(request, 'hisaab/bills.html', {'bills': bills, 'products': products, 'user_groups': user_groups})
    else:
        return render(request, 'hisaab/login.html')


def create_bill(request):
    if not request.user.is_authenticated:
        return render(request, 'hisaab/login.html')

    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Get cleaned data from the form
                    customer_name = form.cleaned_data['customer_name']
                    discount = form.cleaned_data.get('discount', 0)

                    # Calculate the total dynamically from products and quantities
                    total = Decimal(0)
                    products_data = []

                    for i in range(1, 21):  # Loop through up to 20 products
                        product_field = f'product_{i}'
                        quantity_field = f'quantity_{i}'

                        if product_field in form.cleaned_data and quantity_field in form.cleaned_data:
                            product = form.cleaned_data[product_field]
                            quantity = form.cleaned_data[quantity_field]
                            if product and quantity:
                                if product.stockLevel < quantity:
                                    form.add_error(None,
                                                   f'Insufficient stock for {product.name}. Available: {product.stockLevel}, Requested: {quantity}')
                                    raise ValueError(
                                        f'Insufficient stock for {product.name}. Available: {product.stockLevel}, Requested: {quantity}')
                                # Calculate the total amount for this product
                                amount = product.unitPrice * quantity
                                total += amount
                                products_data.append({
                                    'product': product,
                                    'quantity': quantity,
                                    'unit_price': product.unitPrice,
                                    'amount': amount
                                })

                    # Apply discount, ensuring both values are Decimal
                    total = total * (1 - Decimal(discount) / Decimal(100))

                    # Create the bill entry in the database
                    bill = Bill.objects.create(
                        userID=request.user,
                        customerName=customer_name,
                        discount=discount,
                        totalAmount=total
                    )

                    # Loop through the products and quantities to create BillDetails entries
                    for product_data in products_data:
                        product = product_data['product']
                        quantity = product_data['quantity']
                        unit_price = product_data['unit_price']
                        amount = product_data['amount']

                        # Create a BillDetails entry for each product
                        BillDetails.objects.create(
                            billID=bill,
                            productID=product,
                            quantity=quantity,
                            unitPrice=unit_price,
                            amount=amount
                        )

                        # Update stock level of the product
                        product.stockLevel -= quantity
                        product.save()

                    return redirect('bills')  # Redirect to the bills page

            except ValueError as e:
                # Handle insufficient stock error
                return render(request, 'hisaab/create_bill.html', {
                    'form': form,
                    'products': Product.objects.all(),
                    'error': str(e)
                })

    else:
        form = BillForm()

    # Pass all products to the template
    products = Product.objects.all()

    return render(request, 'hisaab/create_bill.html', {
        'form': form,
        'products': products
    })



def delete_bill(request, bill_id):
    if request.user.is_authenticated:
        bill = get_object_or_404(Bill, pk=bill_id)

        # Restore stock for all products in the bill
        bill_details = BillDetails.objects.filter(billID=bill)
        for detail in bill_details:
            product = detail.productID
            product.stockLevel += detail.quantity
            product.save()

        bill_details.delete()  # Delete BillDetails
        bill.delete()  # Delete the Bill

        return redirect('bills')  # Redirect to the bills list page
    else:
        return render(request, 'hisaab/login.html')
