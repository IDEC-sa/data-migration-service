from django.contrib import admin

from .models import Product, ProductList, QuoteRequest, ProductLine, Company, Serial, Report
# Register your models here

class productAdmin(admin.ModelAdmin):
    search_fields = ('internalCode', 'odooRef', 'name')

admin.site.register([ProductList, QuoteRequest, ProductLine, Company, Serial, Report])

admin.site.register(Product, productAdmin)