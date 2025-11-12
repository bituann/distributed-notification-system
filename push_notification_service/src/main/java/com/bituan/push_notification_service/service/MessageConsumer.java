package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.Message;
import com.google.firebase.messaging.Notification;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class MessageConsumer {

    private UserService userService;
    private FirebaseFCMService firebaseFCMService;

    @Autowired
    MessageConsumer(UserService userService, FirebaseFCMService firebaseFCMService) {
        this.userService = userService;
        this.firebaseFCMService = firebaseFCMService;
    }

    @RabbitListener(queues = {"${rabbitmq.queue.name}"})
    public void consume (Message message) {
        // get device token
        String token = userService.getUserById(message.getUserId()).getPushToken();
        // get template
        // create notification id
        String notificationId = message.getRequestId();
        // create notification
        Notification notification = Notification.builder()
                .setTitle("Title")
                .setBody("Body")
                .setImage("Image Link")
                .build();
        // push notification
        firebaseFCMService.pushNotification(token, notification, notificationId);
    }
}
