import django_filters
from .models import QuoteRequest
from users.models import User
from django import forms
class FilterQuotes(django_filters.FilterSet):
    # paginate = forms.NumberInput()
    projectName = django_filters.CharFilter(label = "Project name",
                                             field_name='static_data__projectName', 
                                            lookup_expr = 'contains')
    quoteRef = django_filters.CharFilter(label = "Quotation reference",
                                             field_name='static_data__quotationReference', 
                                            lookup_expr = 'contains')
    class Meta:
        model = QuoteRequest
        fields = ["state", 'projectName']


class SuperFilterQuotes(django_filters.FilterSet):
    projectName = django_filters.CharFilter(label = "Project name",
                                             field_name='static_data__projectName', 
                                            lookup_expr = 'contains')
    quoteRef = django_filters.CharFilter(label = "Quotation reference",
                                             field_name='static_data__quotationReference', 
                                            lookup_expr = 'contains')
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    
    class Meta:
        model = QuoteRequest
        fields = ["state", 'projectName', 'user']
