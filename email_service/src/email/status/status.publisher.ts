import {
  ClientProxy,
  ClientProxyFactory,
  Transport,
} from '@nestjs/microservices';
import { lastValueFrom } from 'rxjs';

export class StatusPublisher {
  private client: ClientProxy;

  constructor() {
    const rmqUrl = process.env.RABBITMQ_URL;
    if (!rmqUrl) throw new Error('RABBITMQ_URL is not defined');

    this.client = ClientProxyFactory.create({
      transport: Transport.RMQ,
      options: {
        urls: [rmqUrl],
        queue: 'email.queue',
        queueOptions: {
          durable: true,
          arguments: { 'x-max-priority': 10 },
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
    return lastValueFrom(this.client.emit('notification_status', payload));
  }

  async publishFailed(notification_id: string, error: string) {
    const payload = {
      notification_id,
      status: 'failed',
      timestamp: new Date().toISOString(),
      error,
    };
    return lastValueFrom(this.client.emit('notification_status', payload));
  }
}
