package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.*;
import com.google.firebase.messaging.Notification;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Map;

@Service
public class MessageConsumer {

    private final UserService userService;
    private final FirebaseFCMService firebaseFCMService;
    private final TemplateService templateService;
    private final APIGatewayService apiGatewayService;

    @Autowired
    MessageConsumer(UserService userService, FirebaseFCMService firebaseFCMService,
                    TemplateService templateService, APIGatewayService apiGatewayService) {
        this.userService = userService;
        this.firebaseFCMService = firebaseFCMService;
        this.templateService = templateService;
        this.apiGatewayService = apiGatewayService;

    }

    @RabbitListener(queues = {"${rabbitmq.queue.name}"})
    public void consume (Message message) {
        // get device token
        String token = userService.getUserById(message.getUserId()).getPushToken();

        // create notification id
        String notificationId = message.getRequestId();

        // get template
        TemplateServiceRequest templateServiceRequest = new TemplateServiceRequest();
        templateServiceRequest.setName(message.getTemplateCode());
        templateServiceRequest.setCategory("email");
        templateServiceRequest.setLanguage("en");
        templateServiceRequest.setContext(Map.of("user", "Tobi"));
        TemplateData template = templateService.getTemplateByName(templateServiceRequest);

        if (template == null) {
            NotificationStatusResponse response = new NotificationStatusResponse();
            response.setNotificationId(notificationId);
            response.setStatus(NotificationStatus.failed);
            response.setTimestamp(Instant.now());
            response.setError("Unable to get notification template");

            apiGatewayService.sendNotificationStatus(response);

            return;
        }

        // create notification
        Notification notification = Notification.builder()
                .setTitle("Title")
                .setBody("Body")
                .setImage("Image Link")
                .build();

        // push notification
        firebaseFCMService.pushNotification(token, notification, notificationId);

        System.out.printf("Message received -> %s%n", message);
    }
}
