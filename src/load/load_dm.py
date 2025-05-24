from database.db_operations import creating_engine, load_clean_data
import logging
import pandas as pd
import traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")

def loading_dimensional_model(dim_demographic, dim_professional_experience, dim_tech_tools, dim_job_satisfaction, dim_miscellaneous, fact_table):
    engine_dm = None
    database_name_for_log = "dev_survey_dm"
    try:
        logging.info(f"Intentando obtener el motor para el Data Mart: '{database_name_for_log}'")
        engine_dm = creating_engine(database_name="dev_survey_dm")
        
        logging.info(f"Motor para '{database_name_for_log}' obtenido. Procediendo a cargar las tablas.")
        
        load_clean_data(engine_dm, dim_demographic, "dim_demographic")
        load_clean_data(engine_dm, dim_professional_experience, "dim_professional_experience")
        load_clean_data(engine_dm, dim_tech_tools, "dim_tech_tools")
        load_clean_data(engine_dm, dim_job_satisfaction, "dim_job_satisfaction")
        load_clean_data(engine_dm, dim_miscellaneous, "dim_miscellaneous")
        load_clean_data(engine_dm, fact_table, "fact_table")
        
        logging.info(f"Todas las tablas se cargaron exitosamente en {database_name_for_log}.")
        
    except Exception as e:

        logging.error(f"Error en loading_dimensional_model para '{database_name_for_log}': {e}")
        logging.error(f"--- Traceback para el error en loading_dimensional_model ({database_name_for_log}) ---")
        logging.error(traceback.format_exc())
        logging.error("--- Fin del Traceback ---")
        
        raise