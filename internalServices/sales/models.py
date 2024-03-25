from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import pandas as pd
from django.urls import reverse
from django.core.validators import FileExtensionValidator
import magic
from django.core import exceptions
from datetime import datetime
# Create your models here.
User = settings.AUTH_USER_MODEL

ext_validator = FileExtensionValidator(['xlsx'], message="Please select a valid excel file")

def validate_file_mimetype(file):
    accept = ["application/vnd.ms-excel"]
    file_mime_type = magic.from_buffer(file.read(1024), mime = True)
    print(file_mime_type)
    if file_mime_type != "application/vnd.ms-excel":
        raise exceptions.ValidationError("unsupported file type")

class StaticData(models.Model):
    ##add constrains to the file upload and validation
    quotationReference = models.TextField(max_length = 100, blank = False, null = False)
    date = models.DateField(blank = False, null = False)
    projectName = models.TextField(blank = False, null = False)
    scopeOfWork =  models.TextField(blank = False, null = False)
    quotationValidity = models.TextField(blank = False, null = False)
    deliveryTime = models.TextField(blank = False, null = False)
    deliveryAddress = models.TextField(blank = False, null = False)
    termsOfPayment = models.TextField(blank = False, null = False)
    warranty = models.TextField(blank = False, null = False)
    General = models.TextField(blank = False, null = False)
    contractReference = models.TextField(max_length = 50, null = False, blank = False)
    contract = models.FileField()

class QuoteRequest(models.Model):

    units = {
        "SAR": _("Saudi Riyals"),
        "USD": _("United States Dollar")
    }
    states = {
        "dra":_("Drafted"),
        "quo" : _("Quotation"), ##once static data is added it is guaranteed that the prods should be created!
        "val": _("Validated"),
        "app": _("Approved"),
        "napp": _("Not Approved"),
    }

    priceUnit = models.CharField(choices = units, max_length=3)
    excel = models.FileField(validators=[ext_validator])
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = False, blank = False)
    state = models.CharField(choices = states, max_length=4, default = "dra")
    date_created = models.DateTimeField(blank = False, default=datetime.now)
    discount = models.FloatField(null = False, default = 0)
    deliveryAndInstallation = models.FloatField(null = False, default = 0)
    static_data = models.OneToOneField(StaticData, on_delete = models.CASCADE, null = True, blank = False)
    productsAdded = models.BooleanField(default = False)

    def df(self):
        return pd.read_excel(self.excel)

    def getCreateUrl(self):
        return reverse("createprods", kwargs={
            "quoteId":self.id
        })
    def getCreateStaticUrl(self):
        return reverse("add-static", kwargs={
            "quoteId":self.id
        })

    def getRewviewUrl(self):
        return reverse("reviewquote", kwargs={
            "quoteId":self.id
        })
    def getSelfUrl(self):
        return reverse("detail-quote", kwargs={
            "pk":self.id
        })
    def get_fields(self):
        return self._meta.get_all_field_names()

    def isReady(self):
        return self.static_data

    def can_view(self, user):
        return user == self.user

class Product(models.Model):
    name = models.TextField(null = False, blank = False)
    internalCode = models.TextField(null = False, blank = False)
    odooRef = models.TextField(null = False, blank = False)

class ProductList(models.Model):
    quoteRequest = models.OneToOneField(QuoteRequest, on_delete = models.CASCADE, related_name = "productList")

class ProductLine(models.Model):
    optional = models.BooleanField(default = False, null = False)
    lineItem = models.PositiveIntegerField(null = False, blank = False)
    quantity = models.PositiveIntegerField(null = False, blank = False)
    unitPrice = models.FloatField(null = False, blank = False)
    product = models.ForeignKey(Product, on_delete = models.DO_NOTHING, null = False, blank = False)
    productList = models.ForeignKey(ProductList, on_delete = models.CASCADE, related_name = "productLines")
