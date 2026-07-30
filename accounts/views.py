from django.shortcuts import render,redirect,get_object_or_404
# from .models import *
from .models import Customer
from .models import MilkEntry
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

        # Required validation
        if not customer_name or not mobile_no or not address:
            messages.error(request, "Please fill all fields")

            return redirect("add_customer")

        # mobile validation
        if len(mobile_no)!=10 or not mobile_no.isdigit():
            messages.error(request, "Mobile number must be exactly 10 digits.")

            return redirect("add_customer")

        # Duplicate Mobile Number Validation
        if Customer.objects.filter(mobile_no=mobile_no).exists():
            messages.error(request, "Mobile number already exists.")
            return redirect("add_customer")
        
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

        customer_id = request.POST.get("customer_id")
        customer_name = request.POST.get("customer_name")
        mobile_no = request.POST.get("mobile_no")
        address = request.POST.get("address")

        # Required Validation
        if not customer_name or not mobile_no or not address:
            messages.error(request, "Please fill all fields.")
            return redirect("edit_customer", id=id)

        # Mobile Number Validation
        if len(mobile_no) != 10 or not mobile_no.isdigit():
            messages.error(request, "Mobile number must be exactly 10 digits.")
            return redirect("edit_customer", id=id)

        # Duplicate Mobile Number Validation
        if Customer.objects.filter(mobile_no=mobile_no).exclude(id=id).exists():
            messages.error(request, "Mobile number already exists.")
            return redirect("edit_customer",id=id)

        customer.customer_id = customer_id
        customer.customer_name = customer_name
        customer.mobile_no = mobile_no
        customer.address = address

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


def add_milk_entry(request):

    customers = Customer.objects.all()

    if request.method == "POST":

        customer_id = request.POST.get("customer")
        date = request.POST.get("date")
        shift = request.POST.get("shift")
        milk_quantity = request.POST.get("milk_quantity")
        milk_type = request.POST.get("milk_type")
        rate = request.POST.get("rate")

        if not customer_id or not date or not shift or not milk_quantity or not milk_type or not rate:

            messages.error(request, "Please fill all fields.")

            return redirect("add_milk_entry")

        customer = get_object_or_404(Customer, id=customer_id)

        MilkEntry.objects.create(
            customer=customer,
            date=date,
            shift=shift,
            milk_quantity=milk_quantity,
            milk_type=milk_type,
            rate=rate
        )

        messages.success(request, "Milk Entry Added Successfully!")

        return redirect("add_milk_entry")

    return render(
        request,
        "add_milk_entry.html",
        {
            "customers": customers
        }
    )


def milk_entry_list(request):

    milk_entries = MilkEntry.objects.all()

    return render(
        request,
        "milk_entry_list.html",
        {
            "milk_entries": milk_entries
        }
    )


def edit_milk_entry(request, id):

    milk_entry = get_object_or_404(MilkEntry, id=id)

    customers = Customer.objects.all()

    if request.method == "POST":

        customer_id = request.POST.get("customer")
        date = request.POST.get("date")
        shift = request.POST.get("shift")
        milk_quantity = request.POST.get("milk_quantity")
        milk_type = request.POST.get("milk_type")
        rate = request.POST.get("rate")

        customer = Customer.objects.get(id=customer_id)
        milk_entry.customer = customer
        milk_entry.date = date
        milk_entry.shift = shift
        milk_entry.milk_quantity = milk_quantity
        milk_entry.milk_type = milk_type
        milk_entry.rate = rate

        milk_entry.save()

        messages.success(request, "Milk Entry Updated Successfully!")

        return redirect("milk_entry_list")

    return render(
              request,
              "edit_milk_entry.html",
              {
                  "milk_entry": milk_entry,
                  "customers": customers
              }
          )
     

def delete_milk_entry(request, id):
    
    milk_entry = get_object_or_404(MilkEntry, id=id)

    milk_entry.delete()

    messages.success(request, "Milk Entry Deleted Successfully!")

    return redirect("milk_entry_list")