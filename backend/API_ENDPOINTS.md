# User Management API Endpoints

This document describes the REST API endpoints implemented for user management in the AI Gym Coach system.

## Endpoints Overview

### Authentication Endpoints (`/api/auth`)

#### 1. POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "weight_kg": 70.5,
  "height_cm": 175.0,
  "body_type": "mesomorph",
  "fitness_goals": ["lose_weight", "build_muscle"]
}
```

**Validation Rules:**
- `email`: Must be a valid email format
- `password`: Minimum 8 characters, at least one uppercase, one lowercase, and one number
- `weight_kg`: Optional, must be greater than 0
- `height_cm`: Optional, must be greater than 0
- `body_type`: Optional, must be one of: "ectomorph", "mesomorph", "endomorph"
- `fitness_goals`: Optional, array of strings

**Success Response (201 Created):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "weight_kg": 70.5,
  "height_cm": 175.0,
  "body_type": "mesomorph",
  "fitness_goals": ["lose_weight", "build_muscle"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Validation errors (invalid email, weak password, etc.)

---

#### 2. POST /api/auth/login
Authenticate user and receive JWT access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect email or password
- `422 Unprocessable Entity`: Invalid request format

---

### User Profile Endpoints (`/api/users`)

All user profile endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

#### 3. GET /api/users/profile
Get current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "weight_kg": 70.5,
  "height_cm": 175.0,
  "body_type": "mesomorph",
  "fitness_goals": ["lose_weight", "build_muscle"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: No authentication token provided
- `404 Not Found`: User not found

---

#### 4. PUT /api/users/profile
Update current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (all fields optional):**
```json
{
  "weight_kg": 72.0,
  "height_cm": 176.0,
  "body_type": "endomorph",
  "fitness_goals": ["lose_weight", "improve_endurance"]
}
```

**Success Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "weight_kg": 72.0,
  "height_cm": 176.0,
  "body_type": "endomorph",
  "fitness_goals": ["lose_weight", "improve_endurance"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: No authentication token provided
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Validation errors

---

## Implementation Details

### Files Created

1. **`backend/app/api/deps.py`**
   - Authentication dependency for protected endpoints
   - JWT token validation
   - Extracts user information from token

2. **`backend/app/api/auth.py`**
   - Registration endpoint (`POST /api/auth/register`)
   - Login endpoint (`POST /api/auth/login`)
   - Input validation using Pydantic schemas
   - Password hashing and JWT token generation

3. **`backend/app/api/users.py`**
   - Get profile endpoint (`GET /api/users/profile`)
   - Update profile endpoint (`PUT /api/users/profile`)
   - Protected by authentication dependency

4. **`backend/app/main.py`** (updated)
   - Registered auth and users routers
   - CORS configuration for frontend integration

5. **`backend/tests/test_api_endpoints.py`**
   - Comprehensive unit tests for all endpoints
   - Tests for valid inputs, invalid inputs, edge cases
   - End-to-end flow testing

### Security Features

- **Password Hashing**: Passwords are hashed using bcrypt before storage
- **JWT Authentication**: Secure token-based authentication with 24-hour expiration
- **Input Validation**: Pydantic schemas validate all inputs
- **Authorization**: Protected endpoints verify JWT tokens
- **CORS**: Configured to allow frontend access

### Testing

To run the tests, ensure the database is running and execute:

```bash
# Start the database
docker compose up -d postgres

# Run the tests
python -m pytest backend/tests/test_api_endpoints.py -v
```

### Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **Requirement 10.1**: User registration with email, password, and profile data
- **Requirement 10.4**: User authentication with session establishment
- **Requirement 10.6**: Profile updates for body stats and fitness goals

### API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example Usage

#### Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123",
    "weight_kg": 75.0,
    "height_cm": 180.0,
    "body_type": "mesomorph",
    "fitness_goals": ["build_muscle"]
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

#### Get profile (with token)
```bash
curl -X GET http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer <your_access_token>"
```

#### Update profile (with token)
```bash
curl -X PUT http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "weight_kg": 77.0,
    "fitness_goals": ["build_muscle", "improve_endurance"]
  }'
```

## Next Steps

1. Start the database: `docker compose up -d postgres`
2. Run the backend server: `cd backend && uvicorn app.main:app --reload`
3. Test the endpoints using the examples above or the Swagger UI
4. Run the test suite to verify all functionality
