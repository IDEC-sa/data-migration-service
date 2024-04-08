import django_filters
from .models import QuoteRequest
from users.models import User
from django import forms


class FilterQuotes(django_filters.FilterSet):

    projectName = django_filters.CharFilter(label = "Project name",
                                             field_name='static_data__projectName', 
                                            lookup_expr = 'contains')
    quoteRef = django_filters.CharFilter(label = "Quotation reference",
                                             field_name='static_data__quotationReference', 
                                            lookup_expr = 'contains')
    serial = django_filters.CharFilter(label= "Quotation serial", 
                                       lookup_expr='contains')
    
    class Meta:
        model = QuoteRequest
        fields = ["state", 'projectName', 'serial']
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        print(f"filters {self.base_filters}")
        super().__init__(data, queryset, request=request, prefix=prefix)

class SuperFilterQuotes(django_filters.FilterSet):
    projectName = django_filters.CharFilter(label = "Project name",
                                             field_name='static_data__projectName', 
                                            lookup_expr = 'contains')
    quoteRef = django_filters.CharFilter(label = "Quotation reference",
                                             field_name='static_data__quotationReference', 
                                            lookup_expr = 'contains')
    serial = django_filters.CharFilter(label= "Quotation serial", 
                                       lookup_expr='contains')
    user = django_filters.ModelChoiceFilter(queryset=User.objects.filter(sysRole = "sman"))
    
    class Meta:
        model = QuoteRequest
        fields = ["state", 'projectName', 'user', 'serial']
