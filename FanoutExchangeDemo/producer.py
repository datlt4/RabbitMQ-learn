import time
import pika
import logging
from uuid import uuid4
from retry import retry

# Configure basic logging settings
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

@retry(tries=10, delay=1, backoff=2, max_delay=10)
def send_message(channel: str, exchange: str, routing_key: str, message:str) -> bool:
    try:
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message)
        logging.info(" [x] Sent %r" % message)
        return True
    except Exception as e:
        logging.error(f"Failed to publish message: {str(e)}")
        raise
    
@retry(tries=10, delay=1, backoff=2, max_delay=10)
def establish_connection():
    """Establish connection to RabbitMQ with retry logic"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host="rabbitmq",
        port=8009, # default 5672
        virtual_host="/",
        credentials=pika.PlainCredentials("datlt4", "Hz8k76Wj5qQrqkV"),
        socket_timeout=5))
    logging.info("Connected successfully!")
    return connection

def main():
    connection = None
    terminate_flag = False

    while not terminate_flag:
        try:
            # Establish a connection to RabbitMQ server
            logging.info("Establishing connection to RabbitMQ server")
            if not connection or connection.is_closed:
                # Connect to rabbitmq server
                connection = establish_connection()

            # Exchange and queue details
            exchange_name = "sport_news"

            # Create channel
            channel = connection.channel()
            routing_key1 = "dont_need_routing_key.A"
            routing_key2 = "dont_need_routing_key.B"
            routing_key3 = "dont_need_routing_key.C"

            # Declare exchange (if it doesn't already exist)
            channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)

            # Publish a message to the "hello" queue
            for i in range(10000000):
                if i % 3 == 0:
                    send_message(channel=channel, exchange=exchange_name, routing_key=routing_key1, message=f"Simulate message {uuid4().hex} - to {routing_key1}")
                elif i % 3 == 1:
                    send_message(channel=channel, exchange=exchange_name, routing_key=routing_key2, message=f"Simulate message {uuid4().hex} - to {routing_key2}")
                else:
                    send_message(channel=channel, exchange=exchange_name, routing_key=routing_key3, message=f"Simulate message {uuid4().hex} - to {routing_key3}")
                time.sleep(1)

        except KeyboardInterrupt:
            terminate_flag = True
        except pika.exceptions.StreamLostError as e:
            logging.error(f"Stream lost: {e}")
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Failed to connect: {e}")
        except pika.exceptions.ChannelClosedByBroker as e:
            logging.error(f"Channel closed by broker: {e}")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            if connection and not connection.is_closed:
                try:
                    connection.close()
                    logging.info("Connection closed in finally block.")
                except Exception as e:
                    logging.error(f"Error closing connection in finally: {e}")
                    time.sleep(5)

if __name__ == "__main__":
    main()
