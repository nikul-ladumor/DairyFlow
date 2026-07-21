from django.db import models

class Customer(models.Model):
    customer_id = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=10)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.customer_name