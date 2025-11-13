from django.test import TestCase

# Create your tests here.
# rabbitmq_check.py
import pika
import os
import json
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MAX_PRIORITY = 10

def main():
    # Connect to RabbitMQ
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Check the exchange
    try:
        channel.exchange_declare(exchange='notifications.direct', passive=True)
        print("Exchange 'notifications.direct' exists.")
    except Exception as e:
        print("Error checking exchange:", e)

    # Check queues
    queues = ['email.queue', 'push.queue', 'failed.queue']
    for q in queues:
        try:
            info = channel.queue_declare(queue=q, passive=True)
            print(f"Queue '{q}' exists:", info)
        except Exception as e:
            print(f"Error checking queue '{q}':", e)

    # Test publishing a message to email.queue
    try:
        test_message = {"test": "hello"}
        channel.basic_publish(
            exchange='notifications.direct',
            routing_key='email',
            body=json.dumps(test_message),
            properties=pika.BasicProperties(delivery_mode=2, priority=1)
        )
        print("Test message sent to 'email.queue'.")
    except Exception as e:
        print("Error sending test message:", e)

    connection.close()

if __name__ == "__main__":
    main()
