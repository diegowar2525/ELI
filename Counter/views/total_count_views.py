from itertools import chain
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
import openpyxl
from ..models import TotalCount, Company, ExpertWord, Expert


@login_required
def total_count_view(request):
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
def export_total_count_excel(request):
    total_counts = TotalCount.objects.all().order_by("-year", "-quantity")

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
            palabras_expert = list(chain.from_iterable(word_obj.words for word_obj in expert_word_objs if word_obj.words))
            total_counts = total_counts.filter(word__in=palabras_expert)
        except Expert.DoesNotExist:
            total_counts = total_counts.none()

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

