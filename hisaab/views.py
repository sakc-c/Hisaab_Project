from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Testing!")


def sign_in(request):
    return render(request, 'hisaab/sign_in.html')

def dashboard(request):
    return render(request, 'hisaab/dashboard.html')

def inventory(request):
    return render(request, 'hisaab/inventory.html', {'inventory_items': []})  # Pass inventory items

def bills(request):
    return render(request, 'hisaab/bills.html', {'bills': []})  # Pass bills data

def admin_page(request):
    return render(request, 'hisaab/admin_page.html')
