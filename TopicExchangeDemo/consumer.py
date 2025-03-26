import pika
import logging
from retry import retry

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def on_message_A(ch, method, properties, body):
    logging.info("Queue: %r - Routing key: %r - Received %r" % ("berlin_agreements", method.routing_key, body))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def on_message_B(ch, method, properties, body):
    logging.info("Queue: %r - Routing key: %r - Received %r" % ("all_agreements", method.routing_key, body))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def on_message_C(ch, method, properties, body):
    logging.info("Queue: %r - Routing key: %r - Received %r" % ("store_agreements", method.routing_key, body))
    ch.basic_ack(delivery_tag=method.delivery_tag)

@retry(tries=10, delay=1, backoff=2, max_delay=10)
def establish_connection():
    """Establish connection to RabbitMQ with retry logic"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host="rabbitmq",
        port=8009,
        virtual_host="/",
        credentials=pika.PlainCredentials("datlt4", "Hz8k76Wj5qQrqkV"),
        socket_timeout=5))
    logging.info("Connected successfully!")
    return connection

def main():
    # Establish connection and channel
    connection = establish_connection()
    channel = connection.channel()
    
    # Exchange and queue details
    exchange_name = "agreements"

    # Declare the exchange (topic type in this example)
    channel.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

    # Routing key and queue name
    routing_key_A = "agreements.eu.berlin.#"
    queue_name_A = "berlin_agreements"  # Assuming this is the bound queue name
    # Declare the queue
    # Bind the queue to the exchange using the routing key
    channel.queue_declare(queue=queue_name_A, durable=True)
    channel.queue_bind(queue=queue_name_A, exchange=exchange_name, routing_key=routing_key_A)
    # Set up basic consumption on the queue
    channel.basic_consume(queue=queue_name_A, on_message_callback=on_message_A)

    logging.info("Waiting for messages on queue: %s" % queue_name_A)

    # Routing key and queue name
    routing_key_B = "agreements.#"
    queue_name_B = "all_agreements"  # Assuming this is the bound queue name
    # Declare the queue
    # Bind the queue to the exchange using the routing key
    channel.queue_declare(queue=queue_name_B, durable=True)
    channel.queue_bind(queue=queue_name_B, exchange=exchange_name, routing_key=routing_key_B)
    # Set up basic consumption on the queue
    channel.basic_consume(queue=queue_name_B, on_message_callback=on_message_B)

    logging.info("Waiting for messages on queue: %s" % queue_name_B)

    # Routing key and queue name
    routing_key_C = "agreements.eu.*.store"
    queue_name_C = "store_agreements"  # Assuming this is the bound queue name
    # Declare the queue
    # Bind the queue to the exchange using the routing key
    channel.queue_declare(queue=queue_name_C, durable=True)
    channel.queue_bind(queue=queue_name_C, exchange=exchange_name, routing_key=routing_key_C)
    # Set up basic consumption on the queue
    channel.basic_consume(queue=queue_name_C, on_message_callback=on_message_C)

    logging.info("Waiting for messages on queue: %s" % queue_name_C)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("Stopping consumption...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == '__main__':
    main()
