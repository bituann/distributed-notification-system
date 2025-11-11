package com.bituan.push_notification_service.service;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Service;

@Service
public class MessageConsumer {
    @RabbitListener(queues = {"${rabbitmq.queue.name}"})
    public void consume (String message) {
        System.out.printf("Message received -> %s%n", message);
    }
}
