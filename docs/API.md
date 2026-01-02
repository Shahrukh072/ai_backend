# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00"
}
```

#### Login

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

### Documents

#### Upload Document

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>
```

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_path": "/uploads/user_1/document.pdf",
  "file_size": 1024000,
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00"
}
```

#### List Documents

```http
GET /api/documents/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "document.pdf",
    "file_size": 1024000,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### Get Document

```http
GET /api/documents/{id}
Authorization: Bearer <token>
```

#### Delete Document

```http
DELETE /api/documents/{id}
Authorization: Bearer <token>
```

### Chat

#### Create Chat (Agentic Workflow)

```http
POST /api/chat/
Authorization: Bearer <token>
Content-Type: application/json

{
  "question": "What is in my documents?",
  "document_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "question": "What is in my documents?",
  "answer": "Based on your documents...",
  "user_id": 1,
  "document_id": 1,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Full Agent Workflow

```http
POST /api/chat/agent
Authorization: Bearer <token>
Content-Type: application/json

{
  "question": "Calculate 5 + 3 and search for Python",
  "document_id": null
}
```

**Response:**
```json
{
  "response": "5 + 3 = 8. Here's what I found about Python...",
  "tool_results": [
    {
      "tool": "calculator",
      "result": "8"
    },
    {
      "tool": "web_search",
      "result": "Python is a programming language..."
    }
  ],
  "iterations": 2,
  "context_used": false
}
```

#### List Chats

```http
GET /api/chat/?document_id=1
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "question": "What is in my documents?",
    "answer": "Based on your documents...",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### Get Chat

```http
GET /api/chat/{id}
Authorization: Bearer <token>
```

### WebSocket Chat

#### Connect

```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws/1');
```

#### Send Message

```javascript
ws.send(JSON.stringify({
  message: "Hello!",
  document_id: 1  // optional
}));
```

#### Receive Messages

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'status':
      console.log('Status:', data.message);
      break;
    case 'stream':
      console.log('Stream:', data.data);
      break;
    case 'complete':
      console.log('Response:', data.response);
      console.log('Tool Results:', data.tool_results);
      break;
    case 'error':
      console.error('Error:', data.message);
      break;
  }
};
```

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

(Implement as needed)

## Pagination

(Implement as needed for list endpoints)

## Filtering and Sorting

(Implement as needed)

