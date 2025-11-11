import { ClientProxyFactory, Transport } from '@nestjs/microservices';
import * as dotenv from 'dotenv';

dotenv.config();

async function sendTestEmail() {
  const client = ClientProxyFactory.create({
    transport: Transport.RMQ,
    options: {
      urls: [process.env.RABBITMQ_URL || 'amqp://localhost:5672'],
      queue: 'email.queue',
      queueOptions: {
        durable: true,
        arguments: {
          'x-dead-letter-exchange': 'notifications.direct',
          'x-dead-letter-routing-key': 'failed',
        },
      },
    },
  });

  const msg = {
    message_id: 'test123_' + Date.now(),
    recipient_email: 'noone12345@nonexistentdomain.com',
    subject: 'Test Email from NestJS',
    message: 'Hello! This is a real email test.',
  };

  try {
    await client.emit('send_email', msg).toPromise();
    console.log('Test email job sent');
  } catch (err) {
    console.error('Failed to send test email:', err);
  }
}

sendTestEmail();
