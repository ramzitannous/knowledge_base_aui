# Knowledge Base AUI

## Getting Started


1. Copy `.env.example` to `.env` and `.env` as needed, and edit the values for your environment.

2. Start the stack:
   ```sh
   docker-compose --env-file .env.docker -f .docker-compose-dev.yaml -p knowledge_base_aui up -d

   ```
   _Environment variables will be loaded from `.env` or `.env` automatically._
---
   #### python for local development instead of docker
1. install uv, follow instructions here https://docs.astral.sh/uv/getting-started/installation/#standalone-installer

2. install project dependencies: 
3. ```sh
   uv pip install .
   ```
4. run the app:
   ```sh
   uvicorn app.main:app --reload --loop uvloop 
   ```
---
   ### URLs:
   1. http://localhost:8000/docs for swagger documentation
   2. http://localhost:9181 for rq-dashboard to monitor running background tasks

---
## Environment Variables

The following environment variables must be set (in `.env` for development or `.env.example` as a template):

**MongoDB Configuration**

| Field Name                   | Type    | Default Value   | Description                  |
|------------------------------|---------|-----------------|------------------------------|
| `MONGO_INITDB_ROOT_USERNAME` | string  | `admin`         | MongoDB root username        |
| `MONGO_INITDB_ROOT_PASSWORD` | string  | `admin`         | MongoDB root password        |
| `MONGODB_HOST`               | string  | `"localhost"`   | MongoDB host address         |
| `MONGODB_PORT`               | string  | `"27017"`       | MongoDB port number          |
| `MONGODB_DB`                 | string  | `knowledge_base`| MongoDB database name        |

**PostgreSQL Configuration**

| Field Name         | Type   | Default Value   | Description            |
|--------------------|--------|-----------------|------------------------|
| `POSTGRES_HOST`    | string | `"localhost"`   | PostgreSQL host address|
| `POSTGRES_PORT`    | string | `"5432"`        | PostgreSQL port number |
| `POSTGRES_USER`    | string | `admin`         | PostgreSQL username    |
| `POSTGRES_PASSWORD`| string | `admin`         | PostgreSQL password    |
| `POSTGRES_DB`      | string | `knowledge_base`| PostgreSQL database name|

**AWS/S3 Configuration**

| Field Name             | Type   | Default Value           | Description                     |
|------------------------|--------|-------------------------|---------------------------------|
| `AWS_ACCESS_KEY_ID`    | string | `aws_key`               | AWS access key ID               |
| `AWS_SECRET_ACCESS_KEY`| string | `aws_secret`            | AWS secret access key           |
| `AWS_DEFAULT_REGION`   | string | `us-east-1`             | AWS region                      |
| `AWS_BUCKET_NAME`      | string | `knowledge-base`        | S3 bucket name                  |
| `AWS_S3_ENDPOINT_URL`  | string | `"http://localhost:9000"`| S3 endpoint URL (for MinIO)     |

**Redis Configuration**

| Field Name  | Type   | Default Value   | Description         |
|-------------|--------|-----------------|---------------------|
| `REDIS_HOST`| string | `"localhost"`   | Redis host address  |
| `REDIS_PORT`| string | `"6379"`        | Redis port number   |

**General Configuration**

| Field Name | Type   | Default Value  | Description            |
|------------|--------|----------------|------------------------|
| `APP_ENV`  | string | `"local"`      | Application environment|
| `API_KEY`  | string | `"my_api_key"` | API authentication key |

**OpenAI Configuration**

| Field Name           | Type   | Default Value           | Description         |
|----------------------|--------|-------------------------|---------------------|
| `OPENAI_API_KEY`     | string | `"your_openai_api_key"` | OpenAI API key      |
| `OPENAI_API_BASE_URL`| string | `"your_openai_api_base_url"` | OpenAI API base URL|

**Other**

| Field Name               | Type    | Default Value | Description                        |
|--------------------------|---------|---------------|------------------------------------|
| `TOKENIZERS_PARALLELISM` | boolean | `false`       | Enable/disable tokenizer parallelism|

Copy `.env.example` to `.env` and fill in your values before starting the application.

---

## Project Structure

```
knowledge_base_aui/
├── app/
│   ├── components/           # Haystack processing components
│   │   ├── converters/       # Document format converters
│   │   ├── fetchers/         # Data fetching utilities
│   │   ├── pipelines/        # Haystack processing pipelines
│   │   ├── document_store.py # Vector database configuration
│   │   ├── generator.py      # LLM generator setup
│   │   └── helpers.py        # Shared utility functions
│   ├── models/               # Database models
│   │   └── __init__.py       # KnowledgeBase, FileResource, StatusEnum
│   ├── routes/               # API endpoints
│   │   ├── file_resources.py # File CRUD endpoints
│   │   ├── knowledge_base.py # Knowledge base CRUD endpoints
│   │   ├── rag.py           # RAG streaming endpoint
│   │   └── vector_search.py # Vector search endpoint
│   ├── schemas/              # Pydantic data models
│   │   ├── file_resources.py # File resource schemas
│   │   ├── knowledge_base.py # Knowledge base schemas
│   │   ├── vector_search.py  # Search request/response schemas
│   │   └── metadata.py       # Metadata filtering schemas
│   ├── services/             # Business logic layer
│   │   ├── cache.py         # FastAPI caching utilities
│   │   ├── clients.py       # External service clients (S3, Redis)
│   │   ├── db.py            # Database initialization
│   │   ├── file_resources.py # File resource business logic
│   │   ├── knowledge_base.py # Knowledge base business logic
│   │   ├── s3.py            # S3 operations (presigned URLs, file ops)
│   │   └── tasks.py         # Background job processing
│   ├── tests/               # Test files
│   ├── config.py            # Application configuration
│   ├── deps.py              # FastAPI dependencies
│   ├── exceptions.py        # Custom exception classes
│   └── main.py              # FastAPI application entry point
├── .env                     # Environment variables
├── .env.example             # Environment template
├── docker-compose-dev.yaml  # Development Docker setup
├── Dockerfile               # Container configuration
├── pyproject.toml           # Python dependencies and project config
└── Readme.md               # Project documentation
```
---

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
- nest_asyncio ([nest_asyncio](https://github.com/andyshinn/nest_asyncio)) for nested event loops
- fastembed ([fastembed](https://github.com/qdrant/fastembed/)) for text embedding using CPU with fast performance
- fastembed-haystack ([fastembed-haystack](https://github.com/qdrant/fastembed-haystack/)) haystack integration for text embedding using CPU with fast performance
- tiktoken ([tiktoken](https://github.com/openai/tiktoken)) for tokenization
- pgvector-haystack ([https://github.com/pgvector/pgvector)) for vector DB support
- docling-haystack ([https://github.com/deepset-ai/docling-haystack)) to parse and extract PDF documents
- docling ([https://github.com/deepset-ai/docling)) to parse and extract PDF documents
- pytesseract ([https://github.com/tesseract-ocr/tesseract)) for OCR support
- pillow ([https://pillow.readthedocs.io/en/stable/]) for image processing
- fastapi-cache2[redis] ([https://github.com/encode/fastapi-cache2]) for caching support for API layer using Redis
- orjson ([https://github.com/ijl/orjson]) for faster JSON serialization

---

## API Specification
### V1 API
- Prefix for all api endpoints: `/api/v1`

### API Rate Limits [Bonus]
- Maximum number of requests per minute: 10
- configuration was done using `slowapi`
- can be adjusted in `config.py` using `API_RATE_LIMITS` in `app_config.py`

### Caching [Bonus]
`GET` one endpoints use Redis caching (via fastapi-cache2). Cache is auto-initialized, invalidated on update or delete
This will improve read performance.

### API Key Authentication
All API endpoints are protected by API key authentication. Every request must include the correct API key in the `X-API-Key` HTTP header.

- The API key is loaded from the `API_KEY` environment variable (see `.env`, `.env.docker`, `.env.example`).
  - If the provided key is missing or invalid, the API returns a 401 Unauthorized error.
  - This is enforced globally for all endpoints.

> **Note:** If `API_KEY` is not set, the server will fail to start or will reject all requests.

### Error Handling

The API uses unified exception handling for resource errors:

- `DBDocumentNotFound` returns HTTP 404 with `{ "error": "..." }`.
- `DBDocumentConflict` returns HTTP 409 with `{ "error": "..." }` (e.g., unique constraint violations).

These are handled globally in `main.py` for consistent error responses across all endpoints.

### File Storage [Bonus]
This project supports AWS S3-compatible storage (including [MinIO](https://min.io/)) using `aioboto3` for async access.
all file uploads are uploaded to S3 and stored in a bucket named `app_config.AWS_BUCKET_NAME`.

---

## Background Worker
- rq is used to offload CPU bound operations to a separate background worker
- The `run_pdf_indexing_task` in `app.tasks` contains background task for processing PDF files and run `pdf_index_pipeline`
- Default Task Timeout is set to 1 hour, defined in `config.py` in `app_config.TASK_TIMEOUT`

---

## MongoDB Document Schema

#### KnowledgeBase Model

| Field Name   | Type                  | Description                                 |
|--------------|-----------------------|---------------------------------------------|
| name         | str | Name of the knowledge base (unique)         |
| description  | str                   | Description of the knowledge base           |
| created_at   | datetime.datetime     | Creation timestamp                          |
| updated_at   | Optional[datetime]    | Last updated timestamp                      |

#### FileResource Model

| Field Name        | Type                        | Description                                 |
|-------------------|-----------------------------|---------------------------------------------|
| knowledge_base_id | PydanticObjectId            | Reference to KnowledgeBase _id              |
| filename          | str                         | Name of the file                            |
| s3_key            | Optional[str]               | S3 key of the file                          |
| size              | Optional[int]               | Size of the file in bytes                   |
| version           | Optional[int] (default=1)   | Version of the file                         |
| status            | StatusEnum                  | Resource status                             |
| error             | Optional[str]               | Error message                               |
| job_id            | Optional[str]               | Job ID for async processing                 |
| created_at        | datetime.datetime           | Creation timestamp                          |
| updated_at        | Optional[datetime.datetime] | Last updated timestamp                      |

#### Relationships:
    KnowledgeBase (1) ────< (many) FileResource
            ^                     |
            |                     |
         _id (referenced by) knowledge_base_id

---
