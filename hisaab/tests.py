from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

class UserManagementViewTest(TestCase):

    @override_settings(SECRET_KEY='dummy-secret-key')
    def setUp(self):
        # Get the custom User mode
        User = get_user_model()
        # Create a user and assign them to the 'h_admin' group
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpassword'
        )
        admin_group = Group.objects.create(name='h_admin')
        self.admin_user.groups.add(admin_group)

        # Create two non-admin users
        self.user1 = User.objects.create_user(
            username='user1',
            password='nonadminpassword'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='anotherpassword'
        )

        cashier_group = Group.objects.create(name='cashier')
        self.user1.groups.add(cashier_group)
        self.user2.groups.add(cashier_group)

    def test_user_management_view_unauthenticated(self):
        response = self.client.get(reverse('user_management'))
        self.assertTemplateUsed(response, 'hisaab/login.html')

    def test_user_management_view_non_admin(self):
        self.client.login(username='user1', password='nonadminpassword')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/unauthorised.html')

    def test_user_management_view_admin(self):
        self.client.login(username='admin_user', password='adminpassword')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hisaab/user_management.html')
        self.assertContains(response, self.user1.username)  # Check for non-admin user in the list
        self.assertContains(response, self.user2.username)  # Check for another user in the list
        self.assertNotContains(response, self.admin_user.username)  # Admin shouldn't be listed (excluded)
