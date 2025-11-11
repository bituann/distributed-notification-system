import { NestFactory } from '@nestjs/core';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { AppModule } from './app.module';
import { setupRabbitMQ } from './bootstrap/rabbitmq.setup';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

async function bootstrap() {
  await setupRabbitMQ();

  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('Email Service API')
    .setDescription('Endpoints for health, metrics, and notification status')
    .setVersion('1.0')
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api/docs', app, document);

  await app.listen(process.env.PORT || 3000);
  console.log(`HTTP server running on port ${process.env.PORT || 3000}`);

  const microservice = app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.RMQ,
    options: {
      urls: [process.env.RABBITMQ_URL || 'amqp://rabbitmq:5672'],
      queue: 'email.queue',
      queueOptions: {
        durable: true,
        arguments: {
          'x-dead-letter-exchange': 'notifications.direct',
          'x-dead-letter-routing-key': 'failed',
        },
      },
      noAck: false,
    },
  });
  await app.startAllMicroservices();
  console.log('Email Service listening to email.queue');
}
bootstrap();
