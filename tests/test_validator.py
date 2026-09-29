from app.services.validator import validar_archivo
from io import BytesIO
from openpyxl import Workbook

def test_csv_valido():

    contenido = (
        "id_venta,id_cliente,nombre_cliente,producto,"
        "categoria,cantidad,precio_unitario,fecha_venta\n"
        "1001,501,Cliente Prueba,Monitor,"
        "Tecnologia,2,750.50,2026-09-29\n"
    ).encode("utf-8")

    resultado = validar_archivo(nombre_archivo="ventas_test.csv", contenido=contenido)

    assert resultado["valido"] is True
    assert resultado["errores"] == []
    assert resultado["filas"] == 1

def test_csv_con_columna_faltante():

    contenido =(
        "id_venta,id_cliente,nombre_cliente,producto,"
        "categoria,cantidad,fecha_venta\n"
        "1002,502,Cliente Error,Mouse,"
        "Accesorios,1,2026-09-29\n"
    ).encode("utf-8")

    resultado = validar_archivo(nombre_archivo="ventas_error.csv", contenido=contenido)

    assert resultado["valido"] is False
    assert len(["errores"]) > 0

def test_csv_con_cantidad_invalida():

    contenido = (
        "id_venta,id_cliente,nombre_cliente,producto,"
        "categoria,cantidad,precio_unitario,fecha_venta\n"
        "1003,503,Cliente Prueba,Teclado,"
        "Accesorios,-5,150.00,2026-09-29\n"
    ).encode("utf-8")

    resultado = validar_archivo(nombre_archivo="ventas_cantidad_invalida.csv", contenido=contenido)

    assert resultado["valido"] is False
    assert len(resultado["errores"]) > 0

def test_csv_con_fecha_invalida():

    contenido = (
        "id_venta,id_cliente,nombre_cliente,producto,"
        "categoria,cantidad,precio_unitario,fecha_venta\n"
        "1004,504,Cliente Prueba,Mouse,"
        "Accesorios,1,80.00,fecha_invalida\n"
    ).encode("utf-8")

    resultado = validar_archivo(nombre_archivo="ventas_fecha_invalida.csv", contenido=contenido)

    assert resultado["valido"] is False
    assert len(resultado["errores"]) > 0

def test_json_valido():

    contenido = (
        '['
        '{'
        '"id_venta": 1005,'
        '"id_cliente": 505,'
        '"nombre_cliente": "Cliente JSON",'
        '"producto": "Laptop",'
        '"categoria": "Tecnologia",'
        '"cantidad": 1,'
        '"precio_unitario": 2500.00,'
        '"fecha_venta": "2026-09-29"'
        '}'
        ']'
    ).encode("utf-8")

    resultado = validar_archivo(nombre_archivo="ventas_test.json", contenido=contenido)

    assert resultado["valido"] is True
    assert resultado["errores"] == []
    assert resultado["filas"] == 1

def test_json_invalido():

    contenido = (
        '['
        '{'
        '"id_venta": 1006,'
        '"id_cliente": 506,'
        '"nombre_cliente": "Cliente JSON Error",'
        '"producto": "Laptop",'
        '"categoria": "Tecnologia",'
        '"cantidad": -2,'
        '"precio_unitario": 2500.00,'
        '"fecha_venta": "2026-09-29"'
        '}'
        ']'
    ).encode("utf-8")

    resultado = validar_archivo(nombre_archivo="ventas_error.json", contenido=contenido)

    assert resultado["valido"] is False
    assert len(resultado["errores"]) > 0

def test_excel_valido():

    libro = Workbook()
    hoja = libro.active

    hoja.append([
        "id_venta",
        "id_cliente",
        "nombre_cliente",
        "producto",
        "categoria",
        "cantidad",
        "precio_unitario",
        "fecha_venta"
    ])

    hoja.append([
        1007,
        507,
        "Cliente Excel",
        "Monitor",
        "Tecnologia",
        1,
        900.00,
        "2026-09-29"
    ])

    memoria = BytesIO()

    libro.save(memoria)

    contenido = memoria.getvalue()

    resultado = validar_archivo(
        nombre_archivo="ventas_test.xlsx",
        contenido=contenido
    )

    assert resultado["valido"] is True
    assert resultado["errores"] == []
    assert resultado["filas"] == 1

def test_excel_invalido():

    libro = Workbook()
    hoja = libro.active

    hoja.append([
        "id_venta",
        "id_cliente",
        "nombre_cliente",
        "producto",
        "categoria",
        "cantidad",
        "fecha_venta"
    ])

    hoja.append([
        1008,
        508,
        "Cliente Excel Error",
        "Teclado",
        "Accesorios",
        1,
        "2026-09-29"
    ])

    memoria = BytesIO()

    libro.save(memoria)

    contenido = memoria.getvalue()

    resultado = validar_archivo(
        nombre_archivo="ventas_error.xlsx",
        contenido=contenido
    )

    assert resultado["valido"] is False
    assert len(resultado["errores"]) > 0

def test_txt_valido():

    contenido = (
        "id_venta,id_cliente,nombre_cliente,producto,"
        "categoria,cantidad,precio_unitario,fecha_venta\n"
        "1009,509,Cliente TXT,Mouse,"
        "Accesorios,1,85.00,2026-09-29\n"
    ).encode("utf-8")

    resultado = validar_archivo(
        nombre_archivo="ventas_test.txt",
        contenido=contenido
    )

    assert resultado["valido"] is True
    assert resultado["errores"] == []
    assert resultado["filas"] == 1

def test_txt_invalido():

    contenido = (
        "id_venta,id_cliente,nombre_cliente,producto,"
        "categoria,cantidad,fecha_venta\n"
        "1010,510,Cliente TXT Error,Mouse,"
        "Accesorios,1,2026-09-29\n"
    ).encode("utf-8")

    resultado = validar_archivo(
        nombre_archivo="ventas_error.txt",
        contenido=contenido
    )

    assert resultado["valido"] is False
    assert len(resultado["errores"]) > 0