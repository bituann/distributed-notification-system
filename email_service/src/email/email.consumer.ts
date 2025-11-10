import { Controller, Logger } from '@nestjs/common';
import { Ctx, EventPattern, Payload, RmqContext } from '@nestjs/microservices';
import { EmailService } from './email.service';
import { RetryHandler } from '../email/utils/retry.utils';

@Controller()
export class EmailConsumer {
  private readonly logger = new Logger(EmailConsumer.name);
  private retryHandler = new RetryHandler();

  constructor(private readonly emailService: EmailService) {}

  @EventPattern('send_email')
  async handleEmail(@Payload() data: any, @Ctx() context: RmqContext) {
    const channel = context.getChannelRef();
    const msg = context.getMessage();

    try {
      await this.emailService.sendEmail(data);
      channel.ack(msg);
    } catch (err) {
      this.logger.error(`Email failed: ${err.message}`);
      const shouldRetry = await this.retryHandler.handleRetry(channel, msg);
      if (!shouldRetry) {
        this.logger.warn('Moving message to dead-letter queue');
        channel.ack(msg);
      }
    }
  }
}
