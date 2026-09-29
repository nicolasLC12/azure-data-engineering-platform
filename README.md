# Azure Data Engineering Platform

Plataforma web de ingesta, validación, transformación, procesamiento y monitoreo de datos construida con **Python, FastAPI y servicios de Microsoft Azure**.

El proyecto implementa un flujo de datos de extremo a extremo que permite recibir archivos desde una interfaz web, validar su estructura y calidad, almacenarlos en Azure Blob Storage, procesarlos mediante Azure Data Factory, cargar la información en Azure SQL Database y monitorear automáticamente el estado de cada ejecución.

---

## 1. Descripción del proyecto

**Azure Data Engineering Platform** es una solución orientada a prácticas de Data Engineering que automatiza el ciclo de procesamiento de archivos de ventas.

La plataforma permite cargar archivos en diferentes formatos:

- CSV
- XLSX
- JSON
- TXT

Antes de ser procesados, los archivos pasan por diferentes controles de calidad.

Dependiendo del resultado:

- Los archivos válidos continúan hacia Azure Data Factory.
- Los archivos inválidos son enviados automáticamente a una zona de rechazados.
- Los archivos procesados correctamente son trasladados a una zona de procesados.
- El historial completo de cada ejecución se registra en Azure SQL Database.

---

## 2. Objetivo

El objetivo del proyecto es implementar una arquitectura de datos que permita automatizar:

1. Ingesta de archivos.
2. Validación de datos.
3. Normalización.
4. Almacenamiento en Azure Blob Storage.
5. Orquestación mediante Azure Data Factory.
6. Procesamiento ETL.
7. Carga en Azure SQL Database.
8. Monitoreo del pipeline.
9. Manejo de archivos procesados y rechazados.
10. Registro histórico de ejecuciones.
11. Pruebas unitarias y de integración.

---

## 3. Arquitectura

El flujo general de la solución es:

```text
Usuario
  |
  v
Dashboard Web
  |
  v
FastAPI
  |
  v
Validación de archivos
  |
  +------------------------------+
  |                              |
  | Archivo válido               | Archivo inválido
  v                              v
Landing                       Rejected
  |                              |
  v                              |
Normalización                    |
  |                              |
  v                              |
Standardized                     |
  |                              |
  v                              |
Azure Data Factory               |
  |                              |
  v                              |
Azure SQL Database               |
  |                              |
  v                              |
Processed                       |
  |                              |
  +--------------+---------------+
                 |
                 v
         Historial de Ingesta