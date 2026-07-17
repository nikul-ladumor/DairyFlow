from django.shortcuts import render

def home(request):
    return render(request,"home.html")


def admin_login(request):
    return render(request,"admin_login.html")


def customer_login(request):
    return render(request,"customer_login.html")