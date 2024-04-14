from typing import Iterable
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
    SYSROLES = {
        "dir":_("director"),
        "sdir":_("Sales Director"),
        "sman":_("Sales man") 
    }
    email = models.EmailField(_("email address"), blank = False, null = False, unique = True)
    sysRole = models.CharField(max_length=4, choices=SYSROLES, default="sman")

    @transaction.atomic
    def save(self, *args, **kwargs):
        adding = self._state.adding
        super().save(*args, **kwargs)
        if adding:
            if self.sysRole == "sdir":
                dirs = Group.objects.get_or_create(name='salesdirectors')[0]
                dirs.user_set.add(self)
                dirs.save()
            elif self.sysRole == "sman":
                salesmen = Group.objects.get_or_create(name='salesmen')[0]
                salesmen.user_set.add(self)
                salesmen.save()

