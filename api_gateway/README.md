
# API Gateway Endpoints Documentation

## 🌐 Base URL
**https://api-gateway-proud-thunder-2459.fly.dev**

---

## 1. Signup Endpoint

**URL:**  
`POST https://api-gateway-proud-thunder-2459.fly.dev/api/v1/signup/`

**Description:**  
Forwards user registration requests to the **User Service**. Creates a user in the system.

**Request Body:**
```json
{
  "name": "string",
  "email": "user@example.com",
  "push_token": "optional_string",
  "preferences": {
    "email": true,
    "push": false
  },
  "password": "string"
}
````

**Response (Success - forwarded from User Service):**

```json
{
  "id": "user-id",
  "name": "string",
  "email": "user@example.com",
  "preferences": {
    "email": true,
    "push": false
  },
  "push_token": "optional_string"
}
```

**Response (Error - User Service unreachable or invalid data):**

```json
{
  "error": "User Service unreachable or invalid data/user already exists",
  "details": "error details here"
}
```

---

## 2. Create Notification Endpoint

**URL:**
`POST https://api-gateway-proud-thunder-2459.fly.dev/api/v1/notifications/`

**Description:**
Queues notifications (**email** and/or **push**) for a user based on their preferences.

**Request Body:**

```json
{
  "user_id": "user-id",
  "message": "string",
  "priority": 0,
  "template_code": "string"
}
```

**Response (Success):**

```json
{
  "success": true,
  "message": "Notification(s) queued successfully",
  "data": {
    "request_id": "b2c833f1-3a69-4e4b-bf74-672b0fef3e12",
    "user_preferences": {
      "email": true,
      "push": false
    },
    "queued": {
      "email": true,
      "push": false
    },
    "notification": {
      "request_id": "b2c833f1-3a69-4e4b-bf74-672b0fef3e12",
      "user_id": "f1b44c10-03b8-4e02-96f2-f4d9aa13a299",
      "email": "jane@example.com",
      "push_token": null,
      "message": "Welcome to our platform!",
      "priority": 5,
      "template_code": "welcome_email",
      "type": "email"
    }
  }
}
```

**Response (Error - invalid request):**

```json
{
  "success": false,
  "message": "Invalid request data",
  "error": {
    "field": ["error description"]
  },
  "data": null,
  "meta": null
}
```

**Response (Error - RabbitMQ failed or user not found):**

```json
{
  "success": false,
  "message": "Failed to queue message",
  "error": "error details here",
  "data": null,
  "meta": null
}
```

---

## 3. Health Check Endpoint

**URL:**
`GET https://api-gateway-proud-thunder-2459.fly.dev/api/v1/health/`

**Description:**
Simple health check to verify that the API Gateway is running.

**Response (Success):**

```json
{
  "status": "ok"
}
```

```
