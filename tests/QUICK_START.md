# Quick Start Guide - Testing Structure

## 📁 Struktur Final

```
tests/
├── __init__.py
├── conftest.py                          # ← ROOT: Markers, environment setup
├── README.md                            # ← Full documentation
├── FIXTURE_OVERRIDE_EXAMPLES.md        # ← Detailed override examples
├── QUICK_START.md                      # ← This file
│
├── integration/                         # ← Integration tests
│   ├── conftest.py                     # ← Integration-wide fixtures
│   ├── fixtures/                       # ← CENTRALIZED fixtures
│   │   ├── __init__.py
│   │   ├── containers.py               # ← Docker containers
│   │   ├── database.py                 # ← DB session & engine
│   │   └── factories.py                # ← Data factories
│   │
│   └── todos/                          # ← Todos FEATURE tests
│       ├── __init__.py
│       ├── conftest.py                 # ← Feature-specific OVERRIDES
│       ├── test_api.py                 # ← API endpoint tests (7 tests)
│       ├── test_crud.py                # ← CRUD layer tests (5 tests)
│       └── test_workflow.py            # ← E2E workflows (3 tests)
│
└── unit/                               # ← Unit tests (future)
    ├── __init__.py
    └── conftest.py                     # ← Unit test fixtures
```

## 🎯 Fixture Hierarchy (Override Pattern)

```
┌─────────────────────────────────────────────────────────────┐
│  ROOT LEVEL (tests/conftest.py)                            │
│  - Test markers (integration, unit, slow, fast)            │
│  - Environment setup                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  INTEGRATION LEVEL (tests/integration/)                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  CENTRALIZED FIXTURES (fixtures/)                    │ │
│  │  - postgres_container() → Docker postgres           │ │
│  │  - db_engine() → SQLAlchemy engine                  │ │
│  │  - db() → Database session [scope=session]          │ │
│  │  - test_client() → FastAPI TestClient              │ │
│  │  - create_todo_data() → Factory function           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  Available to ALL integration tests                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  FEATURE LEVEL (tests/integration/todos/)                  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  FEATURE OVERRIDES & ADDITIONS (todos/conftest.py)  │ │
│  │                                                      │ │
│  │  OVERRIDES:                                          │ │
│  │  - todo_data() → Custom factory defaults            │ │
│  │  - [Optional] db() → Function-scoped + rollback     │ │
│  │                                                      │ │
│  │  NEW FIXTURES (only for todos):                     │ │
│  │  - sample_todo() → Pre-created todo                 │ │
│  │  - multiple_todos() → 5 pre-created todos           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  Only available in todos/ tests                            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run by Type (Using Markers)
```bash
# Integration tests only
pytest -m integration

# Unit tests only
pytest -m unit

# Fast tests only
pytest -m fast

# Slow tests only
pytest -m slow
```

### Run by Feature
```bash
# All todos tests
pytest tests/integration/todos/

# Specific test file
pytest tests/integration/todos/test_api.py

# Specific test
pytest tests/integration/todos/test_api.py::test_create_and_get_todo
```

### Useful Options
```bash
# Verbose output
pytest -v

# Very verbose with print output
pytest -vv -s

# Quiet mode (less output)
pytest -q

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Collect tests without running
pytest --collect-only
```

## 📝 Fixture Override Pattern - Simple Example

### Centralized (Available Everywhere)
```python
# tests/integration/fixtures/factories.py
def create_todo_data(title="Default", **kwargs):
    return {"title": title, ...}
```

### Override (Only in todos/)
```python
# tests/integration/todos/conftest.py
@pytest.fixture
def todo_data():
    def _factory(**kwargs):
        defaults = {"title": "Todos Feature Test"}  # ← Different!
        return create_todo_data(**defaults)
    return _factory
```

### Result
```python
# In tests/integration/todos/test_api.py
def test_something(todo_data):
    data = todo_data()
    # title = "Todos Feature Test" ← Uses override!

# In tests/integration/users/test_api.py (future)
def test_something():
    data = create_todo_data()
    # title = "Default" ← Uses centralized!
```

## 🎓 Key Concepts

### 1. Centralized Fixtures
- **Location:** `tests/integration/fixtures/`
- **Purpose:** Default configuration untuk semua tests
- **Scope:** Available untuk semua integration tests
- **Contoh:** `postgres_container`, `db`, `test_client`

### 2. Override Fixtures
- **Location:** `tests/integration/<feature>/conftest.py`
- **Purpose:** Customize behavior untuk feature tertentu
- **Scope:** Hanya untuk tests di feature tersebut
- **Contoh:** `todo_data`, `db` (optional)

### 3. Helper Fixtures
- **Location:** `tests/integration/<feature>/conftest.py`
- **Purpose:** Feature-specific helpers (not overrides)
- **Scope:** Hanya untuk tests di feature tersebut
- **Contoh:** `sample_todo`, `multiple_todos`

## 📚 What to Read Next

1. **README.md** - Comprehensive documentation
2. **FIXTURE_OVERRIDE_EXAMPLES.md** - Detailed examples with use cases
3. **conftest.py files** - See actual implementations

## ✨ Adding a New Feature

When adding a new feature (e.g., "users"):

```bash
# 1. Create directory
mkdir -p tests/integration/users

# 2. Create conftest.py
cat > tests/integration/users/conftest.py << 'EOF'
import pytest

@pytest.fixture
def user_data():
    def _factory(**kwargs):
        defaults = {"username": "testuser", "email": "test@test.com"}
        defaults.update(kwargs)
        return defaults
    return _factory

@pytest.fixture
def sample_user(test_client, user_data):
    data = user_data()
    response = test_client.post("/api/users/", json=data)
    return response.json()
EOF

# 3. Create test files
touch tests/integration/users/test_api.py
touch tests/integration/users/test_crud.py
```

## 🔍 Debugging

### See Available Fixtures
```bash
pytest --fixtures
pytest --fixtures-per-test
```

### Debug Specific Test
```bash
# With breakpoint
pytest tests/integration/todos/test_api.py::test_create_and_get_todo -s

# With full traceback
pytest tests/integration/todos/test_api.py::test_create_and_get_todo --tb=long

# With print statements
pytest tests/integration/todos/test_api.py::test_create_and_get_todo -s -v
```

## ⚡ Current Test Count

- **Total:** 15 integration tests
- **API Tests:** 7 tests
- **CRUD Tests:** 5 tests
- **Workflow Tests:** 3 tests

All tests are passing! ✅

---

**Happy Testing! 🎉**
