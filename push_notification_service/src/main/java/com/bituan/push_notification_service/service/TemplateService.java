package com.bituan.push_notification_service.service;

import com.bituan.push_notification_service.dto.TemplateData;
import com.bituan.push_notification_service.dto.TemplateServiceRequest;
import com.bituan.push_notification_service.dto.TemplateServiceResponse;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class TemplateService {
    public TemplateData getTemplateByCode (String templateCode) {
        RestTemplate restTemplate = new RestTemplate();
        final String url = "https://template-service.up.railway.app/api/v1/template-service/templates/%s".formatted(templateCode);

        ResponseEntity<TemplateServiceResponse> response = restTemplate.getForEntity(url, TemplateServiceResponse.class);

        if (response.getStatusCode() == HttpStatus.OK) {
            return response.getBody().getData();
        }

        return null;
    }

    public TemplateData getTemplateByName (TemplateServiceRequest requestData) {
        RestTemplate restTemplate = new RestTemplate();
        final String url = "https://template-service.up.railway.app/api/v1/template-service/templates/render";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<TemplateServiceRequest> request = new HttpEntity<>(requestData, headers);

        ResponseEntity<TemplateServiceResponse> response = restTemplate.postForEntity(url, request,TemplateServiceResponse.class);

        if (response.getStatusCode() == HttpStatus.OK) {
            return response.getBody().getData();
        }

        return null;
    }
}
