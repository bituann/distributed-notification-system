package com.bituan.push_notification_service.dto;

import lombok.Data;

@Data
public class User {
    private String name;
    private String email;
    private String pushToken;
    private UserPreference userPreference;
    private String password;
}

@Data
class UserPreference {
    private boolean email;
    private boolean push;
}
