package com.bituan.push_notification_service.dto;

import lombok.Data;

@Data
public class Message {
    private NotificationType notificationType;
    private String userId;
    private String templateCode;
    private String requestId;
    private int priority;
    private Metadata metadata;
}
