package com.bituan.push_notification_service.config;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.firebase.messaging.FirebaseMessaging;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;

import java.io.IOException;

@Configuration
public class FCMConfig {
    @Value("${firebase.config.path}")
    private String firebaseConfigPath;

    // initialize firebase app for push notification
    @Bean
    public FirebaseMessaging firebaseMessaging () {
        try {
            // possible source of error in prod. handle path appropriately then
            GoogleCredentials googleCredentials = GoogleCredentials.fromStream(new ClassPathResource(firebaseConfigPath).getInputStream());
            FirebaseOptions firebaseOptions = FirebaseOptions.builder().setCredentials(googleCredentials).build();

            FirebaseApp app = FirebaseApp.initializeApp(firebaseOptions, "push_notification_service");
            return FirebaseMessaging.getInstance(app);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
