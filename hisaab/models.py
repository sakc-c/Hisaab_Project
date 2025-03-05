from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser): #AbstractUser for password hashing
    userID = models.IntegerField(unique=True)
    role = models.CharField(max_length=128)
    createdAt = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['userID', 'role']

    def __str__(self):
        return self.username


class Report(models.Model):
    reportID = models.IntegerField(unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    reportType = models.CharField(max_length=100)

    def __str__(self):
        return self.reportID

class Bill(models.Model):
    DISCOUNT_CHOICES = [
        (5, "5%"),
        (10, "10%"),
        (15, "15%"),
    ]
    billID = models.IntegerField(unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    totalAmount = models.DecimalField(decimal_places=2, max_digits=20)
    discount = models.IntegerField(choices=DISCOUNT_CHOICES, default=5)

    def __str__(self):
        return f"{self.billID}"


class Category(models.Model):
    NAME_MAX_LENGTH = 128
    categoryID = models.IntegerField(unique=True, editable=False)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()
    image_url = models.URLField(max_length=255, null=True)

    def save(self, *args, **kwargs):
        if not self.categoryID:
            last_category = Category.objects.all().last()
            self.categoryID = last_category.categoryID + 1 if last_category else 1
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    NAME_MAX_LENGTH = 128
    productID = models.IntegerField(unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    unitPrice = models.DecimalField(decimal_places=2, max_digits=20)
    stockLevel = models.IntegerField()
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class BillDetails(models.Model):
    billID = models.ForeignKey(Bill, on_delete=models.CASCADE)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unitPrice = models.DecimalField(decimal_places=2, max_digits=20)
    amount = models.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        unique_together = (("billID", "productID"),)

    def __str__(self):
        return f"Bill ID: {self.billID.billID}"  # Return just the Bill ID as an integer

    def save(self, *args, **kwargs): #Overriding Default Save Behavior
        #calculate the amount based on quantity and unitPrice
        self.amount = self.quantity * self.unitPrice
        super(BillDetails, self).save(*args, **kwargs)
