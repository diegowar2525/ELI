import os
import django
import pandas as pd

# 1. Configurar entorno antes de cualquier importación de modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WordCounter.settings")  # Ajusta "WordCounter" al nombre real de tu proyecto
django.setup()

# 2. Ahora importa tus modelos
from Counter.models import Company, Report, TotalCountReport, TotalCount
from django.db.models import Sum, Count

# 1. Obtener el universo de palabras (con filtros de longitud > 3 y total > 1)
all_words_qs = TotalCount.objects.values('word').annotate(total=Sum('quantity'))

filtered_words = [
    item['word'] for item in all_words_qs
    if len(item['word']) > 3 and item['total'] > 1
]

all_words = filtered_words

# 2. Obtener empresas con exactamente 6 reportes
empresas_ids_con_6_reportes = (
    Report.objects
    .values('company')
    .annotate(reportes_count=Count('id'))
    .filter(reportes_count=6)
    .values_list('company', flat=True)
)

# 3. Obtener todos los años disponibles
anios_disponibles = (
    Report.objects
    .filter(company__in=empresas_ids_con_6_reportes)
    .values_list('year', flat=True)
    .distinct()
)

# 4. Generar una matriz por cada año
for anio in sorted(anios_disponibles):
    print(f"📅 Generando matriz para el año {anio}...")

    # Filtrar reportes del año actual
    reportes_anio = Report.objects.filter(year=anio, company__in=empresas_ids_con_6_reportes)

    # Obtener las empresas que tienen reportes en ese año
    empresas_anio = Company.objects.filter(report__in=reportes_anio).distinct()

    matriz_data = []

    for empresa in empresas_anio:
        reportes_empresa = reportes_anio.filter(company=empresa)
        fila = {word: 0 for word in all_words}
        fila['_empresa'] = empresa.name

        total_counts = TotalCountReport.objects.filter(report__in=reportes_empresa, word__in=all_words)

        for item in total_counts:
            if item.word in fila:
                fila[item.word] += item.quantity

        matriz_data.append(fila)

    # Exportar a CSV
    df = pd.DataFrame(matriz_data)

    if not df.empty:
        df = df.set_index('_empresa')
        nombre_archivo = f"matriz_{anio}_filtered.csv"
        df.to_csv(nombre_archivo, encoding='utf-8-sig')
        print(f"✅ Matriz exportada como '{nombre_archivo}'")
    else:
        print(f"⚠️ Matriz vacía para el año {anio}. No hay empresas con reportes ese año.")
