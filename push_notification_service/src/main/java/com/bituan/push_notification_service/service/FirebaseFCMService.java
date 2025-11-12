package com.bituan.push_notification_service.service;

import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.FirebaseMessagingException;
import com.google.firebase.messaging.Message;
import com.google.firebase.messaging.Notification;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class FirebaseFCMService {
    private final FirebaseMessaging firebaseMessaging;

    @Autowired
    FirebaseFCMService (FirebaseMessaging firebaseMessaging) {
        this.firebaseMessaging = firebaseMessaging;
    }

    @Async
    public  void pushNotification (String token, Notification notification, String notificationId) {
        Message message = Message.builder().setToken(token).setNotification(notification).build();
        try {
            firebaseMessaging.send(message);
        } catch (FirebaseMessagingException e) {
            throw new RuntimeException(e);
        }
    }
}
