from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd

COLUMNAS_OBLIGATORIAS =[
    "id_venta",
    "id_cliente",
    "nombre_cliente",
    "producto",
    "categoria",
    "cantidad",
    "precio_unitario",
    "fecha_venta"
]

def leer_archivo(nombre_archivo: str, contenido: bytes):

    extension = Path(nombre_archivo).suffix.lower()

    match extension:

        case ".csv":
            return pd.read_csv(
                BytesIO(contenido)
            )
        case ".xlsx":
            return pd.read_excel(
                BytesIO(contenido)
            )
        case ".json":
            texto = contenido.decode("utf-8")
            return  pd.read_json(
                StringIO(texto)
            )
        case ".txt":
            texto = contenido.decode("utf-8")
            return pd.read_csv(
                StringIO(texto),
                sep=None,
                engine="python"
            )
        case _:
            raise ValueError(
                f"Formato no soportado: {extension}"
            )


def validar_archivo(nombre_archivo: str, contenido: bytes):

    errores = []

    try:
        df = leer_archivo(
            nombre_archivo, contenido
        )
    except Exception as error:
        return {
            "valido": False,
            "errores": [
                f"No se pudo leer el archivo: {str(error)}"
            ],
            "filas": 0,
            "columnas": []
        }

    # esta parte es para limpiar espacios innecesarios o eso parece no se habra q ver xd
    df.columns = df.columns.astype(str).str.strip()

    # validar archivos vacios 
    if df.empty:
        errores.append(
            "El archivo no contiene registros"
        )

    # validar q las columnas obligatorias esten o no
    columnas_faltantes = [
        columna
        for columna in COLUMNAS_OBLIGATORIAS
        if columna not in df.columns
    ]

    if columnas_faltantes:
        errores.append(
            "Faltan columnas obligatorias: "
            + ", ".join(columnas_faltantes)
        )

    #validar ID de venta
    if "id_venta" in df.columns:

        if df["id_venta"].isnull().any():
            errores.append(
                "Existen registros sin id_venta"
            )
        if df["id_venta"].duplicated().any():
            errores.append(
                "Existen id_venta duplicados"
            )

    #validar la huevda de cantidad
    if "cantidad" in df.columns:

        cantidad = pd.to_numeric(
            df["cantidad"],
            errors="coerce"
        )
        if cantidad.isnull().any(): 
                errores.append(
                    "La columna cantidad contiene valores no numéricos"
                )
        elif (cantidad <= 0).any():
             errores.append(
            "La cantidad debe ser mayor a cero"
        )
    

    #Validar los precios
    if "precio_unitario" in df.columns:

        precio = pd.to_numeric(
            df["precio_unitario"],
            errors="coerce"
        )
        if precio.isnull().any():
                errores.append(
                    "La columna precio_unitario contiene valores no numéricos"
                )
        elif (precio < 0).any():
                errores.append(
                    "El precio_unitario no puede ser negativo"
                )

    #validar fechas
    if "fecha_venta" in df.columns:

        fecha = pd.to_datetime(
            df["fecha_venta"],
            errors="coerce"
        )
        if fecha.isnull().any():
                errores.append(
                    "La columna fecha_venta contiene fechas inválidas"
                )

    return{
        "valido": len(errores) == 0,
        "errores": errores,
        "filas": len(df),
        "columnas": list(df.columns)
    }


def normalizar_archivo(nombre_archivo: str, contenido: bytes):

     df = leer_archivo(
          nombre_archivo,
          contenido
     )

     #limpar columnas y lo q sea q se debe limpiar
     df.columns = df.columns.astype(str).str.strip()

     #mantener las columnas en un solo orden y no hueviar a AZURE
     df = df[COLUMNAS_OBLIGATORIAS].copy()

     #normalizar tipos o lo q sea
     df["id_venta"] = pd.to_numeric(
          df["id_venta"]
     ).astype(int)

     df["cantidad"] = pd.to_numeric(
          df["cantidad"]
     )

     df["fecha_venta"] = pd.to_datetime(
          df["fecha_venta"]
     ).dt.strftime("%Y-%m-%d")

     #de cualquier formato a es mismo formato 
     csv_normalizado = df.to_csv(
          index=False
     )

     return csv_normalizado.encode("utf-8")