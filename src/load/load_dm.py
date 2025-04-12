from database.db_operations import creating_engine, load_clean_data
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")

def loading_dimensional_model(dimension_1, dimension_2, dimension_3, dimension_4, dimension_5, fact_table):
    try:
        engine = creating_engine()
        
        load_clean_data(engine, dimension_1, "dimension_1")
        load_clean_data(engine, dimension_2, "dimension_2")
        load_clean_data(engine, dimension_3, "dimension_3")
        load_clean_data(engine, dimension_4, "dimension_4")
        load_clean_data(engine, dimension_5, "dimension_5")
        load_clean_data(engine, fact_table, "fact_table")
        
        logging.info("All tables loaded successfully.")
        
    except Exception as e:
        logging.error(f"Error loading data into database: {e}")