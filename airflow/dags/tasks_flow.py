import logging
import pandas as pd
import io

from extract.extract_db import extraction_from_db
from extract.extract_api import fetch_github_repositories_data

from gx_services.gx_setup import validate_db, validate_api

from transform.transform_api import transform__api_data
from transform.transform_dm import create_dimensional_model

from merge.merge_both import merge_survey_and_api_data

from load.load_dm import loading_dimensional_model

from kafka_services.producer_service import kafka_producer_fact_table

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def extract_db_data():
    logger.info("Iniciando extracción de datos de la base de datos...")
    try:
        df = extraction_from_db()
        
        if df is None or df.empty:
            logger.warning("No se extrajeron datos de la base de datos o el DataFrame está vacío.")
            return None
        
        logger.info(f"Se extrajeron {len(df)} filas de la base de datos.")
        return df.to_json(orient="records")
    except Exception as e:
        logger.error(f"Error durante la extracción de datos de la base de datos: {e}", exc_info=True)
        return None
    
def validate_db_data_task(db_df_json):
    logger.info("Iniciando validación de datos de la base de datos...")
    if db_df_json is None:
        logger.warning("No hay datos de base de datos para validar (entrada JSON es None).")
        return None
    try:
        raw_db_df = pd.read_json(io.StringIO(db_df_json), orient="records")
        
        validated_df = validate_db(raw_db_df)
        if validated_df is None or validated_df.empty:
            logger.warning("La validación de datos de la base de datos resultó en un DataFrame nulo o vacío.")
            return None
        
        logger.info(f"Se validaron {len(validated_df)} filas de datos de la base de datos.")
        return validated_df.to_json(orient="records")
    except Exception as e:
        logger.error(f"Error durante la validación de datos de la base de datos: {e}", exc_info=True)
        return None
    

def extract_api_data(target_repos=100):
    logger.info(f"Iniciando extracción de datos de la API de GitHub. Objetivo: {target_repos} repositorios...")
    try:
        df = fetch_github_repositories_data(target_repos=target_repos)
        if df is None or df.empty:
            logger.warning("No se extrajeron datos de la API de GitHub o el DataFrame está vacío.")
            return None
        logger.info(f"Se extrajeron {len(df)} filas de la API de GitHub.")
        return df.to_json(orient="records")
    except Exception as e:
        logger.error(f"Error durante la extracción de datos de la API: {e}", exc_info=True)
        return None

def validate_api_data_task(api_df_json):
    logger.info("Iniciando validación de datos de la API...")
    if api_df_json is None:
        logger.warning("No hay datos de API para validar (entrada JSON es None).")
        return None
    
    try:
        raw_api_df = pd.read_json(io.StringIO(api_df_json), orient="records")
        
        validated_df = validate_api(raw_api_df)
        if validated_df is None or validated_df.empty:
            logger.warning("La validación de datos de la API resultó en un DataFrame nulo o vacío.")
            return None
        
        logger.info(f"Se validaron {len(validated_df)} filas de datos de la API.")
        return validated_df.to_json(orient="records")
    except Exception as e:
        logger.error(f"Error durante la validación de datos de la API: {e}", exc_info=True)
        return None

def transform_api_data_task(api_df_json):
    logger.info("Iniciando transformación de datos de la API...")
    if api_df_json is None:
        logger.warning("No hay datos de API para transformar (entrada JSON es None).")
        return None
    try:
        raw_api_df = pd.read_json(io.StringIO(api_df_json), orient="records")
        if raw_api_df.empty:
            logger.info("El DataFrame de API está vacío después de leer JSON. No se realizarán transformaciones.")
            return raw_api_df.to_json(orient="records")
        transformed_df = transform__api_data(raw_api_df)
        if transformed_df is None or transformed_df.empty:
            logger.warning("La transformación de datos de API resultó en un DataFrame nulo o vacío.")
            return None if transformed_df is None else transformed_df.to_json(orient="records")
        logger.info(f"Se transformaron {len(transformed_df)} filas de datos de la API.")
        return transformed_df.to_json(orient="records")
    except Exception as e:
        logger.error(f"Error durante la transformación de datos de la API: {e}", exc_info=True)
        return None

def merge_data_task(db_df_json, api_df_json):
    logger.info("Iniciando la tarea de fusión de datos (merge_data_task)...")
    
    if db_df_json is None or api_df_json is None:
        logger.warning("merge_data_task: No se pueden fusionar datos porque una o ambas entradas JSON son None.")
        return None
    
    try:
        merged_json_output = merge_survey_and_api_data(db_df_json, api_df_json)
        
        if merged_json_output is None:
            logger.warning("merge_data_task: La función 'merge_survey_and_api_data' devolvió None.")
            return None

        temp_df_for_check = pd.read_json(io.StringIO(merged_json_output), orient="records")
        
        if temp_df_for_check.empty:
            logger.warning("merge_data_task: La fusión resultó en un DataFrame vacío (según el JSON decodificado).")
            return None 
        
        logger.info(f"merge_data_task: Se fusionaron {len(temp_df_for_check)} filas de datos.")
        
        return merged_json_output

    except Exception as e:
        logger.error(f"merge_data_task: Error general durante el proceso de fusión de datos: {e}", exc_info=True)
        return None

def transform_dm_task(merged_df_json):
    logger.info("Iniciando transformación a modelo dimensional...")

    if merged_df_json is None:
        logger.warning(
            "No hay datos fusionados para transformar (entrada JSON es None)."
        )
        return None, None, None, None, None, None

    try:
        raw_df = pd.read_json(io.StringIO(merged_df_json), orient="records")

        if raw_df.empty:
            logger.info(
                "Lógica: El DataFrame fusionado está vacío. "
                "El modelo dimensional se creará a partir de un DF vacío."
            )

        (dim_demographic_df,
         dim_professional_experience_df,
         dim_tech_tools_df,
         dim_job_satisfaction_df,
         dim_miscellaneous_df,
         fact_table_df) = create_dimensional_model(raw_df)

        logger.info("Modelo dimensional creado con éxito.")
        
        dim_demographic_json = dim_demographic_df.to_json(orient="records") if dim_demographic_df is not None else None
        dim_professional_experience_json = dim_professional_experience_df.to_json(orient="records") if dim_professional_experience_df is not None else None
        dim_tech_tools_json = dim_tech_tools_df.to_json(orient="records") if dim_tech_tools_df is not None else None
        dim_job_satisfaction_json = dim_job_satisfaction_df.to_json(orient="records") if dim_job_satisfaction_df is not None else None
        dim_miscellaneous_json = dim_miscellaneous_df.to_json(orient="records") if dim_miscellaneous_df is not None else None
        fact_table_json = fact_table_df.to_json(orient="records") if fact_table_df is not None else None

        return (
            dim_demographic_json,
            dim_professional_experience_json,
            dim_tech_tools_json,
            dim_job_satisfaction_json,
            dim_miscellaneous_json,
            fact_table_json
        )

    except Exception as e:
        logger.error(
            f"Error durante la transformación a modelo dimensional: {e}",
            exc_info=True
        )
        return None, None, None, None, None, None

def load_data_task(
    dim_demographic_json,
    dim_professional_experience_json,
    dim_tech_tools_json,
    dim_job_satisfaction_json,
    dim_miscellaneous_json,
    fact_table_json
):
    """
    Carga los datos de las tablas de dimensiones y la tabla de hechos.
    """
    logger.info("Iniciando carga de datos del modelo dimensional...")
    try:
        required_jsons = [
            dim_demographic_json,
            dim_professional_experience_json,
            dim_tech_tools_json,
            dim_job_satisfaction_json,
            dim_miscellaneous_json,
            fact_table_json
        ]
        if not all(required_jsons):
            logger.warning(
                "No se cargarán datos porque una o más entradas JSON "
                "del modelo dimensional son None."
            )
            return

        dim_demographic = pd.read_json(
            io.StringIO(dim_demographic_json), orient="records"
        )
        dim_professional_experience = pd.read_json(
            io.StringIO(dim_professional_experience_json), orient="records"
        )
        dim_tech_tools = pd.read_json(
            io.StringIO(dim_tech_tools_json), orient="records"
        )
        dim_job_satisfaction = pd.read_json(
            io.StringIO(dim_job_satisfaction_json), orient="records"
        )
        dim_miscellaneous = pd.read_json(
            io.StringIO(dim_miscellaneous_json), orient="records"
        )
        fact_table = pd.read_json(
            io.StringIO(fact_table_json), orient="records"
        )

        # Asumiendo que loading_dimensional_model es una función definida en otro lugar
        loading_dimensional_model(
            dim_demographic,
            dim_professional_experience,
            dim_tech_tools,
            dim_job_satisfaction,
            dim_miscellaneous,
            fact_table
        )
        logger.info("Carga de datos del modelo dimensional completada.")

    except Exception as e:
        logger.error(
            f"Error durante la carga de datos del modelo dimensional: {e}",
            exc_info=True
        )


def kafka_streaming_task(fact_table_json: str | None):
    logger.info("Iniciando la tarea de streaming a Kafka...")
    try:
        if fact_table_json is None:
            logger.warning(
                "No hay datos para enviar a Kafka (entrada JSON es None)."
            )
            return

        kafka_producer_fact_table(fact_table_json)
        logger.info("Datos enviados a Kafka con éxito.")

    except Exception as e:
        logger.error(
            f"Error durante el envío de datos a Kafka: {e}",
            exc_info=True
        )