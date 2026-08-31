from django.urls import path
from.import views

urlpatterns=[

    path('',views.home,name='home'),

    path("home/", views.home, name="home"),

    path("admin_login/", views.admin_login, name="admin_login"),

    path("customer_login/", views.customer_login, name="customer_login"),

    path("add_customer/", views.add_customer, name="add_customer"),

    path("customer_list/", views.customer_list, name="customer_list"),

    path("edit_customer/<int:id>/", views.edit_customer, name="edit_customer"),

    path("delete_customer/<int:id>", views.delete_customer, name="delete_customer"),

    path("add_milk_entry/", views.add_milk_entry, name="add_milk_entry"),

    path("milk_entry_list/", views.milk_entry_list, name="milk_entry_list"),

    path("edit_milk_entry/<int:id>", views.edit_milk_entry, name="edit_milk_entry"),

    path("delete_milk_entry/<int:id>", views.delete_milk_entry, name="delete_milk_entry"),

    path("monthly_bill/", views.monthly_bill, name="monthly_bill"),

    path("bill_report/", views.bill_report, name="bill_report"),

    path("download_bill_pdf/", views.download_bill_pdf, name="download_bill_pdf"),

    path("bill_history/", views.bill_history, name="bill_history"),

    path("delete_bill/<int:id>/", views.delete_bill, name="delete_bill"),

    path("generate_bill/", views.generate_bill, name="generate_bill"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("admin_base/", views.admin_base, name="admin_base"),
]