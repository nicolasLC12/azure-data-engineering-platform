import os 

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER")

ACCOUNT_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"

credential = DefaultAzureCredential()

blod_service_client = BlobServiceClient(
    account_url=ACCOUNT_URL,
    credential=credential
)

def obtener_ruta_blob(nombre_archivo: str):

    extension = Path(nombre_archivo).suffix.lower()

    match extension:

        case ".csv":
            carpeta = "csv"
        case ".xlsx":
            carpeta = "excel"
        case ".json":
            carpeta = "json"
        case ".txt":
            carpeta = "txt"

        case _:
            carpeta = "otros"

    return f"landing/{carpeta}/{nombre_archivo}"

def subir_archivo(nombre_archivo: str, contenido: bytes):
    container_client = blod_service_client.get_container_client(
        CONTAINER_NAME
    ) 

    ruta_blod = obtener_ruta_blob(
        nombre_archivo
    )

    blod_client = container_client.get_blob_client(
        ruta_blod
    )

    blod_client.upload_blob(
        contenido,
        overwrite=True
    )
    return ruta_blod

def subir_archivo_normalizado(
        nombre_archivo: str,
        contenido: bytes
):
    container_client = (
        blod_service_client.get_container_client(
            CONTAINER_NAME
        )
    )

    nombre_base = Path(nombre_archivo).stem

    ruta_blod = (
        f"standardized/ventas/"
        f"{nombre_base}_normalizado.csv"
    )

    blod_client = container_client.get_blob_client(
        ruta_blod
    )

    blod_client = container_client.get_blob_client(
        ruta_blod
    )

    blod_client.upload_blob(
        contenido,
        overwrite=True
    )

    return ruta_blod