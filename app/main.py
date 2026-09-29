from fastapi import FastAPI, File, HTTPException, UploadFile

from app.services.validator import (
    validar_archivo, normalizar_archivo
)
from app.services.adf_service import (
    ejecutar_pipeline,
    consultar_estado_pipeline
)
from app.services.blob_service import (subir_archivo, subir_archivo_normalizado, mover_archivo_a_procesados,
                                       subir_archivo_rechazado)
from app.services.sql_service import (registrar_historial_sql, actualizar_historial_sql)

import json
from datetime import datetime
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
import logging

logger = logging.getLogger(__name__)

def traducir_estado_adf(estado_azure: str):

    estados ={
        "Queued": "PENDIENTE",
        "InProgress": "PROCESANDO",
        "Succeeded": "PROCESADO",
        "Failed": "ERROR",
        "Cancelled": "CANCELADO"
    }

    return estados.get(
        estado_azure,
        estado_azure.upper()
    )


app = FastAPI(
    tittle = "Azure Data Engineering Platform",
    description= "Plataforma de ingesta y procesamiento de datos",
    version= "1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(directory="app/templates")

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

@app.get("/")
def inicio():
    return {
        "proyecto": "Azure Data Engineering Platform",
        "estado": "API funcionando"
    }
@app.get("health")
def health():
    return{
    "status": "ok"
}
@app.get("/cargas")
def listar_cargas():
    with open("data/cargas.json ", "r", encoding="utf-8") as archivo:
        cargas = json.load(archivo)

        return {
            "total": len(cargas),
            "cargas": cargas
        }

@app.get("/cargas/actualizar-estados")
def actualizar_estados_adf():

    with open(
        ARCHIVO_LOG,
        "r",
        encoding="utf-8"
    ) as archivo:

        cargas = json.load(archivo)

    actualizados = 0

    for carga in cargas:
        run_id = carga.get("adf_run_id")

        estado_actual = carga.get(
            "estado_adf",
            ""
        )

        if(not run_id or estado_actual not in ["PENDIENTE", "PROCESANDO"]):
            continue

        try:

            resultado = consultar_estado_pipeline(
                run_id
            )

            nuevo_estado = traducir_estado_adf(
                resultado["estado"]
            )

            if nuevo_estado == "PROCESADO":

                archivo_normalizado = carga.get(
                    "archivo_normalizado"
                )

                if archivo_normalizado:

                    ruta_procesado = mover_archivo_a_procesados(
                        archivo_normalizado
                    )

                    carga["ruta_procesado"] = ruta_procesado


            carga["estado_adf"] = nuevo_estado

            actualizar_historial_sql(
                adf_run_id=run_id,
                estado_adf=nuevo_estado,
                ruta_procesado=carga.get(
                    "ruta_procesado",
                    ""
                ),
                detalle=carga.get(
                    "detalle_adf",
                    ""
                )
            )

            actualizados += 1
        except Exception as error:

            carga["estado_adf"] = "ERROR"
            carga["detalle_adf"] = str(error)

            logger.exception("Error actualizando estado ADF/SQL")

    with open(
        ARCHIVO_LOG, "w", encoding="utf-8"
    ) as archivo:

        json.dump(
            cargas, archivo, indent=4, ensure_ascii=False
        )

    return{
        "actualizados": actualizados,
        "cargas": cargas
    }




ARCHIVO_LOG = Path("data/cargas.json")

def registar_carga(nombre: str, tamano: int, estado: str, detalle: str = "",
                   adf_run_id: str = "", estado_adf: str = "", archivo_normalizado: str = "",
                   ruta_rechazo: str = ""):
    with open(ARCHIVO_LOG, "r", encoding="utf-8") as archivos:
        cargas = json.load(archivos)

        cargas.append({
            "archivo": nombre,
        "tipo": nombre.split(".")[-1].upper(),
        "tamano_bytes": tamano,
        "fecha_carga": datetime.now().isoformat(),
        "estado": estado,
        "detalle": detalle,
        "adf_run_id": adf_run_id,
        "estado_adf": estado_adf,
        "archivo_normalizado": archivo_normalizado,
        "ruta_rechazo": ruta_rechazo
        })

        with open(ARCHIVO_LOG, "w", encoding="utf-8") as archivo:
            json.dump(cargas, archivo, indent=4, ensure_ascii=False)

    registrar_historial_sql(
        archivo=nombre,
        tipo=nombre.split(".")[-1].upper(),
        tamano_bytes=tamano,
        fecha_carga=datetime.now(),
        estado=estado,
        detalle=detalle,
        adf_run_id=adf_run_id,
        estado_adf=estado_adf,
        archivo_normalizado=archivo_normalizado,
        ruta_procesado="",
        ruta_rechazo=ruta_rechazo
    )


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    extensiones_permitidas = [
        ".csv",
        ".xlsx",
        ".json",
        ".txt"
        ]

    nombre = file.filename

    if not any(
        nombre.lower().endswith(ext)
        for ext in extensiones_permitidas
    ):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos CSV, XLSX, JSON y TXT"
        )
    contenido = await file.read()

    resultado_validacion = validar_archivo(
        nombre_archivo=nombre,
        contenido=contenido
    )

    if not resultado_validacion["valido"]:

        ruta_rechazo = subir_archivo_rechazado(nombre_archivo=nombre, contenido=contenido)

        registar_carga(
            nombre=nombre,
            tamano=len(contenido),
            estado="ERROR",
            detalle=" | ".join(
                resultado_validacion["errores"]
            ), ruta_rechazo=ruta_rechazo
        )
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": "El archivo no superó las validaciones",
                "errores": resultado_validacion["errores"]
            }
        )

    ruta_blod = subir_archivo(
        nombre_archivo=nombre,
        contenido=contenido
    )

    contenido_normalizado = normalizar_archivo(
        nombre_archivo=nombre,
        contenido=contenido
    )

    ruta_normalizada = subir_archivo_normalizado(
        nombre_archivo=nombre,
        contenido=contenido
    )

    nombre_normalizado = Path(
        ruta_normalizada
    ).name

    run_id = ejecutar_pipeline(
        nombre_normalizado  
    )
    
    registar_carga(
        nombre=nombre,
        tamano=len(contenido),
        estado="CARGADO",
        detalle=(
            f"Archivo validado y enviado a ADF"
            f"Filas: {resultado_validacion['filas']}"
        ),
        adf_run_id=run_id, estado_adf="PROCESANDO", archivo_normalizado=nombre_normalizado
    )
    


    return{
        "archivo": nombre,
        "estado": "CARGADO",
        "filas": resultado_validacion["filas"],
        "columnas": resultado_validacion["columnas"],
        "ruta_original": ruta_blod,
        "ruta_normalizada": ruta_normalizada,
        "archivo_adf": nombre_normalizado,
        "adf_run_id": run_id,
        "estado_Adf": "PROCESANDO",
        "archivo_normalizado": nombre_normalizado,
        "destino": "Azure Blob Storage + Azure Data Factory"
    }