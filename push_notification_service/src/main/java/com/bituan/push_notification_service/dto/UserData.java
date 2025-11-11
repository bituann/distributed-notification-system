package com.bituan.push_notification_service.dto;

import lombok.Data;

@Data
public class UserData {
    private String name;
    private String link;
    private Metadata meta;
}
