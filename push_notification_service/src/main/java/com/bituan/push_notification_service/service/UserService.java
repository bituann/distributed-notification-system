package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.User;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    public User getUserById(String id) {
        return new User("Tobi", "email", "token", null, "password");
    }
}
