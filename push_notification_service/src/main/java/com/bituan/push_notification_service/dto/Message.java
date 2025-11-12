package com.bituan.push_notification_service.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Data;

@Data
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class Message {
    private NotificationType notificationType;
    private String userId;
    private String templateCode;
    private UserData variables;
    private String requestId;
    private int priority;
    private Metadata metadata;
}
