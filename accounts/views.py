from django.shortcuts import render,redirect
from .models import Customer
from django.contrib import messages


def home(request):
    return render(request,"home.html")


def admin_login(request):
    return render(request,"admin_login.html")


def customer_login(request):
    return render(request,"customer_login.html")

def add_customer(request):

    if request.method == "POST":
        
        customer_id = request.POST.get("customer_id")
        customer_name = request.POST.get("customer_name")
        mobile_no = request.POST.get("mobile_no")
        address = request.POST.get("address")

        Customer.objects.create(

            customer_id=customer_id,
            customer_name=customer_name,
            mobile_no=mobile_no,
            address=address

        )

        messages.success(request, "Customer Added Successfully!")
        
        return redirect("add_customer")

    return render(request,"add_customer.html")