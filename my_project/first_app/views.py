# Create your views here.
import logging
import os

from django.http import HttpResponse

logger = logging.getLogger(__name__)


def index(request):
    logger.warning("0" * 30)
    from pprint import pformat
    logger.warning(pformat('First log!'))
    logger.warning("0" * 30)
    return HttpResponse(
        "Hello, world. You're at the first_app index. Settings used: {}".format(os.environ.get('DJANGO_SETTINGS_MODULE')))
