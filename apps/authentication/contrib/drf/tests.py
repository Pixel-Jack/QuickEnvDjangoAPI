import re
from unittest import skipUnless

from django.conf import settings
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .settings import INTERNAL_SETTINGS

# In order to avoid the throttling issue
settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['email_sent'] = '1000/second'


class TestAuthentication(APITestCase):
    fixtures = ['authentication_user.yaml', ]

    def test_fail_obtain_auth_token(self):
        url = reverse('obtain-token')
        data = {'login': 'unknown', 'password': 'unknown'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Token.objects.count(), 0)

    @skipUnless('apps.authentication.backends.AuthenticationModelBackend' in settings.AUTHENTICATION_BACKENDS,
                'This test is designed to see if you can be authenticated with your email and your password which is '
                'possible with our AuthenticationModelBackend. Use it or we can\'t guaranty this functionality.')
    def test_obtain_auth_token_with_email(self):
        url = reverse('obtain-token')
        data = {'login': 'ad.min@test-email.com', 'password': 'clement'}
        response = self.client.post(url, data, format='json')
        token = response.data.get('token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(token)
        self.assertEqual(Token.objects.count(), 1)

    def test_obtain_auth_token_with_username(self):
        url = reverse('obtain-token')
        data = {'login': 'admin', 'password': 'clement'}
        response = self.client.post(url, data, format='json')
        token = response.data.get('token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(token)
        self.assertEqual(Token.objects.count(), 1)

    def test_obtain_auth_token_and_delete(self):
        url = reverse('obtain-token')
        data = {'login': 'admin', 'password': 'clement'}
        response = self.client.post(url, data, format='json')
        token = response.data.get('token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(token)
        self.assertEqual(Token.objects.count(), 1)

        url = reverse('delete-token')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 0)

    def test_fail_not_authenticated_call(self):
        url = reverse('delete-token')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Token.objects.count(), 0)

    def test_password_reset_wrong_email(self):
        url = reverse('reset-password')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)  # email: This field is required.

        data = {'email': 'unknown'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)  # Enter a valid email address.

        data = {'email': 'unknown@no.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # We wont tell if this email is unknown

    def test_password_reset_email(self):
        url = reverse('reset-password')
        data = {'email': 'ad.min@test-email.com'}
        mail.outbox = []
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        mail_sent = mail.outbox[0]
        self.assertEqual(mail_sent.to, ['ad.min@test-email.com'])
        no_reply_email = INTERNAL_SETTINGS.get('SITE_NO_REPLY_EMAIL')
        if no_reply_email:
            self.assertEqual(mail_sent.from_email, no_reply_email)

        site_name = INTERNAL_SETTINGS.get('SITE_NAME') or 'testserver'
        self.assertEqual(mail_sent.subject, 'Password reset on {}'.format(site_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_email_fr(self):
        url = reverse('reset-password')
        data = {'email': 'ad.min@test-email.com'}
        mail.outbox = []
        self.client.credentials(HTTP_ACCEPT_LANGUAGE='fr')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        mail_sent = mail.outbox[0]
        site_name = INTERNAL_SETTINGS.get('SITE_NAME') or 'testserver'
        self.assertEqual(mail_sent.subject, 'Réinitialisation du mot de passe sur {}'.format(site_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAuthenticatiedCalls(APITestCase):
    fixtures = ['authentication_user.yaml', 'authentication_authtoken_token.yaml']

    def test_delete_token(self):
        url = reverse('delete-token')
        token = Token.objects.all().first().key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 0)

    def test_refresh_auth_token(self):
        url = reverse('refresh-token')
        token = Token.objects.all().first().key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 1)
        self.assertNotEquals(Token.objects.all(), response.data.get('token'))

        # Try to make a new authenticated call
        url = reverse('delete-token')
        token = Token.objects.all().first().key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 0)

    def test_password_change_no_params(self):
        url = reverse('change-password')
        token = Token.objects.all().first().key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 'old_password: This field is required.',
        # 'new_password1: This field is required.',
        # 'new_password2: This field is required.'
        self.assertEqual(len(response.data), 3)

    def test_password_change_wrong_old(self):
        url = reverse('change-password')
        token = Token.objects.all().first().key
        data = {
            'old_password': 'wrong',
            'new_password1': 'wrong',
            'new_password2': 'wrong',

        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 'Your old password was entered incorrectly. Please enter it again.'
        self.assertEqual(len(response.data), 1)

    def test_password_change(self):
        url = reverse('change-password')
        token = Token.objects.all().first().key
        data = {
            'old_password': 'clement',
            'new_password1': 'newPassdelamuerte',
            'new_password2': 'newPassdelamuerte',

        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('obtain-token')
        # fail authentication
        data = {'login': 'admin', 'password': 'clement'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Authenticated
        data = {'login': 'admin', 'password': 'newPassdelamuerte'}
        response = self.client.post(url, data, format='json')
        token = response.data.get('token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(token)
        self.assertEqual(Token.objects.count(), 1)


class TestResetPassword(APITestCase):
    fixtures = ['authentication_user.yaml', ]

    def test_process_reset_password_without_token(self):
        pk = 2
        url = reverse('password_reset_confirm', args=(pk, INTERNAL_SETTINGS['INTERNAL_RESET_URL_TOKEN']))
        data = {
            'new_password1': 'newPassdelamuerte',
            'new_password2': 'newPassdelamuerte',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Invalid parameters
        self.assertEqual(len(response.data), 1)


class TestProcessResetPassword(APITestCase):
    fixtures = ['authentication_user.yaml', ]

    def setUp(self):
        url = reverse('reset-password')
        data = {'email': 'ad.min@test-email.com'}
        mail.outbox = []
        self.client.post(url, data, format='json')
        self.assertEqual(len(mail.outbox), 1)

        mail_sent = mail.outbox[0]
        redirect_confirm = INTERNAL_SETTINGS['REDIRECT_CONFIRM']
        pattern = "http.:\/\/.*\/" + re.escape(redirect_confirm) + "(?P<pk>.*)\/(?P<token>.*)(\\n)?"
        regex_uid64_token = re.compile(pattern)
        res = regex_uid64_token.search(mail_sent.body)
        self.assertIsNotNone(res)
        self.pk = res.group('pk')
        token = res.group('token')

        url = reverse('password_reset_confirm', args=(self.pk, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_process_reset_password_no_password(self):
        url = reverse('password_reset_confirm', args=(self.pk, INTERNAL_SETTINGS['INTERNAL_RESET_URL_TOKEN']))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Two error new_password1 et new_password2 are required
        self.assertEqual(len(response.data), 2)

    def test_process_reset_password_mismatch_error(self):
        url = reverse('password_reset_confirm', args=(self.pk, INTERNAL_SETTINGS['INTERNAL_RESET_URL_TOKEN']))
        data = {
            'new_password1': 'salut',
            'new_password2': '09u2354738',

        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # one password_mismatch_errors
        self.assertEqual(len(response.data), 1)

    def test_process_reset_password_too_short_and_common(self):
        url = reverse('password_reset_confirm', args=(self.pk, INTERNAL_SETTINGS['INTERNAL_RESET_URL_TOKEN']))
        data = {
            'new_password1': 'salut',
            'new_password2': 'salut',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Two errors on the validation of the new password: too short and too common
        self.assertEqual(len(response.data), 2)

    def test_process_reset_password_similar_to_email(self):
        url = reverse('password_reset_confirm', args=(self.pk, INTERNAL_SETTINGS['INTERNAL_RESET_URL_TOKEN']))
        data = {
            'new_password1': 'ad.min@test-email.com',
            'new_password2': 'ad.min@test-email.com',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The password is too similar to the email address.
        self.assertEqual(len(response.data), 1)

    def test_process_reset_password(self):
        url = reverse('password_reset_confirm', args=(self.pk, INTERNAL_SETTINGS['INTERNAL_RESET_URL_TOKEN']))
        data = {
            'new_password1': 'newPassdelamuerte',
            'new_password2': 'newPassdelamuerte',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('obtain-token')
        # fail authentication
        data = {'login': 'admin', 'password': 'clement'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Token.objects.count(), 0)
        # Authenticated
        data = {'login': 'admin', 'password': 'newPassdelamuerte'}
        response = self.client.post(url, data, format='json')
        token = response.data.get('token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(token)
        self.assertEqual(Token.objects.count(), 1)
