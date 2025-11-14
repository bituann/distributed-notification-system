package com.bituan.push_notification_service.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;


@Configuration
public class RabbitMQConfig {
    @Value("${rabbitmq.queue.name}")
    private String queue;

    @Value("${rabbitmq.dead.queue.name}")
    private String deadQueue;

    @Value("${rabbitmq.exchange.name}")
    private String exchange;

    @Value("${rabbitmq.routing.key}")
    private String routingKey;

    @Value("${rabbitmq.dead.routing.key}")
    private String deadRoutingKey;

    @Value("${rabbitmq.max.priority}")
    private int maxPriority;


    @Bean
    public Queue queue() {
        return QueueBuilder.durable(queue)
                .withArgument("x-max-priority", maxPriority)
                .build();
    }

    @Bean
    public Queue deadQueue() {
        return new Queue(deadQueue);
    }

    @Bean
    public DirectExchange exchange () {
        return ExchangeBuilder
                .directExchange(exchange)
                .durable(false)
                .build();
    }

    @Bean
    public Binding binding () {
        return BindingBuilder
                .bind(queue())
                .to(exchange())
                .with(routingKey);
    }

    @Bean
    public Binding deadQueueBinding () {
        return BindingBuilder
                .bind(deadQueue())
                .to(exchange())
                .with(deadRoutingKey);
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
}
