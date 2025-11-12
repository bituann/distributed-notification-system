package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.NotificationStatus;
import com.bituan.push_notification_service.dto.NotificationStatusResponse;
import com.google.firebase.messaging.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Recover;
import org.springframework.retry.annotation.Retryable;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
public class FirebaseFCMService {
    private final FirebaseMessaging firebaseMessaging;
    private final APIGatewayService apiGatewayService;

    @Autowired
    FirebaseFCMService (FirebaseMessaging firebaseMessaging, APIGatewayService apiGatewayService) {
        this.firebaseMessaging = firebaseMessaging;
        this.apiGatewayService = apiGatewayService;
    }

    @Async
    @Retryable(
            maxAttempts = 5, // Maximum number of retry attempts
            backoff = @Backoff(delay = 10, multiplier = 2)
    )
    public void pushNotification (String token, Notification notification, String notificationId) {
        Message message = Message.builder().setToken(token).setNotification(notification).build();
        try {
            firebaseMessaging.send(message);
            NotificationStatusResponse response = new NotificationStatusResponse();
            response.setNotificationId(notificationId);
            response.setStatus(NotificationStatus.delivered);
            response.setTimestamp(Instant.now());

            // update notification status
            apiGatewayService.sendNotificationStatus(response);
        } catch (FirebaseMessagingException e) {
            if (e.getMessagingErrorCode() == MessagingErrorCode.UNREGISTERED) {
                //update user token to null
                apiGatewayService.updateUserToken("", null);
            } else {
                throw new RuntimeException(notificationId, e);
            }
        }
    }

    @Recover
    public void failedRetry (RuntimeException e) {
        NotificationStatusResponse response = new NotificationStatusResponse();
        response.setNotificationId(e.getMessage());
        response.setStatus(NotificationStatus.failed);
        response.setTimestamp(Instant.now());
        response.setError("Failed to send. Maximum retry reached");

        // update notification status
        apiGatewayService.sendNotificationStatus(response);
    }
}
