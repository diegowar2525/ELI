import os
import re
import zipfile
from collections import Counter
from tempfile import TemporaryDirectory

from django.db.models import F
from django.core.files import File

from .models import TotalCountReport, Report, TotalCount
from .stopwords import STOPWORDS_ES
from .utils import quitar_tildes, extraer_texto_pdf_inteligente, encontrar_compañia_año

# --- Constantes ---
STOPWORDS_ES_NORMALIZADAS = set(quitar_tildes(p) for p in STOPWORDS_ES)

# --- Funciones utilitarias ---

def count_words(texto: str) -> Counter:
    """Cuenta las palabras en un texto, normalizando y eliminando stopwords."""
    texto = texto.lower()
    palabras = re.findall(r"\b[a-záéíóúüñ]+\b", texto)
    palabras = [quitar_tildes(p) for p in palabras]
    palabras_filtradas = [
        p for p in palabras if len(p) > 2 and p not in STOPWORDS_ES_NORMALIZADAS
    ]
    return Counter(palabras_filtradas)

def find_paragraph(report: Report, palabra: str) -> list[str]:
    """
    Dado un reporte y una palabra, extrae el texto del PDF y devuelve los párrafos que contienen la palabra.
    """
    palabra = quitar_tildes(palabra.lower())
    texto = extraer_texto_pdf_inteligente(report.file.path)
    parrafos = re.split(r'\n{2,}|\r\n{2,}', texto)
    return [
        p.strip() for p in parrafos if palabra in quitar_tildes(p.lower())
    ]

# --- Funciones principales ---

def process_report(report_path: str, report_instance: Report):
    texto = extraer_texto_pdf_inteligente(report_path)
    company, year = encontrar_compañia_año(texto)

    if not getattr(report_instance, "name", None):
        report_instance.name = os.path.basename(report_path)
    if not getattr(report_instance, "company", None):
        report_instance.company = company
    if not getattr(report_instance, "year", None):
        report_instance.year = year
    report_instance.save()

    conteo = count_words(texto)

    for palabra, cantidad in conteo.items():
        TotalCountReport.objects.update_or_create(
            report=report_instance, word=palabra, defaults={"quantity": cantidad}
        )

        # Solo se actualiza el conteo total, sin importar año o empresa
        obj, creado = TotalCount.objects.get_or_create(
            word=palabra,
            defaults={"quantity": cantidad},
        )
        if not creado:
            TotalCount.objects.filter(pk=obj.pk).update(
                quantity=F("quantity") + cantidad
            )


def process_zip(zip_path: str, company=None):
    """Procesa un archivo ZIP que contiene múltiples reportes PDF, incluyendo subcarpetas."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref, TemporaryDirectory() as temp_dir:
        zip_ref.extractall(temp_dir)

        for root, dirs, files in os.walk(temp_dir):
            for filename in files:
                if not filename.lower().endswith(".pdf"):
                    continue  # Ignora archivos que no son PDF

                file_path = os.path.join(root, filename)

                try:
                    with open(file_path, "rb") as f:
                        django_file = File(f)
                        report = Report(company=company)
                        # Guarda el archivo PDF en MEDIA_ROOT con el nombre original
                        report.file.save(filename, django_file, save=True)

                    # Procesa el reporte con la función que ya tienes
                    process_report(report.file.path, report)

                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")
