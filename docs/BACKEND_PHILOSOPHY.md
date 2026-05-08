# Backend Philosophy & Architecture Standards

This document outlines the core architectural principles, standards, and implementation patterns for UnHook backend services. Following these standards ensures consistency, maintainability, and scalability across the microservices ecosystem.

---

## 🏗️ Core Architecture
UnHook services follow a **Decoupled, Event-Driven** architecture managed by **Dependency Injection**.

### Key Tenets:
1.  **Strict Decoupling**: Services should communicate via messages (commands/events) rather than synchronous HTTP calls where possible.
2.  **Explicit Dependencies**: No global state or "magic" singletons. Use Dependency Injection (DI) to provide all required components.
3.  **Type Safety**: Every function, parameter, and class variable MUST have explicit Python type hints.
4.  **Async First**: All I/O operations (Database, Redis, API calls) must be `async`.

---

## 📁 Service Directory Structure
Every service follows a unified layout to ensure ease of navigation for both AIs and Humans:

```text
service_name/
├── config/              # YAML config files and Config class
├── infra/               # Infrastructure (DI registration, etc.)
│   └── dependency_injection/
├── messaging/           # Redis producers, consumers, and routers
├── repositories/        # Database abstraction layer
├── services/            # Core business logic
├── models/              # Pydantic models / Enums
├── app.py               # Main entry point (bootstraps DI)
├── Dockerfile           # Multi-layered optimized build
└── pyproject.toml       # Package and dependency definition
```

---

## 💉 Dependency Injection (DI)
We use the `injector` library with a custom auto-discovery mechanism.

### 1. The `@injectable` Decorator
Defined in `infra/dependency_injection/injectable.py`. Use this to mark a class for automatic registration.

```python
from data_collector_service.infra.dependency_injection.injectable import injectable

@injectable()
class MyService:
    def __init__(self, repository: MyRepository):
        ...
```

### 2. Constructor Injection
All injected dependencies must be **type-hinted** in the `__init__` method and marked with `@inject`.

> [!IMPORTANT]
> Failure to add type hints will cause the Injector to fail with a `TypeError` (NoneType) because it uses these hints to resolve the correct class.

```python
from injector import inject

@inject
def __init__(self, config: Config, producer: MessageProducer):
    ...
```

### 3. Circular Dependency Fix
To avoid "Partially Initialized Module" errors, the `@injectable` decorator and the `_REGISTRY` are stored in a standalone file (`injectable.py`) that contains NO other project imports. The scanning/registration logic lives in `registration.py`.

---

## 📨 Messaging System
We use Redis as our primary message broker.

### 1. Commands (Sequential)
*   **Definition**: A request for a specific service to perform an action.
*   **Pattern**: Implemented using Redis Lists (`BRPOP`).
*   **Behavior**: Processed **sequentially** to ensure order and resource safety (one worker picks one command).

### 2. Events (Broadcast)
*   **Definition**: A fact that has happened (e.g., `UserCreated`).
*   **Pattern**: Implemented using Redis Pub/Sub.
*   **Behavior**: Broadcasted to all services currently listening.

### 3. The Router Pattern
Each service uses a `CommandRouter` and `EventRouter` to dispatch incoming messages to the correct logic.

```python
async def handle(self, command: Command):
    match command.action_name:
        case "collect_data":
            await self.service.do_something()
```

---

## ⚙️ Configuration Management
Config is environment-based, stored in YAML files, and follows a **Fail-Fast** approach.

### Key Rules:
1.  **No Fallbacks**: Never use default values or "safe" fallbacks in the `Config` class. If a key is missing from the YAML, the service MUST raise a `ValueError` or `KeyError` and stop execution immediately.
2.  **Environment Isolation**: Configurations are loaded from `config/local_config.yaml` or `config/prod_config.yaml` based on the `environment` environment variable.
3.  **Strict Typing**: Configuration properties should be explicitly typed (e.g., `: int`, `: str`) to catch type mismatches at startup.

> [!CAUTION]
> Hardcoding default values (like `host: "localhost"`) in the Python code is strictly forbidden. This leads to "silent failures" where a service connects to the wrong resource because of a typo in the config file.

---

## 🐳 Docker Standards
To ensure imports like `from service_name.module import ...` work inside containers:

1.  **WORKDIR**: Always set to `/app`.
2.  **Package Preservation**: Copy the project into a subdirectory: `COPY . ./service_name/`.
3.  **Hatch/Pip Install**: Install the project in editable mode: `RUN uv pip install --system -e ./service_name`.
4.  **Run Command**: Always use the module flag: `CMD ["python", "-m", "service_name.app"]`.

---

## 🧹 Code Quality
*   **Linting**: Use `black` and `isort` for formatting.
*   **Naming**: Use `snake_case` for files and variables, `PascalCase` for classes.
*   **Logging**: Avoid raw `print` statements in production code; use structured logging (standardized per service).
