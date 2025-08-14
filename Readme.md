# Knowledge Base AUI

# Mongodb Collections
### KnowledgeBase Model (knowledge_bases)
| Field       | Type              | Description                                    |
|-------------|-------------------|------------------------------------------------|
| name        | str               | Name of the knowledge base (**unique**)         |
| description | str               | Description of the knowledge base               |
| created_at  | datetime.datetime | Creation timestamp (UTC)                       |
| updated_at  | Optional[datetime.datetime] | Last update timestamp (UTC)           |

### KnowledgeBaseResource Model (knowledge_base_files)
- unique togather (knowledge_base_id, filename, version)

| Field             | Type               | Description                                          |
|-------------------|--------------------|------------------------------------------------------|
| knowledge_base_id | str                | Reference to KnowledgeBase _id                       |
| filename          | str                | Name of the file                                     |
| s3_key            | Optional[str]      | S3 key of the file                                   |
| uploaded_at       | datetime.datetime  | Upload timestamp (UTC)                               |
| size              | Optional[int]      | Size of the file in bytes                            |
| version           | Optional[int]      | Version of the file                                  |
 | status            | StatusEnum        | Resource status: uploading, ingesting, done, error   |
| error             | Optional[str]      | Error message                                        |
- This application is a Python-based tool designed to manage and interact with a knowledge base. The project uses a modular structure with a main entry point in `main.py` and dependency management via `pyproject.toml` (managed with [uv](https://github.com/astral-sh/uv)). The app is intended for local use and can be extended for various knowledge management or automation tasks.

## Key Features

- **Python-based CLI or script**: Main logic in `main.py`.
- **Dependency management**: Uses `pyproject.toml` and [uv](https://github.com/astral-sh/uv) for package requirements.
- **MongoDB and PostgreSQL (with vector DB support)**: Supports both MongoDB and PostgreSQL (with [pgvector](https://github.com/pgvector/pgvector) extension) for storage and vector search capabilities.
- **Extensible structure**: Designed for easy addition of new features or modules.

## Getting Started

1. Install dependencies (requires [uv](https://github.com/astral-sh/uv)):
   ```sh
   uv pip install -r requirements.txt
   ```
   _or use `uv pip install -r pyproject.toml` if you manage dependencies only via `pyproject.toml`._

2. Copy `.env.example` to `.env` and `.env` as needed, and edit the values for your environment.

3. Start the stack:
   ```sh
   docker-compose --env-file .env.docker -f .docker-compose-dev.yaml -p knowledge_base_aui up -d

   ```
   _Environment variables will be loaded from `.env` or `.env` automatically._

4. Run the application:
   ```sh
   uv run uvicorn app.main:app --reload 
   ```

## Environment Variables

The following environment variables must be set (in `.env` for development or `.env.example` as a template):

- `MONGO_INITDB_ROOT_USERNAME`: MongoDB root username
- `MONGO_INITDB_ROOT_PASSWORD`: MongoDB root password
- `POSTGRES_USER`: Postgres database user
- `POSTGRES_PASSWORD`: Postgres database password
- `POSTGRES_DB`: Postgres database name

Copy `.env.example` to `.env` or `.env` and fill in your values before starting the stack.

### Installation

Beanie is included as a dependency in `pyproject.toml`. If you haven't already, install dependencies with:

```bash
pip install .
```

Or, if you use poetry:

```bash
poetry install
```

### Usage Example

Beanie is used to define MongoDB document models and perform async database operations
See the [Beanie docs](https://roman-right.github.io/beanie/) for more details.

## Knowledge Base CRUD API Folder Structure

The project uses a modular structure compatible with FastAPI for building a scalable knowledge base CRUD API:

```
app/
├── main.py                # FastAPI app entry point
├── models/                # Beanie/MongoDB document models
│   └── __init__.py
├── schemas/               # Pydantic schemas for request/response validation
│   └── __init__.py
├── routes/                # API route definitions
│   ├── __init__.py
│   └── knowledge_base.py  # Knowledge base CRUD endpoints
├── services/              # Business logic and service layer
│   └── __init__.py
└── db/                    # Database connection and utilities
    └── __init__.py
```

- Place your Beanie models in `app/models/`
- Define request/response schemas in `app/schemas/`
- Add API endpoints in `app/routes/knowledge_base.py`
- Implement business logic in `app/services/`
- Put DB connection code in `app/db/`

This structure is scalable and follows FastAPI best practices.

## Knowledge Base API Endpoints

### Create Knowledge Base
- **POST** `/`
- **Status Code**: 201 Created
- **Request Body**: `KnowledgeBaseCreate`
- **Response**: Created `KnowledgeBase` object

### List Knowledge Bases
- **GET** `/`
- **Status Code**: 200 OK
- **Response**: List of `KnowledgeBase` objects

### Get Knowledge Base by ID
- **GET** `/{kb_id}`
- **Status Code**: 200 OK (if found), 404 Not Found (if not found)
- **Response**: `KnowledgeBase` object

### Update Knowledge Base
- **PUT** `/{kb_id}`
- **Status Code**: 200 OK (if updated), 404 Not Found (if not found)
- **Request Body**: `KnowledgeBaseUpdate`
- **Response**: Updated `KnowledgeBase` object

### Delete Knowledge Base
- **DELETE** `/{kb_id}`
- **Status Code**: 204 No Content (if deleted), 404 Not Found (if not found)
- **Response**: Empty

#### Example Error Response
```json
{
  "detail": "KnowledgeBase not found"
}
```

#### Example Success Response (Create)
```json
{
  "id": "...",
  "name": "Sample KB",
  ...
}
```

> Status codes now follow RESTful conventions for resource creation, retrieval, update, and deletion.

## API Key Authentication

All API endpoints are protected by API key authentication. Every request must include the correct API key in the `X-API-Key` HTTP header.

### How it works
- The API key is loaded from the `API_KEY` environment variable (see `.env`, `.env.docker`, `.env.example`).
- If the provided key is missing or invalid, the API returns a 401 Unauthorized error.
- This is enforced globally for all endpoints.

### Usage Example

Include the header in your requests:

```http
X-API-Key: your_secret_key_here
```

Or with curl:
```sh
curl -H "X-API-Key: your_secret_key_here" http://localhost:8000/your-endpoint
```

### Configuration
Add your API key to your environment file:
```
API_KEY=your_secret_key_here
```

> **Note:** If `API_KEY` is not set, the server will fail to start or will reject all requests.

## Service Layer Structure

All business logic for knowledge base and resource operations is implemented in a dedicated service layer:

- `app/services/knowledge_base.py`: Handles all logic for KnowledgeBase CRUD and validation.
- `app/services/knowledge_base_resource.py`: Handles all logic for KnowledgeBaseResource CRUD and validation.

FastAPI routes in `app/routes/knowledge_base.py` delegate to these services, keeping the API layer clean and maintainable. This separation makes the codebase easier to test, extend, and reason about.

## Error Handling

The API uses unified exception handling for resource errors:

- `ResourceNotFound` returns HTTP 404 with `{ "error": "..." }`.
- `ResourceConflict` returns HTTP 409 with `{ "error": "..." }` (e.g., unique constraint violations).

These are handled globally in `main.py` for consistent error responses across all endpoints.

## Async S3/MinIO Integration

This project supports AWS S3-compatible storage (including [MinIO](https://min.io/)) using `aioboto3` for async access.

### Setup
1. Install dependencies (already included in `pyproject.toml`):
   ```sh
   uv pip install -r pyproject.toml
   ```
2. Set the following environment variables as needed:
   - `AWS_ACCESS_KEY_ID` (default: `minioadmin`)
   - `AWS_SECRET_ACCESS_KEY` (default: `minioadmin`)
   - `AWS_S3_ENDPOINT_URL` (default: `http://localhost:9000` for MinIO)
   - `AWS_REGION` (default: `us-east-1`)

### Usage Example
In your async Python code, use the provided client factory:
```python
from app.services.clients import get_async_s3_client

async def upload_example():
    async with get_async_s3_client() as s3:
        await s3.put_object(Bucket="mybucket", Key="file.txt", Body=b"data")
```

- The client is fully compatible with both AWS S3 and MinIO.
- See `app/services/clients.py` for implementation details.

## Configuration with Pydantic Settings

Application settings are managed using Pydantic's `BaseSettings` in `app/config.py`. This allows configuration via environment variables or a `.env` file, following FastAPI best practices.

Example `AppConfig`:

```python
from pydantic import BaseSettings

class AppConfig(BaseSettings):
    DEBUG: bool = True
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "knowledge_base"

    class Config:
        env_file = ".env"
```

- Override any setting with environment variables or a `.env` file.
- Use `AppConfig()` to access settings throughout your codebase.

## Running with uvloop

This project uses [uvloop](https://github.com/MagicStack/uvloop) for improved async performance in Python. `uvloop` is a drop-in replacement for the standard asyncio event loop, providing significant speedups for I/O-bound applications such as FastAPI.

### How uvloop is used
- The Dockerfile runs the app with the following command:
  ```sh
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop uvloop --app-dir app
  ```
- This tells `uvicorn` to use `uvloop` as the event loop implementation.

### Benefits
- Faster request handling and lower latency for async APIs.
- No code changes needed—just the `--loop uvloop` flag.

### Requirements
- `uvloop` is installed automatically as part of the dependencies (see `pyproject.toml`).

### Local Docker development
To build and run locally:
```sh
docker build -t myfastapi .
docker run --rm -p 8000:8000 myfastapi
```

Your FastAPI app will now run with `uvloop` for maximum async performance.

## Tech Stack
- uv ([uv](https://github.com/astral-sh/uv))
- FastAPI ([FastAPI](https://fastapi.tiangolo.com/))
- uvicorn ([uvicorn](https://www.starlette.io/))
- dotenv ([python-dotenv](https://github.com/theskumar/python-dotenv))
- docker ([docker](https://www.docker.com/))
- docker-compose ([docker-compose](https://docs.docker.com/compose/))
- MongoDB ([MongoDB](https://www.mongodb.com/)) with vector search support
- PostgreSQL ([pgvector](https://github.com/pgvector/pgvector)) for vector DB support
- Beanie ([Beanie](https://github.com/roman-right/beanie)) as an asynchronous ODM for MongoDB
- pydantic-settings ([pydantic-settings](https://github.com/samuelcolvin/pydantic-settings)) for configuration management
- slowapi ([slowapi](https://github.com/davidgama/slowapi)) for throttling and rate limiting
- pydantic ([pydantic](https://github.com/samuelcolvin/pydantic)) for data validation and serialization
- uvloop ([uvloop](https://github.com/MagicStack/uvloop)) for improved async performance
- aioboto3 ([aioboto3](https://github.com/astral-sh/aioboto3)) for async S3/MinIO integration
- rq ([rq](https://github.com/rq/rq)) for queueing and background tasks
- rq-dashboard ([rq-dashboard](https://github.com/rq/rq-dashboard)) for monitoring queues
- haystack ([haystack](https://github.com/deepset-ai/haystack)) for rag pipeline & semantic search
- pydantic ([pydantic](https://github.com/samuelcolvin/pydantic)) for data validation and serialization
- pypdf ([pypdf](https://github.com/py-pdf/pypdf)) for PDF processing
- nest_asyncio ([nest_asyncio](https://github.com/andyshinn/nest_asyncio)) for nested event loops
- 
## Project Structure

- `main.py` — Main entry point and application logic.
- `pyproject.toml` — Project metadata and dependencies.
- `Readme.md` — Documentation and usage instructions.
- `.docker-compose-dev.yaml` — Docker Compose config for local dev databases.
- `.env`, `.env` — Environment variables for local development (used by Docker Compose).
- `.env.example` — Example environment variable file (template).

### KnowledgeBaseResource Fields

- **knowledge_base_id**: Reference to KnowledgeBase `_id`
- **filename**: Name of the file
- **s3_key**: S3 key of the file (optional)
- **content_type**: Content type (MIME, optional)
- **size**: Size of the file in bytes (optional)
- **version**: Version of the file (default: 1)
- **status**: Resource status (enum)
  - `active`: The resource is available and in use
  - `inactive`: The resource is temporarily disabled
  - `archived`: The resource is archived and not in active use

> The `status` field defaults to `active` if not specified.