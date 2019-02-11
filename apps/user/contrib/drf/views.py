import logging

from django.contrib.auth import (
    get_user_model
)
from rest_framework import parsers, renderers
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser

from . import serializers
from .permissions import IsNotAuthenticated

UserModel = get_user_model()
logger = logging.getLogger(__name__)


class UserCreationView(CreateAPIView):
    # We set no permission to this view (default is Authenticated)
    permission_classes = (IsNotAuthenticated | IsAdminUser,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = serializers.UserCreationSerializer
