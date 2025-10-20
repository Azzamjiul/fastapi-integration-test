# Fixture Override Pattern - Contoh Detail

Dokumen ini memberikan contoh konkret bagaimana fixture override bekerja dalam project ini.

## 🔍 Konsep: Fixtures Centralized vs Override

### Analogi Sederhana

Bayangkan fixtures seperti **pengaturan default di aplikasi**:
- **Centralized fixture** = Pengaturan default aplikasi (untuk semua user)
- **Override fixture** = Pengaturan custom per user (hanya untuk user tertentu)

Sama seperti pengaturan custom tidak mempengaruhi user lain, fixture override hanya mempengaruhi tests di directory tersebut.

---

## 📚 Contoh 1: Override Factory dengan Custom Defaults

### Problem
Anda punya factory umum untuk todo data, tapi feature "todos" butuh default values yang berbeda.

### Centralized Factory
**Location:** `tests/integration/fixtures/factories.py`

```python
def create_todo_data(
    title="Default Test Todo",
    description="Default test description",
    completed=False,
    **kwargs
):
    return {
        "title": title,
        "description": description,
        "completed": completed,
    }
```

Ini adalah factory **umum** yang bisa dipakai semua feature.

### Override di Todos Feature
**Location:** `tests/integration/todos/conftest.py`

```python
@pytest.fixture
def todo_data():
    """Override factory dengan defaults khusus todos feature."""
    def _factory(**kwargs):
        defaults = {
            "title": "Todos Feature Test",  # ← Custom default
            "description": "Created in todos feature tests",  # ← Custom default
            "completed": False,
        }
        defaults.update(kwargs)
        return create_todo_data(**defaults)
    return _factory
```

### Cara Kerja

**Test di `tests/integration/todos/test_api.py`:**
```python
def test_something(todo_data):
    # Memanggil factory tanpa arguments
    data = todo_data()

    # Hasil: Menggunakan defaults DARI OVERRIDE
    # {
    #   "title": "Todos Feature Test",  # ← Dari override!
    #   "description": "Created in todos feature tests",  # ← Dari override!
    #   "completed": False
    # }
```

**Test di `tests/integration/users/test_api.py` (feature lain):**
```python
def test_something():
    # Memanggil centralized factory
    from tests.integration.fixtures.factories import create_todo_data
    data = create_todo_data()

    # Hasil: Menggunakan defaults DARI CENTRALIZED
    # {
    #   "title": "Default Test Todo",  # ← Dari centralized!
    #   "description": "Default test description",  # ← Dari centralized!
    #   "completed": False
    # }
```

**Visual:**
```
tests/integration/
├── fixtures/factories.py
│   └── create_todo_data()  ← Default: "Default Test Todo"
│
├── todos/
│   ├── conftest.py
│   │   └── todo_data() OVERRIDE  ← Custom: "Todos Feature Test"
│   └── test_api.py
│       └── Uses: "Todos Feature Test" ✓
│
└── users/
    └── test_api.py
        └── Uses: "Default Test Todo" ✓
```

---

## 📚 Contoh 2: Override DB Scope untuk Isolation

### Problem
- Default: DB session di-share untuk semua tests (fast)
- Todos feature: Butuh clean DB untuk setiap test (isolated)

### Centralized DB Fixture
**Location:** `tests/integration/fixtures/database.py`

```python
@pytest.fixture(scope="session")  # ← Scope = session (shared)
def db(db_engine):
    """Default: Satu session untuk semua tests."""
    with Session(db_engine) as session:
        yield session
```

**Behavior:**
- Session dibuat **sekali** untuk semua tests
- Data dari test A bisa terlihat di test B
- **Fast** (no overhead per test)
- **Risk**: Tests bisa interfere dengan satu sama lain

### Override di Todos Feature (Commented by Default)
**Location:** `tests/integration/todos/conftest.py`

```python
@pytest.fixture(scope="function")  # ← Scope = function (per test)
def db(db_engine):
    """Override: Session baru untuk setiap test + rollback."""
    with Session(db_engine) as session:
        yield session
        session.rollback()  # ← Rollback setelah test
```

**Behavior:**
- Session dibuat **untuk setiap test**
- Data dari test A **tidak terlihat** di test B
- **Slower** (overhead per test)
- **Safe**: Tests fully isolated

### Kapan Menggunakan?

**Gunakan Centralized (Default):**
- ✓ Tests yang read-only
- ✓ Tests yang tidak saling interfere
- ✓ Butuh speed

**Gunakan Override:**
- ✓ Tests yang modify data dan butuh clean state
- ✓ Tests yang test edge cases dengan specific DB state
- ✓ Tests yang bisa fail jika data dari test lain exists

### Aktivasi Override

Uncomment di `tests/integration/todos/conftest.py`:
```python
# Uncomment 3 lines di bawah untuk activate
@pytest.fixture(scope="function")
def db(db_engine):
    with Session(db_engine) as session:
        yield session
        session.rollback()
```

---

## 📚 Contoh 3: Add Feature-Specific Helper Fixtures

### Problem
Todos tests sering butuh pre-created todo untuk testing update/delete operations.

### Solution: Add Helper Fixture
**Location:** `tests/integration/todos/conftest.py`

```python
@pytest.fixture
def sample_todo(test_client, todo_data):
    """
    Creates a todo dan return hasilnya.
    Ini BUKAN override - ini fixture BARU yang hanya ada di todos/.
    """
    data = todo_data()
    response = test_client.post("/api/todos/", json=data)
    return response.json()


@pytest.fixture
def multiple_todos(test_client, todo_data):
    """Creates 5 todos untuk testing list operations."""
    todos = []
    for i in range(5):
        data = todo_data(title=f"Todo {i+1}")
        response = test_client.post("/api/todos/", json=data)
        todos.append(response.json())
    return todos
```

### Usage dalam Test

**Tanpa Helper Fixture:**
```python
def test_delete_todo(test_client, todo_data):
    # Setup: Create todo
    data = todo_data()
    response = test_client.post("/api/todos/", json=data)
    todo_id = response.json()["id"]

    # Actual test
    response = test_client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204
```

**Dengan Helper Fixture:**
```python
def test_delete_todo(test_client, sample_todo):
    # Todo sudah dibuat oleh fixture!
    todo_id = sample_todo["id"]

    # Langsung test
    response = test_client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204
```

**Benefits:**
- ✓ Less boilerplate code
- ✓ Test focus pada actual behavior
- ✓ Reusable setup logic
- ✓ Easier to maintain

---

## 📚 Contoh 4: Override Test Client dengan Custom Headers

### Problem
Todos feature butuh test authentication headers atau feature flags.

### Centralized Test Client
**Location:** `tests/integration/conftest.py`

```python
@pytest.fixture(scope="session")
def test_client(db):
    """Default client tanpa custom headers."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

### Override di Todos Feature
**Location:** `tests/integration/todos/conftest.py`

```python
@pytest.fixture(scope="function")
def test_client(db):
    """Override: Client dengan custom headers untuk todos."""
    from app.main import app
    from app.database import get_db
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_db] = lambda: db

    # ← Add custom headers
    headers = {
        "X-Test-Feature": "todos",
        "X-API-Version": "v1",
    }

    with TestClient(app, headers=headers) as c:
        yield c

    app.dependency_overrides.clear()
```

### Hasil
Setiap request di todos tests akan automatically include custom headers.

---

## 📚 Contoh 5: Override Postgres Container Configuration

### Problem
Todos feature butuh test dengan Postgres version berbeda atau configuration khusus.

### Centralized Container
**Location:** `tests/integration/fixtures/containers.py`

```python
@pytest.fixture(scope="session")
def postgres_container():
    """Default: Postgres 14"""
    return PostgresContainer(
        image="postgres:14",
        username="postgres",
        password="test_password",
        dbname="test_database",
    )
```

### Override di Feature
**Location:** `tests/integration/todos/conftest.py`

```python
@pytest.fixture(scope="session")
def postgres_container():
    """Override: Postgres 15 dengan custom config"""
    return PostgresContainer(
        image="postgres:15",  # ← Different version
        username="todos_user",  # ← Custom user
        password="todos_pass",
        dbname="todos_test_db",
        port=5432,
    )
```

---

## 🎯 Decision Tree: Kapan Override?

```
Apakah fixture behavior di centralized sudah sesuai?
├─ YES → Gunakan centralized fixture (jangan override)
└─ NO  → Ada berapa feature yang butuh behavior berbeda?
    ├─ Hanya 1-2 features → Override di feature tersebut
    └─ Banyak features → Update centralized fixture
```

### Contoh Cases

**Case 1: "Semua tests butuh faster DB session"**
→ Update centralized fixture, JANGAN override

**Case 2: "Hanya todos tests butuh isolated DB"**
→ Override di todos feature

**Case 3: "Todos dan users butuh isolated, tapi orders tidak"**
→ Override di todos dan users features

---

## 🔧 Tips & Best Practices

### 1. Document Why Override
```python
@pytest.fixture(scope="function")
def db(db_engine):
    """
    OVERRIDE: Function-scoped untuk todos tests.

    WHY: Todos tests modify banyak data dan butuh isolation
    untuk avoid flaky tests.
    """
    ...
```

### 2. Import Centralized untuk Reuse Logic
```python
from tests.integration.fixtures.factories import create_todo_data as base_factory

@pytest.fixture
def todo_data():
    def _factory(**kwargs):
        defaults = {"title": "Custom"}
        defaults.update(kwargs)
        return base_factory(**defaults)  # ← Reuse centralized logic
    return _factory
```

### 3. Use Descriptive Names untuk Helper Fixtures
```python
# Good
@pytest.fixture
def authenticated_user():
    ...

@pytest.fixture
def admin_user():
    ...

# Bad
@pytest.fixture
def user():  # ← Ambiguous
    ...
```

### 4. Keep Overrides Minimal
Hanya override apa yang benar-benar perlu berbeda:
```python
# Good - Only override necessary parts
@pytest.fixture
def todo_data():
    def _factory(**kwargs):
        defaults = {"title": "Custom"}
        defaults.update(kwargs)
        return create_todo_data(**defaults)
    return _factory

# Bad - Recreating everything from scratch
@pytest.fixture
def todo_data():
    def _factory(title="Custom", description="Desc", completed=False, **kwargs):
        return {
            "title": title,
            "description": description,
            "completed": completed,
            # ... duplicate 50 lines
        }
    return _factory
```

---

## 🎓 Practice Exercise

Coba buat feature baru "users" dengan override pattern:

**Task:**
1. Create `tests/integration/users/` directory
2. Create `conftest.py` dengan:
   - `user_data()` fixture (factory)
   - `sample_user()` fixture (helper)
   - Override `db` fixture untuk isolated tests
3. Create `test_api.py` dengan basic CRUD tests

**Template:**
```python
# tests/integration/users/conftest.py
import pytest
from tests.integration.fixtures.factories import create_todo_data

@pytest.fixture
def user_data():
    """Factory untuk user data dengan custom defaults."""
    def _factory(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
        }
        defaults.update(kwargs)
        return defaults
    return _factory

@pytest.fixture
def sample_user(test_client, user_data):
    """Pre-created user untuk testing."""
    data = user_data()
    response = test_client.post("/api/users/", json=data)
    return response.json()

# Optional: Uncomment untuk isolated DB
# @pytest.fixture(scope="function")
# def db(db_engine):
#     with Session(db_engine) as session:
#         yield session
#         session.rollback()
```

---

## ❓ FAQ

**Q: Apakah override mempengaruhi tests di folder lain?**
A: Tidak. Override hanya berlaku untuk tests di directory tersebut dan child directories.

**Q: Bisa override fixture dari pytest built-in?**
A: Ya! Contoh: `tmp_path`, `monkeypatch`, dll.

**Q: Bagaimana cara debug fixture mana yang dipakai?**
A: Gunakan `pytest --fixtures-per-test` atau add print di fixture.

**Q: Bisa ada multiple levels of override?**
A: Ya! Contoh:
```
tests/integration/conftest.py → db() with scope=session
tests/integration/todos/conftest.py → db() with scope=function
tests/integration/todos/special/conftest.py → db() with custom rollback
```

**Q: Kapan TIDAK menggunakan override?**
A: Ketika behavior yang diinginkan bisa dicapai dengan:
- Factory parameters
- Test parametrization
- Conditional logic dalam centralized fixture

---

**Selamat mencoba! 🚀**
