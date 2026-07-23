from django.shortcuts import render,redirect,get_object_or_404
from .models import Customer
from django.contrib import messages
# from django.shortcuts import get_object_or_404


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


def customer_list(request):

    customers = Customer.objects.all()

    return render(request,"customer_list.html",
                    {
                        "customers":customers
                    }
                )


def edit_customer(request, id):

    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":

        customer.customer_id = request.POST.get("customer_id")
        customer.customer_name = request.POST.get("customer_name")
        customer.mobile_no = request.POST.get("mobile_no")
        customer.address = request.POST.get("address")

        customer.save()

        messages.success(request, "Customer Updated Successfully!")

        return redirect("customer_list")

    return render(
        request,
        "edit_customer.html",
        {
            "customer": customer
        }
    )


def delete_customer(request, id):
    
    customer = get_object_or_404(Customer, id=id)

    customer.delete()

    messages.success(request, "Customer Deleted Successfully!")

    return redirect("customer_list")