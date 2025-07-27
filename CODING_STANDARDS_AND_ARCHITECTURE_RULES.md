# UnHook Services - Coding Standards and Architecture Rules

## Overview
This document defines the coding standards, architectural patterns, and development rules for the UnHook microservices ecosystem. It covers three main services:
- **User Service** - User management and preferences
- **Data Collector Service** - Data collection from external sources
- **Data Processing Service** - AI-powered content processing and analysis

## Table of Contents
1. [General Standards](#general-standards)
2. [Service-Specific Patterns](#service-specific-patterns)
3. [Data Model Architecture](#data-model-architecture)
4. [AI Agent Patterns](#ai-agent-patterns)
5. [Database Patterns](#database-patterns)
6. [API Design Patterns](#api-design-patterns)
7. [Repository Patterns](#repository-patterns)
8. [Service Layer Patterns](#service-layer-patterns)

---

## General Standards

### Code Formatting
- **Line Length**: 88 characters (Black default)
- **Python Version**: >=3.8
- **Import Sorting**: Use `isort` with Black profile
- **String Normalization**: Disabled (preserve quotes as written)

### Dependencies
- **Core Dependencies**:
  - `pydantic>=2.0.0` - Data validation and serialization
  - `python-dateutil>=2.8.2` - Date/time utilities
  - `motor>=3.0.0` - Async MongoDB driver
  - `pymongo>=4.0.0` - MongoDB operations
  - `python-dotenv>=0.19.0` - Environment configuration
  - `typing-extensions>=4.0.0` - Type hints

### Project Structure
```
service_name/
├── __init__.py
├── pyproject.toml
├── .gitignore
├── models/           # Domain models
├── repositories/     # Data access layer
├── services/         # Business logic
├── controllers/      # API controllers (if applicable)
├── api/             # FastAPI setup (if applicable)
├── exceptions/      # Custom exceptions
└── external/        # External service clients
```

---

## Service-Specific Patterns

### User Service
**Purpose**: User management, preferences, and configuration

**Key Patterns**:
- **FastAPI-based REST API** with dependency injection
- **UUID-based primary keys** for users
- **Pydantic models** for validation and serialization
- **MongoDB** as primary database
- **Repository pattern** with adapters for data transformation

**Directory Structure**:
```
user_service/
├── api/
│   ├── app.py              # FastAPI application setup
│   └── dependencies.py     # Dependency injection
├── controllers/
│   └── user_controller.py  # HTTP request handlers
├── models/
│   ├── user.py            # Main user domain model
│   ├── interests.py       # User interests
│   ├── manual_config.py   # User configuration
│   ├── youtube_config.py  # YouTube-specific config
│   └── enums.py          # Enumerations
├── repositories/
│   ├── mongodb/
│   │   ├── models/        # Database models
│   │   ├── adapters/      # Data transformation
│   │   └── config/        # Database configuration
│   └── user_repository.py # Repository interface
└── services/
    └── user_service.py    # Business logic
```

### Data Collector Service
**Purpose**: Collect data from external sources (YouTube, etc.)

**Key Patterns**:
- **Collector pattern** with base classes for different collection types
- **External service clients** for cross-service communication
- **Status tracking** for collected content
- **Repository pattern** for data persistence

**Directory Structure**:
```
data_collector_service/
├── collectors/
│   ├── base_discover.py   # Base discover collector
│   ├── base_static.py     # Base static collector
│   └── youtube/
│       ├── discover.py    # YouTube discover implementation
│       ├── static.py      # YouTube static implementation
│       ├── models/        # YouTube-specific models
│       ├── tools/         # YouTube-specific tools
│       └── adapters/      # Data transformation
├── models/
│   ├── user_collected_content.py  # Main content model
│   └── enums.py                  # Content types
├── repositories/
│   └── mongodb/           # MongoDB repositories
├── external/
│   └── user_service/      # User service client
└── service.py             # Main orchestration service
```

### Data Processing Service
**Purpose**: AI-powered content processing and analysis

**Key Patterns**:
- **AI Agent pattern** with structured input/output
- **Multi-stage processing** with status tracking
- **Prompt management** with external files
- **Batch processing** for efficiency
- **Repository pattern** for data persistence

**Directory Structure**:
```
data_processing_service/
├── ai/
│   ├── base.py           # Base AI client
│   └── config.py         # AI configuration
├── services/
│   └── processing/
│       ├── youtube/
│       │   ├── categorize_content/
│       │   │   ├── ai_agent/
│       │   │   │   ├── models/      # Input/output models
│       │   │   │   ├── adaptors/    # Data transformation
│       │   │   │   ├── prompts/     # Prompt templates
│       │   │   │   └── categorization_agent.py
│       │   │   └── categorize_youtube_content_service.py
│       │   ├── generate_complete_content/
│       │   └── generate_required_content/
│       └── process_moderated_content_service.py
├── models/
│   ├── generated_content.py  # Processing results
│   └── youtube/
│       └── subtitle_data.py  # YouTube-specific models
└── repositories/
    └── mongodb/           # MongoDB repositories
```

---

## Data Model Architecture

### Domain Models (Internal)
**Purpose**: Business logic representation

**Patterns**:
- Use **Pydantic BaseModel** for validation
- Include **Field validators** for business rules
- Use **UUID** for primary keys
- Include **created_at/updated_at** timestamps
- Use **enums** for constrained values
- Include **Config class** for JSON serialization

**Example**:
```python
from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    name: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("created_at")
    def validate_created_at(cls, v):
        if not isinstance(v, datetime):
            raise ValueError("created_at must be a datetime object")
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z", UUID: str}
```

### Database Models
**Purpose**: Database-specific representation

**Patterns**:
- Use **Pydantic BaseModel** for validation
- Use **string IDs** (MongoDB `_id` field)
- Store **datetimes as ISO strings** with 'Z' suffix
- Use **Field aliases** for MongoDB field names
- Include **Config.populate_by_name = True**

**Example**:
```python
from pydantic import BaseModel, Field

class UserDBModel(BaseModel):
    id: str = Field(alias="_id")  # MongoDB _id field
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    name: str = Field(..., min_length=1)
    created_at: str  # Stored as ISO format string with 'Z' suffix

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
```

### Status Tracking Models
**Purpose**: Track processing states

**Patterns**:
- Use **string enums** for status values
- Include **status history** with timestamps
- Use **dataclasses** for simple status details
- Include **reason fields** for status changes

**Example**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List

class ContentStatus(str, Enum):
    COLLECTED = "COLLECTED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    REJECTED = "REJECTED"

@dataclass
class StatusDetail:
    status: ContentStatus
    created_at: datetime
    reason: str = ""

@dataclass
class UserCollectedContent:
    id: str
    status: ContentStatus
    status_details: List[StatusDetail] = field(default_factory=list)
    
    def set_status(self, status: ContentStatus, reason: str = ""):
        status_detail = StatusDetail(
            status=status, created_at=datetime.utcnow(), reason=reason
        )
        self.status_details.append(status_detail)
        self.status = status
```

---

## AI Agent Patterns

### Base AI Client
**Purpose**: Common AI functionality across all agents

**Patterns**:
- **Generic base class** with structured output support
- **Multiple model provider support** (DeepSeek, OpenAI)
- **Prompt management** with external files
- **Response logging** with date-based directories
- **Markdown code block handling** for responses

**Example**:
```python
from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseAIClient(Generic[T], ABC):
    def __init__(self, output_model: Type[T], model_config: ModelConfig, log_dir: Optional[str] = None):
        self.output_model = output_model
        self.model_config = model_config
        self.llm = self._initialize_llm()
        self.log_dir = log_dir

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def _create_output_format_guide(self) -> str:
        pass

    async def generate_structured_response(self, user_input: str) -> T:
        # Implementation with logging and response parsing
        pass
```

### AI Agent Structure
**Purpose**: Specific AI functionality for use cases

**Directory Structure**:
```
ai_agent/
├── models/
│   ├── input.py      # Input data models
│   └── output.py     # Output data models
├── adaptors/
│   ├── input_adaptor.py   # Convert domain to AI input
│   └── output_adaptor.py  # Convert AI output to domain
├── prompts/
│   ├── system_prompt.txt      # System instructions
│   ├── generation_prompt.txt  # Main prompt template
│   └── output_prompt.txt      # Output format guide
├── generated/         # Log directory (auto-created)
└── agent_name.py     # Main agent implementation
```

### Input/Output Models
**Purpose**: Structured data for AI interactions

**Patterns**:
- Use **Pydantic BaseModel** for validation
- Include **Field descriptions** for clarity
- Use **nested models** for complex data
- Include **type hints** for all fields

**Example**:
```python
from typing import List
from pydantic import BaseModel, Field

class CategoryOutputItem(BaseModel):
    id: str = Field(..., description="Original id of the content item.")
    category: str = Field(..., description="One of the predefined categories.")
    category_description: str = Field(..., description="1 sentence description of the category.")
    category_tags: List[str] = Field(..., description="3-5 tags.")

class CategorizationDataOutput(BaseModel):
    output: List[CategoryOutputItem] = Field(..., description="List of category info objects for each content item.")
```

### Adapters
**Purpose**: Transform between domain and AI models

**Patterns**:
- Use **static methods** for transformations
- Include **validation** for required fields
- Handle **missing data** gracefully
- Use **type hints** for clarity

**Example**:
```python
from typing import List

class CategorizationInputAdaptor:
    @staticmethod
    def from_generated_content_list(
        generated_content_list: List[GeneratedContent],
    ) -> List[CategorizationDataInput]:
        inputs = []
        for content in generated_content_list:
            title = ""
            short_summary = ""
            if content.generated and "VERY_SHORT" in content.generated:
                title = content.generated["VERY_SHORT"].string
            if content.generated and "SHORT" in content.generated:
                short_summary = content.generated["SHORT"].string
            if not title or not short_summary:
                raise ValueError(f"Either title or short_summary is empty for content id: {content.id}")
            inputs.append(CategorizationDataInput(id=content.id, title=title, short_summary=short_summary))
        return inputs
```

---

## Database Patterns

### MongoDB Configuration
**Purpose**: Database connection and configuration

**Patterns**:
- Use **singleton pattern** for database connection
- Include **connection pooling** configuration
- Use **environment variables** for configuration
- Include **connection lifecycle management**

**Example**:
```python
import motor.motor_asyncio
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "unhook"

class MongoDB:
    db = None
    client = None

    @classmethod
    async def connect_to_database(cls):
        settings = DatabaseSettings()
        cls.client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
        cls.db = cls.client[settings.database_name]

    @classmethod
    async def close_database_connection(cls):
        if cls.client:
            cls.client.close()
```

### Repository Pattern
**Purpose**: Data access abstraction

**Patterns**:
- Use **interface/implementation separation**
- Include **CRUD operations** as abstract methods
- Use **async/await** for database operations
- Include **error handling** and logging

**Example**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass
```

### Adapter Pattern
**Purpose**: Transform between domain and database models

**Patterns**:
- Use **static methods** for transformations
- Handle **datetime conversions** (domain ↔ string)
- Handle **UUID conversions** (domain ↔ string)
- Include **bidirectional conversion** methods

**Example**:
```python
class UserAdapter:
    @staticmethod
    def to_db_model(user: User) -> UserDBModel:
        return UserDBModel(
            id=str(user.id),
            email=user.email,
            name=user.name,
            created_at=user.created_at.isoformat() + "Z",
        )

    @staticmethod
    def to_internal_model(db_model: UserDBModel) -> User:
        return User(
            id=UUID(db_model.id),
            email=db_model.email,
            name=db_model.name,
            created_at=datetime.fromisoformat(db_model.created_at[:-1]),
        )
```

---

## API Design Patterns

### FastAPI Structure
**Purpose**: RESTful API endpoints

**Patterns**:
- Use **APIRouter** for endpoint grouping
- Include **dependency injection** for services
- Use **Pydantic models** for request/response validation
- Include **proper HTTP status codes**
- Use **tags** for API documentation

**Example**:
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User)
async def create_user(
    user_data: Dict[str, Any], 
    user_service: UserService = Depends(get_user_service)
) -> User:
    try:
        user = User(**user_data)
        return await user_service.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Dependency Injection
**Purpose**: Service instantiation and management

**Patterns**:
- Use **FastAPI Depends** for injection
- Create **factory functions** for services
- Include **database connection** management
- Use **singleton pattern** for expensive resources

**Example**:
```python
from fastapi import Depends
from functools import lru_cache

@lru_cache()
def get_user_service() -> UserService:
    return UserService(get_user_repository())

def get_user_repository() -> UserRepository:
    return MongoDBUserRepository(MongoDB.get_database())
```

---

## Service Layer Patterns

### Business Logic Services
**Purpose**: Orchestrate business operations

**Patterns**:
- Use **repository pattern** for data access
- Include **validation logic** before operations
- Use **async/await** for database operations
- Include **proper error handling**
- Use **logging** for debugging

**Example**:
```python
import logging
from typing import Optional

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.logger = logging.getLogger(__name__)

    async def create_user(self, user: User) -> User:
        try:
            # Validate user data
            if not user.email or not user.name:
                raise ValueError("Email and name are required")
            
            # Check if user already exists
            existing_user = await self.user_repository.get_user_by_email(user.email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Create user
            created_user = await self.user_repository.create_user(user)
            self.logger.info(f"Created user with ID: {created_user.id}")
            return created_user
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            raise
```

### Processing Services
**Purpose**: Handle complex processing workflows

**Patterns**:
- Use **batch processing** for efficiency
- Include **status tracking** throughout process
- Use **AI agents** for intelligent processing
- Include **progress logging**
- Handle **partial failures** gracefully

**Example**:
```python
import asyncio
import logging
from copy import deepcopy
from typing import List

class CategorizeYoutubeContentService:
    def __init__(self):
        self.user_content_repository = MongoDBUserContentRepository()
        self.logger = logging.getLogger(__name__)
        self.categorization_agent = CategorizationAgent()

    async def categorize_generated_content(self) -> None:
        generated_content_list = self.user_content_repository.get_generated_content(
            status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
            content_type=ContentType.YOUTUBE_VIDEO,
        )
        
        batch_size = 8
        for i in range(0, len(generated_content_list), batch_size):
            batch = generated_content_list[i : i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1} with {len(batch)} items...")
            
            # Process batch
            categorized_batch = await self.categorization_agent.categorize_content(batch)
            
            # Update status and persist
            updated_batch = []
            for original, categorized in zip(batch, categorized_batch):
                cloned = deepcopy(categorized)
                cloned.set_status(GeneratedContentStatus.CATEGORIZATION_COMPLETED, "Categorization Complete.")
                updated_batch.append(cloned)
            
            self.user_content_repository.update_generated_content_batch(updated_batch)
```

---

## Development Guidelines

### Creating New Services
1. **Copy the standard directory structure** from existing services
2. **Set up pyproject.toml** with appropriate dependencies
3. **Create domain models** using Pydantic BaseModel
4. **Implement repository pattern** with MongoDB adapters
5. **Create service layer** for business logic
6. **Add API controllers** if needed (FastAPI)
7. **Include proper error handling** and logging

### Creating New AI Agents
1. **Extend BaseAIClient** with specific output model
2. **Create input/output models** for structured data
3. **Implement adapters** for data transformation
4. **Create prompt files** in prompts/ directory
5. **Add logging configuration** for debugging
6. **Test with sample data** before integration

### Adding New Data Models
1. **Create domain model** with Pydantic validation
2. **Create database model** with MongoDB field mapping
3. **Implement adapter** for bidirectional conversion
4. **Add to repository** with CRUD operations
5. **Update service layer** to use new model
6. **Add proper indexing** for performance

### Error Handling
1. **Use custom exceptions** for business logic errors
2. **Include proper HTTP status codes** in API responses
3. **Log errors** with appropriate levels
4. **Handle partial failures** gracefully
5. **Provide meaningful error messages** to users

### Testing Guidelines
1. **Unit test** all business logic
2. **Integration test** database operations
3. **Test AI agents** with sample data
4. **Mock external dependencies** for isolation
5. **Test error scenarios** and edge cases

---

## Quick Reference

### Common Imports
```python
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from enum import Enum
import logging
import asyncio
```

### Model Patterns
```python
# Domain Model
class DomainModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z", UUID: str}

# Database Model
class DBModel(BaseModel):
    id: str = Field(alias="_id")
    created_at: str
    
    class Config:
        populate_by_name = True
```

### Service Pattern
```python
class BusinessService:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    async def process_data(self, data: DomainModel) -> DomainModel:
        try:
            # Business logic here
            result = await self.repository.save(data)
            self.logger.info(f"Processed data: {result.id}")
            return result
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            raise
```

This document serves as the definitive guide for maintaining consistency across all UnHook services and should be referenced when creating new features or services. 