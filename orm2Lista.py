import os
import django
from openpyxl import Workbook
from django.db.models import F, Value, CharField
from django.db.models.functions import Length

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WordCounter.settings")
django.setup()

from Counter.models import TotalCount, TotalCountReport

# Agregar longitud como anotación y filtrar por ella
filtered_words_qs = (
    TotalCount.objects
    .annotate(word_length=Length('word'))  # Anotar longitud
    .filter(quantity__gt=1, word_length__gt=3)
    .values_list('word', flat=True)
)

# Crear conjunto de palabras válidas
global_words = set(filtered_words_qs)

# Años a considerar
years = [2019, 2020, 2021, 2022, 2023, 2024]

for year in years:
    print(f"Procesando año {year}...")

    # Palabras únicas del año que estén en el universo global filtrado
    words_for_year = set(
        TotalCountReport.objects
        .filter(report__year=year, word__in=global_words)
        .values_list('word', flat=True)
        .distinct()
    )

    # Guardar en Excel
    wb = Workbook()
    ws = wb.active
    ws.title = f"Palabras_{year}"

    ws.append(['Palabras'])

    for word in sorted(words_for_year):
        ws.append([word])

    wb.save(f'palabras_unicas_{year}.xlsx')
