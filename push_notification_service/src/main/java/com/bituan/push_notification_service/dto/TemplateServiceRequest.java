package com.bituan.push_notification_service.dto;

import lombok.Data;

import java.util.Map;

@Data
public class TemplateServiceRequest {
    private String name;
    private Map<String, Object> context;
    private String language;
    private String category;
}
