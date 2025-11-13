
## Description

The Email Service is a NestJS microservice responsible for sending emails in a distributed notification system. It consumes messages from RabbitMQ, fetches templates from the Template Service, sends emails via SMTP (Nodemailer), and publishes delivery status events.

## Project setup

```
- $ git clone https://github.com/your-username/distributed-notification-system-email-service.git.
- cd distributed-notification-system-email-service.
-  npm install. 
```

### Set up environment variables in a .env file:

- RABBITMQ_URL=amqp://localhost:5672
- SMTP_USER=your-email@gmail.com
- SMTP_PASS=your-app-password
- PORT=3000
- REDIS_URL
- TEMPLATE_SERVICE_URL

###  Start the NestJS service
- npm run start:dev

## Features
- RabbitMQ Integration: Consumes messages from email.queue bound to notifications.direct.

- Template Service: Fetches email templates via HTTP 

- SMTP Delivery: Uses Nodemailer with Gmail credentials.

- Circuit breaker to prevent cascading failures.

- Redis idempotency to avoid duplicate sends.

- Metrics: Tracks emailsSent, emailsFailed, and emailsBounced.

- Status Publishing: Publishes delivered or failed events back to RabbitMQ.

