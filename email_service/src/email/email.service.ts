import { Injectable, Logger } from '@nestjs/common';
import * as nodemailer from 'nodemailer';
import * as handlebars from 'handlebars';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';
import { CircuitBreaker } from '../email/utils/circuit-breaker.utils';
import { redisClient } from './utils/redis.utils';
import { StatusPublisher } from './status/status.publisher';
import { classifySmtpError } from './utils/bounce.utils';

import {
  emailsSent,
  emailsFailed,
  emailsBounced,
} from './metrics/metrics.controller';

@Injectable()
export class EmailService {
  private readonly logger = new Logger(EmailService.name);
  private circuitBreaker = new CircuitBreaker();
  private statusPublisher = new StatusPublisher();
  private transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });

  async sendEmail(payload: any) {
    const idempotencyKey = payload.request_id;
    if (!this.circuitBreaker.canRequest())
      throw new Error('Circuit breaker open');

    if (await redisClient.get(`email_sent:${idempotencyKey}`)) {
      this.logger.warn('Duplicate email skipped: ' + idempotencyKey);
      return;
    }

    try {
      const templateUrl = process.env.TEMPLATE_SERVICE_URL;
      if (!templateUrl) throw new Error('TEMPLATE_SERVICE_URL not set');

      const response = await axios.get(templateUrl);
      const template = response.data?.html || '<p>{{message}}</p>';

      const compiled = handlebars.compile(template);
      const html = compiled({
        name: payload.email,
        message: payload.message,
      });

      await this.transporter.sendMail({
        from: process.env.SMTP_USER,
        to: payload.email,
        subject: payload.template_code || 'Notification',
        html,
      });

      this.logger.log(`Email sent to ${payload.email}`);
      emailsSent.inc();

      await redisClient.set(`email_sent:${idempotencyKey}`, '1', { EX: 86400 });
      this.circuitBreaker.recordSuccess();

      await this.statusPublisher.publishDelivered(idempotencyKey);
    } catch (err) {
      this.logger.error('Failed to send email', err);
      this.circuitBreaker.recordFailure();

      const { permanent, reason } = classifySmtpError(err);

      if (permanent) {
        emailsBounced.inc();
        await this.statusPublisher.publishFailed(idempotencyKey, reason);
      } else {
        emailsFailed.inc();
        await this.statusPublisher.publishFailed(idempotencyKey, reason);
      }

      throw err;
    }
  }
}
