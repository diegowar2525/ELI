from django import forms
from .models import Report


class IndividualReportUploadForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["company", "year", "file"]
        widgets = {
            "company": forms.Select(attrs={"class": "border rounded px-2 py-1"}),
            "year": forms.NumberInput(
                attrs={"min": 2000, "max": 2100, "class": "border rounded px-2 py-1"}
            ),
            "file": forms.ClearableFileInput(
                attrs={"class": "border rounded px-2 py-1"}
            ),
        }


class ZipUploadForm(forms.Form):
    zip_file = forms.FileField(label="Archivo ZIP")

