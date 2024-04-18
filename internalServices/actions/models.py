from typing import Iterable
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from sales.models import QuoteRequest
from datetime import datetime
from django.utils import timezone
from django.contrib import admin
import logging
User = settings.AUTH_USER_MODEL

# Create your models here.
actionLogger = logging.getLogger("actionsLogger")
print(actionLogger)
class Action(models.Model):

    types = {
        "vis": _("visit"),
        "logi" : _("login"),
        "logo": _("logout"),
        "cre": _("create"),
        "rev": _("review"),
        "adds": _("add-static"),
        "val": _("validate"),
        "app": _("approve"),
        "dra": _("draften"),
        "napp": _("disapprove"),
        "edit": _("edit"),
        "srch":_("search")
    }

    actor = models.ForeignKey(User, null=False, blank=False, on_delete = models.DO_NOTHING)
    type = models.CharField(choices = types, max_length=4, default = "dra")
    quote = models.ForeignKey(QuoteRequest, null=True, blank=True, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(blank=False, null=False, editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        actionLogger.log(msg=str(self), level=logging.INFO)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"[{self.date.astimezone()}] Actor: {self.actor} has  made the following: {self.get_type_display()} {f'on quote: {self.quote.serial}' if self.quote else ''}"
