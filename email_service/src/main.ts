import { NestFactory } from '@nestjs/core';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { AppModule } from './app.module';
import { setupRabbitMQ } from './bootstrap/rabbitmq.setup';

async function bootstrap() {
  await setupRabbitMQ();

  const app = await NestFactory.createMicroservice<MicroserviceOptions>(
    AppModule,
    {
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
    },
  );
  await app.listen();
  console.log('Email Service listening to email.queue');
}
bootstrap();
