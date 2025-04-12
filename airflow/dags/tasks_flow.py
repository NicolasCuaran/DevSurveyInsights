from extract.extract_db import extraction_from_db

from transform.transform_dm import dimensional_model

from load.load_dm import loading_dimensional_model

import json
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def extract_db_data():
    try:
        df = extraction_from_db()
        return df
    except Exception as e:
        logging.error(f"Error extracting data from database: {e}")
        return None

def transform_dm(df_json):
    try:
        json_data = json.loads(df_json)
        raw_df = pd.DataFrame(json_data)
        dimension_1, dimension_2, dimension_3, dimension_4, dimension_5, fact_table = dimensional_model(raw_df)
        
        return dimension_1.to_json(orient="records"),\
            dimension_2.to_json(orient="records"),\
            dimension_3.to_json(orient="records"),\
            dimension_4.to_json(orient="records"),\
            dimension_5.to_json(orient="records"),\
            fact_table.to_json(orient="records")
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        return None, None, None, None, None, None
    
def load_data(json_1, json_2, json_3, json_4, json_5, json_6):
    try:
        dimension_1 = pd.read_json(json_1, orient="records")
        dimension_2 = pd.read_json(json_2, orient="records")
        dimension_3 = pd.read_json(json_3, orient="records")
        dimension_4 = pd.read_json(json_4, orient="records")
        dimension_5 = pd.read_json(json_5, orient="records")
        fact_table = pd.read_json(json_6, orient="records")

        loading_dimensional_model(dimension_1, dimension_2, dimension_3, dimension_4, dimension_5, fact_table)
           
    except Exception as e:
        logging.error(f"Error loading data into database: {e}")