from decimal import Decimal

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password
from django.db.models import F, Sum, ProtectedError
from django.contrib.auth import get_user_model

from hisaab_project import settings

User = get_user_model()

from hisaab.forms import CategoryForm, ProductForm, CreateUserForm, CustomPasswordChangeForm, BillForm
from hisaab.models import Category, Product, Bill, BillDetails, Report

from django.contrib.auth.models import Group
from hisaab.helpers import get_bill_context


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
            BillDetails.objects
            .values('productID', 'productID__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:3]
        )
        top_three_revenue_generating_products = (
            BillDetails.objects
            .values('productID', 'productID__name')
            .annotate(
                total_revenue=Sum(F('quantity') * F('unitPrice'))  # Multiply quantity and unitPrice
            )
            .order_by('-total_revenue')[:3]
        )
        sold_labels = [item['productID__name'] for item in top_three_products_sold]
        sold_data = [item['total_quantity'] for item in top_three_products_sold]
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


# def delete_user_page(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#     return render(request, 'hisaab/delete_user.html', context={'user': user})


def delete_user(request, user_id):
    if request.user.is_authenticated:
        # Check user permission
        if not request.user.groups.filter(name__in=['h_admin']).exists():
            return render(request, 'hisaab/unauthorised.html')

        # Get the user to delete
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        users = User.objects.exclude(groups__name='h_admin')
        return redirect('user_management')
    else:
        return render(request, 'hisaab/login.html')


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

        # Get all bills for display
        bills = Bill.objects.all().order_by('-createdAt')  # Most recent bills first

        context = {
            'bills': bills,
            'MEDIA_URL': settings.MEDIA_URL,
        }

        return render(request, 'hisaab/bills.html', context)
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
        users = User.objects.exclude(id=request.user.id)
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
                try:
                    form.save()  # Save the category
                    return redirect('inventory')
                except Exception as e:
                    messages.error(request, f"Error: {e}")
                    return redirect('inventory')  # Redirect to inventory in case of failure
            else:
                messages.error(request, "Category with this name already exists.")  # Show error for duplicate name
                return redirect('inventory')
        else:
            form = CategoryForm()

        return render(request, 'hisaab/InventoryMain.html', {'form': form})

    else:
        return render(request, 'hisaab/login.html')


def edit_category(request, category_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')

        category = get_object_or_404(Category, id=category_id)

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

        category = get_object_or_404(Category, id=category_id)
        try:
            category.delete()
            messages.success(request, "Category deleted successfully.")
        except ProtectedError:
            messages.error(request, "Cannot delete this category because products are linked to it.")

        return redirect('inventory')  # Redirect to inventory after deletion attempt
    else:
        return render(request, 'hisaab/login.html')


def category_detail(request, category_id):
    if request.user.is_authenticated:
        if not request.user.groups.filter(name__in=['h_admin', 'inventory_manager']).exists():
            return render(request, 'hisaab/unauthorised.html')
        category = get_object_or_404(Category, id=category_id)
        inventory_items = Product.objects.filter(categoryID=category)  # Ensure filtering correctly

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
            form = ProductForm(request.POST, instance=product)
            category_id = request.POST.get('categoryID')
            if category_id:
                try:
                    form.instance.categoryID = Category.objects.get(id=category_id)
                except (ValueError, Category.DoesNotExist) as e:
                    return redirect('category', category_id=product.categoryID.id)

            if form.is_valid():
                form.save()  # Save the form with updated product and category
                return redirect('category', category_id=product.categoryID.id)  # Redirect to category page
            else:
                print(form.errors)
                return redirect('category', category_id=product.categoryID.id)

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
        product = get_object_or_404(Product, id=product_id)
        category_id = product.categoryID.id  # Get the category ID before deleting the product
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
                product.user = request.user  # Automatically set createdBy to the current user
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
        if not request.user.groups.filter(name__in=['h_admin', 'cashier']).exists():
            return render(request, 'hisaab/unauthorised.html')
        user_groups = list(request.user.groups.values_list('name', flat=True))
        bills = Bill.objects.all()
        products = Product.objects.all()
        context = {
            'bills': bills,
            'products': products,
            'user_groups': user_groups,
            'MEDIA_URL': settings.MEDIA_URL,  # Pass MEDIA_URL to the template
        }
        return render(request, 'hisaab/bills.html', context)
    else:
        return render(request, 'hisaab/login.html')


def create_bill(request):
    if not request.user.is_authenticated:
        return render(request, 'hisaab/login.html')
    if not request.user.groups.filter(name__in=['h_admin', 'cashier']).exists():
        return render(request, 'hisaab/unauthorised.html')

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
                    discount_amount = total * (Decimal(discount) / Decimal(100))
                    final_total = total - discount_amount

                    # Create the bill entry in the database
                    bill = Bill.objects.create(
                        user=request.user,
                        customerName=customer_name,
                        discount=discount,
                        totalAmount=final_total
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

                    context = get_bill_context(bill)  # get the context for the PDF

                    # Generate and send PDF as a response
                    return bill.generate_pdf(context, "hisaab/bill_pdf.html")

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
        if not request.user.groups.filter(name__in=['h_admin', 'cashier']).exists():
            return render(request, 'hisaab/unauthorised.html')
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


def download_pdf(request, bill_id):
    if request.user.is_authenticated:
        bill = Bill.objects.get(id=bill_id)
        context = get_bill_context(bill)  # Get the context for the PDF
        response = bill.generate_pdf(context,
                                     "hisaab/bill_pdf.html")  # Use the Render class to generate the PDF dynamically
        return response
    else:
        return render(request, 'hisaab/login.html')


def reports_page(request):
    # Check if the user is logged in and admin
    if not request.user.is_authenticated:
        return render(request, 'hisaab/login.html')

    if not request.user.groups.filter(name="h_admin").exists():
        return render(request, 'hisaab/unauthorised.html')

    reports = Report.objects.all()
    return render(request, "hisaab/reports.html", {"reports": reports})


def create_report(request, report_type):
    # Check if the user is logged in and admin
    if not request.user.is_authenticated:
        return render(request, 'hisaab/login.html')

    if not request.user.groups.filter(name="h_admin").exists():
        return render(request, 'hisaab/unauthorised.html')

        # Create a new report entry in the database
    report = Report.objects.create(user=request.user, reportType=report_type)

    # Fetch all products and bills (based on report type)
    all_products = Product.objects.all() if report_type == "stock" else None
    all_bills = Bill.objects.all() if report_type == "sales" else None

    context = {
        "report": report,
        "createdBy": report.user.username if report.user else "Unknown",
        "dateCreated": report.createdAt.strftime('%Y-%m-%d'),
        "products": all_products,
        "bills": all_bills,
    }

    template = "hisaab/stock_report.html" if report.reportType == "stock" else "hisaab/sales_report.html"
    response = report.generate_pdf(context, template)  # Generate the PDF

    return response


def download_report(request, report_id):
    # Check if the user is logged in and admin
    if not request.user.is_authenticated:
        return render(request, 'hisaab/login.html')

    if not request.user.groups.filter(name="h_admin").exists():
        return render(request, 'hisaab/unauthorised.html')

    report = get_object_or_404(Report, pk=report_id)

    # Determine context and template based on report type
    if report.reportType == 'stock':
        context = {
            "report": report,
            "createdBy": report.user.username,
            "dateCreated": report.createdAt.strftime('%Y-%m-%d'),
            "products": Product.objects.select_related("categoryID").all(),
        }
        template = "hisaab/stock_report.html"
    elif report.reportType == 'sales':
        context = {
            "report": report,
            "createdBy": report.user.username,
            "dateCreated": report.createdAt.strftime('%Y-%m-%d'),
            "bills": Bill.objects.all(),
        }
        template = "hisaab/sales_report.html"
    else:
        return HttpResponse("Invalid report type", status=400)

    # Generate and return the PDF response
    return report.generate_pdf(context, template)


def delete_report(request, report_id):
    # Check if the user is logged in and admin
    if not request.user.is_authenticated:
        return render(request, 'hisaab/login.html')

    if not request.user.groups.filter(name="h_admin").exists():
        return render(request, 'hisaab/unauthorised.html')

    report = get_object_or_404(Report, pk=report_id)
    report.delete()  # Delete the report from the database
    return redirect('reports_page')
