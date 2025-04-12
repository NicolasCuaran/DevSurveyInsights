from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, Float, String, DateTime, inspect, MetaData, Table, Column, BIGINT
from sqlalchemy_utils import database_exists, create_database

import os
import logging
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
    engine = create_engine(url)
    
    if not database_exists(engine):
        create_database(url)
        logging.info(f"Database {database_name} created successfully.")
        
    return engine

def _infer_sqlalchemy_type(dtype, column_name):
    if column_name == "eventid":
        return BIGINT
    elif "int" in dtype.name:
        return Integer
    elif "float" in dtype.name:
        return Float
    elif "object" in dtype.name:
        return String(500)
    elif "datetime" in dtype.name:
        return DateTime
    else:
        return String(500)

def load_clean_data(engine, df, table_name, primary_key="id"):

    logging.info(f"Attempting to create/load table {table_name} from Pandas DataFrame")

    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        logging.info(f"Table {table_name} does not exist. Creating it...")
        metadata = MetaData()

        columns = [
            Column(
                name,
                _infer_sqlalchemy_type(dtype, name),
                primary_key=(name == primary_key)
            )
            for name, dtype in df.dtypes.items()
        ]

        table = Table(table_name, metadata, *columns)
        table.create(engine)
        logging.info(f"Table schema for {table_name} created.")

        try:
            df.to_sql(table_name, con=engine, if_exists="append", index=False)
            logging.info(f"Data successfully loaded into table {table_name}.")
        except Exception as e:
            logging.error(f"Error loading data into table {table_name}: {e}")

    else:
        warnings.warn(f"Table {table_name} already exists in the database. No actions taken.")