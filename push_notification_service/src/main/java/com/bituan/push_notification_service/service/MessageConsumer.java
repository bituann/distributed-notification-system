package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class MessageConsumer {

    private UserService userService;

    @Autowired
    MessageConsumer(UserService userService) {
        this.userService = userService;
    }

    @RabbitListener(queues = {"${rabbitmq.queue.name}"})
    public void consume (Message message) {
        System.out.printf("Message received -> %s%n", message);
    }
}
