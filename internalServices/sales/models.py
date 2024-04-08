from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import pandas as pd
from django.urls import reverse
from django.core.validators import FileExtensionValidator, MinLengthValidator, MinValueValidator
import magic
from django.core import exceptions
from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save, post_init
from django.db.models import Q

# Create your models here.
User = settings.AUTH_USER_MODEL

excel_validator = FileExtensionValidator(['xlsx'], message="Please select a valid excel file")
pdf_validator = FileExtensionValidator(['pdf'], message="Please select a valid excel file")
zeroPositiveValidator = MinValueValidator(0, "Negative values are not allowed")


    
# class SerialMixin():
#     Serial = models.ForeignKey(Serial, on_delete=models.DO_NOTHING)

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

    priceUnit = models.CharField(choices = units, max_length=3)
    excel = models.FileField(validators=[excel_validator])
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = False, blank = False)
    state = models.CharField(choices = states, max_length=4, default = "dra")
    date_created = models.DateTimeField(blank = False, default=datetime.now)
    discount = models.DecimalField(null = False, default = 0, 
                                   decimal_places=3, 
                                   max_digits=15,
                                   validators=[zeroPositiveValidator], 
                                   error_messages ={
                                        "null":"the discount field can'b be empty"
                                        })
    deliveryAndInstallation = models.DecimalField(null = False, default = 0,
                                                decimal_places=3, 
                                                max_digits=15,
                                                validators=[zeroPositiveValidator]
                                                )
    static_data = models.OneToOneField(StaticData, on_delete = models.CASCADE, null = True, blank = False)
    productsAdded = models.BooleanField(default = False)
    company = models.ForeignKey(Company, on_delete = models.DO_NOTHING, null = False, blank = False)
    serial = models.CharField(max_length=100, editable=False, null=True)

    # def getSerial(self):
    #     serial = Serial.objects.get_or_create(prefix="qutoe-")
    #     return serial.getNext()
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
    unitPrice = models.DecimalField(null = False, blank = False, decimal_places=4, max_digits=15)
    product = models.ForeignKey(Product, on_delete = models.DO_NOTHING, null = False, blank = False, error_messages ={
                    "null":"The internal code field is not valid",
                    })
    productList = models.ForeignKey(ProductList, on_delete = models.CASCADE, related_name = "productLines")

class Serial(models.Model):
    prefix = models.CharField(default="A", null=False, blank=False, max_length=30)
    postfix = models.CharField(default="A", null=False, blank=False, max_length=30)
    next = models.PositiveBigIntegerField(default=0, null=False, blank=False)
    
    class Meta:
        unique_together = ('prefix', 'postfix')

    def getNext(self):
        tmp = self.next
        self.next += 1
        self.save()
        return self.prefix + str(tmp) + self.postfix

    @receiver(post_save, sender=QuoteRequest)
    def _post_save_receiver(sender, instance, created, **kwargs):
        if created or not instance.serial:
            qsSerial, cr = Serial.objects.get_or_create(prefix="quo-", postfix="/2023")
            print(f"created is {cr}")
            instance.serial = qsSerial.getNext()
