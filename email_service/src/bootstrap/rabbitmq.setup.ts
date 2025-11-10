import * as amqp from 'amqplib';

export async function setupRabbitMQ() {
  const url = process.env.RABBITMQ_URL || 'amqp://rabbitmq:5672';
  const EXCHANGE = 'notifications.direct';
  const EMAIL_QUEUE = 'email.queue';
  const FAILED_QUEUE = 'failed.queue';

  const conn = await amqp.connect(url);
  const ch = await conn.createChannel();

  await ch.assertExchange(EXCHANGE, 'direct', { durable: true });

  await ch.assertQueue(EMAIL_QUEUE, {
    durable: true,
    arguments: {
      'x-dead-letter-exchange': EXCHANGE,
      'x-dead-letter-routing-key': 'failed',
    },
  });

  await ch.assertQueue(FAILED_QUEUE, { durable: true });

  await ch.bindQueue(EMAIL_QUEUE, EXCHANGE, 'send_email');
  await ch.bindQueue(FAILED_QUEUE, EXCHANGE, 'failed');

  await ch.close();
  await conn.close();
}
