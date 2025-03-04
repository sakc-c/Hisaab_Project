import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisaab_project.settings')

import django
django.setup()
from hisaab.models import *

def populate():
    # Create Users
    users = [
        {"userID": 1, "username": "Sakshi", "password": "sakshi123", "role": "Admin"},
        {"userID": 2, "username": "Vanshika", "password": "vanshika123", "role": "Inventory Manager"},
        {"userID": 3, "username": "Akash", "password": "akash123", "role": "Cashier"},
    ]

    for user_data in users:
        # Create user without password first
        user = User.objects.create(
            userID=user_data["userID"],
            username=user_data["username"],
            role=user_data["role"],
        )

        # Set password and hash it
        user.set_password(user_data["password"])  # Hash the password using set_password()

        # Save the user to the database
        user.save()

        print(f"Created User: {user}")

    # Create Categories
    categories = [
        {"categoryID": 1, "name": "Engine Oil", "description": "Various types of engine oils"},
        {"categoryID": 2, "name": "Brake Pads", "description": "Brake pads for different car models"},
        {"categoryID": 3, "name": "Air Filters", "description": "Air filters for engines"},
    ]

    category_instances = {}  # To store category instances for later use

    for category_data in categories:
        category = Category.objects.create(
            categoryID=category_data["categoryID"],
            name=category_data["name"],
            description=category_data["description"],
        )
        category_instances[category_data["categoryID"]] = category  # Store category instance
        print(f"Created Category: {category}")

    # Create Products
    products = [
        {"productID": 1, "name": "Castrol 5W-30", "categoryID": 1, "unitPrice": 50.00, "stockLevel": 100, "createdBy": User.objects.get(userID=2)},  # Created by Vanshika
        {"productID": 2, "name": "Bosch Brake Pads", "categoryID": 2, "unitPrice": 120.00, "stockLevel": 50, "createdBy": User.objects.get(userID=2)},  # Created by Vanshika
        {"productID": 3, "name": "K&N Air Filter", "categoryID": 3, "unitPrice": 80.00, "stockLevel": 75, "createdBy": User.objects.get(userID=2)},  # Created by Vanshika
    ]

    for product_data in products:
        category_instance = category_instances.get(product_data["categoryID"])  # Retrieve the category instance
        product = Product.objects.create(
            productID=product_data["productID"],
            name=product_data["name"],
            categoryID=category_instance,  # Use the category instance here
            unitPrice=product_data["unitPrice"],
            stockLevel=product_data["stockLevel"],
            createdBy=product_data["createdBy"],
        )
        print(f"Created Product: {product}")

    # Create Bills
    bills = [
        {"billID": 1, "userID": User.objects.get(userID=3), "totalAmount": 0, "discount": 5},  # Created by Akash
        {"billID": 2, "userID": User.objects.get(userID=3), "totalAmount": 0, "discount": 10},  # Created by Akash
    ]

    for bill_data in bills:
        bill = Bill.objects.create(
            billID=bill_data["billID"],
            userID=bill_data["userID"],
            totalAmount=bill_data["totalAmount"],
            discount=bill_data["discount"],
        )
        print(f"Created Bill: {bill}")

    # Create BillDetails
    bill_details = [
        {"billID": Bill.objects.get(billID=1), "productID": Product.objects.get(productID=1), "quantity": 2, "unitPrice": 50.00},
        {"billID": Bill.objects.get(billID=1), "productID": Product.objects.get(productID=2), "quantity": 1, "unitPrice": 120.00},
        {"billID": Bill.objects.get(billID=2), "productID": Product.objects.get(productID=3), "quantity": 3, "unitPrice": 80.00},
    ]

    for detail_data in bill_details:
        bill_detail = BillDetails.objects.create(
            billID=detail_data["billID"],
            productID=detail_data["productID"],
            quantity=detail_data["quantity"],
            unitPrice=detail_data["unitPrice"],
        )
        print(f"Created BillDetail: {bill_detail}")

        # Update the total amount of the bill
        bill = detail_data["billID"]
        bill.totalAmount += Decimal(bill_detail.quantity) * Decimal(bill_detail.unitPrice)
        bill.save()

    print("Population complete!")

if __name__ == "__main__":
    print("Starting population script...")
    populate()