from django.shortcuts import render
from django.http import HttpResponse


def sign_in(request):
    return render(request, 'hisaab/sign_in.html')

def dashboard(request):
    return render(request, 'hisaab/dashboard.html')

def inventory(request):
    return render(request, 'hisaab/inventory.html', {'inventory_items': []})  # Pass inventory items

def bills(request):
    return render(request, 'hisaab/bills.html', {'bills': []})  # Pass bills data

def reports(request):
    return render(request, 'hisaab/reports.html', {'report': []})  # Pass reports data

def user_management(request):
    return render(request, 'hisaab/user_management.html')
