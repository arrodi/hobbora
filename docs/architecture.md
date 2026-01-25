# Hobbora Architecture

## System Architecture Diagram

```mermaid
flowchart TB
    subgraph Client
        Browser[Web Browser]
    end

    subgraph "Hobbora Microservices"
        subgraph "Web UI :8000"
            WebUI[Flask Web Server<br/>Jinja2 Templates<br/>Session Management]
        end

        subgraph "Postgres DB API :8001"
            DBAPI[Flask REST API<br/>User Routes<br/>Hobby Routes<br/>Catalog Routes]
        end

        subgraph "Picture API :8002"
            PicAPI[Flask REST API<br/>Picture Routes<br/>Metadata Routes]
        end
    end

    subgraph "Data Storage"
        subgraph "PostgreSQL :5432"
            DB[(PostgreSQL Database)]
        end

        subgraph "MinIO S3 :9000"
            S3[(S3 Object Storage<br/>Profile Pictures<br/>Hobby Pictures)]
        end
    end

    Browser -->|HTTP| WebUI
    WebUI -->|REST API| DBAPI
    WebUI -->|REST API| PicAPI
    DBAPI -->|psycopg2| DB
    PicAPI -->|boto3| S3
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User Browser
    participant W as Web UI :8000
    participant D as DB API :8001
    participant P as Picture API :8002
    participant DB as PostgreSQL
    participant S3 as MinIO S3

    Note over U,S3: User Login Flow
    U->>W: POST /auth/sign-in
    W->>D: POST /user/authenticate
    D->>DB: SELECT user by email
    DB-->>D: User data
    D-->>W: Auth response
    W-->>U: Set session cookie

    Note over U,S3: View Profile Flow
    U->>W: GET /account/profile
    W->>D: POST /user/get
    D->>DB: SELECT user data
    DB-->>D: User record
    D-->>W: User JSON
    W->>P: POST /picture/profile/get
    P->>S3: GetObject
    S3-->>P: Image bytes
    P-->>W: Base64 image
    W-->>U: Rendered HTML
```

## Database Schema

```mermaid
erDiagram
    USER_ACCOUNTS ||--o{ USER_HOBBIES : has
    USER_ACCOUNTS ||--o| USER_TUTOR_ACCOUNTS : becomes
    USER_ACCOUNTS ||--o{ TUTORING_AVAILABILITY : sets
    USER_HOBBIES ||--o| USER_HOBBIES_TUTORING : enables
    USER_HOBBIES_TUTORING ||--o{ TUTORING_SESSION : books
    TUTORING_AVAILABILITY ||--o{ TUTORING_SESSION : schedules
    TUTORING_SESSION ||--o{ TUTORING_SESSION_REVIEWS : receives
    TUTORING_SESSION ||--o{ PAYMENT_TRANSACTIONS : generates

    USER_ACCOUNTS {
        text USER_ID PK
        text EMAIL
        text USERNAME
        text FIRST_NAME
        text LAST_NAME
        text ABOUT
        text PASSWORD
        boolean TUTORING
        timestamp CRT_DT
        timestamp UPD_DT
    }

    USER_HOBBIES {
        text HOBBY_ID PK
        text USER_ID FK
        text NAME
        text DESCRIPTION
        text PROFICIENCY
        boolean TUTORING
        integer EXPERIENCE_YEARS
        integer EXPERIENCE_MONTHS
    }

    USER_HOBBIES_TUTORING {
        text HOBBY_ID FK
        integer HOURLY_RATE
        text COUNTRY
        text CITY
        boolean MODE_LIVE_CALL
        boolean MODE_PUBLIC_IN_PERSON
        boolean MODE_PRIVATE_IN_PERSON
    }

    TUTORING_SESSION {
        text SESSION_ID PK
        text AVAILABILITY_ID FK
        text USER_TUTOR_ID FK
        text USER_STUDENT_ID FK
        text HOBBY_ID FK
        text MODE
        timestamp SESSION_SCHEDULED_START_TIME
        timestamp SESSION_SCHEDULED_END_TIME
    }

    TUTORING_SESSION_REVIEWS {
        text REVIEW_ID PK
        text USER_ID FK
        text SESSION_ID FK
        text SESSION_REVIEW_TEXT
        integer SESSION_RATING
    }

    PAYMENT_TRANSACTIONS {
        text TRANSACTION_ID PK
        text SESSION_ID FK
        text PAYER_ID FK
        text PAYEE_ID FK
        decimal AMOUNT
        text CURRENCY
        text PAYMENT_STATUS
    }
```

## Service Ports Summary

| Service | Port | Technology |
|---------|------|------------|
| Web UI | 8000 | Flask + Waitress |
| Postgres DB API | 8001 | Flask + Waitress |
| Picture API | 8002 | Flask + Waitress |
| PostgreSQL | 5432 | PostgreSQL 16.4 |
| MinIO (S3) | 9000 | MinIO |
| MinIO Console | 9001 | MinIO Web UI |

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, Jinja2 Templates |
| Web Server | Flask + Waitress |
| Database | PostgreSQL 16.4 |
| Object Storage | MinIO (S3-compatible) |
| Authentication | bcrypt + Flask Sessions |
| Containerization | Docker |
| Orchestration | Kubernetes |
