from django.contrib import admin
from hisaab.models import *

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class BillDetailsAdmin(admin.ModelAdmin):
    list_display = ('billID', 'product_name', 'quantity', 'unitPrice', 'amount')  # Change 'bill' to 'billID'

    def product_name(self, obj):
        return obj.productID.name  # Access the product name through FK

class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'totalAmount', 'discount', 'createdAt')  # Fixed field names

class ProductAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('name', 'category_name', 'unitPrice', 'stockLevel')

    # Custom method to display the category name
    def category_name(self, obj):
        return obj.categoryID.name  # Access the category name via the foreign key

# Registering the models
admin.site.register(User)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(BillDetails, BillDetailsAdmin)
