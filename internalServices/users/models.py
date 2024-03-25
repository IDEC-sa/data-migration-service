from django.db import models
from django.utils.translation import gettext_lazy as _


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
