from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """ Test publicly available ingredients API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ test that login is required to access ingredients """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """ test ingredients can be retrieve by logged in user """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='test@gmail.com',
            password='test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """ test retrieving ingredient list """
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """ test that only authenticated user can access ingredient """
        user2 = get_user_model().objects.create_user(
            email='test2@gmail.com',
            password='test123'
        )
        Ingredient.objects.create(user=user2, name='Kale')
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredients_success(self):
        """ test that ingredient has been created successfully """
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENTS_URL, payload)

        exist = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exist)

    def test_create_ingredient_invalid(self):
        """ test that creating ingredients failed """
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
