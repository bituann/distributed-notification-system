package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.NotificationStatus;
import com.bituan.push_notification_service.dto.NotificationStatusResponse;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
public class APIGatewayService {
    @Async
    public void sendNotificationStatus (NotificationStatusResponse status) {
        // send notification status to status endpoint
        System.out.println(status);
    }

    public void updateUserToken (String userId, String token) {
        // use update endpoint to update user token
        System.out.println(token);
    }
}
