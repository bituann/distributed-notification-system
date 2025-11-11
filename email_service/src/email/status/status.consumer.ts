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

  @EventPattern('notification_status')
  async handleStatus(@Payload() data: any) {
    this.logger.log(`Got status update: ${JSON.stringify(data)}`);

    const { status, notification_id, error } = data;

    switch (status) {
      case 'delivered':
        emailsSent.inc();
        this.logger.log(`Incremented emailsSent for ${notification_id}`);
        break;

      case 'failed':
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
        break;

      default:
        this.logger.warn(`Unknown status: ${status} for ${notification_id}`);
    }
  }
}
