import { redisClient } from './redis.utils';

export class RetryHandler {
  private maxRetries = 3;

  async handleRetry(channel, msg): Promise<boolean> {
    const msgId = msg.properties.messageId || msg.properties.correlationId;
    const retriesStr = (await redisClient.get(`retry:${msgId}`)) || '0';
    const retries = parseInt(retriesStr, 10);

    if (retries < this.maxRetries) {
      await redisClient.set(`retry:${msgId}`, (retries + 1).toString(), {
        EX: 3600,
      });
      const delay = Math.pow(2, retries) * 1000;

      setTimeout(() => channel.nack(msg, false, true), delay);
      return true;
    } else {
      channel.nack(msg, false, false);
      return false;
    }
  }
}
