import pika
import uuid  
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from .serializers import NotificationRequestSerializer
from dotenv import load_dotenv
import os
load_dotenv()

USER_SERVICE_URL = "https://user-service-cool-morning-1264.fly.dev/api/v1/users/"

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

@api_view(['POST'])
def signup_gateway(request):

    try:
        # Forward the request data to User Service
        r = requests.post(USER_SERVICE_URL, json=request.data)
        r.raise_for_status()  # Raise error if status code >= 400
        return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        # If User Service is down or request failed
        return Response(
            {"error": "User Service unreachable or invalid data/user already exists", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )



USER_SERVICE_URL = "https://user-service-cool-morning-1264.fly.dev/api/v1/users/"

RABBITMQ_URL = os.getenv("RABBITMQ_URL")


MAX_PRIORITY = 10  # Maximum priority for queues


def get_rabbitmq_channel():
    """Create and return a RabbitMQ channel with exchanges and queues including priority support."""
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare exchange
    channel.exchange_declare(exchange='notifications.direct', exchange_type='direct')

    # Declare queues with max priority
    queues = ['email.queue', 'push.queue', 'failed.queue']
    for queue in queues:
        channel.queue_declare(
            queue=queue,
            durable=True,
            arguments={'x-max-priority': MAX_PRIORITY} if queue != 'failed.queue' else None
        )
        # Bind queues to the exchange
        routing_key = queue.split('.')[0] if queue != 'failed.queue' else 'failed'
        channel.queue_bind(exchange='notifications.direct', queue=queue, routing_key=routing_key)

    return connection, channel



@api_view(['POST'])
def create_notification(request):
    serializer = NotificationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "success": False,
            "message": "Invalid request data",
            "error": serializer.errors,
            "data": None,
            "meta": None
        }, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user_id = data.get("user_id")
    message_text = data.get("message", "")
    priority = data.get("priority", 0)  # default priority 0
    template_code = data.get("template_code")

    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Fetch user info from User Service
    try:
        r = requests.get(f"{USER_SERVICE_URL}{user_id}/")
        r.raise_for_status()
        user_info = r.json()
    except requests.RequestException:
        return Response({
            "success": False,
            "message": "User Service unreachable or user not found",
            "error": "User not found",
            "data": None,
            "meta": None
        }, status=status.HTTP_400_BAD_REQUEST)

    preferences = user_info.get("preferences", {})
    email_pref = preferences.get("email", False)
    push_pref = preferences.get("push", False)

    # Include request_id in message
    message = {
        "request_id": request_id,
        "user_id": str(user_id),
        "email": user_info.get("email"),
        "push_token": user_info.get("push_token"),
        "message": message_text,
        "priority": priority,
        "template_code": template_code
    }

    try:
        connection, channel = get_rabbitmq_channel()

        if email_pref:
            channel.basic_publish(
                exchange='notifications.direct',
                routing_key='email',
                body=json.dumps({**message, "type": "email"}),
                properties=pika.BasicProperties(delivery_mode=2, priority=priority)
            )
        if push_pref:
            channel.basic_publish(
                exchange='notifications.direct',
                routing_key='push',
                body=json.dumps({**message, "type": "push"}),
                properties=pika.BasicProperties(delivery_mode=2, priority=priority)
            )
        if not email_pref and not push_pref:
            channel.basic_publish(
                exchange='notifications.direct',
                routing_key='failed',
                body=json.dumps({**message, "type": "none", "error": "No preferences enabled"}),
                properties=pika.BasicProperties(delivery_mode=2)
            )

        connection.close()

    except Exception as e:
        try:
            connection, channel = get_rabbitmq_channel()
            channel.basic_publish(
                exchange='notifications.direct',
                routing_key='failed',
                body=json.dumps({**message, "error": str(e)}),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
        except:
            pass

        return Response({
            "success": False,
            "message": "Failed to queue message",
            "error": str(e),
            "data": None,
            "meta": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "success": True,
        "message": "Notification(s) queued successfully",
        "error": None,
        "data": {
            "request_id": request_id,
            "user_preferences": preferences,
            "queued": {"email": email_pref, "push": push_pref},
            "notification": message,
            "user_info": user_info
        },
        "meta": None
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint.
    Returns 200 OK if service is running.
    """
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

