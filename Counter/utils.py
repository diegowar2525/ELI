import re
import unicodedata
import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from fuzzywuzzy import fuzz
from pdf2image import convert_from_path

from .models import Province, Company


def extraer_texto_pdf(path: str) -> str:
    """Extrae texto de un PDF digital."""
    texto = ""
    with fitz.open(path) as doc:
        for page in doc:
            texto += page.get_text()
    return texto 


def extraer_texto_ocr_pdf(path: str) -> str:
    """Extrae texto de un PDF escaneado (OCR)."""
    texto = ""
    paginas = convert_from_path(path)
    for img in paginas:
        texto += pytesseract.image_to_string(img, lang="spa")
    return texto


def extraer_texto_pdf_inteligente(path: str) -> str:
    """Detecta si el PDF es digital o escaneado y extrae el texto apropiadamente."""
    texto = extraer_texto_pdf(path)
    if not texto.strip():  # Si el texto está vacío, probablemente es un PDF escaneado
        texto = extraer_texto_ocr_pdf(path)
    return texto


def quitar_tildes(palabra: str) -> str:
    """Quita tildes y diacríticos de una palabra."""
    return "".join(
        c
        for c in unicodedata.normalize("NFD", palabra)
        if unicodedata.category(c) != "Mn"
    )


def encontrar_compañia_año(text: str):
    """Busca el nombre de la empresa y un año en el texto. Devuelve valores por defecto si no encuentra coincidencias."""
    year_match = re.search(r"\b(19|20)\d{2}\b", text)
    year = int(year_match.group()) if year_match else 2023

    best_score = 0
    best_company = None

    companies = Company.objects.all()
    for company in companies:
        score = fuzz.partial_ratio(company.name.lower(), text.lower())
        if score > best_score and score > 60:
            best_score = score
            best_company = company

    if not best_company:
        try:
            best_company = Company.objects.get(name__iexact="Sin empresa")
        except Company.DoesNotExist:
            best_company = Company.objects.create(name="Sin empresa")

    return best_company, year


def insertar_empresas(archivo_excel):
    """Carga empresas desde un archivo Excel."""
    df = pd.read_excel(archivo_excel)

    for _, row in df.iterrows():
        nombre_empresa = row["NOMBRE DE LA ENTIDAD"]
        ruc_empresa = row["IDENTIFICACIÓN"]
        nombre_provincia = row["provincia"]

        provincia, _ = Province.objects.get_or_create(name=nombre_provincia)

        if (
            not Company.objects.filter(name=nombre_empresa).exists()
            and not Company.objects.filter(ruc=ruc_empresa).exists()
        ):
            Company.objects.create(
                name=nombre_empresa, ruc=ruc_empresa, province=provincia
            )
        else:
            print(
                f"Empresa '{nombre_empresa}' con RUC '{ruc_empresa}' ya existe. No se insertó."
            )

    print("Empresas importadas correctamente.")





#from Counter.models import Province, Company
#from Counter.utils import insertar_empresas

#insertar_empresas(r"D:\Prácticas\Empresas.xlsx")