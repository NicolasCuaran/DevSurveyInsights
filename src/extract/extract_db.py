from database.db_operations import creating_engine
import pandas as pd
import logging
import traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")

def extraction_from_db():
    engine = None
    df = None
    nombre_de_tabla = "clean_survey"

    try:
        logging.info(f"Iniciando la conexión con la base de datos para acceder a la tabla '{nombre_de_tabla}'.")
        engine = creating_engine()

        if engine is None:
            logging.error(f"No se pudo establecer la conexión (el motor es nulo) para la tabla '{nombre_de_tabla}'.")
            return None

        logging.info(f"Procediendo a leer todos los registros de la tabla '{nombre_de_tabla}'.")
        consulta_sql = f"SELECT * FROM {nombre_de_tabla}"
        df = pd.read_sql(consulta_sql, engine)
        
        logging.info(f"Se completó la extracción de la tabla '{nombre_de_tabla}'. Número de filas obtenidas: {len(df) if df is not None else 0}.")
        return df
    except Exception as e:
        logging.error(f"Ocurrió un error al intentar extraer datos de la tabla '{nombre_de_tabla}': {e}")
        logging.error(traceback.format_exc())
        return None