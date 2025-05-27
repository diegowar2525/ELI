import re
from collections import Counter
from .models import TotalCountReport, Report
from .stopwords import STOPWORDS_ES
from .utils import quitar_tildes, extraer_texto_pdf_inteligente, encontrar_compañia_año

import zipfile
import os
from tempfile import TemporaryDirectory

STOPWORDS_ES_NORMALIZADAS = set(quitar_tildes(p) for p in STOPWORDS_ES)

def contar_palabras(texto: str) -> Counter:
    """Cuenta las palabras en un texto, normalizando y eliminando stopwords."""

    texto = texto.lower()
    palabras = re.findall(r"\b[a-záéíóúüñ]+\b", texto)
    palabras = [quitar_tildes(p) for p in palabras]
    palabras_filtradas = [
        p for p in palabras if len(p) > 2 and p not in STOPWORDS_ES_NORMALIZADAS
    ]
    return Counter(palabras_filtradas)


def process_report(report_path: str, report_instance: Report):
    """Procesa un reporte PDF, actualiza nombre, empresa y año, y guarda su conteo de palabras."""
    texto = extraer_texto_pdf_inteligente(report_path)
    company, year = encontrar_compañia_año(texto)

    # Actualiza los campos del reporte solo si no se han proporcionado

    if not getattr(report_instance, 'name', None):
        report_instance.name = os.path.basename(report_path)
    if not getattr(report_instance, 'company', None):
        report_instance.company = company
    if not getattr(report_instance, 'year', None):
        report_instance.year = year
    report_instance.save()

    conteo = contar_palabras(texto)
    for palabra, cantidad in conteo.items():
        TotalCountReport.objects.update_or_create(
            report=report_instance, word=palabra, defaults={"quantity": cantidad}
        )



def process_zip(zip_path: str, company=None):
    """Procesa un archivo ZIP que contiene múltiples reportes PDF, incluyendo subcarpetas."""

    with zipfile.ZipFile(zip_path, 'r') as zip_ref, TemporaryDirectory() as temp_dir:
        zip_ref.extractall(temp_dir)

        for root, dirs, files in os.walk(temp_dir):
            for filename in files:
                if not filename.lower().endswith('.pdf'):
                    continue  # Ignora archivos que no son PDF

                file_path = os.path.join(root, filename)

                try:
                    report = Report.objects.create(
                        file=file_path,
                        company=company,
                    )
                    process_report(file_path, report)

                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")


