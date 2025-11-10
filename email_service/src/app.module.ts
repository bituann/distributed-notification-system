import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { EmailService } from './email/email.service';
import { EmailConsumer } from './email/email.consumer';
import { HealthController } from './email/health/health.controller';

@Module({
  imports: [ConfigModule.forRoot({ isGlobal: true })],
  controllers: [HealthController, EmailConsumer],
  providers: [EmailService],
})
export class AppModule {}
