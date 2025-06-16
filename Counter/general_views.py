import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Company
from .forms import IndividualReportUploadForm, ZipUploadForm
from .main import process_report, process_zip


# * ---------------------------------------- VISTAS GENERALES ----------------------------------------
def index_view(request):
    return render(request, "index.html")


@login_required
def panel_view(request):
    return render(request, "panel.html")


@login_required
def upload_view(request):
    individual_form = IndividualReportUploadForm()
    zip_form = ZipUploadForm()
    companies = Company.objects.all()

    if request.method == "POST":
        if "upload_individual" in request.POST:
            individual_form = IndividualReportUploadForm(request.POST, request.FILES)
            if individual_form.is_valid():
                reporte = individual_form.save()
                
                # Función para procesar el reporte individual
                process_report(reporte.file.path, reporte)

                messages.success(request, f"Reporte subido y procesado correctamente.")
                return redirect("upload")

        elif "upload_zip" in request.POST:
            zip_form = ZipUploadForm(request.POST, request.FILES)
            if zip_form.is_valid():
                zip_file = zip_form.cleaned_data["zip_file"]
                company = zip_form.cleaned_data["company"]
                zip_path = os.path.join(
                    settings.MEDIA_ROOT, "zip_uploads", zip_file.name
                )
                os.makedirs(os.path.dirname(zip_path), exist_ok=True)

                with open(zip_path, "wb+") as destination:
                    for chunk in zip_file.chunks():
                        destination.write(chunk)

                # Procesa el archivo ZIP que acabas de guardar
                process_zip(zip_path, company)

                messages.success(
                    request, f"Archivo ZIP subido y procesado correctamente."
                )
                return redirect("upload")

    return render(
        request,
        "upload.html",
        {
            "individual_form": individual_form,
            "zip_form": zip_form,
            "companies": companies,
        },
    )


@login_required
def concealment_detection_view(request):
    return render(request, "concealment_detection.html")


@login_required
def comparative_analysis_view(request):
    return render(request, "comparative_analysis.html")


@login_required
def user_view(request):
    return render(request, "users.html")
