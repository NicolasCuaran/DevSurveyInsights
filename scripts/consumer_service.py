from kafka import KafkaConsumer
from json import loads
from dotenv import load_dotenv
import os
import logging
import threading # Para ejecutar el consumidor en un hilo separado
import uvicorn # Servidor ASGI para FastAPI
from fastapi import FastAPI
import pandas as pd # Para manejar los datos en formato tabular
from typing import List, Dict, Any

# --- Configuración del Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

load_dotenv()

# --- Almacenamiento en Memoria para los Mensajes de Kafka ---
# Esta lista almacenará todos los mensajes recibidos.
# En un entorno de producción, considera una base de datos o un sistema de caché más robusto.
received_messages: List[Dict[Any, Any]] = []
data_lock = threading.Lock() # Para asegurar el acceso seguro a received_messages

# --- Lógica del Consumidor de Kafka ---
def create_kafka_consumer(topic_name: str, bootstrap_server: List[str]):
    logging.info(f"Creando KafkaConsumer para topic '{topic_name}', server '{bootstrap_server}'")
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=bootstrap_server,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: loads(m.decode('utf-8')),
        )
        return consumer
    except Exception as e:
        logging.error(f"Error al crear KafkaConsumer: {e}", exc_info=True)
        raise

def process_and_store_message(message_value: Any):
    """
    Procesa el mensaje y lo almacena en la lista global.
    Maneja tanto mensajes individuales como lotes de mensajes.
    """
    global received_messages
    if not isinstance(message_value, list):
        # Si no es una lista, asumimos que es un único registro y lo envolvemos en una lista
        logging.warning(f"El valor del mensaje no es una lista. Envolviendo: {type(message_value)}, Valor: {message_value}")
        records_to_process = [message_value]
    else:
        records_to_process = message_value

    if not records_to_process:
        logging.info("Mensaje (lote) recibido está vacío, no hay registros individuales que procesar.")
        return

    num_records_in_batch = len(records_to_process)
    logging.info(f"Procesando lote con {num_records_in_batch} registro(s):")

    new_records_for_storage = []
    for index, record in enumerate(records_to_process):
        logging.info(f"  Registro Lote [{index + 1}/{num_records_in_batch}]: {record}")
        if isinstance(record, dict): # Asegurarse de que el registro sea un diccionario
            new_records_for_storage.append(record)
        else:
            logging.warning(f"  Registro Lote [{index + 1}/{num_records_in_batch}] no es un diccionario y será omitido: {record}")

    if new_records_for_storage:
        with data_lock:
            received_messages.extend(new_records_for_storage)
        logging.info(f"{len(new_records_for_storage)} registro(s) añadido(s) al almacenamiento en memoria.")

def run_kafka_consumer_thread(topic_name: str = "DevSurveyKafkaTopic", kafka_server: List[str] = ['localhost:9092']):
    consumer = None
    try:
        consumer = create_kafka_consumer(topic_name, bootstrap_server=kafka_server)
        logging.info(f"Consumidor iniciado en un hilo y escuchando en el topic '{topic_name}'.")

        for message in consumer:
            logging.info(f"--- Mensaje de Kafka recibido --- Partition: {message.partition}, Offset: {message.offset} ---")
            process_and_store_message(message.value)
            logging.info(f"--- Fin del procesamiento del mensaje (Offset: {message.offset}) ---")

    except KeyboardInterrupt:
        logging.info("Interrupción por teclado detectada en el hilo del consumidor.")
    except Exception as e:
        logging.error(f"Error crítico en el bucle del consumidor (hilo): {e}", exc_info=True)
    finally:
        if consumer:
            logging.info("Cerrando el consumidor de Kafka (hilo).")
            consumer.close()
            logging.info("Consumidor de Kafka cerrado (hilo).")

# --- API con FastAPI ---
app = FastAPI(
    title="Kafka Consumer API",
    description="API para exponer datos consumidos de un topic de Kafka.",
    version="1.0.0"
)

@app.get("/data", summary="Obtener datos de Kafka", description="Devuelve todos los mensajes recibidos por el consumidor de Kafka hasta el momento.")
async def get_kafka_data() -> List[Dict[Any, Any]]:
    """
    Endpoint para obtener los datos almacenados.
    Devuelve los datos como una lista de diccionarios (registros).
    """
    try:
        with data_lock:
            # Crear una copia para evitar problemas de concurrencia si la lista se modifica mientras se lee
            data_copy = list(received_messages)

        if not data_copy:
            logging.info("API: No hay datos disponibles para enviar.")
            return []

        # Opcional: Si siempre esperas una estructura de DataFrame y quieres devolverlo como JSON orientado a registros
        # df = pd.DataFrame(data_copy)
        # response_data = df.to_dict(orient='records')

        response_data = data_copy # Devuelve la lista de diccionarios directamente

        logging.info(f"API: Enviados {len(response_data)} mensajes.")
        return response_data
    except Exception as e:
        logging.error(f"API Error al obtener datos: {e}", exc_info=True)
        return {"error": str(e)}

@app.get("/health", summary="Chequeo de salud", description="Verifica si la API está funcionando.")
async def health_check():
    return {"status": "API funcionando correctamente"}

# --- Punto de Entrada Principal ---
if __name__ == "__main__":
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "DevSurveyKafkaTopic")
    KAFKA_SERVER_STR = os.getenv("KAFKA_SERVER", "localhost:9092")
    KAFKA_SERVER_LIST = [s.strip() for s in KAFKA_SERVER_STR.split(',')] # Permite múltiples servidores separados por coma

    logging.info(f"Iniciando la aplicación...")
    logging.info(f"Topic de Kafka: {KAFKA_TOPIC}")
    logging.info(f"Servidores de Kafka: {KAFKA_SERVER_LIST}")

    # Iniciar el consumidor de Kafka en un hilo separado
    consumer_thread = threading.Thread(
        target=run_kafka_consumer_thread,
        args=(KAFKA_TOPIC, KAFKA_SERVER_LIST),
        daemon=True  # El hilo del consumidor terminará cuando el hilo principal termine
    )
    consumer_thread.start()
    logging.info("Hilo del consumidor de Kafka iniciado.")

    # Iniciar el servidor FastAPI
    # Puedes cambiar 'host' y 'port' según tus necesidades
    # host="0.0.0.0" permite acceso desde otras máquinas en la red
    logging.info("Iniciando servidor FastAPI con Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")