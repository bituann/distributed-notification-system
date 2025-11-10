import {
  ClientProxy,
  ClientProxyFactory,
  Transport,
} from '@nestjs/microservices';

export class StatusPublisher {
  private client: ClientProxy;

  constructor() {
    this.client = ClientProxyFactory.create({
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
      },
    });
  }

  async publishDelivered(notification_id: string) {
    const payload = {
      notification_id,
      status: 'delivered',
      timestamp: new Date().toISOString(),
      error: null,
    };

    return this.client.emit('notification_status', payload).toPromise();
  }

  async publishFailed(notification_id: string, error: string) {
    const payload = {
      notification_id,
      status: 'failed',
      timestamp: new Date().toISOString(),
      error,
    };
    return this.client.emit('notification_status', payload).toPromise();
  }
}
