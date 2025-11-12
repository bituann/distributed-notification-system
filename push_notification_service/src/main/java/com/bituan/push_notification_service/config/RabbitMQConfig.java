package com.bituan.push_notification_service.config;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.firebase.messaging.FirebaseMessaging;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;

import java.io.IOException;

@Configuration
public class RabbitMQConfig {
    @Value("${rabbitmq.queue.name}")
    private String queue;

    @Value("${rabbitmq.exchange.name}")
    private String exchange;

    @Value("${rabbitmq.routing.key}")
    private String routingKey;

    @Value("${firebase.config.path}")
    private String firebaseConfigPath;

    @Bean
    public Queue queue() {
        return new Queue(queue);
    }

    @Bean
    public TopicExchange exchange () {
        return new TopicExchange(exchange);
    }

    @Bean
    public Binding binding () {
        return BindingBuilder
                .bind(queue())
                .to(exchange())
                .with(this.routingKey);
    }

    // configure message converter for serializing json to dto and vice versa
    @Bean
    public MessageConverter messageConverter () {
        return new Jackson2JsonMessageConverter();
    }

    // template that uses serializer
    @Bean
    public AmqpTemplate amqpTemplate (ConnectionFactory connectionFactory) {
        RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(messageConverter());

        return rabbitTemplate;
    }

    // initialize firebase app for push notification
    @Bean
    @CircuitBreaker(name="fcmService")
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
