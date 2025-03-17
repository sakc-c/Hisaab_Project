from django.db import models
from django.contrib.auth.models import AbstractUser, Group

class User(AbstractUser): #AbstractUser for password hashing
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Report(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Set user to NULL if deleted
    reportType = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)

class Bill(models.Model):
    DISCOUNT_CHOICES = [
        (0, "No Discount"),
        (5, "5%"),
        (10, "10%"),
        (15, "15%"),
    ]
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Set user to NULL if deleted
    customerName = models.CharField(max_length=255, blank=True, null=True)
    totalAmount = models.DecimalField(decimal_places=2, max_digits=20)
    discount = models.IntegerField(choices=DISCOUNT_CHOICES, default=5)

    def __str__(self):
        return f"{self.id}"

    def generate_pdf(self, context, template):
        from hisaab.helpers import Render
        filename = f"bill_{self.id}"
        return Render.render_to_response(template, context, filename)


class Category(models.Model):
    NAME_MAX_LENGTH = 128
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()
    image_url = models.URLField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    NAME_MAX_LENGTH = 128
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    categoryID = models.ForeignKey(Category, on_delete=models.PROTECT)
    unitPrice = models.DecimalField(decimal_places=2, max_digits=20)
    stockLevel = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Set user to NULL if deleted

    def __str__(self):
        return self.name

class BillDetails(models.Model):
    billID = models.ForeignKey(Bill, on_delete=models.CASCADE)  # ForeignKey to Bill
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unitPrice = models.DecimalField(decimal_places=2, max_digits=20)
    amount = models.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        unique_together = (("billID", "productID"),)

    def __str__(self):
        return f"Bill {self.billID.id}: {self.productID.name}"  # Return Bill ID and Product Name

    def save(self, *args, **kwargs): #Overriding Default Save Behavior
        #calculate the amount based on quantity and unitPrice
        self.amount = self.quantity * self.unitPrice
        super(BillDetails, self).save(*args, **kwargs)
