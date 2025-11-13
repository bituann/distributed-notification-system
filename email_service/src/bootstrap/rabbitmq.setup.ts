import * as amqp from 'amqplib';

export async function setupRabbitMQ() {
  const url = process.env.RABBITMQ_URL || 'amqp://rabbitmq:5672';
  const EXCHANGE = 'notifications.direct';
  const EMAIL_QUEUE = 'email.queue';
  const PUSH_QUEUE = 'push.queue';
  const FAILED_QUEUE = 'failed.queue';
  const MAX_PRIORITY = 10;

  const conn = await amqp.connect(url);
  const ch = await conn.createChannel();

  await ch.assertExchange(EXCHANGE, 'direct', { durable: false });

  await ch.assertQueue(EMAIL_QUEUE, {
    durable: true,
    arguments: { 'x-max-priority': MAX_PRIORITY },
  });
  await ch.assertQueue(PUSH_QUEUE, {
    durable: true,
    arguments: { 'x-max-priority': MAX_PRIORITY },
  });
  await ch.assertQueue(FAILED_QUEUE, { durable: true });

  await ch.bindQueue(EMAIL_QUEUE, EXCHANGE, 'email');
  await ch.bindQueue(PUSH_QUEUE, EXCHANGE, 'push');
  await ch.bindQueue(FAILED_QUEUE, EXCHANGE, 'failed');

  console.log('RabbitMQ setup complete');

  await ch.close();
  await conn.close();
}
