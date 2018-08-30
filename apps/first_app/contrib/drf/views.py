# Create your views here.
import logging
import os

from django.http import HttpResponse

logger = logging.getLogger(__name__)

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


def index(request):
    logger.warning("0" * 30)
    from pprint import pformat
    logger.warning(pformat('First log!'))
    logger.warning("0" * 30)

    return HttpResponse(
        "Hello, You're at the first_app index. Settings used: {}".format(os.environ.get('DJANGO_SETTINGS_MODULE')))
