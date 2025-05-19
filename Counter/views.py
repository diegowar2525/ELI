from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Report, Company
from .forms import IndividualReportUploadForm, ZipUploadForm, CompanyForm
from django.contrib import messages
from django.http import JsonResponse
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json


# Create your views here.
def index_view(request):
    return render(request, "index.html")


@login_required
def panel_view(request):
    return render(request, "panel.html")


def companies_view(request):
    companies = (
        Company.objects.all().order_by("name")
    )
    return render(
        request,
        "companies.html",
        {
            "companies": companies
        },
    )


def see_company_json(request, company_id):
    company = Company.objects.get(id=company_id)
    data = {
        "ruc": company.ruc,
        "name": company.name
    }
    return JsonResponse(data)


@csrf_exempt
def create_company(request):
    if request.method == "POST":
        ruc = request.POST.get("ruc")
        name = request.POST.get("name")

        errors = {}

        if not ruc:
            errors["ruc"] = ["Este campo es obligatorio."]
        if not name:
            errors["name"] = ["Este campo es obligatorio."]


        if errors:
            return JsonResponse({"errors": errors}, status=400)

        company = Company.objects.create(ruc=ruc, name=name)

        return JsonResponse(
            {
                "id": company.id,
                "ruc": company.ruc,
                "name": company.name
            }
        )

    return JsonResponse({"error": "Método no permitido"}, status=405)


def update_company(request, company_id):
    data = json.loads(request.body)
    try:
        company = Company.objects.get(id=company_id)
        company.ruc = data["ruc"]
        company.name = data["name"]
        company.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


def delete_company(request, company_id):
    Company.objects.filter(id=company_id).delete()
    return HttpResponse(status=204)


@csrf_exempt
def edit_company(request, id):
    company = Company.objects.get(id=id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            company = form.save()
            return JsonResponse(
                {
                    "id": company.id,
                    "ruc": company.ruc,
                    "name": company.name
                }
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def reports_view(request):
    reports = Report.objects.select_related('company').all()
    companies = Company.objects.all()
    return render(request, "reports.html", {
        "reports": reports,
        "companies": companies,
    })



def see_report_json(request, report_id):
    report = Report.objects.get(id=report_id)
    data = {
        "id": report.id,
        "name": report.name,
        "year": report.year,
        "company": {
            "id": report.company.id,
            "name": report.company.name,
        },
        "upload_date": report.upload_date.strftime("%Y-%m-%d"),
    }
    return JsonResponse(data)


def delete_report(request, report_id):
    Report.objects.filter(id=report_id).delete()
    return HttpResponse(status=204)


def update_report(request, report_id):
    data = json.loads(request.body)
    try:
        report = Report.objects.get(id=report_id)
        report.name = data["name"]
        report.year = data["year"]
        report.company = Company.objects.get(id=data["company"])
        report.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


def totalcount_view(request):
    return render(request, "totalcount.html")


def upload_view(request):
    individual_form = IndividualReportUploadForm()
    zip_form = ZipUploadForm()
    companies = Company.objects.all()

    if request.method == "POST":
        if "upload_individual" in request.POST:
            individual_form = IndividualReportUploadForm(request.POST, request.FILES)
            if individual_form.is_valid():
                individual_form.save()
                messages.success(request, "Reporte subido correctamente.")
                return redirect("upload")

        elif "upload_zip" in request.POST:
            zip_form = ZipUploadForm(request.POST, request.FILES)
            if zip_form.is_valid():
                zip_file = zip_form.cleaned_data["zip_file"]
                zip_path = os.path.join(
                    settings.MEDIA_ROOT, "zip_uploads", zip_file.name
                )
                os.makedirs(os.path.dirname(zip_path), exist_ok=True)

                with open(zip_path, "wb+") as destination:
                    for chunk in zip_file.chunks():
                        destination.write(chunk)

                messages.success(request, "Archivo ZIP subido correctamente.")
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
