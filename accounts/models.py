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

class Bill(models.Model):

        customer = models.ForeignKey(
            Customer,
            on_delete=models.CASCADE
        )

        bill_number = models.CharField(
            max_length=30,
            unique=True
        )

        bill_date = models.DateField()

        from_date = models.DateField()

        to_date = models.DateField()

        total_quantity = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0
        )

        total_amount = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0
        )

        created_at = models.DateTimeField(
            auto_now_add=True
        )

        def __str__(self):
            return self.bill_number