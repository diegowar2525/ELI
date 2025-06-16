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
    year = request.GET.get("selected_year")
    company_id = request.GET.get("company")
    expert = request.user.expert_profile  # gracias al related_name='expert_profile'
    expert_lists = ExpertWord.objects.filter(expert=expert)
    years = total_counts.values_list("year", flat=True).distinct().order_by("-year")

    if year:
        total_counts = total_counts.filter(year=year)
    if company_id:
        total_counts = total_counts.filter(company__id=company_id)
    
    # Filtrar por la lista de palabras clave seleccionada en el front (expert_lists.name)
    selected_list_name = request.GET.get("selected_list")
    if selected_list_name:
        try:
            # Buscar la lista de palabras clave del experto con el nombre seleccionado
            expert_word_obj = ExpertWord.objects.filter(expert=expert, name=selected_list_name).first()
            if expert_word_obj and expert_word_obj.words:
                expert_words = list(expert_word_obj.words)
                total_counts = total_counts.filter(word__in=expert_words)
            else:
                total_counts = total_counts.none()
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
        "expert_lists": expert_lists,
        "selected_list_name": selected_list_name,
        "years": years,
        "selected_year": year,
    })


@login_required
def export_total_count_excel(request):
    total_counts = TotalCount.objects.all().order_by("-year", "-quantity")

    # Leer los mismos parámetros que la vista principal
    year = request.GET.get("selected_year")
    company_id = request.GET.get("company")
    selected_list = request.GET.get("selected_list")

    # Aplicar filtros igual que en total_count_view
    if year:
        total_counts = total_counts.filter(year=year)
    if company_id:
        total_counts = total_counts.filter(company__id=company_id)

    if selected_list:
        try:
            expert = request.user.expert_profile  # gracias al related_name='expert_profile'
            expert_word_obj = ExpertWord.objects.filter(expert=expert, name=selected_list).first()
            if expert_word_obj and expert_word_obj.words:
                expert_words = list(expert_word_obj.words)
                total_counts = total_counts.filter(word__in=expert_words)
            else:
                total_counts = total_counts.none()
        except Expert.DoesNotExist:
            total_counts = total_counts.none()

    # Cálculos estadísticos
    total_quantity = total_counts.aggregate(suma=Sum("quantity"))["suma"] or 0
    count = total_counts.count()
    average = round(total_quantity / count, 2) if count > 0 else 0

    word_average = {
        item.id: round(item.quantity / average, 2) if item.quantity > 0 else 0
        for item in total_counts
    }

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

    # Fila vacía
    ws.append([])

    # Promedio total
    ws.append(["", "", "Promedio total:", average])

    # Preparar la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=conteo_total.xlsx'
    wb.save(response)
    return response


