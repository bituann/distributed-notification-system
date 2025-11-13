package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.TemplateData;
import com.bituan.push_notification_service.dto.TemplateServiceResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class TemplateService {
    public TemplateData getTemplate (String templateCode) {
        RestTemplate restTemplate = new RestTemplate();
        final String catFactApiUri = "https://template-service.up.railway.app/api/v1/template-service/templates/%s".formatted(templateCode);

        ResponseEntity<TemplateServiceResponse> response = restTemplate.getForEntity(catFactApiUri, TemplateServiceResponse.class);

        if (response.getStatusCode() == HttpStatus.OK) {
            return response.getBody().getData();
        }

        return null;
    }
}
