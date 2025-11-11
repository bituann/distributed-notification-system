import { Controller, Get } from '@nestjs/common';
import * as amqp from 'amqplib';
import { redisClient } from '../utils/redis.utils';
import * as nodemailer from 'nodemailer';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('health')
@Controller('health')
export class HealthController {
  @Get()
  @ApiOperation({ summary: 'Check service health' })
  @ApiResponse({ status: 200, description: 'Service health status' })
  async getHealth() {
    const meta: any = { smtp: false, redis: false, rabbitmq: false };

    try {
      const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
      });
      await transporter.verify();
      meta.smtp = true;
    } catch {
      meta.smtp = false;
    }

    try {
      const pong = await redisClient.ping();
      meta.redis = pong === 'PONG';
    } catch {
      meta.redis = false;
    }

    try {
      const url = process.env.RABBITMQ_URL || 'amqp://rabbitmq:5672';
      const conn = await amqp.connect(url);
      const ch = await conn.createChannel();
      await ch.close();
      await conn.close();
      meta.rabbitmq = true;
    } catch {
      meta.rabbitmq = false;
    }

    const success = meta.smtp && meta.redis && meta.rabbitmq;
    return {
      success,
      message: success ? 'ok' : 'degraded',
      meta,
    };
  }
}
