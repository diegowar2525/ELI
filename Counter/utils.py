import pandas as pd
from .models import Company, Province


def insertar_empresas(archivo_excel):
    # Leer el archivo Excel
    df = pd.read_excel(archivo_excel)

    for _, row in df.iterrows():
        nombre_empresa = row['NOMBRE DE LA ENTIDAD']
        ruc_empresa = row['IDENTIFICACIÓN']
        nombre_provincia = row['provincia']

        # Obtener o crear la provincia
        provincia, _ = Province.objects.get_or_create(name=nombre_provincia)

        # Verificar si la empresa ya existe por nombre o por ruc
        if not Company.objects.filter(name=nombre_empresa).exists() and not Company.objects.filter(ruc=ruc_empresa).exists():
            Company.objects.create(
                name=nombre_empresa,
                ruc=ruc_empresa,
                province=provincia
            )
        else:
            print(f"Empresa '{nombre_empresa}' con RUC '{ruc_empresa}' ya existe. No se insertó.")

    print("Empresas importadas correctamente.")



from Counter.utils import insertar_empresas

insertar_empresas(r'C:\Users\Usuario\Downloads\Prácticas\Empresas.xlsx')
