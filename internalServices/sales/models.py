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

class Company(models.Model):
    arabic_name = models.CharField(blank = False, null = False, max_length = 200)
    latin_name = models.CharField(blank = False, null = False, max_length = 200)
    code = models.CharField(blank = False, null = False, max_length = 200)
    def __str__(self) -> str:
        return self.latin_name

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

    @property
    def user(self):
        print("enterdeddddd")
        return self.quoteRequest.user

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
    class Meta:
        permissions = [
            ("can_approve_quote", "can approve quotations"),
            ("can_disapprove_quote", "can disapprove quotations"),
            ("can_validate_quote", "can validate a quote"),
            ("can_add_static_to_quote", "can add static data to quote"),
            ("can_draften_quote", "can draften quotation"),
            ("can_review_quote", "can review a quotations")
        ]

    def can_views(self, user):
        # Custom logic to check if the user can view this instance
        print(user.sysRole)
        print("entered auth")
        return  user == self.user or user.is_superuser  or user.sysRole == "sdir"
    
    priceUnit = models.CharField(choices = units, max_length=3)
    excel = models.FileField(validators=[excel_validator])
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = False, blank = False)
    state = models.CharField(choices = states, max_length=4, default = "dra")
    date_created = models.DateTimeField(blank = False, default=datetime.now)
    discount = models.FloatField(null = False, default = 0, error_messages ={
                    "null":"the discount field can'b be empty"
                    })
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
    def getEditUrl(self):
        return reverse("update-quote", kwargs= {
            "pk":self.id
        })
    def get_fields(self):
        return self._meta.get_all_field_names()

    def isReady(self):
        return self.static_data

    def can_view(self, user):
        return user == self .user

class Product(models.Model):
    name = models.TextField(null = False, blank = False, error_messages ={
                    "null":"The line item field is not valid",
                    })
    internalCode = models.TextField(null = False, blank = False, error_messages ={
                    "null":"The line item field is not valid",
                    })
    odooRef = models.TextField(null = False, blank = False, unique = True, error_messages ={
                    "null":"The line item field is not valid",
                    })

class ProductList(models.Model):
    quoteRequest = models.OneToOneField(QuoteRequest, on_delete = models.CASCADE, related_name = "productList")

class ProductLine(models.Model):
    optional = models.BooleanField(default = False, null = False, )
    lineItem = models.PositiveIntegerField(null = False, blank = False, error_messages ={
                    "null":"The line item field is not valid",
                    })
    quantity = models.PositiveIntegerField(null = False, blank = False)
    unitPrice = models.FloatField(null = False, blank = False, error_messages ={
                    "null":"The unit price field is not valid",
                    })
    product = models.ForeignKey(Product, on_delete = models.DO_NOTHING, null = False, blank = False, error_messages ={
                    "null":"The internal code field is not valid",
                    })
    productList = models.ForeignKey(ProductList, on_delete = models.CASCADE, related_name = "productLines")
