from database.db_operations import creating_engine

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")

## ----- DB Extract ----- ##

def extraction_from_db():
    """
    Extracting data from the table and return it as a DataFrame.   

    """
    engine = creating_engine()
    
    try:
        logging.info("Starting to extract the data from the table.")
        df = pd.read_sql_table("clean_survey", engine)
        logging.info("Data extracted from the DevSurvey table.")
        
        return df
    except Exception as e:
        logging.error(f"Error extracting data from the DevSurvey table: {e}.")
