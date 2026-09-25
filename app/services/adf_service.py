import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from dotenv import load_dotenv

load_dotenv()


SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
DATA_FACTORY_NAME = os.getenv("AZURE_DATA_FACTORY_NAME")
PIPELINE_NAME = os.getenv("AZURE_PIPELINE_NAME")

VARIABLES_REQUERIDAS = {
    "AZURE_SUBSCRIPTION_ID": SUBSCRIPTION_ID,
    "AZURE_RESOURCE_GROUP": RESOURCE_GROUP,
    "AZURE_DATA_FACTORY_NAME": DATA_FACTORY_NAME,
    "AZURE_PIPELINE_NAME": PIPELINE_NAME,
}

for nombre, valor in VARIABLES_REQUERIDAS.items():
    if not valor:
        raise ValueError(
            f"Falta configurar la variable {nombre} en el archivo .env"
        )

credential = DefaultAzureCredential()

adf_client = DataFactoryManagementClient(
    credential=credential,
    subscription_id=SUBSCRIPTION_ID
)

def ejecutar_pipeline(nombre_archivo: str):

    parametros = {
        "p_nombre_archivo": nombre_archivo
    }

    respuesta = adf_client.pipelines.create_run(
        resource_group_name=RESOURCE_GROUP,
        factory_name=DATA_FACTORY_NAME,
        pipeline_name=PIPELINE_NAME,
        parameters=parametros
    )

    return respuesta.run_id

def consultar_estado_pipeline(run_id: str):

    ejecucion = (
        adf_client.pipeline_runs.get(
            resource_group_name=RESOURCE_GROUP,
            factory_name=DATA_FACTORY_NAME,
            run_id=run_id
        )
    )

    return {
        "run_id": run_id,
        "estado": ejecucion.status,
        "inicio": ejecucion.run_start,
        "fin": ejecucion.run_end,
        "mensaje": ejecucion.message
    }