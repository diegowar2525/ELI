import re
import unicodedata
import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from fuzzywuzzy import fuzz
from pdf2image import convert_from_path
from .models import Province, Company

#Extraer texto de PDF digital
def extraer_texto_pdf(path: str) -> str:
    texto = ""
    with fitz.open(path) as doc:
        for page in doc:
            texto += page.get_text()
    return texto 


#Extraer texto de PDF Escaneado
def extraer_texto_ocr_pdf(path: str) -> str:
    texto = ""
    paginas = convert_from_path(path)
    for img in paginas:
        texto += pytesseract.image_to_string(img, lang="spa")
    return texto


#Verificar si el PDF es digital o escaneado
def extraer_texto_pdf_inteligente(path: str) -> str:
    texto = extraer_texto_pdf(path)
    if not texto.strip():  
        texto = extraer_texto_ocr_pdf(path)
    return texto


#Quita tildes y diacriticos de una palabra
def quitar_tildes(palabra: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", palabra)
        if unicodedata.category(c) != "Mn"
    )


#Busca el nombre de empresa y una año en el texto de un PDF. Devuelve valores por defecto si no hay coincidencias
def encontrar_compañia_año(text: str):
    year_match = re.search(r"\b(19|20)\d{2}\b", text)
    year = int(year_match.group()) if year_match else None

    best_score = 0
    best_company = None

    companies = Company.objects.all()
    for company in companies:
        score = fuzz.partial_ratio(company.name.lower(), text.lower())
        if score > best_score and score > 60:
            best_score = score
            best_company = company

    return best_company, year


#Cargar empresas desde un archivo Excel
def insertar_empresas(archivo_excel):
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
#insertar_empresas(r"C:\Users\SOMOS UNEMI\Downloads\Prácticas\Empresas.xlsx")