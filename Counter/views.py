import os
import json
import openpyxl
from itertools import chain

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Prefetch
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Report, Company, Province, TotalCountReport, TotalCount, ExpertWord
from User.models import Expert
from .forms import IndividualReportUploadForm, ZipUploadForm
from .main import process_report, process_zip


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


@login_required
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

    # Filtrar por año, empresa y palabras clave
    year = request.GET.get("year")
    company_id = request.GET.get("company")
    solo_claves = request.GET.get("expert_words")

    if year:
        total_counts = total_counts.filter(year=year)
    if company_id:
        total_counts = total_counts.filter(company__id=company_id)
    
    if solo_claves is not None:
        try:
            expert = request.user.expert_profile  # gracias al related_name='expert_profile'
            expert_word_objs = ExpertWord.objects.filter(expert=expert)
            # Obtener palabras asociadas al experto
            expert_words = list(chain.from_iterable(word_obj.words for word_obj in expert_word_objs if word_obj.words))
            # Filtrar los conteos solo por palabras clave del experto
            total_counts = total_counts.filter(word__in=expert_words)
        except Expert.DoesNotExist:
            total_counts = total_counts.none()  # Usuario no tiene perfil de experto

    # Cálculos estadísticos
    total_quantity = total_counts.aggregate(suma=Sum("quantity"))["suma"] or 0
    count = total_counts.count()
    average = round(total_quantity / count, 2) if count > 0 else 0

    # Diccionario con pesos por ID
    word_average = {
        item.id: round(item.quantity / average, 2) if item.quantity > 0 else 0
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
    palabras_expert = list(chain.from_iterable(e.words for e in expert_words if e.words))

    if year:
        total_counts = total_counts.filter(year=year)
    if company_id:
        total_counts = total_counts.filter(company__id=company_id)
    if solo_claves is not None:
        expert_words = ExpertWord.objects.values_list("word", flat=True)
        total_counts = total_counts.filter(word__in=palabras_expert)

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


@login_required
def concealment_detection_view(request):
    return render(request, "concealment_detection.html")


@login_required
def comparative_analysis_view(request):
    return render(request, "comparative_analysis.html")


@login_required
def users_view(request):
    return render(request, "users.html")


# * ---------------------------------------- CRUD EXPERT LISTS  ----------------------------------------

def expert_lists_view(request):
    """Muestra el template con todos los expertos y sus listas."""
    experts = Expert.objects.prefetch_related("word_lists")
    
    return render(request, "expert_lists.html", {"experts": experts})


@csrf_exempt
def create_list(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("DEBUG DATA:", data)
        expert_id = data.get('expert_id')
        name = data.get('name')
        words = data.get('words', [])
        expert = get_object_or_404(Expert, id=expert_id)
        new_list = ExpertWord.objects.create(expert=expert, name=name, words=words)
        return JsonResponse({'success': True, 'id': new_list.id})
    return JsonResponse({'success': False}, status=400)


def get_list_json(request, list_id):
    lista = get_object_or_404(ExpertWord, id=list_id)
    return JsonResponse({
        "id": lista.id,
        "name": lista.name,
        "words": lista.words
    })


@csrf_exempt
def update_list(request, list_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    data  = json.loads(request.body)

    try:
        lista = ExpertWord.objects.get(id=list_id)
    except ExpertWord.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    # Solo tocar los campos presentes en el JSON -------------------------
    if "name" in data and data["name"] is not None:
        lista.name = data["name"]

    if "words" in data:                       # puede ser [] si el usuario las vacía a propósito
        lista.words = data["words"]

    lista.save()
    return JsonResponse({"success": True})


@csrf_exempt
def delete_list(request, list_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        lista = ExpertWord.objects.get(id=list_id)
        lista.delete()
        return JsonResponse({"success": True})
    except ExpertWord.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

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
