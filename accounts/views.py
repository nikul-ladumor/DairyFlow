from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from django.core.paginator import Paginator
from django.shortcuts import render,redirect,get_object_or_404
# from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import check_password, make_password
from .models import Customer, MilkEntry, Bill, PasswordResetOTP
from datetime import timedelta
import random
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import datetime
from .models import Customer
from .models import MilkEntry
from .models import Bill
from django.contrib import messages
from django.db.models import Sum, F, DecimalField, ExpressionWrapper

# from django.shortcuts import get_object_or_404


def home(request):
    return render(request, "base.html")


def admin_base(request):
    return render(request, "admin_base.html")


def admin_logout(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("admin_login")


def customer_logout(request):

    request.session.flush()

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("customer_login")



def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_superuser:

            login(request, user)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

        return redirect("admin_login")

    return render(
        request,
        "admin_login.html"
    )

@login_required(login_url="admin_login")
def dashboard(request):

    # Total Customers
    total_customers = Customer.objects.count()

    # Total Milk Entries
    total_milk_entries = MilkEntry.objects.count()

    # Total Bills
    total_bills = Bill.objects.count()

    # Total Milk Quantity
    total_milk_quantity = MilkEntry.objects.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    # Total Bill Amount
    total_bill_amount = Bill.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    # Cow Milk
    cow_milk = MilkEntry.objects.filter(
        milk_type="Cow"
    ).aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    # Buffalo Milk
    buffalo_milk = MilkEntry.objects.filter(
        milk_type="Buffalo"
    ).aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    # Recent Milk Entries
    recent_milk_entries = MilkEntry.objects.select_related(
        "customer"
    ).order_by("-date")[:5]

    # Recent Bills
    recent_bills = Bill.objects.select_related(
        "customer"
    ).order_by("-bill_date")[:5]

    return render(
        request,
        "dashboard.html",
        {
            "total_customers": total_customers,
            "total_milk_entries": total_milk_entries,
            "total_bills": total_bills,
            "total_milk_quantity": total_milk_quantity,
            "total_bill_amount": total_bill_amount,
            "cow_milk": cow_milk,
            "buffalo_milk": buffalo_milk,
            "recent_milk_entries": recent_milk_entries,
            "recent_bills": recent_bills,
        }
    )


def customer_login(request):

    if request.method == "POST":

        customer_id = request.POST.get("customer_id")
        password = request.POST.get("password")

        try:

            customer = Customer.objects.get(
                customer_id=customer_id
            )

        except Customer.DoesNotExist:

            messages.error(
                request,
                "Invalid Customer ID or Password."
            )

            return redirect("customer_login")


        if check_password(password, customer.password):

            request.session["customer_id"] = customer.id

            return redirect("customer_dashboard")


        messages.error(
            request,
            "Invalid Customer ID or Password."
        )

        return redirect("customer_login")


    return render(
        request,
        "customer_login.html"
    )


def forgot_password(request):

    if request.method == "POST":

        customer_id = request.POST.get("customer_id")
        mobile_no = request.POST.get("mobile_no")

        try:

            customer = Customer.objects.get(
                customer_id=customer_id,
                mobile_no=mobile_no
            )

        except Customer.DoesNotExist:

            messages.error(
                request,
                "Invalid Customer ID or Mobile Number."
            )

            return redirect("forgot_password")

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save hashed OTP
        PasswordResetOTP.objects.create(
            customer=customer,
            otp_hash=make_password(otp)
        )

        # Store customer in session for next step
        request.session["reset_customer_id"] = customer.id

        # Development testing
        print("================================")
        print("DairyFlow Password Reset OTP:", otp)
        print("================================")

        messages.success(
            request,
            "OTP generated successfully. Check the server console."
        )

        return redirect("verify_otp")

    return render(
        request,
        "forgot_password.html"
    )


def verify_otp(request):

    customer_id = request.session.get("reset_customer_id")

    if not customer_id:

        messages.error(
            request,
            "Please start the password reset process again."
        )

        return redirect("forgot_password")

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        otp_record = PasswordResetOTP.objects.filter(
            customer=customer,
            is_verified=False
        ).order_by("-created_at").first()

        # OTP record not found
        if not otp_record:

            messages.error(
                request,
                "OTP not found. Please request a new OTP."
            )

            return redirect("forgot_password")

        # OTP expired after 5 minutes
        if timezone.now() > (
            otp_record.created_at + timedelta(minutes=5)
        ):

            messages.error(
                request,
                "OTP has expired. Please request a new OTP."
            )

            return redirect("forgot_password")

        # Maximum 3 attempts
        if otp_record.attempts >= 3:

            messages.error(
                request,
                "Too many incorrect attempts. Please request a new OTP."
            )

            return redirect("forgot_password")

        # Check OTP
        if check_password(
            entered_otp,
            otp_record.otp_hash
        ):

            otp_record.is_verified = True
            otp_record.save()

            request.session["otp_verified"] = True

            messages.success(
                request,
                "OTP verified successfully."
            )

            return redirect("reset_password")

        # Wrong OTP
        otp_record.attempts += 1
        otp_record.save()

        messages.error(
            request,
            "Invalid OTP."

        )

        return redirect("verify_otp")

    return render(
        request,
        "verify_otp.html"
    )


def reset_password(request):

    customer_id = request.session.get("reset_customer_id")
    otp_verified = request.session.get("otp_verified")

    # Check OTP verification
    if not customer_id or not otp_verified:

        messages.error(
            request,
            "Please verify OTP first."
        )

        return redirect("forgot_password")

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    if request.method == "POST":

        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Password length
        if len(new_password) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters."
            )

            return redirect("reset_password")

        # Password confirmation
        if new_password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("reset_password")

        # Save hashed password
        customer.password = make_password(
            new_password
        )

        customer.save()

        # Clear password reset session
        request.session.pop(
            "reset_customer_id",
            None
        )

        request.session.pop(
            "otp_verified",
            None
        )

        messages.success(
            request,
            "Password reset successfully. Please login."
        )

        return redirect("customer_login")

    return render(
        request,
        "reset_password.html"
    )


def customer_dashboard(request):

    customer_id = request.session.get("customer_id")

    if not customer_id:
        messages.error(
            request,
            "Please login first."
        )

        return redirect("customer_login")


    customer = get_object_or_404(
        Customer,
        id=customer_id
    )


    milk_entries = MilkEntry.objects.filter(
        customer=customer
    ).order_by("-date", "-id")


    total_milk_quantity = milk_entries.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0


    cow_milk = milk_entries.filter(
        milk_type="Cow"
    ).aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0


    buffalo_milk = milk_entries.filter(
        milk_type="Buffalo"
    ).aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0


    recent_milk_entries = milk_entries[:5]


    bills = Bill.objects.filter(
        customer=customer
    ).order_by("-bill_date", "-id")


    recent_bills = bills[:5]


    return render(
        request,
        "customer_dashboard.html",
        {
            "customer": customer,
            "total_milk_quantity": total_milk_quantity,
            "cow_milk": cow_milk,
            "buffalo_milk": buffalo_milk,
            "recent_milk_entries": recent_milk_entries,
            "recent_bills": recent_bills,
        }
    )



def customer_profile(request):

    customer_id = request.session.get("customer_id")

    if not customer_id:

        messages.error(
            request,
            "Please login first."
        )

        return redirect("customer_login")

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    return render(
        request,
        "customer_profile.html",
        {
            "customer": customer,
        }
    )

def change_password(request):

    customer_id = request.session.get("customer_id")

    if not customer_id:

        messages.error(
            request,
            "Please login first."
        )

        return redirect("customer_login")

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check current password
        if not check_password(
            current_password,
            customer.password
        ):

            messages.error(
                request,
                "Current password is incorrect."
            )

            return redirect("change_password")

        # Check new password
        if len(new_password) < 8:

            messages.error(
                request,
                "New password must be at least 8 characters."
            )

            return redirect("change_password")

        # Confirm password
        if new_password != confirm_password:

            messages.error(
                request,
                "New passwords do not match."
            )

            return redirect("change_password")

        # Save hashed password
        customer.password = make_password(
            new_password
        )

        customer.save()

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect("customer_profile")

    return render(
        request,
        "change_password.html"
    )

    

def add_customer(request):

    if request.method == "POST":

        customer_id = request.POST.get("customer_id")
        customer_name = request.POST.get("customer_name")
        mobile_no = request.POST.get("mobile_no")
        address = request.POST.get("address")

        # Required validation
        if not customer_id or not customer_name or not mobile_no or not address:

            messages.error(
                request,
                "Please fill all fields"
            )

            return redirect("add_customer")


        # Mobile validation
        if len(mobile_no) != 10 or not mobile_no.isdigit():

            messages.error(
                request,
                "Mobile number must be exactly 10 digits."
            )

            return redirect("add_customer")


        # Duplicate Customer ID
        if Customer.objects.filter(
            customer_id=customer_id
        ).exists():

            messages.error(
                request,
                "Customer ID already exists."
            )

            return redirect("add_customer")


        # Duplicate Mobile Number
        if Customer.objects.filter(
            mobile_no=mobile_no
        ).exists():

            messages.error(
                request,
                "Mobile number already exists."
            )

            return redirect("add_customer")


        # --------------------------------
        # Default Password
        # --------------------------------

        default_password = f"DairyFlow{customer_id}"


        # --------------------------------
        # Create Customer
        # --------------------------------

        Customer.objects.create(

            customer_id=customer_id,

            customer_name=customer_name,

            mobile_no=mobile_no,

            address=address,

            password=make_password(default_password)

        )


        messages.success(
            request,
            f"Customer Added Successfully! "
            f"Default Password: {default_password}"
        )


        return redirect("add_customer")


    return render(
        request,
        "add_customer.html"
    )


def customer_list(request):

    customers = Customer.objects.all().order_by("id")

    # --------------------------------
    # Pagination
    # --------------------------------

    paginator = Paginator(customers, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "customer_list.html",
        {
            "customers": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
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




def monthly_bill(request):

    customers = Customer.objects.all()

    if request.method == "POST":

        customer_id = request.POST.get("customer")

        from_date = request.POST.get("from_date")

        to_date = request.POST.get("to_date")

        return redirect(
            "bill_report",
            customer_id=customer_id,
            from_date=from_date,
            to_date=to_date
        )

    return render(
        request,
        "monthly_bill.html",
        {
            "customers": customers
        }
    )


def bill_report(request):

    # --------------------------------
    # Get Saved Bill
    # --------------------------------

    bill_id = request.GET.get("bill_id")

    bill = get_object_or_404(
        Bill,
        id=bill_id
    )

    # --------------------------------
    # Customer + Bill Details
    # --------------------------------

    customer = bill.customer

    from_date = bill.from_date
    to_date = bill.to_date

    bill_number = bill.bill_number
    bill_date = bill.bill_date

    # --------------------------------
    # Milk Entries
    # --------------------------------

    milk_entries = MilkEntry.objects.filter(
        customer=customer,
        date__range=[from_date, to_date]
    ).annotate(
        amount=ExpressionWrapper(
            F("milk_quantity") * F("rate"),
            output_field=DecimalField(
                max_digits=10,
                decimal_places=2
            )
        )
    ).order_by("date")

    # --------------------------------
    # Cow
    # --------------------------------

    cow_entries = milk_entries.filter(
        milk_type="Cow"
    )

    cow_qty = cow_entries.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    cow_amount = cow_entries.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # --------------------------------
    # Buffalo
    # --------------------------------

    buffalo_entries = milk_entries.filter(
        milk_type="Buffalo"
    )

    buffalo_qty = buffalo_entries.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    buffalo_amount = buffalo_entries.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # --------------------------------
    # Grand Total
    # --------------------------------

    grand_qty = cow_qty + buffalo_qty

    grand_amount = cow_amount + buffalo_amount

    # --------------------------------
    # Render Report
    # --------------------------------

    return render(
    request,
    "bill_report.html",
    {
        "customer": customer,

        "bill": bill,

        "bill_number": bill_number,
        "bill_date": bill_date,

        "milk_entries": milk_entries,

        "from_date": from_date,
        "to_date": to_date,

        "cow_qty": cow_qty,
        "buffalo_qty": buffalo_qty,

        "cow_amount": cow_amount,
        "buffalo_amount": buffalo_amount,

        "grand_qty": grand_qty,
        "grand_amount": grand_amount,
    },
)

def generate_bill(request):

    if request.method != "POST":
        return redirect("monthly_bill")

    customer_id = request.POST.get("customer")
    from_date = request.POST.get("from_date")
    to_date = request.POST.get("to_date")

    # Customer
    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    # --------------------------------
    # Duplicate Bill Check
    # --------------------------------

    existing_bill = Bill.objects.filter(
        customer=customer,
        from_date=from_date,
        to_date=to_date
    ).first()

    if existing_bill:

        messages.info(
            request,
            f"Bill already exists: {existing_bill.bill_number}"
        )

        return redirect(
            f"/bill_report/?customer={customer.id}"
            f"&from_date={from_date}"
            f"&to_date={to_date}"
        )

    # --------------------------------
    # Milk Entries
    # --------------------------------

    milk_entries = MilkEntry.objects.filter(
        customer=customer,
        date__range=[from_date, to_date]
    ).annotate(
        amount=ExpressionWrapper(
            F("milk_quantity") * F("rate"),
            output_field=DecimalField(
                max_digits=10,
                decimal_places=2
            )
        )
    )

    # --------------------------------
    # Cow
    # --------------------------------

    cow_entries = milk_entries.filter(
        milk_type="Cow"
    )

    cow_qty = cow_entries.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    cow_amount = cow_entries.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # --------------------------------
    # Buffalo
    # --------------------------------

    buffalo_entries = milk_entries.filter(
        milk_type="Buffalo"
    )

    buffalo_qty = buffalo_entries.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    buffalo_amount = buffalo_entries.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # --------------------------------
    # Grand Total
    # --------------------------------

    grand_qty = cow_qty + buffalo_qty
    grand_amount = cow_amount + buffalo_amount

    # --------------------------------
    # Bill Date
    # --------------------------------

    bill_date = datetime.now().date()

    # --------------------------------
    # Sequential Bill Number
    # --------------------------------

    month_code = bill_date.strftime("%Y%m")

    last_bill = Bill.objects.filter(
        bill_number__startswith=f"BILL-{month_code}-"
    ).order_by("-id").first()

    if last_bill:

        last_number = int(
            last_bill.bill_number.split("-")[-1]
        )

        next_number = last_number + 1

    else:

        next_number = 1

    bill_number = (
        f"BILL-{month_code}-{next_number:04d}"
    )

    # --------------------------------
    # Save Bill
    # --------------------------------

    bill = Bill.objects.create(
        customer=customer,
        bill_number=bill_number,
        bill_date=bill_date,
        from_date=from_date,
        to_date=to_date,
        total_quantity=grand_qty,
        total_amount=grand_amount
    )

    messages.success(
        request,
        f"Bill Generated Successfully: {bill_number}"
    )

    # --------------------------------
    # Bill Report
    # --------------------------------

    return redirect(
    f"/bill_report/?bill_id={bill.id}"
)


def download_bill_pdf(request):

    bill_id = request.GET.get("bill_id")

    bill = get_object_or_404(
        Bill,
        id=bill_id
    )

    customer = bill.customer

    from_date = bill.from_date
    to_date = bill.to_date

    # --------------------------------
    # Milk Entries
    # --------------------------------

    milk_entries = MilkEntry.objects.filter(
        customer=customer,
        date__range=[from_date, to_date]
    ).annotate(
        amount=ExpressionWrapper(
            F("milk_quantity") * F("rate"),
            output_field=DecimalField(
                max_digits=10,
                decimal_places=2
            )
        )
    ).order_by("date")

    # --------------------------------
    # Cow
    # --------------------------------

    cow_entries = milk_entries.filter(
        milk_type="Cow"
    )

    cow_qty = cow_entries.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    cow_amount = cow_entries.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # --------------------------------
    # Buffalo
    # --------------------------------

    buffalo_entries = milk_entries.filter(
        milk_type="Buffalo"
    )

    buffalo_qty = buffalo_entries.aggregate(
        total=Sum("milk_quantity")
    )["total"] or 0

    buffalo_amount = buffalo_entries.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # --------------------------------
    # Grand Total
    # --------------------------------

    grand_qty = cow_qty + buffalo_qty
    grand_amount = cow_amount + buffalo_amount

    # --------------------------------
    # PDF Setup
    # --------------------------------

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    left = 18 * mm
    right = width - 18 * mm

    # --------------------------------
    # Header
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawCentredString(
        width / 2,
        height - 25 * mm,
        "DairyFlow"
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawCentredString(
        width / 2,
        height - 33 * mm,
        "MONTHLY MILK BILL"
    )

    pdf.line(
        left,
        height - 38 * mm,
        right,
        height - 38 * mm
    )

    # --------------------------------
    # Customer + Bill Details
    # --------------------------------

    box_top = height - 45 * mm
    box_bottom = height - 75 * mm

    pdf.rect(
        left,
        box_bottom,
        right - left,
        box_top - box_bottom
    )

    middle = width / 2

    pdf.line(
        middle,
        box_bottom,
        middle,
        box_top
    )

    # Customer title

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        left + 5 * mm,
        box_top - 7 * mm,
        "CUSTOMER DETAILS"
    )

    # Customer details

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        left + 5 * mm,
        box_top - 14 * mm,
        f"Name    : {customer.customer_name}"
    )

    pdf.drawString(
        left + 5 * mm,
        box_top - 20 * mm,
        f"Mobile  : {customer.mobile_no}"
    )

    pdf.drawString(
        left + 5 * mm,
        box_top - 26 * mm,
        f"Address : {customer.address}"
    )

    # Bill title

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        middle + 5 * mm,
        box_top - 7 * mm,
        "BILL DETAILS"
    )

    # Bill details

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        middle + 5 * mm,
        box_top - 14 * mm,
        f"Bill No.  : {bill.bill_number}"
    )

    pdf.drawString(
        middle + 5 * mm,
        box_top - 20 * mm,
        f"Bill Date : {bill.bill_date.strftime('%d %b %Y')}"
    )

    pdf.drawString(
        middle + 5 * mm,
        box_top - 26 * mm,
        f"Period    : {from_date} - {to_date}"
    )

    # --------------------------------
    # Milk Table
    # --------------------------------

    table_top = box_bottom - 10 * mm

    col_x = [
        left,
        left + 32 * mm,
        left + 58 * mm,
        left + 94 * mm,
        left + 120 * mm,
        left + 147 * mm,
        right
    ]

    row_height = 8 * mm

    # --------------------------------
    # Table Header
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        8
    )

    # Header border

    pdf.rect(
        left,
        table_top - row_height,
        right - left,
        row_height
    )

    # Header vertical lines

    for x in col_x[1:-1]:

        pdf.line(
            x,
            table_top - row_height,
            x,
            table_top
        )

    headers = [
        "Date",
        "Shift",
        "Milk Type",
        "Quantity",
        "Rate",
        "Amount"
    ]

    for i, header in enumerate(headers):

        center_x = (
            col_x[i] + col_x[i + 1]
        ) / 2

        pdf.drawCentredString(
            center_x,
            table_top - 5.5 * mm,
            header
        )

    # --------------------------------
    # Table Rows
    # --------------------------------

    y = table_top - row_height

    pdf.setFont(
        "Helvetica",
        8
    )

    for entry in milk_entries:

        y -= row_height

        # Row border

        pdf.rect(
            left,
            y,
            right - left,
            row_height
        )

        # Vertical lines

        for x in col_x[1:-1]:

            pdf.line(
                x,
                y,
                x,
                y + row_height
            )

        values = [
            entry.date.strftime("%d %b %Y"),
            str(entry.shift),
            str(entry.milk_type),
            f"{entry.milk_quantity:.2f}",
            f"{entry.rate:.2f}",
            f"Rs. {entry.amount:.2f}"
        ]

        for i, value in enumerate(values):

            center_x = (
                col_x[i] + col_x[i + 1]
            ) / 2

            pdf.drawCentredString(
                center_x,
                y + 2.7 * mm,
                value
            )

    # --------------------------------
    # No Milk Entries
    # --------------------------------

    if not milk_entries.exists():

        y -= row_height

        pdf.rect(
            left,
            y,
            right - left,
            row_height
        )

        pdf.setFont(
            "Helvetica-Oblique",
            9
        )

        pdf.drawCentredString(
            width / 2,
            y + 2.7 * mm,
            "No milk entries found"
        )

    # --------------------------------
    # Summary
    # --------------------------------

    summary_top = y - 12 * mm

    # Cow

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        left,
        summary_top,
        "Cow Total"
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        left + 35 * mm,
        summary_top,
        f"{cow_qty:.2f} L"
    )

    pdf.drawRightString(
        right,
        summary_top,
        f"Rs. {cow_amount:.2f}"
    )

    # Buffalo

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        left,
        summary_top - 7 * mm,
        "Buffalo Total"
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        left + 35 * mm,
        summary_top - 7 * mm,
        f"{buffalo_qty:.2f} L"
    )

    pdf.drawRightString(
        right,
        summary_top - 7 * mm,
        f"Rs. {buffalo_amount:.2f}"
    )

    # --------------------------------
    # Grand Total
    # --------------------------------

    grand_top = summary_top - 15 * mm
    grand_bottom = grand_top - 16 * mm

    pdf.rect(
        left,
        grand_bottom,
        right - left,
        16 * mm
    )

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        left + 5 * mm,
        grand_bottom + 10 * mm,
        "GRAND TOTAL"
    )

    pdf.drawString(
        left + 60 * mm,
        grand_bottom + 10 * mm,
        f"{grand_qty:.2f} L"
    )

    pdf.drawRightString(
        right - 5 * mm,
        grand_bottom + 10 * mm,
        f"Rs. {grand_amount:.2f}"
    )

    # --------------------------------
    # Footer
    # --------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawCentredString(
        width / 2,
        25 * mm,
        "Thank You!"
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawCentredString(
        width / 2,
        19 * mm,
        "DairyFlow Milk Center"
    )

    # --------------------------------
    # Save PDF
    # --------------------------------

    pdf.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{bill.bill_number}.pdf"'
    )

    return response


def bill_history(request):

    bills = Bill.objects.select_related(
        "customer"
    ).order_by("-bill_date", "-id")

    # --------------------------------
    # Filters
    # --------------------------------

    customer_id = request.GET.get("customer")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if customer_id:
        bills = bills.filter(
            customer_id=customer_id
        )

    if from_date:
        bills = bills.filter(
            bill_date__gte=from_date
        )

    if to_date:
        bills = bills.filter(
            bill_date__lte=to_date
        )

    # --------------------------------
    # Pagination
    # --------------------------------

    from django.core.paginator import Paginator

    paginator = Paginator(
        bills,
        10
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    # --------------------------------
    # Customers
    # --------------------------------

    customers = Customer.objects.all().order_by(
        "customer_name"
    )

    return render(
        request,
        "bill_history.html",
        {
            "page_obj": page_obj,
            "bills": page_obj.object_list,

            "customers": customers,

            "selected_customer": customer_id,
            "from_date": from_date,
            "to_date": to_date,
        }
    )


def delete_bill(request, id):

    if request.method != "POST":
        return redirect("bill_history")

    bill = get_object_or_404(
        Bill,
        id=id
    )

    bill_number = bill.bill_number

    bill.delete()

    messages.success(
        request,
        f"Bill {bill_number} deleted successfully."
    )

    return redirect("bill_history")
