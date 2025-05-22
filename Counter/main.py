import re
from collections import Counter
from .models import TotalCountReport, Report
from .stopwords import STOPWORDS_ES
from .utils import quitar_tildes, extraer_texto_pdf_inteligente

STOPWORDS_ES_NORMALIZADAS = set(quitar_tildes(p) for p in STOPWORDS_ES)


def contar_palabras(texto: str) -> Counter:
    """Cuenta las palabras en un texto, normalizando y eliminando stopwords."""

    texto = texto.lower()
    palabras = re.findall(r"\b[a-záéíóúüñ]+\b", texto)
    palabras = [quitar_tildes(p) for p in palabras]
    palabras_filtradas = [
        p for p in palabras if len(p) > 1 and p not in STOPWORDS_ES_NORMALIZADAS
    ]
    return Counter(palabras_filtradas)


def process_report(report_path: str, report_instance: Report):
    """Procesa un reporte PDF y guarda su conteo de palabras."""
    texto = extraer_texto_pdf_inteligente(report_path)
    conteo = contar_palabras(texto)

    for palabra, cantidad in conteo.items():
        TotalCountReport.objects.update_or_create(
            report=report_instance, word=palabra, defaults={"quantity": cantidad}
        )


def process_zip(zip_path: str):
    """Procesa un archivo ZIP que contiene múltiples reportes."""
    # Implementación pendiente
    pass
