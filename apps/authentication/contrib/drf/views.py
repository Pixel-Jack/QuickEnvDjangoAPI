import logging

from django.contrib.auth import (
    get_user_model, password_validation
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_variables
from rest_framework import parsers, renderers
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .settings import INTERNAL_SETTINGS

UserModel = get_user_model()
logger = logging.getLogger(__name__)

# If you want to update the login date of your user your user model must implement a update_last_login method
IMPLEMENT_UPDATE_LAST_LOGIN = False
if 'update_last_login' in dir(UserModel):
    IMPLEMENT_UPDATE_LAST_LOGIN = True


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = serializers.AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if IMPLEMENT_UPDATE_LAST_LOGIN:
            user.update_last_login()

        return Response({'token': token.key})


class RefreshAuthToken(APIView):
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request, format=None):
        user = request.user
        user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        if IMPLEMENT_UPDATE_LAST_LOGIN:
            user.update_last_login()
        return Response({'token': token.key})


class DeleteAuthToken(APIView):
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def delete(self, request, format=None):
        request.user.auth_token.delete()
        return Response({'message': 'success'})


class PasswordChangeView(APIView):
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = serializers.PasswordChangeSerializer

    @method_decorator(sensitive_variables('password'))
    @method_decorator(never_cache)
    def post(self, request, format=None):
        request.sensitive_post_parameters = ['old_password', 'new_password1', 'new_password2']
        serializer = self.serializer_class(data=request.data, user=request.user)
        serializer.is_valid(raise_exception=True)
        # and set new password
        password = serializer.validated_data.get("new_password1")
        password_validation.validate_password(password, request.user)
        request.user.set_password(password)
        request.user.save()

        logger.info("Password change POST for pk={pk}".format(pk=request.user.pk))
        return Response({'message': 'success'})


# Class-based password reset views
# - PasswordResetView sends the mail
# - PasswordResetConfirmView checks the link the user clicked
# and save in the session the fact that the user will change its password,
# then with a post on this same view it will change the password

class PasswordResetView(APIView):
    # Stay aware of this restriction
    throttle_scope = 'email_sent'
    # We set no permission to this view (default is Authenticated)
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = serializers.EmailSerializer

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = UserModel.objects.filter(**{
            '%s__iexact' % UserModel.get_email_field_name(): email,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())

    def post(self, request, format=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        subject_template_name = INTERNAL_SETTINGS['SUBJECT_TEMPLATE_NAME']
        email_template_name = INTERNAL_SETTINGS['EMAIL_TEMPLATE_NAME']
        site_domain = INTERNAL_SETTINGS['SITE_DOMAIN']
        site_name = INTERNAL_SETTINGS['SITE_NAME']
        use_https = INTERNAL_SETTINGS['SITE_USE_HTTPS']
        redirect_confirm = INTERNAL_SETTINGS['REDIRECT_CONFIRM']  # This is the url in the front app
        token_generator = INTERNAL_SETTINGS['TOKEN_GENERATOR']
        from_email = INTERNAL_SETTINGS['SITE_NO_REPLY_EMAIL']
        contact_email = INTERNAL_SETTINGS['SITE_CONTACT_EMAIL']
        html_email_template_name = INTERNAL_SETTINGS['HTML_EMAIL_TEMPLATE_NAME']

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        unknown_email = True
        for user in self.get_users(email):
            unknown_email = False
            if not site_domain or not site_name:
                current_site = get_current_site(request)
                if not site_domain:
                    site_domain = current_site.domain
                if not site_name:
                    site_name = current_site.name

            context = {
                'email': email,
                'site_name': site_name,
                'site_domain': site_domain,
                'redirect_confirm': redirect_confirm,
                'uid': user.pk,
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                'contact_email': contact_email
            }

            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )

        if unknown_email:
            logger.info("Reset password for unknown email: {}".format(email))
        else:
            logger.info("Reset password for email: {}".format(email))

        # Here we return to the front if self.get_users(email) is actually returning a
        # user on purpose because this prevent to use this path to find user in db.
        return Response({'message': 'success'})


class PasswordResetConfirmView(APIView):
    # We set no permission to this view (default is Authenticated)
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = serializers.SetPasswordSerializer
    token_generator = INTERNAL_SETTINGS['TOKEN_GENERATOR']

    def get_user(self, pk):
        try:
            user = UserModel.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    @method_decorator(never_cache)
    def get(self, request, pk, token, format=None):
        user = self.get_user(pk)
        if user is not None and self.token_generator.check_token(user, token):
            # Store the token in the session and redirect to the
            # password reset form at a URL without the token. That
            # avoids the possibility of leaking the token in the
            # HTTP Referer header.
            request.session[INTERNAL_SETTINGS['INTERNAL_RESET_SESSION_TOKEN']] = token
            logger.info("Password reset confirm success for pk={pk}".format(pk=pk))
            return Response({'message': 'success'})

        logger.info("Password reset confirm GET with invalid params for pk={pk}".format(pk=pk))
        return Response({'message': 'error invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(sensitive_variables('password'))
    @method_decorator(never_cache)
    def post(self, request, pk, token, format=None):
        # replace field new_password1 and new_password2 with ***** if error log
        request.sensitive_post_parameters = ['new_password1', 'new_password2']

        user = self.get_user(pk)

        if user is not None and token == INTERNAL_SETTINGS['INTERNAL_RESET_URL_TOKEN']:
            session_token = self.request.session.get(INTERNAL_SETTINGS['INTERNAL_RESET_SESSION_TOKEN'])
            if self.token_generator.check_token(user, session_token):
                # If the token is valid check the two passwords
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                # and set new password
                password = serializer.validated_data.get("new_password1")
                password_validation.validate_password(password, user)
                user.set_password(password)
                user.save()

                # Finaly
                del request.session[INTERNAL_SETTINGS['INTERNAL_RESET_SESSION_TOKEN']]
                return Response({'message': 'success'})

        logger.info("Password reset confirm POST with invalid params for pk={pk}".format(pk=pk))
        return Response([_('Invalid parameters')], status=status.HTTP_400_BAD_REQUEST)
