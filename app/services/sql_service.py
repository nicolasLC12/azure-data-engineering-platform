import os
import time
import pyodbc
from dotenv import load_dotenv

from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

SQL_SERVER = os.getenv("AZURE_SQL_SERVER")
SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME")
SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")

def obtener_conexion(
    intentos: int = 5,
    espera_segundos: int = 10
):

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=60;"
    )

    ultimo_error = None

    for intento in range(1, intentos + 1):

        try:

            conexion = pyodbc.connect(
                connection_string
            )

            return conexion

        except pyodbc.OperationalError as error:

            ultimo_error = error

            logger.warning(
                "Intento SQL %s/%s fallido.",
                intento,
                intentos
            )

            if intento < intentos:

                logger.info(
                    "Reintentando conexión SQL en %s segundos...",
                    espera_segundos
                )

                time.sleep(
                    espera_segundos
                )

    raise ultimo_error

def registrar_historial_sql(
        archivo: str,
        tipo: str,
        tamano_bytes:int,
        fecha_carga,
        estado: str,
        detalle: str,
        adf_run_id: str = "",
        estado_adf: str ="",
        archivo_normalizado: str = "",
        ruta_procesado: str = "",
        ruta_rechazo: str = ""
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
        INSERT INTO dbo.Historial_Ingesta (
            archivo,
            tipo,
            tamano_bytes,
            fecha_carga,
            estado,
            detalle,
            adf_run_id,
            estado_adf,
            archivo_normalizado,
            ruta_procesado,
            ruta_rechazo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    valores = (
        archivo,
        tipo,
        tamano_bytes,
        fecha_carga,
        estado,
        detalle or None,
        adf_run_id or None,
        estado_adf or None,
        archivo_normalizado or None,
        ruta_procesado or None,
        ruta_rechazo or None
    )

    try:
        cursor.execute(
            consulta,
            valores
        )

        conexion.commit()

    finally:

        cursor.close()
        conexion.close()



def actualizar_historial_sql(
    adf_run_id: str,
    estado_adf: str,
    ruta_procesado: str = "",
    detalle: str = ""
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
        UPDATE dbo.Historial_Ingesta
        SET
            estado_adf = ?,
            ruta_procesado = ?,
            detalle = CASE
                WHEN ? <> '' THEN ?
                ELSE detalle
            END,
            fecha_actualizacion = SYSDATETIME()
        WHERE adf_run_id = ?
    """

    try:

        cursor.execute(
            consulta,
            (
                estado_adf,
                ruta_procesado or None,
                detalle,
                detalle,
                adf_run_id
            )
        )

        conexion.commit()

    finally:

        cursor.close()
        conexion.close()