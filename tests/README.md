# Testing Documentation

Dokumentasi lengkap tentang struktur testing dan cara kerja fixture override pattern.

## 📁 Struktur Directory

```
tests/
├── conftest.py                          # Root-level config & markers
├── integration/                         # Integration tests
│   ├── conftest.py                     # Integration-wide fixtures
│   ├── fixtures/                       # Centralized fixtures
│   │   ├── __init__.py
│   │   ├── containers.py               # Docker containers
│   │   ├── database.py                 # Database fixtures
│   │   └── factories.py                # Data factories
│   └── todos/                          # Todos feature tests
│       ├── conftest.py                 # Feature-specific fixtures
│       ├── test_api.py                 # API endpoint tests
│       ├── test_crud.py                # CRUD layer tests
│       └── test_workflow.py            # End-to-end workflows
└── unit/                               # Unit tests
    ├── conftest.py                     # Unit test fixtures
    └── ...

```

## 🎯 Fixture Hierarchy

Pytest mencari fixtures dengan urutan berikut:

1. **Test file level** - Fixtures di dalam test file itu sendiri
2. **conftest.py di directory test** - `tests/integration/todos/conftest.py`
3. **conftest.py parent directories** - `tests/integration/conftest.py`
4. **conftest.py root** - `tests/conftest.py`

**Ketika fixture dengan nama yang sama ditemukan di beberapa level, Pytest menggunakan yang PALING DEKAT dengan test.**

## 🔄 Fixture Override Pattern

### Konsep Dasar

**Centralized Fixture** (di `tests/integration/conftest.py`):
```python
@pytest.fixture(scope="session")
def db(db_engine):
    """Default: Session-scoped database"""
    with Session(db_engine) as session:
        yield session
```

**Override di Feature** (di `tests/integration/todos/conftest.py`):
```python
@pytest.fixture(scope="function")
def db(db_engine):
    """Override: Function-scoped with rollback"""
    with Session(db_engine) as session:
        yield session
        session.rollback()  # Rollback after each test
```

**Hasil:**
- Tests di `tests/integration/todos/` akan menggunakan fixture yang di-override (function-scoped dengan rollback)
- Tests di feature lain tetap menggunakan centralized fixture (session-scoped)

### Contoh 1: Override Factory dengan Default Berbeda

**Centralized Factory** (`tests/integration/fixtures/factories.py`):
```python
def create_todo_data(
    title="Default Test Todo",
    description="Default description",
    completed=False,
    **kwargs
):
    return {"title": title, "description": description, "completed": completed}
```

**Override di Feature** (`tests/integration/todos/conftest.py`):
```python
@pytest.fixture
def todo_data():
    def _factory(**kwargs):
        defaults = {
            "title": "Todos Feature Test",  # Different default
            "description": "Created in todos feature",
            "completed": False,
        }
        defaults.update(kwargs)
        return create_todo_data(**defaults)
    return _factory
```

**Usage dalam test:**
```python
def test_something(todo_data):
    # Menggunakan defaults dari feature override
    data = todo_data()
    # title = "Todos Feature Test" (bukan "Default Test Todo")

    # Override specific fields
    data = todo_data(title="Custom Title")
    # title = "Custom Title"
```

### Contoh 2: Override Scope untuk Isolation

**Use Case:** Todos feature butuh clean database untuk setiap test, tapi feature lain bisa share database session.

**Centralized (Fast, shared):**
```python
@pytest.fixture(scope="session")
def db(db_engine):
    with Session(db_engine) as session:
        yield session
```

**Override (Isolated per test):**
```python
@pytest.fixture(scope="function")
def db(db_engine):
    with Session(db_engine) as session:
        yield session
        session.rollback()  # Clean up after each test
```

### Contoh 3: Add Feature-Specific Fixtures

Anda juga bisa menambahkan fixture BARU yang hanya tersedia di feature tertentu:

```python
@pytest.fixture
def sample_todo(test_client, todo_data):
    """
    Creates a sample todo in DB.
    Only available in todos/ tests.
    """
    data = todo_data()
    response = test_client.post("/api/todos/", json=data)
    return response.json()

@pytest.fixture
def multiple_todos(test_client, todo_data):
    """Creates 5 todos for list testing."""
    todos = []
    for i in range(5):
        data = todo_data(title=f"Todo {i+1}")
        response = test_client.post("/api/todos/", json=data)
        todos.append(response.json())
    return todos
```

### Contoh 4: Override dengan Custom Behavior

**Centralized:**
```python
@pytest.fixture(scope="session")
def test_client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Override dengan custom headers:**
```python
@pytest.fixture(scope="function")
def test_client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, headers={"X-Test-Feature": "todos"}) as c:
        yield c
    app.dependency_overrides.clear()
```

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run by Type
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

### Run with Verbosity
```bash
# Verbose output
pytest -v

# Very verbose with output
pytest -vv -s
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

## 📝 Test Organization Guidelines

### Integration Tests (`tests/integration/`)

**Per Feature Directory:**
- `test_api.py` - API endpoint tests
- `test_crud.py` - Database CRUD operations
- `test_workflow.py` - End-to-end workflows
- `conftest.py` - Feature-specific fixtures and overrides

**When to Create New Feature Directory:**
- Ketika menambah resource/entity baru (users, products, orders, etc.)
- Ketika butuh fixture configuration yang berbeda
- Ketika butuh isolasi testing dari feature lain

### Unit Tests (`tests/unit/`)

Organize by layer:
- `test_crud/` - Test CRUD functions with mocked DB
- `test_schemas/` - Test Pydantic schemas
- `test_models/` - Test SQLAlchemy models
- `test_utils/` - Test utility functions

## 🎨 Best Practices

### 1. Use Centralized Fixtures as Defaults
Buat fixtures di `tests/integration/fixtures/` untuk configurasi umum yang reusable.

### 2. Override Only When Needed
Jangan override kecuali benar-benar butuh behavior berbeda untuk feature tersebut.

### 3. Document Overrides
Selalu beri komentar kenapa override dilakukan.

```python
@pytest.fixture(scope="function")
def db(db_engine):
    """
    OVERRIDE: Function-scoped for todos tests.
    Reason: Todos tests need isolated DB state per test.
    """
    ...
```

### 4. Keep Tests Independent
Setiap test harus bisa run independently dan dalam urutan apapun.

### 5. Use Factories for Test Data
Gunakan factory functions untuk create test data, bukan hardcode values.

```python
# Good
def test_create(todo_data):
    data = todo_data(title="Test")

# Bad
def test_create():
    data = {"title": "Test", "description": "...", "completed": False}
```

### 6. Name Tests Clearly
```python
# Good
def test_create_todo_returns_201_with_valid_data()
def test_create_todo_returns_422_with_missing_title()

# Bad
def test_create()
def test_1()
```

## 🔍 Debugging Tips

### 1. Print Fixture Values
```bash
pytest --fixtures  # List all available fixtures
pytest --fixtures-per-test  # Show which fixtures each test uses
```

### 2. See Which Fixture is Used
```python
def test_debug(db):
    print(f"Using db fixture: {db}")
    print(f"Scope: {db._pytestfixturefunction.scope}")
```

### 3. Run Single Test with Output
```bash
pytest tests/integration/todos/test_api.py::test_create_and_get_todo -v -s
```

### 4. Use Breakpoints
```python
def test_something(test_client):
    breakpoint()  # Will pause here
    response = test_client.get("/api/todos/")
```

## 📚 Adding New Features

Ketika menambah feature baru (misalnya `users`):

1. **Create directory:**
   ```bash
   mkdir -p tests/integration/users
   ```

2. **Create conftest.py:**
   ```python
   # tests/integration/users/conftest.py
   import pytest

   @pytest.fixture
   def user_data():
       def _factory(**kwargs):
           defaults = {"username": "testuser", "email": "test@example.com"}
           defaults.update(kwargs)
           return defaults
       return _factory

   @pytest.fixture
   def sample_user(test_client, user_data):
       data = user_data()
       response = test_client.post("/api/users/", json=data)
       return response.json()
   ```

3. **Create test files:**
   - `test_api.py` - API tests
   - `test_crud.py` - CRUD tests
   - `test_workflow.py` - Workflow tests

4. **Override fixtures if needed:**
   ```python
   # Override db for user tests if needed
   @pytest.fixture(scope="function")
   def db(db_engine):
       # Custom behavior for user tests
       pass
   ```

## 🎓 Learning Path

1. ✅ Pahami struktur directory
2. ✅ Lihat centralized fixtures di `fixtures/`
3. ✅ Lihat contoh override di `todos/conftest.py`
4. ✅ Run existing tests untuk lihat hasilnya
5. ✅ Coba modifikasi override untuk experiment
6. ✅ Buat feature baru dengan pattern yang sama

## ❓ Common Questions

**Q: Kapan harus override fixture?**
A: Override ketika feature butuh behavior berbeda dari default. Contoh: scope berbeda, seed data berbeda, configuration berbeda.

**Q: Apakah override mempengaruhi feature lain?**
A: Tidak. Override hanya berlaku untuk tests di directory tersebut dan subdirectorynya.

**Q: Bisa override fixture dari pytest atau plugin?**
A: Ya, termasuk built-in fixtures seperti `tmp_path`, `monkeypatch`, dll.

**Q: Bagaimana cara debug fixture yang digunakan?**
A: Gunakan `pytest --fixtures` atau tambahkan print statement di fixture.

---

**Happy Testing! 🧪**
