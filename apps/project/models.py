from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ProjectCategory(models.Model):
    name = models.CharField(_('name'), max_length=255, unique=True)

    class Meta:
        db_table = 'project_category'
        indexes = [
            models.Index(fields=['name'], name='project_category_name_idx'),
        ]


class Project(models.Model):
    COMMON = 0
    BANNED = 1
    STATUS_CHOICES = (
        (COMMON, 'common'),
        (BANNED, 'banned'),
    )
    id_status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=COMMON,
    )
    id_category = None
    name = models.CharField(_('name'), max_length=255, unique=True)
    description = models.TextField(_('description'), blank=True)
    is_private = models.BooleanField(_('private project'), default=False)
    date_last_modified = models.DateTimeField(_('last modification date'), default=timezone.now)
    date_created = models.DateTimeField(_('creation date'), default=timezone.now)

    class Meta:
        db_table = 'project'
        indexes = [
            models.Index(fields=['name'], name='project_name_idx'),
            models.Index(fields=['is_private'], name='project_is_private_idx'),
            models.Index(fields=['date_last_modified'], name='project_date_last_modified_idx'),
        ]
