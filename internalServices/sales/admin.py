from django.contrib import admin

from .models import Product, ProductList, QuoteRequest, ProductLine, Company, Serial, Report
# Register your models here

class productAdmin(admin.ModelAdmin):
    search_fields = ('internalCode', 'odooRef', 'name')


class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('arabic_name', 'code', 'latin_name')


admin.site.register([ProductList, QuoteRequest, ProductLine, Serial, Report])
admin.site.register(Company, CompanyAdmin)
admin.site.register(Product, productAdmin)