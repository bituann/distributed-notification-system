package com.bituan.push_notification_service.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.time.Instant;

@Data
public class NotificationStatusResponse {
    private String notificationId;
    private NotificationStatus status;
    private Instant timestamp;
    private String error;
}
