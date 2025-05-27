from django import forms
from .models import Report, Company


class IndividualReportUploadForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["company", "year", "name", "file"]
        widgets = {
            "company": forms.Select(attrs={"class": "border rounded px-2 py-1"}),
            "year": forms.NumberInput(
                attrs={"min": 2000, "max": 2100, "class": "border rounded px-2 py-1"}
            ),
            "name": forms.TextInput(attrs={"class": "border rounded px-2 py-1"}),
            "file": forms.ClearableFileInput(
                attrs={"class": "border rounded px-2 py-1"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].required = False
        self.fields["year"].required = False
        self.fields["name"].required = False
        self.fields["file"].required = True



class ZipUploadForm(forms.Form):
    zip_file = forms.FileField(
        label="Archivo ZIP",
        widget=forms.ClearableFileInput(attrs={"class": "border rounded px-2 py-1"})
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "border rounded px-2 py-1"})
    )


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["ruc", "name", "province"]
        widgets = {
            "ruc": forms.TextInput(attrs={"class": "border rounded px-2 py-1"}),
            "name": forms.TextInput(attrs={"class": "border rounded px-2 py-1"}),
            "province": forms.Select(attrs={"class": "border rounded px-2 py-1"}),
        }
