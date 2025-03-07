from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models import Max

class User(AbstractUser): #AbstractUser for password hashing
    userID = models.IntegerField(unique=True, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['userID']

    def save(self, *args, **kwargs):
        if self.userID is None:
            max_user_id = User.objects.aggregate(Max('userID'))['userID__max']
            self.userID = (max_user_id or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Report(models.Model):
    reportID = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    reportType = models.CharField(max_length=100)

    def __str__(self):
        return str(self.reportID)

class Bill(models.Model):
    DISCOUNT_CHOICES = [
        (5, "5%"),
        (10, "10%"),
        (15, "15%"),
    ]
    billID = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    totalAmount = models.DecimalField(decimal_places=2, max_digits=20)
    discount = models.IntegerField(choices=DISCOUNT_CHOICES, default=5)

    def __str__(self):
        return f"{self.billID}"


class Category(models.Model):
    NAME_MAX_LENGTH = 128
    categoryID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()
    image_url = models.URLField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    NAME_MAX_LENGTH = 128
    productID = models.AutoField(primary_key=True)
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
