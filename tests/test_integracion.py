from uuid import uuid4
from app.services.blob_service import (subir_archivo_rechazado, subir_archivo_normalizado, mover_archivo_a_procesados)
from datetime import datetime
from app.services.sql_service import (
    obtener_conexion,
    registrar_historial_sql,
    actualizar_historial_sql
)

def test_subir_archivo_a_rejected():

    nombre_archivo = (f"prueba_integracion_{uuid4().hex[:8]}.csv")

    contenido = (
        "id_venta,nombre\n"
        "999,Prueba Integracion\n"
    ).encode("utf-8")

    ruta = subir_archivo_rechazado(nombre_archivo=nombre_archivo, contenido=contenido)

    assert ruta == (f"rejected/csv/{nombre_archivo}")

def test_mover_archivo_a_processed():

    nombre_archivo = (f"prueba_processed_{uuid4().hex[:8]}.csv")

    contenido = (
        "id_venta,id_cliente,nombre_cliente,producto,"
        "categoria,cantidad,precio_unitario,fecha_venta\n"
        "2001,601,Cliente Integracion,Monitor,"
        "Tecnologia,1,950.00,2026-09-29\n"
    ).encode("utf-8")

    ruta_standardized = subir_archivo_normalizado(
        nombre_archivo=nombre_archivo,
        contenido=contenido
    )

    nombre_normalizado = ruta_standardized.split("/")[-1]

    assert ruta_standardized == (f"standardized/ventas/{nombre_normalizado}")

    ruta_processed = mover_archivo_a_procesados(nombre_normalizado)

    assert ruta_processed == (f"processed/ventas/{nombre_normalizado}")

def test_historial_sql_insert_y_update():

    identificador = uuid4().hex[:8]

    archivo = f"prueba_sql_{identificador}.csv"
    run_id = f"pytest-{identificador}"

    registrar_historial_sql(
        archivo=archivo,
        tipo="CSV",
        tamano_bytes=150,
        fecha_carga=datetime.now(),
        estado="CARGADO",
        detalle="Prueba de integracion",
        adf_run_id=run_id,
        estado_adf="PROCESANDO",
        archivo_normalizado=f"prueba_sql_{identificador}_normalizado.csv",
        ruta_procesado="",
        ruta_rechazo=""
    )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT
                estado,
                estado_adf
            FROM dbo.Historial_Ingesta
            WHERE adf_run_id = ?
            """,
            run_id
        )

        fila = cursor.fetchone()

        assert fila is not None
        assert fila.estado == "CARGADO"
        assert fila.estado_adf == "PROCESANDO"

    finally:

        cursor.close()
        conexion.close()


    ruta_processed = (
        f"processed/ventas/"
        f"prueba_sql_{identificador}_normalizado.csv"
    )

    actualizar_historial_sql(
        adf_run_id=run_id,
        estado_adf="PROCESADO",
        ruta_procesado=ruta_processed
    )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            SELECT
                estado_adf,
                ruta_procesado
            FROM dbo.Historial_Ingesta
            WHERE adf_run_id = ?
            """,
            run_id
        )

        fila = cursor.fetchone()

        assert fila is not None
        assert fila.estado_adf == "PROCESADO"
        assert fila.ruta_procesado == ruta_processed

        cursor.execute(
            """
            DELETE FROM dbo.Historial_Ingesta
            WHERE adf_run_id = ?
            """,
            run_id
        )

        conexion.commit()

    finally:

        cursor.close()
        conexion.close()