package com.bituan.push_notification_service.dto;

public class User {
    private String name;
    private String email;
    private String pushToken;
    private UserPreference userPreference;
    private String password;

    public User() {}

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public String getPushToken() {
        return pushToken;
    }

    public UserPreference getUserPreference() {
        return userPreference;
    }

    public String getPassword() {
        return password;
    }
}

class UserPreference {
    private boolean email;
    private boolean push;

    public UserPreference() {}

    public boolean isEmail() {
        return email;
    }

    public boolean isPush() {
        return push;
    }
}
