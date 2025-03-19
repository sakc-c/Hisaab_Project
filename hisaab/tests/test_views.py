from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.messages import get_messages
from django.db.models.deletion import ProtectedError
from django.test.utils import override_settings
from decimal import Decimal
from unittest.mock import patch, MagicMock

from hisaab.models import Category, Product, Bill, BillDetails
from hisaab.forms import CategoryForm, ProductForm, BillForm


class BaseViewTestCase(TestCase):
    @override_settings(SECRET_KEY='dummy-secret-key')
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()

        # Create groups
        self.groups = {
            'admin': Group.objects.create(name='h_admin'),
            'inventory': Group.objects.create(name='inventory_manager'),
            'cashier': Group.objects.create(name='cashier'),
        }

        # Create users and assign groups
        self.users = {
            'admin_user': self._create_user('admin_user', 'adminpassword', self.groups['admin']),
            'inventory_user': self._create_user('inventory_user', 'inventorypassword', self.groups['inventory']),
            'cashier_user': self._create_user('cashier_user', 'cashierpassword', self.groups['cashier']),
            'regular_user': self._create_user('regular_user', 'regularpassword'),
            'user1': self._create_user('user1', 'user1password', self.groups['cashier']),
            'user2': self._create_user('user2', 'user2password', self.groups['cashier']),
        }

    def _create_user(self, username, password, group=None):
        """Helper method to create a user and optionally add them to a group."""
        user = self.User.objects.create_user(username=username, password=password)
        if group:
            user.groups.add(group)
        return user

    def test_user_management_view_unauthenticated(self):
        response = self.client.get(reverse('user_management'))
        self.assertTemplateUsed(response, 'hisaab/login.html')

    def test_user_management_view_non_admin(self):
        self.client.login(username='user1', password='user1password')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/unauthorised.html')

    def test_user_management_view_admin(self):
        self.client.login(username='admin_user', password='adminpassword')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/user_management.html')
        self.assertContains(response, self.users['user1'].username)  # Check for non-admin user in the list
        self.assertContains(response, self.users['user2'].username)  # Check for another user in the list
        self.assertNotContains(response, self.users['admin_user'].username)  # Admin shouldn't be listed (excluded)


class CategoryManagementTest(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')

    def test_inventory_view_admin(self):
        self.client.login(username='admin_user', password='adminpassword')
        response = self.client.get(reverse('inventory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/inventoryMain.html')
        self.assertIn('categories', response.context)


    def test_add_category_post_success(self):
        self.client.login(username='admin_user', password='adminpassword')

        data = {
            'name': 'New Category',
            'description': 'Test category description',
            'image_url': ''  # Explicitly sending an empty string
        }

        response = self.client.post(reverse('add_category'), data)

        self.assertRedirects(response, reverse('inventory'))
        self.assertTrue(Category.objects.filter(name='New Category').exists())


    def test_add_category_post_duplicate(self):
        self.client.login(username='admin_user', password='adminpassword')
        data = {'name': 'Test Category'}  # Same name as in setUp
        response = self.client.post(reverse('add_category'), data)
        self.assertRedirects(response, reverse('inventory'))

    # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Category with this name already exists.")

    def test_edit_category_post_success(self):
        self.client.login(username='admin_user', password='adminpassword')
        data = {'name': 'Updated Category Name', 'description': 'Updated description'}  # Add description
        response = self.client.post(reverse('edit_category', args=[self.category.id]), data)

        self.assertRedirects(response, reverse('inventory'))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category Name')

    def test_delete_category_success(self):
        self.client.login(username='admin_user', password='adminpassword')
        category = Category.objects.create(name='Category To Delete')
        response = self.client.post(reverse('delete_category', args=[category.id]))
        self.assertRedirects(response, reverse('inventory'))

        # Check if category was deleted
        self.assertFalse(Category.objects.filter(name='Category To Delete').exists())

    @patch('hisaab.models.Category.delete')
    def test_delete_category_protected_error(self, mock_delete):
        # Mock the delete method to raise ProtectedError
        mock_delete.side_effect = ProtectedError("Cannot delete", mock_delete)

        self.client.login(username='admin_user', password='adminpassword')
        response = self.client.post(reverse('delete_category', args=[self.category.id]))
        self.assertRedirects(response, reverse('inventory'))

        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Cannot delete this category because products are linked to it.")

class ProductManagementTest(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            categoryID=self.category,
            unitPrice=Decimal('10.00'),
            stockLevel=100,
            user=self.users['admin_user']
        )

    def test_add_product_get(self):
        self.client.login(username='admin_user', password='adminpassword')
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/InventoryMain.html')
        self.assertIn('form', response.context)

    def test_add_product_post_success(self):
        self.client.login(username='admin_user', password='adminpassword')
        data = {
            'name': 'New Product',
            'categoryID': self.category.id,
            'unitPrice': Decimal('15.00'),
            'stockLevel': 50
        }
        response = self.client.post(reverse('add_product'), data)
        self.assertRedirects(response, reverse('category', args=[self.category.id]))
        self.assertTrue(Product.objects.filter(name='New Product').exists())

    def test_edit_product_post_success(self):
        self.client.login(username='admin_user', password='adminpassword')
        data = {
            'name': 'Updated Product Name',
            'categoryID': self.category.id,
            'unitPrice': Decimal('20.00'),
            'stockLevel': 75
        }
        response = self.client.post(reverse('edit_product', args=[self.product.id]), data)
        self.assertRedirects(response, reverse('category', args=[self.category.id]))

        # Refresh from database and check if updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product Name')
        self.assertEqual(self.product.unitPrice, Decimal('20.00'))
        self.assertEqual(self.product.stockLevel, 75)

    def test_delete_product(self):
        self.client.login(username='admin_user', password='adminpassword')
        response = self.client.post(reverse('delete_product', args=[self.product.id]))
        self.assertRedirects(response, reverse('category', args=[self.category.id]))

        # Check if product was deleted
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())


class BillManagementTest(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            categoryID=self.category,
            unitPrice=Decimal('10.00'),
            stockLevel=100,
            user=self.users['admin_user']
        )

        self.bill = Bill.objects.create(
            user=self.users['admin_user'],
            customerName='Test Customer',
            discount=10,
            totalAmount=Decimal('90.00')
        )

        self.bill_detail = BillDetails.objects.create(
            billID=self.bill,
            productID=self.product,
            quantity=10,
            unitPrice=Decimal('10.00'),
            amount=Decimal('100.00')
        )

    def test_create_bill_get(self):
        self.client.login(username='admin_user', password='adminpassword')
        response = self.client.get(reverse('create_bill'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/create_bill.html')
        self.assertIn('form', response.context)
        self.assertIn('products', response.context)


    def test_create_bill_post_success(self):
        self.client.login(username='admin_user', password='adminpassword')
        data = {
            'customer_name': 'New Customer',
            'discount': 5,
            'product_1': self.product.id,
            'quantity_1': 2
        }
        response = self.client.post(reverse('create_bill'), data)

        # Check that a new bill was created
        self.assertEqual(Bill.objects.count(), 2)
        new_bill = Bill.objects.latest('id')
        self.assertEqual(new_bill.customerName, 'New Customer')
        self.assertEqual(new_bill.discount, 5)

        # Check if stock was deducted correctly
        self.product.refresh_from_db()
        self.assertEqual(self.product.stockLevel, 98)  # Original was 100, 2 deducted

    @patch('hisaab.models.Bill.generate_pdf')
    def test_create_bill_insufficient_stock(self, mock_generate_pdf):
        self.client.login(username='admin_user', password='adminpassword')
        data = {
            'customer_name': 'New Customer',
            'discount': 5,
            'product_1': self.product.id,
            'quantity_1': 200  # More than available stock (100)
        }
        response = self.client.post(reverse('create_bill'), data)

        # Check that form shows error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/create_bill.html')
        self.assertIn('error', response.context)
        self.assertIn('Insufficient stock', response.context['error'])

        # Check that no new bill was created
        self.assertEqual(Bill.objects.count(), 1)

        # Check that PDF generation was not called
        mock_generate_pdf.assert_not_called()

    def test_delete_bill(self):
        self.client.login(username='admin_user', password='adminpassword')

        # Store the original stock level
        original_stock = self.product.stockLevel

        response = self.client.post(reverse('delete_bill', args=[self.bill.id]))
        self.assertRedirects(response, reverse('bills'))

        # Check if bill was deleted
        self.assertFalse(Bill.objects.filter(id=self.bill.id).exists())
        self.assertFalse(BillDetails.objects.filter(billID=self.bill).exists())

        # Check if stock was restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.stockLevel, original_stock + self.bill_detail.quantity)


