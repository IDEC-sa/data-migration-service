from typing import Any
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import QuoteRequest, StaticData
from .services import validate_prods
import magic
from django.core.validators import FileExtensionValidator
from django.core import exceptions
ext_validator = FileExtensionValidator(['xlsx'], message="Please select a valid excel file")

def validate_file_mimetype(file):
    accept = ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/zip"]
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
        
    # def __init__(self, data: exceptions.Mapping[str, Any] | None = ..., files: exceptions.Mapping[str, File] | None = ..., auto_id: bool | str = ..., prefix: str | None = ..., initial: dict[str, Any] | None = ..., error_class: type[ErrorList] = ..., label_suffix: str | None = ..., empty_permitted: bool = ..., instance: Model | None = ..., use_required_attribute: bool | None = ..., renderer: Any = ...) -> None:
    #     super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance, use_required_attribute, renderer)
    #     excel.widget.attrs.update({'class': 'rounded_list'})
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
    class Meta:
        model = StaticData
        fields = "__all__"



class ProductsForm(forms.Form):
    products = forms.FileField(validators=[ext_validator, validate_file_mimetype], 
                            help_text="this is a sample help text", 
                            widget=forms.FileInput(attrs={
                                'accept':'.xlsx',
                            }))
