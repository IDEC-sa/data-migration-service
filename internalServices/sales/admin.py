from django.contrib import admin

from .models import Product, ProductList, QuoteRequest, ProductLine
# Register your models here

admin.site.register([Product, ProductList, QuoteRequest, ProductLine])