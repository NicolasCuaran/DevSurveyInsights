from kafka import KafkaProducer
from json import dumps
from dotenv import load_dotenv
import io
import logging
import time
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")

def create_kafka_producer():
    return KafkaProducer(
        value_serializer=lambda m: dumps(m).encode('utf-8'),
        bootstrap_servers=['kafka:29092'],
    )

def send_in_batches(producer, data_json_string, batch_size=1000, topic_name="DevSurveyKafkaTopic"):
    """
    Send data to Kafka one record per second.
    
    Parameters:
        producer (KafkaProducer): The Kafka producer instance.
        data_json_string (str): The JSON string representing the DataFrame to be sent.
        batch_size (int): Ignored, kept for compatibility.
        topic_name (str): The Kafka topic to send messages to.
    """
    try:
        data = pd.read_json(io.StringIO(data_json_string), orient="records")
    except ValueError as e:
        logging.error(f"Error reading JSON string into DataFrame: {e}")
        logging.error(f"Problematic JSON string (first 500 chars): {data_json_string[:500]}")
        raise
        
    if data.empty:
        logging.info("DataFrame is empty. Nothing to send.")
        return

    for i in range(len(data)):
        record = data.iloc[i:i + 1].to_dict(orient='records')[0]
        producer.send(topic_name, value=record)
        producer.flush()
        logging.info(f"Record sent to topic '{topic_name}': 1 record.")
        logging.info(f"Record content: {record}")
        time.sleep(1)

def kafka_producer_fact_table(fact_table_json_string: str, topic: str = "DevSurveyKafkaTopic"):
    producer = None
    try:
        producer = create_kafka_producer()
        logging.info(f"Kafka producer created. Sending data to topic: {topic}")
        send_in_batches(producer, fact_table_json_string, topic_name=topic)
        logging.info(f"All data from fact table successfully sent to Kafka topic '{topic}'")
        return f"Fact table data sent to Kafka topic '{topic}'"
    except Exception as e:
        logging.error(f"Error during Kafka production for topic '{topic}': {e}", exc_info=True)
        return None
    finally:
        if producer:
            producer.close()
            logging.info("Kafka producer closed.")