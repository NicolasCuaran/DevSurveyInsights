from datetime import datetime, timedelta
from airflow.decorators import dag, task

from tasks_flow import *

default_args = {
    'owner': "airflow",
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email': "example@example.com",
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

@dag(
    default_args=default_args,
    description='Pipeline - DevSurveyInsights',
    schedule=timedelta(days=1),
    max_active_runs=1,
    catchup=False,
    concurrency=4,
)

def dev_survey_dag():

    @task 
    def extract_from_db_task():
        return extract_db_data()
        
    # @task
    # def extract_from_api_task():
    #     pass
    
    # @task
    # def transform_api_task(raw_api_df):
    #     pass
    
    # @task
    # def merge_task(df_db, df_api):
    #     pass
    
    @task
    def transform_dm_task(df):
        
        data = transform_dm(df)
        
        return {
            'dimension_1': data[0],
            'dimension_2': data[1],
            'dimension_3': data[2],
            'dimension_4': data[3],
            'dimension_5': data[4],
            'fact_table': data[5]
        }
    
    @task
    def load_task(df):
        
        dimension_1 = df['dimension_1']
        dimension_2 = df['dimension_2']
        dimension_3 = df['dimension_3']
        dimension_4 = df['dimension_4']
        dimension_5 = df['dimension_5']
        fact_table = df['fact_table']
        
        load_data(dimension_1, dimension_2, dimension_3, dimension_4, dimension_5, fact_table)
        
        return fact_table

    db_data = extract_from_db_task()
    # api_data = extract_from_api_task()
    
    # api_transformed = transform_api_task(api_data)
    
    # merged_data = merge_task(db_data, api_transformed)
    
    # dimensional_model = transform_dm_task(merged_data)
    dimensional_model = transform_dm_task(db_data)
    
    loaded_data = load_task(dimensional_model)

    
dev_survey_dag = dev_survey_dag()