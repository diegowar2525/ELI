from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Report, Company, Province, TotalCountReport, TotalCount, ExpertWord
from .forms import IndividualReportUploadForm, ZipUploadForm, CompanyForm
from django.contrib import messages
from django.db.models import Sum
from .main import process_report, process_zip
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import os
import openpyxl
from openpyxl.utils import get_column_letter


# * ---------------------------------------- VISTAS GENERALES ----------------------------------------


def index_view(request):
    return render(request, "index.html")


@login_required
def panel_view(request):
    return render(request, "panel.html")


@login_required
def companies_view(request):
    companies = Company.objects.all()
    provinces = Province.objects.all()
    return render(
        request,
        "companies.html",
        {
            "companies": companies,
            "provinces": provinces,
        },
    )


@login_required
def reports_view(request):
    reports = Report.objects.select_related("company").all()
    companies = Company.objects.all()
    return render(
        request,
        "reports.html",
        {
            "reports": reports,
            "companies": companies,
        },
    )


def totalcountreport_view(request, report_id):
    results = list(
        TotalCountReport.objects.filter(report__id=report_id).order_by("-quantity")
    )
    report = Report.objects.get(id=report_id)
    conteos = TotalCountReport.objects.filter(report=report).order_by('-quantity')[:10]

    mid = len(results) // 2
    left = results[:mid]
    right = results[mid:]

    # Rellenar la lista más corta con None para igualar tamaños
    max_len = max(len(left), len(right))
    left += [None] * (max_len - len(left))
    right += [None] * (max_len - len(right))

    paired_results = list(zip(left, right))

    return render(
        request,
        "totalcountreport.html",
        {
            "paired_results": paired_results,
            "report": report,
            "top10_words": conteos,
        },
    )


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
def totalcount_view(request):
    total_counts = TotalCount.objects.all().order_by("-year", "-quantity")
    
    year = request.GET.get("year")
    company_id = request.GET.get("company")
    solo_claves = request.GET.get("expert_words")

    if year:
        total_counts = total_counts.filter(year=year)
    if company_id:
        total_counts = total_counts.filter(company__id=company_id)
    if solo_claves is not None:
        expert_words = ExpertWord.objects.values_list("word", flat=True)
        total_counts = total_counts.filter(word__in=expert_words)
    
    total_quantity = total_counts.aggregate(suma=Sum("quantity"))["suma"] or 0
    count = total_counts.count()
    average = round(total_quantity / count, 2) if count > 0 else 0

    # Diccionario con pesos por ID
    word_average = {
        item.id: round(item.quantity/average, 2) if item.quantity > 0 else 0
        for item in total_counts
    }

    companies = Company.objects.all().order_by("name")

    return render(request, "totalcount.html", {
        "total_counts": total_counts,
        "companies": companies,
        "average": average,
        "word_average": word_average,
    })


@login_required
def export_totalcount_excel(request):
    total_counts = TotalCount.objects.all().order_by("-year", "-quantity")

    year = request.GET.get("year")
    company_id = request.GET.get("company")
    solo_claves = request.GET.get("expert_words")

    if year:
        total_counts = total_counts.filter(year=year)
    if company_id:
        total_counts = total_counts.filter(company__id=company_id)
    if solo_claves is not None:
        expert_words = ExpertWord.objects.values_list("word", flat=True)
        total_counts = total_counts.filter(word__in=expert_words)

    total_quantity = total_counts.aggregate(suma=Sum("quantity"))["suma"] or 0
    count = total_counts.count()
    average = round(total_quantity / count, 2) if count > 0 else 0

    word_average = {
        item.id: round(item.quantity / average, 2) if item.quantity > 0 else 0
        for item in total_counts
    }

    # Crear libro Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Conteo Total"

    # Escribir encabezados
    ws.append(["Palabra", "Cantidad", "Peso", "Empresa", "Año"])

    # Escribir datos
    for item in total_counts:
        ws.append([
            item.word,
            item.quantity,
            word_average.get(item.id, 0),
            item.company.name,
            item.year,
        ])

    # Fila vacía como separador
    ws.append([])

    # Fila de promedio total
    ws.append(["", "", "Promedio total:", average])

    # Preparar respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=conteo_total.xlsx'
    wb.save(response)
    return response


# * ---------------------------------------- CRUD COMPANIES  ----------------------------------------
@login_required
def see_company_json(request, company_id):
    company = Company.objects.get(id=company_id)
    data = {"ruc": company.ruc, "name": company.name, "province": company.province.name}
    return JsonResponse(data)


@csrf_exempt
def create_company(request):
    if request.method == "POST":
        ruc = request.POST.get("ruc")
        name = request.POST.get("name")
        province_id = request.POST.get("province")
        errors = {}

        if not ruc:
            errors["ruc"] = ["Este campo es obligatorio."]
        if not name:
            errors["name"] = ["Este campo es obligatorio."]
        if not province_id:
            errors["province"] = ["Este campo es obligatorio."]
        else:
            try:
                province = Province.objects.get(id=province_id)
            except Province.DoesNotExist:
                errors["province"] = ["Provincia no válida."]

        if errors:
            return JsonResponse({"errors": errors}, status=400)

        company = Company.objects.create(ruc=ruc, name=name, province=province)

        return JsonResponse(
            {
                "id": company.id,
                "ruc": company.ruc,
                "name": company.name,
                "province": company.province.name,
            }
        )

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def delete_company(request, company_id):
    Company.objects.filter(id=company_id).delete()
    return HttpResponse(status=204)


@csrf_exempt
def update_company(request, company_id):
    company = Company.objects.get(id=company_id)
    data = json.loads(request.body)

    ruc = data.get("ruc")
    name = data.get("name")
    province_id = data.get("province")

    if not (ruc and name and province_id):
        return JsonResponse({"error": "Faltan datos"}, status=400)

    try:
        province = Province.objects.get(id=province_id)
    except Province.DoesNotExist:
        return JsonResponse({"error": "Provincia inválida"}, status=400)

    company.ruc = ruc
    company.name = name
    company.province = province
    company.save()

    return JsonResponse({"success": True})


# * ---------------------------------------- CRUD REPORT  ----------------------------------------


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
