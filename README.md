# Social Media Application - Like and Dislike Comments Feature

This repository contains the implementation for the "Like and Dislike Comments" feature, addressing Jira issue SCRUM-38. This feature allows users to express their sentiment towards comments by liking or disliking them, and to see real-time updates of reaction counts.

## Project Structure

The core of this feature is a new microservice, the `Reaction Service`, which handles all business logic related to comment reactions.

```
.
├── reaction_service/
│   ├── __init__.py
│   ├── main.py             # Flask application for Reaction Service
│   ├── database.py         # SQLAlchemy models and database session management
│   ├── config.py           # Configuration settings
│   ├── schemas.py          # Pydantic schemas for request/response validation
│   ├── services.py         # Business logic for reactions
│   └── tests/
│       └── test_reactions.py # Unit tests for the Reaction Service
├── .gitignore              # Git ignore file
├── Dockerfile              # Dockerfile for the Reaction Service
└── requirements.txt        # Python dependencies
```

## Features

*   **Like/Dislike Comments**: Users can like or dislike any comment.
*   **Toggle Reactions**: Users can change their reaction (e.g., from like to dislike, or remove a reaction).
*   **Real-time Updates**: Reaction counts are updated in near real-time. (Note: Real-time service integration is part of the HLD but not fully implemented in this initial backend-focused deliverable).
*   **RESTful API**: Dedicated endpoints for managing comment reactions.
*   **Persistent Storage**: Reactions are stored in a PostgreSQL database.
*   **Caching**: (Planned, but not fully implemented in this initial deliverable) Redis for caching reaction counts to improve performance.

## Getting Started

### Prerequisites

*   Python 3.9+
*   Docker (optional, for containerized deployment)
*   PostgreSQL database instance
*   Redis instance (optional, for caching)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/p67428378-afk/social-media.git
    cd social-media
    git checkout ISSUE-SCRUM-38
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the `reaction_service` directory based on `reaction_service/.env.example` (will be created later) and fill in your database connection details.

    ```
    # reaction_service/.env
    DATABASE_URL="postgresql://user:password@host:port/database_name"
    ```

4.  **Run Database Migrations (if applicable):**
    (This project assumes a simple SQLAlchemy setup. For production, consider Alembic for migrations.)
    The `database.py` script will create tables if they don't exist.

### Running the Reaction Service

```bash
# From the project root
export FLASK_APP=reaction_service/main.py
export FLASK_ENV=development # or production
flask run
```

The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

All endpoints are prefixed with `/api/comments/{comment_id}/react`.

### `POST /api/comments/<comment_id>/react`

Registers or updates a user's reaction to a comment.

*   **Method**: `POST`
*   **URL**: `/api/comments/{comment_id}/react`
*   **Headers**: `Authorization: Bearer <JWT_TOKEN>` (for authentication)
*   **Request Body**:
    ```json
    {
        "user_id": "uuid_of_user",
        "reaction_type": "like" | "dislike"
    }
    ```
*   **Responses**:
    *   `200 OK`: Reaction successfully recorded/updated.
        ```json
        {
            "message": "Reaction updated successfully",
            "reaction": {
                "reaction_id": "uuid",
                "user_id": "uuid",
                "comment_id": "uuid",
                "reaction_type": "like",
                "created_at": "timestamp",
                "updated_at": "timestamp"
            }
        }
        ```
    *   `400 Bad Request`: Invalid input.
    *   `401 Unauthorized`: Missing or invalid authentication token.
    *   `404 Not Found`: Comment not found.
    *   `500 Internal Server Error`: Server error.

### `DELETE /api/comments/<comment_id>/react`

Removes a user's reaction from a comment.

*   **Method**: `DELETE`
*   **URL**: `/api/comments/{comment_id}/react`
*   **Headers**: `Authorization: Bearer <JWT_TOKEN>`
*   **Request Body**:
    ```json
    {
        "user_id": "uuid_of_user"
    }
    ```
*   **Responses**:
    *   `200 OK`: Reaction successfully removed.
        ```json
        {
            "message": "Reaction removed successfully"
        }
        ```
    *   `400 Bad Request`: Invalid input.
    *   `401 Unauthorized`: Missing or invalid authentication token.
    *   `404 Not Found`: Comment or reaction not found.
    *   `500 Internal Server Error`: Server error.

### `GET /api/comments/<comment_id>/reactions`

Retrieves the current like and dislike counts for a comment.

*   **Method**: `GET`
*   **URL**: `/api/comments/{comment_id}/reactions`
*   **Responses**:
    *   `200 OK`: Successfully retrieved counts.
        ```json
        {
            "comment_id": "uuid",
            "likes": 15,
            "dislikes": 3
        }
        ```
    *   `404 Not Found`: Comment not found.
    *   `500 Internal Server Error`: Server error.

## Development Notes

*   **Authentication**: A placeholder authentication mechanism is included. In a real-world scenario, this would integrate with an existing Identity Provider.
*   **Real-time Updates**: The HLD mentions WebSockets for real-time updates. This initial implementation focuses on the core API and database logic. Integration with a WebSocket service would be a subsequent step.
*   **Caching**: Basic caching logic for reaction counts is outlined but can be further optimized with a dedicated Redis client and more sophisticated invalidation strategies.

## Running Tests

```bash
# From the project root
pytest reaction_service/tests/
```
