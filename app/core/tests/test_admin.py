from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    """ setup task before every test
    that needs to be done """
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='testing123'
        )
        """ log user in with django auth """
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password = 'pass123',
            name='User Test'
        )

    def test_user_listed(self):
        """ test user listed on user page """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_change_page(self):
        """ test user edit page works """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEquals(res.status_code, 200)

    def test_create_user_page(self):
        """ test create user page works """
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEquals(res.status_code, 200)