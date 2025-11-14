package com.bituan.push_notification_service.config;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.firebase.messaging.FirebaseMessaging;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Base64;

@Configuration
public class FCMConfig {
//    @Value("${firebase.config.path}")
//    private String firebaseConfigPath;

    @Value("${firebase.config}")
    private String firebaseConfig;

    // initialize firebase app for push notification
    @Bean
    public FirebaseMessaging firebaseMessaging () {
        try {
            // prod version - use base 64 env variable rather than file path
            byte[] decodedBytes = Base64.getDecoder().decode(firebaseConfig);
            ByteArrayInputStream serviceAccount = new ByteArrayInputStream(decodedBytes);

            FirebaseOptions firebaseOptions = FirebaseOptions.builder()
                    .setCredentials(GoogleCredentials.fromStream(serviceAccount))
                    .build();

            // possible source of error in prod. handle path appropriately then
//            GoogleCredentials googleCredentials = GoogleCredentials.fromStream(new ClassPathResource(firebaseConfigPath).getInputStream());
//            FirebaseOptions firebaseOptions = FirebaseOptions.builder().setCredentials(googleCredentials).build();

            FirebaseApp app = FirebaseApp.initializeApp(firebaseOptions, "push_notification_service");
            return FirebaseMessaging.getInstance(app);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
