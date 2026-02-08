# Python 项目编程标准

## 注释规范

### 注释类型区分（核心约定）

本项目使用不同的注释标记来区分注释的用途：

#### 1. 代码功能说明注释(非代码) `##;`

**用途**：

- [关键]与纯代码注释 `#` 区分,
  - use `##;` to explain with natural language, 支持变体 `# #;` (black format style)
  - use `#` to comment the program code , usually for un-used code or temporary code.

**使用场景**：

- 解释复杂的业务逻辑
- 说明算法实现思路
- 阐述为什么这样写（设计决策）
- 模块、类、函数的文档字符串

**示例**：

```python
##; 计算订单折扣
##; 折扣规则：
##; - VIP 用户：订单金额的 15%
##; - 普通用户：订单金额的 10%
##; - 订单金额 < 100 元不享受折扣
def calculate_discount(amount: float, user_level: str) -> float:
    ##; 小额订单不参与折扣活动
    if amount < 100:
        return 0

    ##; 根据用户等级计算折扣率
    rate = 0.15 if user_level == "VIP" else 0.10

    return amount * rate
```

#### 2. 非代码注释 `##;@`

**用途**：元信息、开发备注、待办事项、调试信息

**使用场景**：

- `##;@TODO:` - 待实现的功能
- `##;@FIXME:` - 需要修复的问题
- `##;@NOTE:` - 开发者备注
- `##;@HACK:` - 临时解决方案
- `##;@OPTIMIZE:` - 性能优化点
- `##;@DEPRECATED:` - 已废弃的代码
- `##;@DEBUG:` - 调试信息
- `##;@XXX:` - 需要注意的问题

**示例**：

```python
def process_order(order: dict) -> None:
    ##;@TODO: 添加订单金额验证
    ##;@NOTE: 这里需要考虑并发安全问题

    ## 计算订单总金额
    total = calculate_total(order)

    ##;@FIXME: Redis 连接偶尔会超时，需要添加重试机制
    cache.set(order['id'], total)

    ##;@HACK: 临时方案，等待支付网关 API 升级后移除
    if order.get('payment_method') == 'alipay_v1':
        return process_legacy_alipay(order)

    ##;@OPTIMIZE: 这里可以使用批量查询减少数据库访问
    for item in order['items']:
        product = db.get_product(item['product_id'])
        ##; 处理商品...

##;@DEPRECATED: 使用 process_order_v2 替代
##;此函数将在 v2.0 版本移除
def process_order_legacy(order: dict) -> None:
    pass
```

#### 3. 注释使用原则

**强制规则（MUST）**：

- ✅ 所有模块、类、公共函数必须有文档字符串（使用 `"""`）
- ✅ 复杂逻辑必须有解释注释（使用 `##;`）
- ✅ 所有 TODO、FIXME 等必须使用 `##;` 前缀
- ✅ 用注释注释掉代码(调试注释、临时备注)使用 `#` 前缀
- ✅ 代码应该自解释, 如果代码比较清晰简单, 不需要添加注释.

**推荐规则（SHOULD）**：

- 注释应该解释"为什么"而不是"是什么"
- 注释应该与代码保持同步更新

**注释检查工具**：

```bash
# 查找所有非代码注释
grep -r "##;" . --include="*.py"

# 查找所有 TODO
grep -r "##;@TODO:" . --include="*.py"

# 查找所有需要修复的问题
grep -r "##;@FIXME:" . --include="*.py"

# 查找已废弃的代码
grep -r "##;@DEPRECATED:" . --include="*.py"
```

---

## 命名规范

### 模块命名

**规则**：

- 使用小写单词，使用下划线分隔
- 简短且有意义
- 避免使用泛化名称（util、common、base）

**示例**：

```python
✅ user_service.py
✅ payment_gateway.py
✅ cache_manager.py

❌ userService.py  # 应该用下划线
❌ utils.py       # 太泛化
```

### 变量命名

**规则**：

- 使用小写加下划线（snake_case）
- 私有变量使用单下划线前缀
- 强内部使用变量使用双下划线前缀
- 常量使用全大写加下划线

**示例**：

```python
# 普通变量
user_name = "John"
order_count = 10

# 私有变量
_internal_cache = {}

# 强私有变量（名称修饰）
__password_hash = ""

# 常量
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# 类属性
class User:
    MAX_LOGIN_ATTEMPTS = 5  # 类常量

    def __init__(self, name: str):
        self._name = name  # 保护属性
        self.__id = None   # 私有属性
```

### 函数命名

**规则**：

- 使用小写加下划线（snake_case）
- 动词开头，表达清晰的动作
- 布尔返回值的函数以 `is_`、`has_`、`can_`、`enable_`、`disable_` 等开头

**示例**：

```python
##; 普通函数
def calculate_total(items: list) -> float:
    pass

def send_email(to: str, body: str) -> None:
    pass

##; 布尔函数
def is_valid_email(email: str) -> bool:
    pass

def has_permission(user: dict, resource: str) -> bool:
    pass

def can_edit(user: dict) -> bool:
    pass

##; Getter/Setter
class User:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
```

### 类命名

**规则**：

- 使用大驼峰命名法（PascalCase）
- 抽象基类以 `Base` 或 `Abstract` 开头或结尾
- 异常类以 `Error` 或 `Exception` 结尾

**示例**：

```python
##; 普通类
class User:
    pass

class OrderService:
    pass
```

### 类型变量命名

**规则**：

- 使用大驼峰命名法
- 泛型类型变量使用 `T`、`K`、`V` 等单字母

**示例**：

```python
from typing import TypeVar, Generic

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Container(Generic[T]):
    def __init__(self, item: T) -> None:
        self._item = item
```

---

## 代码组织

### 文件结构

**标准文件顺序**：

```python
#!/usr/bin/env python3
##; 1. Shebang（可选）

##; 2. 模块文档字符串
"""
用户管理模块。

提供用户注册、登录、信息管理等功能。
"""

##; 3. 导入语句分组（标准库 -> 第三方库 -> 本项目）
##; 标准库
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict

##; 第三方库
import requests
from sqlalchemy import Column, Integer, String

##; 本项目
from myproject.models import Base
from myproject.utils import logger

##; 4. 常量定义
MAX_NAME_LENGTH = 50
DEFAULT_TIMEOUT = 30

##; 5. 类型别名（可选）
UserID = int
Email = str

##; 6. 异常定义
class UserNotFoundError(Exception):
    pass

##; 7. 类定义
class User(Base):
    """用户模型类。"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    # deleted_at = Column(DateTime, nullable=True)

    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email

    def validate(self) -> bool:
        ##; 验证用户数据
        return bool(self.name and self.email)

##; 8. 公共函数
def create_user(name: str, email: str) -> User:
    ##; 创建新用户
    user = User(name=name, email=email)
    ##; 验证用户数据
    if not user.validate():
        raise ValueError("Invalid user data")
    return user

##; 9. 私有函数
def _normalize_email(email: str) -> str:
    ##; 标准化邮箱地址
    return email.lower().strip()

##; 10. 主程序入口（可选）
if __name__ == '__main__':
    ##; 测试代码
    user = create_user("John", "john@example.com")
    print(user)
```

### 包结构

**推荐的项目结构**：

```
myproject/
├── pyproject.toml          # 项目配置
├── README.md               # 项目说明
├── LICENSE                 # 许可证文件 (可选)
├── Makefile                # 构建脚本 (可选)
├── src/                    # 源代码
│   └── myproject/
│       ├── __init__.py
│       ├── api/                # API层（路由层）
│       │   ├── __init__.py
│       │   ├── handlers/       # 请求/响应处理器
│       │   │   ├── error_handler.py
│       │   │   ├── request_parser.py
│       │   │   └── response_builder.py
│       │   ├── schemas/        # DTO定义（请求/响应模型）
│       │   │   ├── request/
│       │   │   │   ├── user_request.py
│       │   │   │   └── ...
│       │   │   └── response/
│       │   │       ├── user_response.py
│       │   │       └── ...
│       │   └── v1/             # API版本
│       │       ├── __init__.py
│       │       ├── users.py    # 用户相关路由
│       │       └── ...
│       ├── controllers/    # 业务逻辑
│       │   ├── __init__.py
│       │   └── user_service.py
│       ├── bus/            # 数据访问
│       │   ├── __init__.py
│       │   ├── database.py     # 数据库连接
│       │   ├── unit_of_work.py # 工作单元模式
│       │   └── redis_cache.py
│       ├── models/         # 数据模型
│       │   ├── __init__.py
│       │   └── user.py
│       ├── utils/          # 工具函数
│       │   ├── __init__.py
│       │   ├── logging.py
│       │   └── helpers.py
│       └── config.py       # 配置文件
├── tests/                  # 测试代码
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── docs/                   # 文档
├── misc/                   # 杂项文件
└── scripts/                # 脚本文件
```

**分层原则**：

```python
## ✅ 推荐：清晰的分层
handler -> service -> bus -> database
  |          |         |
  v          v         v
HTTP      业务逻辑    数据访问

## ❌ 禁止：跨层调用
handler -> bus (跳过 service)
handler -> database   (跳过 service 和 bus)
```

---

## 类型注解

### 基本使用

**规则**：

- 所有函数参数和返回值必须添加类型注解
- 使用 `typing` 模块中的类型
- 复杂类型使用类型别名

**示例**：

```python
from typing import Optional, List, Dict, Union, Callable

## 基本类型
def greet(name: str) -> str:
    return f"Hello, {name}"

## 可选类型
def find_user(user_id: int) -> Optional[dict]:
    ##; 可能返回 None
    pass

## 列表和字典
def process_users(users: List[dict]) -> Dict[str, int]:
    pass

## 联合类型
def parse_value(value: Union[str, int]) -> int:
    pass

## 或 Python 3.10+
def parse_value(value: str | int) -> int:
    pass

## 回调函数
def execute_callback(callback: Callable[[int], str]) -> None:
    pass
```

### 类方法类型注解

**示例**：

```python
from typing import Self  ## Python 3.11+

class User:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(name=data["name"], email=data["email"])

    def copy(self) -> "User":
        return User(name=self.name, email=self.email)
```

---

## 错误处理

### 异常定义

**规则**：

- 继承 `Exception` 或其子类创建自定义异常
- 异常类名以 `Error` 结尾
- 提供有意义的错误信息

**示例**：

```python
## 基础异常
class AppError(Exception):
    """应用基础异常。"""
    pass

## 具体异常
class ValidationError(AppError):
    """数据验证失败。"""
    pass

class UserNotFoundError(AppError):
    """用户不存在。"""
    pass

class DuplicateEmailError(AppError):
    """邮箱已存在。"""
    pass

## 使用异常链
def get_user(user_id: int) -> dict:
    try:
        user = db.find_by_id(user_id)
    except DatabaseError as e:
        ##;@NOTE: 使用 raise from 保留原始异常
        raise UserNotFoundError(f"User {user_id} not found") from e
    return user
```

### 错误处理模式

**推荐模式**：

```python
## ✅ 推荐：及早返回
def process_order(order: dict) -> None:
    if not validate_order(order):
        raise ValidationError("Invalid order data")

    if not check_inventory(order):
        raise InventoryError("Out of stock")

    if not process_payment(order):
        raise PaymentError("Payment failed")

    update_inventory(order)

## ❌ 避免：嵌套过深
def process_order(order: dict) -> None:
    if validate_order(order):
        if check_inventory(order):
            if process_payment(order):
                update_inventory(order)
            else:
                raise PaymentError("Payment failed")
        else:
            raise InventoryError("Out of stock")
    else:
        raise ValidationError("Invalid order data")
```

---

## 函数设计

### 函数长度

**规则**：

- 单个函数 ≤ 50 行（推荐）
- 圈复杂度 ≤ 10
- 参数数量 ≤ 5 个

**重构建议**：

```python
## ❌ 函数过长
def process_order(order: dict) -> None:
    ## 100+ 行代码...
    pass

## ✅ 拆分为多个小函数
def process_order(order: dict) -> None:
    validate_order(order)
    calculate_total(order)
    process_payment(order)
    update_inventory(order)

def validate_order(order: dict) -> None: pass
def calculate_total(order: dict) -> None: pass
def process_payment(order: dict) -> None: pass
def update_inventory(order: dict) -> None: pass
```

### 参数传递

**规则**：

- 超过 3 个参数考虑使用 dataclass 或字典
- 使用 `*` 强制关键字参数

**示例**：

```python
from dataclasses import dataclass

## ❌ 参数过多
def create_user(
    name: str,
    email: str,
    phone: str,
    address: str,
    city: str,
    country: str,
    age: int,
    is_active: bool
) -> dict:
    pass

## ✅ 使用 dataclass
@dataclass
class CreateUserRequest:
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "CN"
    age: Optional[int] = None
    is_active: bool = True

def create_user(req: CreateUserRequest) -> dict:
    pass

## ✅ 使用关键字参数
def create_user(
    name: str,
    email: str,
    *,
    phone: Optional[str] = None,
    address: Optional[str] = None
) -> dict:
    pass
```

---

## 异步编程

### async/await 使用

**规则**：

- 使用 `async def` 定义协程函数
- 使用 `await` 等待异步操作
- 使用 `asyncio` 管理事件循环

**示例**：

```python
import asyncio
from typing import AsyncGenerator

## ✅ 推荐：使用 async/await
async def fetch_user(user_id: int) -> dict:
    ##; 异步获取用户
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/api/users/{user_id}") as resp:
            return await resp.json()

## ✅ 并发执行
async def fetch_multiple_users(user_ids: List[int]) -> List[dict]:
    ##;@NOTE: 使用 asyncio.gather 并发执行
    tasks = [fetch_user(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)

## ✅ 异步上下文管理器
class DatabaseConnection:
    async def __aenter__(self):
        self.conn = await create_connection()
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        await self.conn.close()

## ✅ 异步生成器
async def fetch_users_in_batches() -> AsyncGenerator[dict, None]:
    offset = 0
    while True:
        batch = await db.fetch_users(limit=100, offset=offset)
        if not batch:
            break
        for user in batch:
            yield user
        offset += 100
```

---

## 测试规范

### 测试文件组织

**规则**：

- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 使用 pytest 框架

**示例**：

```python
## user_service.py
def validate_email(email: str) -> bool:
    return "@" in email

## test_user_service.py
import pytest
from user_service import validate_email

def test_validate_email_valid():
    assert validate_email("test@example.com") is True

def test_validate_email_missing_at():
    assert validate_email("testexample.com") is False

## 使用参数化测试
@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("user@domain.org", True),
    ("invalid", False),
    ("", False),
])
def test_validate_email(email: str, expected: bool):
    assert validate_email(email) is expected
```

### 测试覆盖率

**要求**：

- 单元测试覆盖率 ≥ 80%
- 关键业务逻辑覆盖率 ≥ 95%

**检查命令**：

```bash
## 运行测试并查看覆盖率
pytest --cov=src tests/

## 生成覆盖率报告
pytest --cov=src --cov-report=html tests/
```

---

## 性能优化

### 字符串拼接

**规则**：

- 少量拼接使用 `+` 或 f-string
- 循环中使用 `list` + `join()`
- 格式化使用 f-string

**示例**：

```python
## ✅ 少量拼接（f-string）
name = f"{first_name} {last_name}"

## ✅ 循环中拼接
items = []
for item in data:
    items.append(process(item))
result = ",".join(items)

## ❌ 避免：循环中使用 +=
result = ""
for item in data:
    result += item + ","  ## 每次都会创建新字符串
```

### 列表推导式

**规则**：

- 简单逻辑使用列表推导式
- 复杂逻辑使用普通循环

**示例**：

```python
## ✅ 简单推导
squares = [x**2 for x in range(10)]

## ✅ 带条件的推导
even_numbers = [x for x in range(100) if x % 2 == 0]

## ✅ 字典推导
user_map = {u["id"]: u for u in users}

## ❌ 避免：过于复杂的推导
result = [
    transform(x, y)
    for x in data1
    if x > 0
    for y in data2
    if y < 100
    if x + y % 2 == 0
]  ## 太难理解，应该用循环
```

---

## 代码审查清单

### 提交前检查

**必须检查项**：

- [MUST] 代码已格式化 , 统一使用 `autopep8` 忽略注释的风格, 如`autopep8 --in-place --aggressive --ignore=E265,E266,W291 your_script.py`, 如果使用 black 格式化, 建议忽略注释的风格, 如`black --skip-string-normalization your_script.py`
  
- [ ] 通过 linter 检查（`ruff check` 或 `pylint`）
- [ ] 通过类型检查（`mypy`）
- [ ] 所有测试通过（`pytest`）
- [ ] 测试覆盖率达标（≥ 80%）
- [ ] 注释使用正确的标记（`#` vs `##;` vs `##;@`）
- [ ] 所有 `##;@TODO` 和 `##;@FIXME` 都已记录

**推荐检查项**：

- [ ] 函数长度 ≤ 50 行
- [ ] 圈复杂度 ≤ 10
- [ ] 没有重复代码
- [ ] 错误处理完整
- [ ] 类型注解完整

---

## 工具配置

### Ruff 配置

创建 `pyproject.toml`：

```toml
[tool.ruff]
target-version = "py310"  ## Python 版本
line-length = 100

[tool.ruff.lint]
select = [
    "E",   ## pycodestyle errors
    "F",   ## Pyflakes
    "I",   ## isort
    "N",   ## pep8-naming
    "W",   ## pycodestyle warnings
    "UP",  ## pyupgrade
    "B",   ## flake8-bugbear
    "C4",  ## flake8-comprehensions
    "SIM", ## flake8-simplify
]
ignore = ["E501"]  ## 行长度由 formatter 处理

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### MyPy 配置

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
warn_redundant_casts = true
warn_unused_ignores = true
show_error_codes = true
```

### VS Code 配置

创建 `.vscode/settings.json`：

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "
}
```

---

## 总结

本编程标准的核心要点：

1. **注释区分**：
   - `##` 用于纯代码注释
   - `##;` 用于代码功能注释
   - `##;@` 用于 TODO、FIXME、DEBUG 等元信息

2. **代码质量**：
   - 函数长度 ≤ 50 行
   - 圈复杂度 ≤ 10
   - 测试覆盖率 ≥ 80%

3. **类型注解**：
   - 所有函数参数和返回值必须添加类型注解
   - 使用 mypy 进行类型检查

4. **错误处理**：
   - 使用自定义异常类
   - 及早返回，避免嵌套
   - 使用 `raise from` 保留异常链

5. **测试要求**：
   - 使用 pytest 框架
   - 使用参数化测试
   - 确保测试覆盖率

**参考资源**：

- [PEP 8 - Python Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Python Type Checking Guide](https://realpython.com/python-type-checking/)
