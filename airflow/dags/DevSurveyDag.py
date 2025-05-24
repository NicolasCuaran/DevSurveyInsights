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
    def extract_from_db():
        return extract_db_data()
    
    @task
    def validate_db_data(db_df):
        return validate_db_data_task(db_df)
        
    @task
    def extract_from_api():
        return extract_api_data(target_repos=100)
    
    @task
    def validate_api_data(api_df):
        return validate_api_data_task(api_df)
    
    @task
    def transform_api(raw_api_df):
        return transform_api_data_task(raw_api_df)
    
    @task
    def merge(df_db, df_api):
        return merge_data_task(df_db, df_api)
    
    @task
    def transform_dm(df):
        
        data = transform_dm_task(df)
        
        return {
            'dim_demographic': data[0],
            'dim_professional_experience': data[1],
            'dim_tech_tools': data[2],
            'dim_job_satisfaction': data[3],
            'dim_miscellaneous': data[4],
            'fact_table': data[5]
        }
    
    @task
    def load(df):
        
        dim_demographic = df['dim_demographic']
        dim_professional_experience = df['dim_professional_experience']
        dim_tech_tools = df['dim_tech_tools']
        dim_job_satisfaction = df['dim_job_satisfaction']
        dim_miscellaneous = df['dim_miscellaneous']
        fact_table = df['fact_table']
        
        load_data_task(dim_demographic, dim_professional_experience, dim_tech_tools, dim_job_satisfaction, dim_miscellaneous, fact_table)
        
        return fact_table
    
    @task
    def kafka_producer(fact_table_json_string):
        kafka_producer_fact_table(fact_table_json_string)

    db_data = extract_from_db()    
    api_data = extract_from_api()

    db_validated_data = validate_db_data(db_data)
    api_validated_data = validate_api_data(api_data)
    
    api_transformed = transform_api(api_validated_data)
    
    merged_data = merge(db_validated_data, api_transformed)
    
    dimensional_model = transform_dm(merged_data)
    
    fact_table = load(dimensional_model)
    
    kafka_producer(fact_table)

    
dev_survey_dag = dev_survey_dag()