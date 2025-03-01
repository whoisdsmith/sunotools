# Sunozara.com API Documentation

Base URL: `https://sunozara.com/api`

## Authentication

### Login

- **URL**: `/login`
- **Method**: `POST`
- **Body**:

```json
{
    "email": "user@example.com",
    "password": "password"
}
```

- **Response**:

```json
{
    "token": "access_token_here",
    "user": {
        "id": 1,
        "name": "User Name",
        "email": "user@example.com"
    }
}
```

### Register

- **URL**: `/register`
- **Method**: `POST`
- **Body**:

```json
{
    "name": "User Name",
    "email": "user@example.com",
    "password": "password",
    "password_confirmation": "password"
}
```

## Audio Management

### Get All Audios

- **URL**: `/audios`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Query Parameters**:
  - `page`: Page number (optional)
  - `limit`: Items per page (optional)
  - `category`: Filter by category (optional)
  - `language`: Filter by language (optional)

### Upload Audio

- **URL**: `/audios`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer {token}`
  - `Content-Type: multipart/form-data`
- **Body**:

```form-data
title: "Audio Title"
description: "Audio Description"
category_id: 1
language_id: 1
audio_file: [file]
cover_image: [file]
```

### Get Audio Details

- **URL**: `/audios/{id}`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Update Audio

- **URL**: `/audios/{id}`
- **Method**: `PUT`
- **Headers**:
  - `Authorization: Bearer {token}`
  - `Content-Type: multipart/form-data`
- **Body**: Same as Upload Audio

### Delete Audio

- **URL**: `/audios/{id}`
- **Method**: `DELETE`
- **Headers**:
  - `Authorization: Bearer {token}`

## Categories

### Get All Categories

- **URL**: `/categories`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Create Category

- **URL**: `/categories`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Body**:

```json
{
    "name": "Category Name",
    "description": "Category Description"
}
```

## Languages

### Get All Languages

- **URL**: `/languages`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Add Language

- **URL**: `/languages`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Body**:

```json
{
    "name": "Language Name",
    "code": "lang_code"
}
```

## User Management

### Get User Profile

- **URL**: `/user/profile`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Update User Profile

- **URL**: `/user/profile`
- **Method**: `PUT`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Body**:

```json
{
    "name": "Updated Name",
    "email": "updated@email.com",
    "avatar": [file]
}
```

### Get User Favorites

- **URL**: `/user/favorites`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Add to Favorites

- **URL**: `/user/favorites/{audio_id}`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer {token}`

### Remove from Favorites

- **URL**: `/user/favorites/{audio_id}`
- **Method**: `DELETE`
- **Headers**:
  - `Authorization: Bearer {token}`

## Additional APIs

### Articles

- **URL**: `/api/articles`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Query Parameters**:
  - `page`: Page number
  - `limit`: Items per page
  - `category`: Filter by category

### Audio Books

- **URL**: `/api/audiobooks`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Query Parameters**:
  - `page`: Page number
  - `category`: Filter by category
  - `language`: Filter by language

### Episodes

- **URL**: `/api/episodes/{audiobook_id}`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Phone Verification

- **URL**: `/api/auth/verify-phone`
- **Method**: `POST`
- **Body**:

```json
{
    "phone": "+919876543210",
    "otp": "123456"
}
```

### Location APIs

- **URL**: `/api/locations`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Subscription

- **URL**: `/api/subscriptions`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Response**:

```json
{
    "plans": [
        {
            "id": 1,
            "name": "Basic",
            "price": 99,
            "duration": 30,
            "features": []
        }
    ]
}
```

### Tags

- **URL**: `/api/tags`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

### Products

- **URL**: `/api/products`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Query Parameters**:
  - `page`: Page number
  - `category`: Filter by category

### Coupons

- **URL**: `/api/coupons/verify`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer {token}`
- **Body**:

```json
{
    "code": "DISCOUNT50"
}
```

## Error Responses

All endpoints may return these error responses:

- **401 Unauthorized**

```json
{
    "message": "Unauthenticated."
}
```

- **403 Forbidden**

```json
{
    "message": "You do not have permission to perform this action."
}
```

- **404 Not Found**

```json
{
    "message": "Resource not found."
}
```

- **422 Validation Error**

```json
{
    "message": "The given data was invalid.",
    "errors": {
        "field": [
            "Error message"
        ]
    }
}
```

## Rate Limiting

All API endpoints are rate-limited to prevent abuse. The current limits are:

- 60 requests per minute for authenticated users
- 30 requests per minute for unauthenticated users

When you exceed the rate limit, you'll receive a 429 Too Many Requests response.

## Testing the API

You can test these APIs using tools like:

- Postman
- cURL
- Any HTTP client library

Example cURL request:

```bash
curl -X POST https://sunozara.com/api/login \
    -H "Content-Type: application/json" \
    -d '{"email":"user@example.com","password":"password"}'
```

## Support

For API support or questions, please contact:

- Email: <support@sunozara.com>
- Technical Support: <tech@sunozara.com>
