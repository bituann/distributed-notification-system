package com.bituan.push_notification_service.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Data;

@Data
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class Message {
    private NotificationType type;
    private String userId;
    private String requestId;
    private String email;
    private String pushToken;
    private String message;
    private String templateCode;
    private int priority;
}
