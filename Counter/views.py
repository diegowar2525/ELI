from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Report, Company
from .forms import IndividualReportUploadForm, ZipUploadForm
from django.contrib import messages
import os
from django.conf import settings

# Create your views here.
def index_view(request):
    return render(request, "index.html")


@login_required
def panel_view(request):
    return render(request, "panel.html")


def companies_view(request):
    companies = Company.objects.select_related('province__country').all().order_by('name')
    return render(request, 'companies.html', {'companies': companies})


def reports_view(request):
    reports = Report.objects.all().order_by('upload_date')
    return render(request, 'reports.html', {'reports': reports})
    

def totalcount_view(request):
    return render(request, "totalcount.html")


def upload_view(request):
    individual_form = IndividualReportUploadForm()
    zip_form = ZipUploadForm()
    companies = Company.objects.all()

    if request.method == 'POST':
        if 'upload_individual' in request.POST:
            individual_form = IndividualReportUploadForm(request.POST, request.FILES)
            if individual_form.is_valid():
                individual_form.save()
                messages.success(request, "Reporte subido correctamente.")
                return redirect('upload')

        elif 'upload_zip' in request.POST:
            zip_form = ZipUploadForm(request.POST, request.FILES)
            if zip_form.is_valid():
                zip_file = zip_form.cleaned_data['zip_file']
                zip_path = os.path.join(settings.MEDIA_ROOT, 'zip_uploads', zip_file.name)
                os.makedirs(os.path.dirname(zip_path), exist_ok=True)

                with open(zip_path, 'wb+') as destination:
                    for chunk in zip_file.chunks():
                        destination.write(chunk)

                messages.success(request, "Archivo ZIP subido correctamente.")
                return redirect('upload')

    return render(request, 'upload.html', {
        'individual_form': individual_form,
        'zip_form': zip_form,
        'companies': companies,
    })


