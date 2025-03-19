from decimal import Decimal
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import ProtectedError
from unittest.mock import patch

from hisaab.models import Report, Bill, Category, Product, BillDetails

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertTrue(isinstance(self.user.createdAt, type(self.user.date_joined)))
        self.assertEqual(str(self.user), 'testuser')


class BillModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.bill = Bill.objects.create(
            user=self.user,
            customerName='Test Customer',
            totalAmount=Decimal('50.50'),
            discount=10
        )

    def test_bill_creation(self):
        self.assertEqual(self.bill.customerName, 'Test Customer')
        self.assertEqual(self.bill.totalAmount, Decimal('50.50'))
        self.assertEqual(self.bill.discount, 10)
        self.assertEqual(self.bill.user, self.user)
        self.assertTrue(self.bill.createdAt is not None)
        self.assertEqual(str(self.bill), f"{self.bill.id}")

    def test_bill_user_deletion(self):
        bill_id = self.bill.id
        self.user.delete()
        # Bill should still exist with user set to NULL
        self.assertTrue(Bill.objects.filter(id=bill_id).exists())
        updated_bill = Bill.objects.get(id=bill_id)
        self.assertIsNone(updated_bill.user)

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items and gadgets',
            image_url='https://example.com/electronics.jpg'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.description, 'Electronic items and gadgets')
        self.assertEqual(self.category.image_url, 'https://example.com/electronics.jpg')
        self.assertEqual(str(self.category), 'Electronics')


class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items and gadgets'
        )
        self.product = Product.objects.create(
            name='Laptop',
            categoryID=self.category,
            unitPrice=Decimal('1200.99'),
            stockLevel=10,
            user=self.user
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Laptop')
        self.assertEqual(self.product.categoryID, self.category)
        self.assertEqual(self.product.unitPrice, Decimal('1200.99'))
        self.assertEqual(self.product.stockLevel, 10)
        self.assertEqual(self.product.user, self.user)
        self.assertEqual(str(self.product), 'Laptop')

    def test_product_user_deletion(self):
        product_id = self.product.id
        self.user.delete()
        # Product should still exist with user set to NULL
        self.assertTrue(Product.objects.filter(id=product_id).exists())
        updated_product = Product.objects.get(id=product_id)
        self.assertIsNone(updated_product.user)

    def test_category_protected_deletion(self):
        # Test that we can't delete a category that is associated with products
        with self.assertRaises(ProtectedError):
            self.category.delete()

        # Create another category and verify it can be deleted when no products reference it
        empty_category = Category.objects.create(name='Empty', description='Empty category')
        self.assertTrue(empty_category.delete())


class BillDetailsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items'
        )
        self.product = Product.objects.create(
            name='Laptop',
            categoryID=self.category,
            unitPrice=Decimal('1200.99'),
            stockLevel=10,
            user=self.user
        )
        self.bill = Bill.objects.create(
            user=self.user,
            customerName='Test Customer',
            totalAmount=Decimal('1200.99'),
            discount=0
        )
        self.bill_detail = BillDetails.objects.create(
            billID=self.bill,
            productID=self.product,
            quantity=1,
            unitPrice=Decimal('1200.99'),
            amount=Decimal('1200.99')
        )

    def test_bill_details_creation(self):
        self.assertEqual(self.bill_detail.billID, self.bill)
        self.assertEqual(self.bill_detail.productID, self.product)
        self.assertEqual(self.bill_detail.quantity, 1)
        self.assertEqual(self.bill_detail.unitPrice, Decimal('1200.99'))
        self.assertEqual(self.bill_detail.amount, Decimal('1200.99'))
        self.assertEqual(str(self.bill_detail), f"Bill {self.bill.id}: {self.product.name}")

    def test_bill_details_uniqueness(self):
        # Test that we can't create duplicate bill details for the same bill and product
        with self.assertRaises(IntegrityError):
            BillDetails.objects.create(
                billID=self.bill,
                productID=self.product,
                quantity=2,
                unitPrice=Decimal('1200.99'),
                amount=Decimal('2401.98')
            )

    def test_bill_detail_auto_amount_calculation(self):
        # Create a new bill detail with specific quantity and unit price
        new_bill_detail = BillDetails.objects.create(
            billID=self.bill,
            productID=Product.objects.create(
                name='Mouse',
                categoryID=self.category,
                unitPrice=Decimal('25.99'),
                stockLevel=20,
                user=self.user
            ),
            quantity=3,
            unitPrice=Decimal('25.99')
        )

        # The save method should calculate the amount
        self.assertEqual(new_bill_detail.amount, Decimal('77.97'))  # 3 * 25.99

    def test_cascade_delete(self):
        # Test that bill details are deleted when bill is deleted
        bill_detail_id = self.bill_detail.id
        self.bill.delete()
        self.assertFalse(BillDetails.objects.filter(id=bill_detail_id).exists())


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.report = Report.objects.create(
            user=self.user,
            reportType='Monthly Sales'
        )

    def test_report_creation(self):
        self.assertEqual(self.report.reportType, 'Monthly Sales')
        self.assertEqual(self.report.user, self.user)
        self.assertTrue(self.report.createdAt is not None)
        self.assertEqual(str(self.report), str(self.report.id))

    def test_report_user_deletion(self):
        report_id = self.report.id
        self.user.delete()
        # Report should still exist with user set to NULL
        self.assertTrue(Report.objects.filter(id=report_id).exists())
        updated_report = Report.objects.get(id=report_id)
        self.assertIsNone(updated_report.user)