package com.bituan.push_notification_service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.retry.annotation.EnableRetry;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
@EnableRetry
public class PushNotificationServiceApplication {
	public static void main(String[] args) {
		SpringApplication.run(PushNotificationServiceApplication.class, args);
	}
}
