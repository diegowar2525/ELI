from itertools import chain
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
import openpyxl

from ..models import TotalCount, Company, ExpertWord, Expert, TotalCountReport, Report


from django.db.models import Sum

def get_filtered_total_counts(request):
    """
    Aplica filtros sobre los reportes (año, empresa, lista de experto) y devuelve un conteo agrupado por palabra.
    """
    queryset = TotalCountReport.objects.all()
    year = request.GET.get("selected_year")
    company_id = request.GET.get("company")
    selected_list_name = request.GET.get("selected_list")

    if year:
        queryset = queryset.filter(report__year=year)
    if company_id:
        queryset = queryset.filter(report__company__id=company_id)

    if selected_list_name:
        try:
            expert = request.user.expert_profile
            expert_word_obj = ExpertWord.objects.filter(expert=expert, name=selected_list_name).first()
            if expert_word_obj and expert_word_obj.words:
                expert_words = list(expert_word_obj.words)
                queryset = queryset.filter(word__in=expert_words)
            else:
                return []  # Lista vacía si no hay palabras
        except Expert.DoesNotExist:
            return []  # Usuario sin perfil de experto

    # Agrupar por palabra y sumar cantidad
    total_counts = (
        queryset
        .values("word")
        .annotate(quantity=Sum("quantity"))
        .order_by("-quantity")
    )

    return total_counts


def get_word_average(total_counts, average):
    return {
        item["word"]: round(item["quantity"] / average, 2) if item["quantity"] > 0 else 0
        for item in total_counts
    }



@login_required
def total_count_view(request):
    total_counts = get_filtered_total_counts(request)

    years = Report.objects.values_list("year", flat=True).distinct().order_by("-year")
    companies = Company.objects.filter(report__isnull=False).distinct().order_by("name")
    expert = request.user.expert_profile
    expert_lists = ExpertWord.objects.filter(expert=expert)

    selected_list_name = request.GET.get("selected_list")
    selected_year = request.GET.get("selected_year")

    total_quantity = sum(item["quantity"] for item in total_counts)
    count = len(total_counts)
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
        "selected_year": selected_year,
    })



@login_required
def export_total_count_excel(request):
    total_counts = get_filtered_total_counts(request)  # ya devuelve valores agrupados
    total_quantity = sum(item["quantity"] for item in total_counts)
    count = len(total_counts)
    average = round(total_quantity / count, 2) if count > 0 else 0
    word_average = get_word_average(total_counts, average)

    # Crear Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Conteo Total"
    ws.append(["Palabra", "Cantidad", "Peso"])  # Solo columnas globales

    for item in total_counts:
        ws.append([
            item["word"],
            item["quantity"],
            word_average.get(item["word"], 0),
        ])

    ws.append([])
    ws.append(["", "Promedio total:", average])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=conteo_total.xlsx'
    wb.save(response)
    return response

