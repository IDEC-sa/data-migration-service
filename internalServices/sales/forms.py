from typing import Any
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import QuoteRequest, StaticData
from .services import validate_prods
import magic
from django.core.validators import FileExtensionValidator, BaseValidator
from django.core import exceptions
from dal import autocomplete

ext_validator = FileExtensionValidator(['xlsx'], message="Please select a valid excel file")
pdf_validator = FileExtensionValidator(['pdf'], message="Please select a valid excel file")

#refactor to class based validator

def validate_file_mimetype(file):
    accept = ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/zip"]
    file_mime_type = magic.from_buffer(file.read(1024), mime = True)
    print(file_mime_type)
    if file_mime_type not in accept:
        raise exceptions.ValidationError("unsupported file type")

def validate_file_mimetype2(file):
    accept = ["application/pdf"]
    file_mime_type = magic.from_buffer(file.read(1024), mime = True)
    print(file_mime_type)
    if file_mime_type not in accept:
        raise exceptions.ValidationError("unsupported file type")


class UploadForm(forms.ModelForm):
    
    excel = forms.FileField(validators=[ext_validator, validate_file_mimetype], 
                            help_text="this is a sample help text", 
                            widget=forms.FileInput(attrs={
                                'accept':'.xlsx',
                            }))
    
    class Meta:
        model = QuoteRequest
        exclude = ["user", "state", "date_created", "static_data","productsAdded"]
        widgets = {
            'company': autocomplete.ModelSelect2(url='company-autocomplete')
        }
    def clean_excel(self) -> dict[str, Any]:
        excel = self.cleaned_data["excel"]
        try:
            validate_prods(excel)
        except Exception as e:
            raise forms.ValidationError(e)
        return excel

    def save(self, commit: bool = ...) -> Any:
        print(self.instance)
        return super().save(commit)

class StaticDataForm(forms.ModelForm):
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )
    contract = forms.FileField(validators=[pdf_validator, validate_file_mimetype2], 
                            help_text="this is a sample help text", 
                            widget=forms.FileInput(attrs={
                                'accept':'.pdf',
                            }))
    
    class Meta:
        model = StaticData
        fields = "__all__"



class ProductsForm(forms.Form):
    products = forms.FileField(validators=[ext_validator, validate_file_mimetype], 
                            help_text="this is a sample help text", 
                            widget=forms.FileInput(attrs={
                                'accept':'.xlsx',
                            }))
    def header(self):
        return "Add products to the db"


class CompaniesForm(forms.Form):
    Companies = forms.FileField(validators=[ext_validator, validate_file_mimetype], 
                            help_text="this is a sample help text", 
                            widget=forms.FileInput(attrs={
                                'accept':'.xlsx',
                            }))
    def header(self):
        return "Add Companies to the db"
