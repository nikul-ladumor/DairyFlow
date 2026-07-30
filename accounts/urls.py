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
]