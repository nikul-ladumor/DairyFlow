from django.db import models

class Customer(models.Model):
    customer_id = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=10)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.customer_name


SHIFT_CHOICES = [
        ("Morning", "Morning"),
        ("Evening", "Evening"),
    ]

MILK_TYPEE_CHOICES = [
    ("Cow", "Cow"),
    ("Buffalo", "Buffalo"),
]

class MilkEntry(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    date = models.DateField()
    shift = models.CharField(
        max_length=10,
        choices=SHIFT_CHOICES
    )
    milk_quantity = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    milk_type = models.CharField(
        max_length=10,
        choices=MILK_TYPEE_CHOICES
    )
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )