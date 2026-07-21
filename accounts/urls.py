from django.urls import path
from.import views

urlpatterns=[

    path('',views.home,name='home'),

    path("home/", views.home, name="home"),

    path("admin_login/", views.admin_login, name="admin_login"),

    path("customer_login/", views.customer_login, name="customer_login"),

    path("add_customer/", views.add_customer, name="add_customer")
    
]