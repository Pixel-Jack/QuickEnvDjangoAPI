from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.core.exceptions import ObjectDoesNotExist


class TestUserCreation(APITestCase):
    fixtures = ['user_user.yaml', 'user_authtoken_token.yaml',]

    def test_user_creation_empty_data_error(self):
        url = reverse('user-creation')
        data = {}
        response = self.client.post(url, data, format='json')

        errors = ['email: This field is required.',
                  'username: This field is required.',
                  'password: This field is required.',
                  'password_confirmation: This field is required.']

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, errors)

    def test_user_creation_invalid_email_and_unique_username_error(self):
        url = reverse('user-creation')
        data = {'username': "admin",
                'email': "admin",
                'password': "admin",
                'password_confirmation': "admin"}
        response = self.client.post(url, data, format='json')
        errors = ['Enter a valid email address.', 'A user with that username already exists.']

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, errors)

    def test_user_creation_unique_email_error(self):
        url = reverse('user-creation')
        data = {'username': "admin0",
                'email': "ad.min@test-email.com",
                'password': "admin",
                'password_confirmation': "admin"}
        response = self.client.post(url, data, format='json')

        errors = ['A user with that email already exists.']

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, errors)

    def test_user_creation_email_as_username_error(self):
        url = reverse('user-creation')
        data = {'username': 'c@gogo.com', 'password': 'salut', 'password_confirmation': 'salut', 'email': 'c@gogo.com'}
        response = self.client.post(url, data, format='json')

        errors = ["You can't use an email address for this field."]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, errors)

    def test_user_creation_not_authenticated(self):
        # It should be the most common usage
        url = reverse('user-creation')
        data = {'username': 'clement', 'password': 'salut', 'password_confirmation': 'salut', 'email': 'c@gogo.com'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'email': 'c@gogo.com', 'username': 'clement'})
        try:
            get_user_model().objects.get(email=data['email'], username=data['username'])
        except ObjectDoesNotExist:
            self.fail("User not found")

    def test_user_creation_by_admin_user(self):
        url = reverse('user-creation')
        token = get_user_model()._default_manager.get(username='admin').auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        data = {'username': 'clement', 'password': 'salut', 'password_confirmation': 'salut', 'email': 'c@gogo.com'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'email': 'c@gogo.com', 'username': 'clement'})
        try:
            get_user_model().objects.get(email=data['email'], username=data['username'])
        except ObjectDoesNotExist:
            self.fail("User not found")

    def test_user_creation_by_common_user_wrong(self):
        url = reverse('user-creation')
        token = get_user_model()._default_manager.get(username='common').auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        data = {'username': 'clement', 'password': 'salut', 'password_confirmation': 'salut', 'email': 'c@gogo.com'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, ['You do not have permission to perform this action.'])

