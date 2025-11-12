package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.NotificationStatus;
import com.bituan.push_notification_service.dto.NotificationStatusResponse;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
public class APIGatewayService {
    @Async
    public void sendNotificationStatus (String notificationId) {
        NotificationStatusResponse notificationStatusResponse = new NotificationStatusResponse();
        notificationStatusResponse.setNotificationId(notificationId);
        notificationStatusResponse.setStatus(NotificationStatus.delivered);
        notificationStatusResponse.setTimestamp(Instant.now());

        // send notification status to status endpoint
    }
}
