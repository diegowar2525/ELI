from itertools import chain
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
import openpyxl

from ..models import TotalCount, Company, ExpertWord, Expert


def get_filtered_total_counts(request, total_counts=None):
    """
    Aplica los filtros de año, empresa y lista de palabras clave al queryset de TotalCount.
    """
    if total_counts is None:
        total_counts = TotalCount.objects.all().order_by("-year", "-quantity")

    year = request.GET.get("selected_year")
    company_id = request.GET.get("company")
    selected_list_name = request.GET.get("selected_list")

    if year:
        total_counts = total_counts.filter(year=year)
    if company_id:
        total_counts = total_counts.filter(company__id=company_id)

    if selected_list_name:
        try:
            expert = request.user.expert_profile  # gracias al related_name='expert_profile'
            expert_word_obj = ExpertWord.objects.filter(expert=expert, name=selected_list_name).first()
            if expert_word_obj and expert_word_obj.words:
                expert_words = list(expert_word_obj.words)
                total_counts = total_counts.filter(word__in=expert_words)
            else:
                total_counts = total_counts.none()
        except Expert.DoesNotExist:
            total_counts = total_counts.none()

    return total_counts


def get_word_average(total_counts, average):
    """
    Calcula el peso de cada palabra en relación al promedio.
    """
    return {
        item.id: round(item.quantity / average, 2) if item.quantity > 0 else 0
        for item in total_counts
    }


@login_required
def total_count_view(request):
    total_counts = TotalCount.objects.all().order_by("-year", "-quantity")
    total_counts = get_filtered_total_counts(request, total_counts)

    # Datos auxiliares para filtros
    years = TotalCount.objects.values_list("year", flat=True).distinct().order_by("-year")
    companies = Company.objects.filter(totalcount__isnull=False).distinct().order_by("name")
    expert = request.user.expert_profile
    expert_lists = ExpertWord.objects.filter(expert=expert)
    selected_list_name = request.GET.get("selected_list")
    year = request.GET.get("selected_year")

    # Cálculos estadísticos
    total_quantity = total_counts.aggregate(suma=Sum("quantity"))["suma"] or 0
    count = total_counts.count()
    average = round(total_quantity / count, 2) if count > 0 else 0
    word_average = get_word_average(total_counts, average)

    return render(request, "totalcount.html", {
        "total_counts": total_counts,
        "companies": companies,
        "average": average,
        "word_average": word_average,
        "expert_lists": expert_lists,
        "selected_list_name": selected_list_name,
        "years": years,
        "selected_year": year,
    })


@login_required
def export_total_count_excel(request):
    total_counts = TotalCount.objects.all().order_by("-year", "-quantity")
    total_counts = get_filtered_total_counts(request, total_counts)

    # Cálculos estadísticos
    total_quantity = total_counts.aggregate(suma=Sum("quantity"))["suma"] or 0
    count = total_counts.count()
    average = round(total_quantity / count, 2) if count > 0 else 0
    word_average = get_word_average(total_counts, average)

    # Crear el archivo Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Conteo Total"

    # Encabezados
    ws.append(["Palabra", "Cantidad", "Peso", "Empresa", "Año"])

    # Filas de datos
    for item in total_counts:
        ws.append([
            item.word,
            item.quantity,
            word_average.get(item.id, 0),
            item.company.name,
            item.year,
        ])

    # Fila vacía y promedio total
    ws.append([])
    ws.append(["", "", "Promedio total:", average])

    # Preparar la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=conteo_total.xlsx'
    wb.save(response)
    return response
