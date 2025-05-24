from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, Float, String, DateTime, inspect, MetaData, Table, Column, BIGINT
from sqlalchemy_utils import database_exists, create_database

import os
import logging
import traceback
import warnings

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

route = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(route)

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

def creating_engine(database_name=database):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}"
    engine = None 
    
    try:
        engine = create_engine(url)
        db_existe_antes = database_exists(url)
        if not db_existe_antes:
            create_database(url)
            logging.info(f"Base de datos {database_name} creada exitosamente.")
        else:
            logging.info(f"Base de datos {database_name} ya existente.")
            
    except Exception as e:
        logging.error("Ocurrió un error durante la creación del motor o la base de datos:")
        logging.error(traceback.format_exc())
        
    return engine


def _infer_sqlalchemy_type(dtype, column_name):
    if column_name == "eventid":
        return BIGINT
    elif "datetime" in dtype.name: 
        return DateTime
    elif "int" in dtype.name:
        return Integer
    elif "float" in dtype.name:
        return Float
    elif "object" in dtype.name:
        return String(500)
    else:
        return String(500)

def load_clean_data(engine, df, table_name, primary_key="id"):
    logging.info(f"Intentando crear/cargar la tabla '{table_name}' desde el DataFrame.")

    if engine is None:
        logging.error(f"El motor de base de datos es None. No se puede cargar la tabla '{table_name}'.")
        return

    inspector = inspect(engine)
    
    if inspector.has_table(table_name):
        original_warn_format = warnings.formatwarning
        warnings.formatwarning = lambda message, category, filename, lineno, line=None: f'{filename}:{lineno}: {category.__name__}: {message}\n'
        warnings.warn(f"Advertencia: La tabla '{table_name}' ya existe en la base de datos. No se tomarán acciones de creación de esquema o carga de datos duplicados si 'if_exists' no es 'append'.", UserWarning)
        warnings.formatwarning = original_warn_format
        
        logging.info(f"La tabla '{table_name}' ya existe. No se realizarán operaciones de carga de datos.")

    else:
        logging.info(f"La tabla '{table_name}' no existe. Procediendo a crearla...")
        metadata_obj = MetaData()

        lista_columnas = []
        for name, dtype in df.dtypes.items():
            es_pk = (name == primary_key)
            col_type = _infer_sqlalchemy_type(dtype, name)
            lista_columnas.append(Column(name, col_type, primary_key=es_pk))

        table = Table(table_name, metadata_obj, *lista_columnas)
        
        try:
            metadata_obj.create_all(engine, tables=[table])
            logging.info(f"Esquema para la tabla '{table_name}' creado correctamente.")
        except Exception as e_create:
            logging.error(f"Error al crear el esquema de la tabla '{table_name}': {e_create}")
            logging.error(traceback.format_exc())
            return 

        try:
            df.to_sql(table_name, con=engine, if_exists="append", index=False)
            logging.info(f"Datos cargados exitosamente en la tabla '{table_name}'.")
        except Exception as e_load:
            logging.error(f"Error al cargar datos en la tabla '{table_name}': {e_load}")
            logging.error(traceback.format_exc())