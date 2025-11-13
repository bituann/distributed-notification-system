import { Controller, Logger } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import {
  emailsSent,
  emailsFailed,
  emailsBounced,
} from '../metrics/metrics.controller';

@Controller()
export class StatusConsumer {
  private readonly logger = new Logger(StatusConsumer.name);

  @EventPattern('email')
  async handleEmail(@Payload() data: any) {
    this.logger.log(`Got email notification: ${JSON.stringify(data)}`);
    emailsSent.inc();
  }

  @EventPattern('push')
  async handlePush(@Payload() data: any) {
    this.logger.log(`Got push notification: ${JSON.stringify(data)}`);
  }

  @EventPattern('failed')
  async handleFailed(@Payload() data: any) {
    this.logger.warn(`Got failed notification: ${JSON.stringify(data)}`);
    const { notification_id, error } = data;

    if (
      /user unknown|mailbox unavailable|invalid recipient|no such user/i.test(
        error || '',
      )
    ) {
      emailsBounced.inc();
      this.logger.warn(`Incremented emailsBounced for ${notification_id}`);
    } else {
      emailsFailed.inc();
      this.logger.warn(`Incremented emailsFailed for ${notification_id}`);
    }
  }
}
