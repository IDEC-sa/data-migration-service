from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import pandas as pd
from django.urls import reverse
from django.core.validators import FileExtensionValidator, MinLengthValidator
import magic
from django.core import exceptions
from datetime import datetime
# Create your models here.
User = settings.AUTH_USER_MODEL

excel_validator = FileExtensionValidator(['xlsx'], message="Please select a valid excel file")
pdf_validator = FileExtensionValidator(['pdf'], message="Please select a valid excel file")

# def validate_file_mimetype(file):
#     accept = ["application/vnd.ms-excel"]
#     file_mime_type = magic.from_buffer(file.read(1024), mime = True)
#     print(file_mime_type)
#     if file_mime_type != "application/vnd.ms-excel":
#         raise exceptions.ValidationError("unsupported file type")

# def validate_file_mimetype2(file):
#     accept = ["application/pdf"]
#     file_mime_type = magic.from_buffer(file.read(1024), mime = True)
#     print(file_mime_type)
#     if file_mime_type not in accept:
#         raise exceptions.ValidationError("unsupported file type")

class Company(models.Model):
    arabic_name = models.CharField(blank = False, null = False, max_length = 200)
    latin_name = models.CharField(blank = False, null = False, max_length = 200)
    code = models.CharField(blank = False, null = False, max_length = 200)

class StaticData(models.Model):
    ##add constrains to the file upload and validation
    quotationReference = models.CharField(max_length = 100, blank = True, null = False)
    date = models.DateField(blank = False, null = False)
    projectName = models.CharField(blank = False, null = False, max_length = 100, 
                                   validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    scopeOfWork =  models.CharField(blank = False, null = False, max_length = 100,
                                    validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    quotationValidity = models.CharField(blank = False, null = False, max_length = 100,
                                         validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    deliveryTime = models.CharField(blank = False, null = False, max_length = 100,
                                    validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    deliveryAddress = models.CharField(blank = False, null = False, max_length = 100,
                                       validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    termsOfPayment = models.CharField(blank = False, null = False, max_length = 100, 
                                      validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    warranty = models.CharField(blank = False, null = False, max_length = 100,
                                validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    General = models.CharField(blank = False, null = False, max_length = 100,
                               validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    contractReference = models.CharField(max_length = 50, null = False, blank = False,
                                         validators=[
            MinLengthValidator(5, 'the field must contain at least 5 characters')
            ])
    contract = models.FileField(validators=[pdf_validator])

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
    excel = models.FileField(validators=[excel_validator])
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = False, blank = False)
    state = models.CharField(choices = states, max_length=4, default = "dra")
    date_created = models.DateTimeField(blank = False, default=datetime.now)
    discount = models.FloatField(null = False, default = 0)
    deliveryAndInstallation = models.FloatField(null = False, default = 0)
    static_data = models.OneToOneField(StaticData, on_delete = models.CASCADE, null = True, blank = False)
    productsAdded = models.BooleanField(default = False)
    company = models.ForeignKey(Company, on_delete = models.DO_NOTHING, null = False, blank = False)

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
    odooRef = models.TextField(null = False, blank = False, unique = True)

class ProductList(models.Model):
    quoteRequest = models.OneToOneField(QuoteRequest, on_delete = models.CASCADE, related_name = "productList")

class ProductLine(models.Model):
    optional = models.BooleanField(default = False, null = False)
    lineItem = models.PositiveIntegerField(null = False, blank = False)
    quantity = models.PositiveIntegerField(null = False, blank = False)
    unitPrice = models.FloatField(null = False, blank = False)
    product = models.ForeignKey(Product, on_delete = models.DO_NOTHING, null = False, blank = False)
    productList = models.ForeignKey(ProductList, on_delete = models.CASCADE, related_name = "productLines")
