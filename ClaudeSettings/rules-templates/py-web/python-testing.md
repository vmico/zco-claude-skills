# Python 测试规则

## Python 测试基础规范

### 文件命名

**规则：测试文件必须以 `test_` 开头。**

```
user_service.py       → test_user_service.py
validator.py          → test_validator.py
models/user.py        → tests/test_models/test_user.py
```

### 测试函数签名

**规则：测试函数必须符合 pytest 规范。**

```python
## ✓ 正确
def test_register_user():
    pass

def test_register_user_valid_input():
    pass

## ❌ 错误
def register_user_test():  ## 不以 test_ 开头
    pass

class TestUserService:  ## 测试类必须以 Test 开头
    def test_register(self):  ## 测试方法以 test_ 开头
        pass
```

### 包声明

**规则：测试文件放在 `tests/` 目录中，可以独立为包。**

```
tests/
├── __init__.py
├── conftest.py          ## pytest 配置和 fixtures
├── unit/
│   ├── __init__.py
│   ├── test_user_service.py
│   └── test_validator.py
└── integration/
    ├── __init__.py
    └── test_database.py
```

---

## pytest 基础

### 基本断言

```python
import pytest

def test_basic_assertions():
    ## 基本断言
    assert 1 + 1 == 2
    assert "hello" in "hello world"
    assert True is True
    assert None is None
    
    ## 异常断言
    with pytest.raises(ValueError):
        int("not a number")
    
    ## 异常断言并检查消息
    with pytest.raises(ValueError, match="invalid literal"):
        int("not a number")
```

### 推荐使用 pytest

**安装：**
```bash
pip install pytest pytest-cov pytest-asyncio
```

**使用：**
```python
import pytest
from myapp.user_service import create_user

def test_create_user():
    user = create_user("test@example.com", "Pass123!")
    
    ## 基本断言
    assert user is not None
    assert user.email == "test@example.com"
    assert user.id is not None
    assert len(user.id) > 0
```

### 推荐 Fixtures

**使用 fixtures 进行测试准备：**

```python
import pytest
from myapp.database import Database

## 模块级别 fixture
@pytest.fixture(scope="module")
def database():
    db = Database(":memory:")
    db.setup_tables()
    yield db
    db.cleanup()

## 函数级别 fixture
@pytest.fixture
def fresh_user():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

## 使用 fixture
def test_create_user(database, fresh_user):
    user_id = database.create_user(fresh_user)
    assert user_id is not None
    
    user = database.get_user(user_id)
    assert user["email"] == fresh_user["email"]
```

---

## 参数化测试（Parametrize）

**pytest 推荐的测试模式，适合测试多个相似场景。**

### 基本结构

```python
import pytest
from myapp.validator import validate_email

@pytest.mark.parametrize("email,expected_valid", [
    ("user@example.com", True),
    ("test.user@domain.org", True),
    ("user+tag@example.com", True),
    ("invalid", False),
    ("missing@", False),
    ("@domain.com", False),
    ("", False),
    (None, False),
])
def test_validate_email(email, expected_valid):
    result = validate_email(email)
    assert result is expected_valid

## 多个参数
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert a + b == expected
```

### 参数化测试命名

```python
@pytest.mark.parametrize(
    "email,expected",
    [
        ("user@example.com", True),
        ("invalid", False),
    ],
    ids=["valid_email", "invalid_email"]  ## 自定义测试名称
)
def test_validate_email(email, expected):
    pass

## 或使用 lambda
@pytest.mark.parametrize("email,expected", [
    pytest.param("user@example.com", True, id="valid"),
    pytest.param("invalid", False, id="missing_at"),
])
def test_validate_email(email, expected):
    pass
```

---

## 测试组织

### 测试类组织

**使用类组织相关测试：**

```python
class TestUserService:
    """用户服务测试类。"""
    
    def test_create_user_success(self):
        pass
    
    def test_create_user_duplicate_email(self):
        pass
    
    def test_create_user_invalid_password(self):
        pass

class TestUserAuthentication:
    """用户认证测试类。"""
    
    def test_login_success(self):
        pass
    
    def test_login_wrong_password(self):
        pass
    
    def test_login_nonexistent_user(self):
        pass
```

### 子测试（Subtests）

**使用 pytest-subtests 插件：**

```python
import pytest

def test_user_service():
    users = [
        {"email": "user1@example.com", "password": "Pass123!"},
        {"email": "user2@example.com", "password": "Pass456!"},
    ]
    
    for user_data in users:
        with pytest.subtest(email=user_data["email"]):
            user = create_user(**user_data)
            assert user.email == user_data["email"]
```

---

## 测试辅助函数

### Setup 和 Teardown

**使用 fixtures 进行测试准备和清理：**

```python
import pytest
import tempfile
import os

## 函数级别
@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)

## 类级别
@pytest.fixture(scope="class")
def class_resource():
    resource = ExpensiveResource()
    yield resource
    resource.cleanup()

## 模块级别
@pytest.fixture(scope="module")
def database():
    db = create_test_database()
    yield db
    db.drop_all()

## 使用
def test_with_temp_file(temp_file):
    with open(temp_file, 'w') as f:
        f.write("test data")
```

### 测试辅助函数命名

**辅助函数应该以 `_` 开头，避免被识别为测试函数。**

```python
## ✓ 正确：辅助函数
def _create_test_user(email: str = "test@example.com") -> User:
    """创建测试用户辅助函数。"""
    return User(email=email, password="Pass123!")

def _cleanup_test_data():
    """清理测试数据辅助函数。"""
    db.execute("DELETE FROM users WHERE email LIKE '%test%'")

## 在测试中使用
def test_user_operations():
    user = _create_test_user()
    ## ...
    _cleanup_test_data()
```

---

## Mock 和 Patch

### 使用 unittest.mock

**标准库 mock：**

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    ## 创建 mock 对象
    mock_repo = Mock()
    mock_repo.get_user.return_value = {"id": 1, "name": "Test"}
    
    service = UserService(mock_repo)
    user = service.get_user(1)
    
    assert user["name"] == "Test"
    mock_repo.get_user.assert_called_once_with(1)

## 使用 patch
def test_send_email():
    with patch("myapp.services.smtp_client.send") as mock_send:
        mock_send.return_value = True
        
        result = send_welcome_email("user@example.com")
        
        assert result is True
        mock_send.assert_called_once()

## patch 装饰器
@patch("myapp.services.user_repository")
def test_create_user(mock_repo):
    mock_repo.create.return_value = {"id": 1}
    
    user = create_user("test@example.com")
    
    assert user["id"] == 1
```

### Mock 最佳实践

```python
## ✅ 正确：只 mock 外部依赖
@patch("myapp.services.requests.get")
def test_fetch_user(mock_get):
    mock_get.return_value.json.return_value = {"id": 1}
    
    user = fetch_user_from_api(1)
    
    assert user["id"] == 1
    mock_get.assert_called_with("https://api.example.com/users/1")

## ❌ 错误：mock 被测代码
@patch("myapp.services.UserService.get_user")  ## 不要这样
def test_user_service(mock_get_user):
    pass
```

---

## Python 特定的测试技巧

### 1. 使用接口进行 Mock

**定义协议或抽象基类：**

```python
from typing import Protocol
from abc import ABC, abstractmethod

## 使用 Protocol（Python 3.8+）
class UserRepository(Protocol):
    def get_user(self, user_id: int) -> dict:
        ...
    
    def save_user(self, user: dict) -> None:
        ...

## 或使用 ABC
class AbstractUserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> dict:
        pass

## 服务依赖接口
def get_user_service(repo: UserRepository, user_id: int) -> dict:
    return repo.get_user(user_id)

## 测试中可以使用任何实现
class FakeUserRepository:
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Fake"}

def test_get_user_service():
    fake_repo = FakeUserRepository()
    user = get_user_service(fake_repo, 1)
    assert user["id"] == 1
```

### 2. 测试异步代码

**使用 pytest-asyncio：**

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_fetch_data()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_mock():
    with patch("myapp.async_client.fetch") as mock_fetch:
        mock_fetch.return_value = {"data": "test"}
        
        result = await async_fetch_data()
        
        assert result["data"] == "test"

## 测试并发
@pytest.mark.asyncio
async def test_concurrent_access():
    counter = SafeCounter()
    
    tasks = [
        asyncio.create_task(counter.increment())
        for _ in range(100)
    ]
    
    await asyncio.gather(*tasks)
    
    assert counter.value == 100
```

### 3. 测试异常

```python
import pytest

def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_custom_exception():
    with pytest.raises(ValueError, match="invalid email"):
        validate_email("invalid")

def test_exception_with_details():
    with pytest.raises(ValueError) as exc_info:
        process_order(None)
    
    assert "order cannot be None" in str(exc_info.value)
    assert exc_info.type is ValueError
```

### 4. 使用 Testdata 目录

**Python 约定：测试数据放在 `tests/data/` 或 `testdata/` 目录中。**

```
tests/
├── test_user.py
└── data/
    ├── valid_user.json
    ├── invalid_user.json
    └── test_config.yaml
```

```python
import json
import pytest
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def test_load_user():
    with open(DATA_DIR / "valid_user.json") as f:
        data = json.load(f)
    
    user = User.from_dict(data)
    assert user.email == data["email"]

## 使用 fixture
@pytest.fixture
def valid_user_data():
    with open(DATA_DIR / "valid_user.json") as f:
        return json.load(f)

def test_create_user_from_data(valid_user_data):
    user = User.from_dict(valid_user_data)
    assert user.is_valid()
```

---

## Fixtures 进阶

### conftest.py

**共享 fixtures：**

```python
## tests/conftest.py
import pytest
from myapp.database import Database

@pytest.fixture(scope="session")
def db():
    """整个测试会话共享的数据库。"""
    database = Database("postgresql://localhost/test")
    database.create_tables()
    yield database
    database.drop_all()

@pytest.fixture
def db_transaction(db):
    """每个测试在独立事务中运行。"""
    transaction = db.begin_transaction()
    yield db
    transaction.rollback()

@pytest.fixture
def test_user(db_transaction):
    """创建一个测试用户。"""
    user = db_transaction.create_user(
        email="test@example.com",
        name="Test User"
    )
    return user
```

### Fixture 工厂模式

```python
@pytest.fixture
def create_user(db):
    """返回一个创建用户的工厂函数。"""
    created_users = []
    
    def _create_user(email: str, **kwargs):
        user = db.create_user(email=email, **kwargs)
        created_users.append(user)
        return user
    
    yield _create_user
    
    ## 清理
    for user in created_users:
        db.delete_user(user.id)

def test_multiple_users(create_user):
    user1 = create_user("user1@example.com")
    user2 = create_user("user2@example.com")
    
    assert user1.id != user2.id
```

---

## pytest 命令

### 基本命令

```bash
## 运行所有测试
pytest

## 运行并显示详细输出
pytest -v

## 运行特定文件
pytest tests/test_user.py

## 运行特定测试
pytest tests/test_user.py::test_create_user

## 运行特定类
pytest tests/test_user.py::TestUserService

## 运行匹配关键字的测试
pytest -k "create_user"

## 运行不包含关键字的测试
pytest -k "not slow"
```

### 覆盖率

```bash
## 显示覆盖率
pytest --cov=myproject tests/

## 生成覆盖率报告
pytest --cov=myproject --cov-report=html tests/

## 查看覆盖率详情
pytest --cov=myproject --cov-report=term-missing tests/
```

### 其他有用参数

```bash
## 失败时停止
pytest -x

## 失败前最多运行 N 个测试
pytest --maxfail=3

## 按节点 ID 运行
pytest --collect-only  ## 列出所有测试

## 并行运行测试（需要 pytest-xdist）
pytest -n auto

## 重跑失败的测试（需要 pytest-rerunfailures）
pytest --reruns 3

## 只运行上次失败的测试
pytest --lf

## 先运行上次失败的测试，然后运行其他
pytest --ff
```

---

## 测试组织最佳实践

### 1. 文件组织

```
tests/
├── conftest.py              ## 共享 fixtures
├── unit/                    ## 单元测试
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/             ## 集成测试
│   ├── test_database.py
│   └── test_api.py
├── e2e/                     ## 端到端测试
│   └── test_workflows.py
└── data/                    ## 测试数据
    ├── users.json
    └── orders.json
```

### 2. 使用标记分类测试

```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    pass

@pytest.mark.integration
def test_database_connection():
    pass

@pytest.mark.api
def test_http_endpoints():
    pass
```

```bash
## 只运行单元测试（跳过慢速和集成测试）
pytest -m "not slow and not integration"

## 只运行集成测试
pytest -m integration

## 运行 API 测试
pytest -m api
```

### 3. 配置 pytest.ini

```ini
## pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    api: marks tests as API tests
```

---

## 常见陷阱

### ❌ 陷阱 1：共享状态

```python
## ❌ 错误：测试间共享状态
test_users = []

def test_create_user():
    user = create_user("test@example.com")
    test_users.append(user)

def test_update_user():
    ## 依赖上一个测试
    update_user(test_users[0], "new@example.com")

## ✓ 正确：每个测试独立
def test_update_user():
    user = create_user("test@example.com")
    update_user(user, "new@example.com")
```

### ❌ 陷阱 2：忽略异常

```python
## ❌ 错误
def test_create_user():
    user, _ = create_user("test@example.com")  ## 忽略错误
    assert user is not None

## ✓ 正确
def test_create_user():
    user = create_user("test@example.com")
    assert user is not None
    assert user.email == "test@example.com"
```

### ❌ 陷阱 3：不使用 fixtures

```python
## ❌ 错误：重复代码
def test_create_user():
    db = Database(":memory:")
    db.setup()
    user = db.create_user("test@example.com")
    assert user is not None

def test_delete_user():
    db = Database(":memory:")  ## 重复！
    db.setup()
    user = db.create_user("test@example.com")
    db.delete_user(user.id)
    assert db.get_user(user.id) is None

## ✓ 正确：使用 fixtures
@pytest.fixture
def db():
    database = Database(":memory:")
    database.setup()
    return database

def test_create_user(db):
    user = db.create_user("test@example.com")
    assert user is not None

def test_delete_user(db):
    user = db.create_user("test@example.com")
    db.delete_user(user.id)
    assert db.get_user(user.id) is None
```

### ❌ 陷阱 4：过度 mock

```python
## ❌ 错误：mock 太多
def test_user_service():
    with patch("module.a") as mock_a, \
         patch("module.b") as mock_b, \
         patch("module.c") as mock_c:
        ## 测试失去了意义
        pass

## ✓ 正确：只 mock 外部依赖
@patch("requests.get")
def test_api_client(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
    result = api_client.fetch()
    assert result["data"] == "test"
```

---

## 测试覆盖率目标

- **包级别**：≥ 80%
- **关键业务逻辑**：≥ 90%
- **公共 API**：100%
- **错误处理路径**：≥ 80%

## 质量检查清单

- [MUST] 所有测试文件以 `test_` 开头
- [MUST] 测试函数以 `test_` 开头
- [ ] 使用参数化测试处理多个场景
- [ ] 使用 fixtures 共享测试资源
- [ ] 辅助函数使用 `_` 前缀
- [ ] 不忽略异常返回值
- [ ] 测试相互独立
- [ ] 覆盖率达标
- [ ] 测试执行快速
