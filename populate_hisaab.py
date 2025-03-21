import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisaab_project.settings')

import django
django.setup()
from hisaab.models import *

from django.contrib.auth import get_user_model
User = get_user_model()

def populate():
    # Create three groups if they don't exist
    group_names = ['h_admin', 'inventory_manager', 'cashier']
    groups = {}

    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)
        groups[group_name] = group
        if created:
            print(f"Created Group: {group_name}")
        else:
            print(f"Group {group_name} already exists")

    # Create Users
    users = [
        {"username": "AdminUser", "password": "admin123"},
        {"username": "Sakshi", "password": "sakshi123"},
        {"username": "Vanshika", "password": "vanshika123"},
        {"username": "Akash", "password": "akash123"},
        {"username": "inventoryManager1", "password": "im112345"},
        {"username": "inventoryManager2", "password": "im212345"},
        {"username": "inventoryManager3", "password": "im312345"},
        {"username": "Cashier1", "password": "cash11234"},
        {"username": "Cashier2", "password": "cash21234"},
        {"username": "Cashier3", "password": "cash31234"},
        {"username": "AdminUserBackup", "password": "admin2123"},
    ]

    user_instances = []
    for user_data in users:
        user = User.objects.create(username=user_data["username"])
        user.set_password(user_data["password"])
        user.save()
        user_instances.append(user)
        print(f"Created User: {user}")
    
    # Add to appropriate groups
    for i in range(4):
        user_instances[i].groups.add(Group.objects.get(name="h_admin"))
    for i in range(4, 7):
        user_instances[i].groups.add(Group.objects.get(name="inventory_manager"))
    for i in range(7, 10):
        user_instances[i].groups.add(Group.objects.get(name="inventory_manager"))
    user_instances[10].groups.add(Group.objects.get(name="h_admin"))
    print("Added created users in appropriate groups")

    # Create Categories
    categories = [
        {"name": "Engine Oil", "description": "Various types of engine oils"},
        {"name": "Brake Pads", "description": "Brake pads for different car models"},
        {"name": "Air Filters", "description": "Air filters for engines"},
        {"name": "Spark Plugs", "description": "High-performance spark plugs for various engines"},
        {"name": "Coolants", "description": "Engine coolants for temperature regulation"},
    ]

    category_instances = {}
    for category_data in categories:
        category = Category.objects.create(**category_data)
        category_instances[category_data["name"]] = category
        print(f"Created Category: {category}")

    # Create Products
    products = [
        {"name": "Castrol 5W-30", "categoryID": category_instances["Engine Oil"], "unitPrice": 50.00, "stockLevel": 100, "user": user_instances[1]},
        {"name": "Bosch Brake Pads", "categoryID": category_instances["Brake Pads"], "unitPrice": 120.00, "stockLevel": 50, "user": user_instances[1]},
        {"name": "K&N Air Filter", "categoryID": category_instances["Air Filters"], "unitPrice": 80.00, "stockLevel": 75, "user": user_instances[1]},
        {"name": "Mobil 1 0W-40", "categoryID": category_instances["Engine Oil"], "unitPrice": 60.00, "stockLevel": 90, "user": user_instances[0]},
        {"name": "ACDelco Brake Pads", "categoryID": category_instances["Brake Pads"], "unitPrice": 110.00, "stockLevel": 60, "user": user_instances[2]},
        {"name": "FRAM Air Filter", "categoryID": category_instances["Air Filters"], "unitPrice": 70.00, "stockLevel": 80, "user": user_instances[0]},
        {"name": "NGK Iridium Spark Plug", "categoryID": category_instances["Spark Plugs"], "unitPrice": 25.00, "stockLevel": 150, "user": user_instances[1]},
        {"name": "Bosch Spark Plug", "categoryID": category_instances["Spark Plugs"], "unitPrice": 30.00, "stockLevel": 140, "user": user_instances[2]},
        {"name": "Prestone Coolant", "categoryID": category_instances["Coolants"], "unitPrice": 40.00, "stockLevel": 95, "user": user_instances[0]},
        {"name": "Zerex Coolant", "categoryID": category_instances["Coolants"], "unitPrice": 45.00, "stockLevel": 85, "user": user_instances[2]},
    ]
    
    product_instances = []
    for product_data in products:
        product = Product.objects.create(**product_data)
        product_instances.append(product)
        print(f"Created Product: {product}")

    # Create Bills
    bills = [
        {"user": user_instances[0], "totalAmount": 0, "discount": 5},
        {"user": user_instances[1], "totalAmount": 0, "discount": 10},
        {"user": user_instances[2], "totalAmount": 0, "discount": 15},
        {"user": user_instances[0], "totalAmount": 0, "discount": 7},
        {"user": user_instances[1], "totalAmount": 0, "discount": 12},
        {"user": user_instances[2], "totalAmount": 0, "discount": 8},
        {"user": user_instances[0], "totalAmount": 0, "discount": 6},
    ]
    
    bill_instances = []
    for bill_data in bills:
        bill = Bill.objects.create(**bill_data)
        bill_instances.append(bill)
        print(f"Created Bill: {bill}")
    
    # Create BillDetails and update totalAmount
    bill_details = [
        {"billID": bill_instances[0], "productID": product_instances[0], "quantity": 2, "unitPrice": 50.00},
        {"billID": bill_instances[1], "productID": product_instances[1], "quantity": 1, "unitPrice": 120.00},
        {"billID": bill_instances[2], "productID": product_instances[2], "quantity": 3, "unitPrice": 80.00},
        {"billID": bill_instances[3], "productID": product_instances[3], "quantity": 2, "unitPrice": 60.00},
        {"billID": bill_instances[4], "productID": product_instances[4], "quantity": 1, "unitPrice": 110.00},
        {"billID": bill_instances[5], "productID": product_instances[5], "quantity": 4, "unitPrice": 70.00},
        {"billID": bill_instances[6], "productID": product_instances[6], "quantity": 3, "unitPrice": 25.00},
    ]
    
    for detail_data in bill_details:
        bill_detail = BillDetails.objects.create(**detail_data)
        bill = detail_data["billID"]
        bill.totalAmount += Decimal(bill_detail.quantity) * Decimal(bill_detail.unitPrice)
        bill.save()
        print(f"Created BillDetail: {bill_detail}")

    print("Database population complete!")
if __name__ == "__main__":
    print("Starting population script...")
    populate()