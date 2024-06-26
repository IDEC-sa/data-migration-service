from typing import Any
from django import forms
from django.forms.utils import ErrorList
from .models import QuoteRequest, StaticData
from .services import validate_prods
import magic
from django.core.validators import FileExtensionValidator, BaseValidator
from django.core import exceptions
from dal import autocomplete
from datetime import date

ext_validator = FileExtensionValidator(['xlsx'], message="Please select a valid excel file")
pdf_validator = FileExtensionValidator(['pdf'], message="Please select a valid pdf file")

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
                            widget=forms.ClearableFileInput(attrs={
                                'accept':'.xlsx',
                            }))

    class Meta:
        model = QuoteRequest
        exclude = ["user", "state", "date_created", "static_data","productsAdded"]
        widgets = {
            'company': autocomplete.ModelSelect2(url='company-autocomplete')
        }

    def get_fields (self):
        obj:QuoteRequest = self.instance
        if obj.productsAdded:
            self.fields.pop("excel")

    def __init__(self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
        renderer=None,) -> None:
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance, use_required_attribute, renderer)
 
        self.get_fields()

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
                            )
    
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

