import { NestFactory } from '@nestjs/core';
import { Transport, RmqOptions } from '@nestjs/microservices';
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

  await app.listen(process.env.PORT || 3000, '0.0.0.0');
  console.log(`HTTP server running on port ${process.env.PORT || 3000}`);

  const rmqUrl = process.env.RABBITMQ_URL;
  if (!rmqUrl) throw new Error('RABBITMQ_URL is not defined');

  const microservice = app.connectMicroservice<RmqOptions>({
    transport: Transport.RMQ,
    options: {
      urls: [rmqUrl],
      queue: 'email.queue',
      queueOptions: {
        durable: true,
        arguments: { 'x-max-priority': 10 },
      },
      noAck: false,
    },
  });

  await app.startAllMicroservices();
  console.log('Email Service listening to email.queue');
}

bootstrap();
