# Node.js 项目编程标准

## 注释规范

### 注释类型区分（核心约定）

本项目使用不同的注释标记来区分注释的用途：

#### 1. 代码功能注释 `//; `
**用途**：解释代码的功能、逻辑、算法，与纯代码注释 `//` 区分

**使用场景**：
- 解释复杂的业务逻辑
- 说明算法实现思路
- 阐述为什么这样写（设计决策）
- JSDoc/TSDoc 文档注释

**示例**：
```javascript
//; 计算订单折扣
//; 折扣规则：
//; - VIP 用户：订单金额的 15%
//; - 普通用户：订单金额的 10%
//; - 订单金额 < 100 元不享受折扣
function calculateDiscount(amount, userLevel) {
  //; 小额订单不参与折扣活动
  if (amount < 100) {
    return 0;
  }

  //; 根据用户等级计算折扣率
  const rate = userLevel === 'VIP' ? 0.15 : 0.10;
  
  return amount * rate;
}
```

#### 2. 非代码注释 `//;@`
**用途**：元信息、开发备注、待办事项、调试信息

**使用场景**：
- `//;@TODO:` - 待实现的功能
- `//;@FIXME:` - 需要修复的问题
- `//;@NOTE:` - 开发者备注
- `//;@HACK:` - 临时解决方案
- `//;@OPTIMIZE:` - 性能优化点
- `//;@DEPRECATED:` - 已废弃的代码
- `//;@DEBUG:` - 调试信息
- `//;@XXX:` - 需要注意的问题

**示例**：
```javascript
function processOrder(order) {
  //;@TODO: 添加订单金额验证
  //;@NOTE: 这里需要考虑并发安全问题

  // 计算订单总金额
  const total = calculateTotal(order);

  //;@FIXME: Redis 连接偶尔会超时，需要添加重试机制
  await cache.set(order.id, total);

  //;@HACK: 临时方案，等待支付网关 API 升级后移除
  if (order.paymentMethod === 'alipay_v1') {
    return processLegacyAlipay(order);
  }

  //;@OPTIMIZE: 这里可以使用批量查询减少数据库访问
  for (const item of order.items) {
    const product = await db.getProduct(item.productId);
    //; 处理商品...
  }
}

//;@DEPRECATED: 使用 processOrderV2 替代
//;@此函数将在 v2.0 版本移除
function processOrderLegacy(order) {
  // ...
}
```

#### 3. 注释使用原则

**强制规则（MUST）**：
- ✅ 所有公共函数、类、模块必须有 JSDoc/TSDoc 注释
- ✅ 复杂逻辑必须有解释注释（使用 `//;`）
- ✅ 所有 TODO、FIXME 等必须使用 `//;` 前缀
- ✅ 调试注释、临时备注必须使用 `//;` 前缀
- ❌ 禁止用注释注释掉代码（应该删除或使用 Git）

**推荐规则（SHOULD）**：
- 注释应该解释"为什么"而不是"是什么"
- 代码应该自解释，减少不必要的注释
- 注释应该与代码保持同步更新

**注释检查工具**：
```bash
# 查找所有非代码注释
grep -r "//;" . --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx"

# 查找所有 TODO
grep -r "//;@TODO:" . --include="*.js" --include="*.ts"

# 查找所有需要修复的问题
grep -r "//;@FIXME:" . --include="*.js" --include="*.ts"

# 查找已废弃的代码
grep -r "//;@DEPRECATED:" . --include="*.js" --include="*.ts"
```

---

## 命名规范

### 文件命名

**规则**：
- 使用小写单词，使用连字符或下划线分隔
- 测试文件以 `.test.js` 或 `.spec.js` 结尾
- TypeScript 文件使用 `.ts` 或 `.tsx`

**示例**：
```javascript
✅ user-service.js
✅ user_service.js
✅ user-service.test.js
✅ user-service.spec.ts

❌ userService.js  // 应该使用连字符或下划线
❌ UserService.js  // 不要大写开头
```

### 变量命名

**规则**：
- 使用 camelCase（驼峰命名法）
- 常量使用 UPPER_SNAKE_CASE
- 私有变量使用下划线前缀（约定俗成）
- 布尔变量使用 `is`、`has`、`can`、`should` 等前缀

**示例**：
```javascript
// 普通变量
const userName = 'John';
let orderCount = 10;

// 常量
const MAX_RETRY_COUNT = 3;
const DEFAULT_TIMEOUT = 30000;

// 私有变量（约定）
class User {
  constructor() {
    this._internalId = generateId();  // 私有
    this.name = '';                    // 公共
  }
}

// 布尔变量
const isActive = true;
const hasPermission = checkPermission(user);
const canEdit = user.role === 'admin';
const shouldRetry = error.code === 'ETIMEOUT';
```

### 函数命名

**规则**：
- 使用 camelCase
- 动词开头，表达清晰的动作
- 布尔返回值的函数以 `is`、`has`、`can` 等开头
- 异步函数使用 `async` 关键字

**示例**：
```javascript
// 普通函数
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

const sendEmail = (to, body) => {
  // ...
};

// 异步函数
async function fetchUser(userId) {
  const response = await api.get(`/users/${userId}`);
  return response.data;
}

// 布尔函数
function isValidEmail(email) {
  return email.includes('@');
}

function hasPermission(user, resource) {
  return user.permissions.includes(resource);
}

// 工厂函数
function createUser(data) {
  return new User(data);
}
```

### 类命名

**规则**：
- 使用 PascalCase（大驼峰）
- 名词或名词短语
- 单数形式

**示例**：
```javascript
// 类
class User {
  constructor(name, email) {
    this.name = name;
    this.email = email;
  }
}

class OrderService {
  async createOrder(data) {
    // ...
  }
}

class UserRepository {
  async findById(id) {
    // ...
  }
}

// 继承
class AdminUser extends User {
  constructor(name, email) {
    super(name, email);
    this.role = 'admin';
  }
}
```

### 接口/类型命名（TypeScript）

**规则**：
- 使用 PascalCase
- 接口不使用 `I` 前缀（现代 TypeScript 风格）
- 类型别名使用 PascalCase
- 泛型参数使用单个大写字母

**示例**：
```typescript
// 接口
interface User {
  id: string;
  name: string;
  email: string;
}

interface Repository<T> {
  findById(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
  delete(id: string): Promise<void>;
}

// 类型别名
type UserId = string;
type Email = string;
type UserOrNull = User | null;

// 联合类型
type Status = 'pending' | 'active' | 'inactive';

// 泛型
function wrapInArray<T>(value: T): T[] {
  return [value];
}

// 映射类型
type ReadonlyUser = Readonly<User>;
type PartialUser = Partial<User>;
```

### 枚举命名

**规则**：
- 枚举名使用 PascalCase
- 枚举成员使用 PascalCase 或 UPPER_SNAKE_CASE

**示例**：
```typescript
// PascalCase 成员（推荐）
enum OrderStatus {
  Pending = 'pending',
  Paid = 'paid',
  Shipped = 'shipped',
  Completed = 'completed',
  Cancelled = 'cancelled',
}

// UPPER_SNAKE_CASE 成员
enum HttpStatusCode {
  OK = 200,
  NOT_FOUND = 404,
  SERVER_ERROR = 500,
}
```

---

## 代码组织

### 文件结构

**标准文件顺序**：
```javascript
/**
 * @fileoverview 用户服务模块
 * @module services/user
 */

// 1. 导入语句分组（内置模块 -> 第三方模块 -> 本项目）
// 内置模块
const path = require('path');
const fs = require('fs').promises;

// 第三方模块
const express = require('express');
const axios = require('axios');

// 本项目模块
const { User } = require('../models');
const { logger } = require('../utils');

// 2. 常量定义
const MAX_NAME_LENGTH = 50;
const DEFAULT_TIMEOUT = 30000;

// 3. 类型定义（TypeScript）
/**
 * @typedef {Object} CreateUserRequest
 * @property {string} name
 * @property {string} email
 */

// 4. 类定义
class UserService {
  constructor(repository) {
    this.repository = repository;
  }

  /**
   * 创建新用户
   * @param {CreateUserRequest} data
   * @returns {Promise<User>}
   */
  async create(data) {
    //; 验证用户数据
    this.validate(data);
    
    //; 检查邮箱是否已存在
    const existing = await this.repository.findByEmail(data.email);
    if (existing) {
      throw new Error('Email already exists');
    }
    
    return this.repository.save(data);
  }

  validate(data) {
    if (!data.name || !data.email) {
      throw new Error('Name and email are required');
    }
  }
}

// 5. 函数定义
async function getUserById(id) {
  // ...
}

// 6. 导出
module.exports = { UserService };
// 或 ES Module
export { UserService };
export default UserService;
```

### 项目结构

**推荐的项目结构**：
```
my-project/
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript 配置
├── README.md              # 项目说明
├── src/                   # 源代码
│   ├── index.js           # 入口文件
│   ├── app.js             # 应用实例
│   ├── config/            # 配置文件
│   ├── controllers/       # 控制器
│   ├── services/          # 业务逻辑
│   ├── repositories/      # 数据访问
│   ├── models/            # 数据模型
│   ├── middlewares/       # 中间件
│   ├── utils/             # 工具函数
│   └── routes/            # 路由定义
├── tests/                 # 测试代码
├── scripts/               # 脚本文件
└── docs/                  # 文档
```

**分层原则**：
```javascript
// ✅ 推荐：清晰的分层
Controller -> Service -> Repository -> Database

// ❌ 禁止：跨层调用
Controller -> Repository (跳过 Service)
```

---

## 类型系统（TypeScript）

### 基本使用

**规则**：
- 所有函数参数和返回值必须添加类型注解
- 使用 `strict` 模式
- 避免使用 `any`

**示例**：
```typescript
// 基本类型
function greet(name: string): string {
  return `Hello, ${name}`;
}

// 可选参数和默认值
function createUser(
  name: string,
  email: string,
  age?: number,
  isActive: boolean = true
): User {
  return { name, email, age, isActive };
}

// 联合类型
function formatValue(value: string | number): string {
  return String(value);
}

// Promise 类型
async function fetchUser(id: string): Promise<User> {
  const response = await api.get<User>(`/users/${id}`);
  return response.data;
}
```

### 接口 vs 类型别名

**推荐**：
- 对象形状使用 `interface`（可扩展）
- 联合类型使用 `type`

**示例**：
```typescript
// 接口 - 可扩展
interface User {
  id: string;
  name: string;
}

// 类型别名 - 联合类型
type Status = 'active' | 'inactive' | 'pending';
type ID = string | number;
```

---

## 错误处理

### 错误类型

**规则**：
- 创建自定义错误类继承 `Error`
- 错误类名以 `Error` 结尾
- 提供有意义的错误信息

**示例**：
```javascript
// 基础应用错误
class AppError extends Error {
  constructor(message, code = 'INTERNAL_ERROR', statusCode = 500) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}

// 具体错误类型
class ValidationError extends AppError {
  constructor(message) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}

class NotFoundError extends AppError {
  constructor(resource) {
    super(`${resource} not found`, 'NOT_FOUND', 404);
  }
}

// 使用
async function getUser(id) {
  const user = await db.users.findById(id);
  if (!user) {
    throw new NotFoundError('User');
  }
  return user;
}
```

### 异步错误处理

**推荐模式**：
```javascript
// ✅ 推荐：使用 try-catch
async function processOrder(orderData) {
  try {
    //; 验证订单数据
    validateOrder(orderData);
    
    //; 检查库存
    await checkInventory(orderData);
    
    //; 处理支付
    await processPayment(orderData);
    
    return { success: true };
  } catch (error) {
    //;@NOTE: 记录错误日志
    logger.error('Failed to process order', { error, orderData });
    throw new AppError('Order processing failed', 'ORDER_ERROR', 500);
  }
}

// ✅ Express 错误处理中间件
app.use((err, req, res, next) => {
  logger.error('Unhandled error', err);
  
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.code,
      message: err.message,
    });
  }
  
  res.status(500).json({
    error: 'INTERNAL_ERROR',
    message: 'Internal server error',
  });
});
```

---

## 异步编程

### Promise 和 Async/Await

**规则**：
- 优先使用 `async/await` 而不是 Promise 链
- 使用 `Promise.all` 进行并发操作
- 正确处理错误

**示例**：
```javascript
// ✅ 推荐：使用 async/await
async function fetchUserData(userId) {
  try {
    const user = await db.users.findById(userId);
    const orders = await db.orders.findByUserId(userId);
    return { user, orders };
  } catch (error) {
    logger.error('Failed to fetch user data', { userId, error });
    throw error;
  }
}

// ✅ 并发执行
async function fetchMultipleUsers(userIds) {
  //;@NOTE: 使用 Promise.all 并发执行
  const users = await Promise.all(
    userIds.map(id => fetchUser(id))
  );
  return users;
}
```

---

## 测试规范

### 测试框架

**使用 Jest**（推荐）：
```javascript
// user.service.test.js
const { UserService } = require('./user.service');

jest.mock('../repositories/user.repository');

describe('UserService', () => {
  let userService;
  let mockRepository;
  
  beforeEach(() => {
    mockRepository = {
      findById: jest.fn(),
      save: jest.fn(),
    };
    userService = new UserService(mockRepository);
  });
  
  describe('create', () => {
    it('should create a new user successfully', async () => {
      // Arrange
      const userData = { name: 'John', email: 'john@example.com' };
      mockRepository.findByEmail.mockResolvedValue(null);
      mockRepository.save.mockResolvedValue({ id: '1', ...userData });
      
      // Act
      const result = await userService.create(userData);
      
      // Assert
      expect(result).toHaveProperty('id');
      expect(result.email).toBe(userData.email);
    });
    
    it('should throw error if email already exists', async () => {
      const userData = { name: 'John', email: 'john@example.com' };
      mockRepository.findByEmail.mockResolvedValue({ id: '1', ...userData });
      
      await expect(userService.create(userData))
        .rejects
        .toThrow('Email already exists');
    });
  });
});
```

### 测试覆盖率

**要求**：
- 单元测试覆盖率 ≥ 80%
- 关键业务逻辑覆盖率 ≥ 95%

---

## 性能优化

### 字符串拼接

**规则**：
- 使用模板字符串而不是 `+` 拼接
- 大量拼接时使用数组 `join`

**示例**：
```javascript
// ✅ 模板字符串
const message = `Hello, ${name}! You have ${count} messages.`;

// ✅ 数组 join（大量数据）
const lines = [];
for (const item of items) {
  lines.push(process(item));
}
const result = lines.join('\n');

// ❌ 避免：循环中使用 +=
let result = '';
for (const item of items) {
  result += item + ',';
}
```

### 异步优化

```javascript
// ✅ 使用 Promise.all 并发
async function fetchDashboardData() {
  const [users, orders, stats] = await Promise.all([
    fetchUsers(),
    fetchOrders(),
    fetchStats(),
  ]);
  return { users, orders, stats };
}
```

---

## 代码审查清单

### 提交前检查

**必须检查项**：
- [ ] 代码已格式化（`prettier` 或 `eslint --fix`）
- [ ] 通过 ESLint 检查
- [ ] 通过类型检查（如果使用 TypeScript）
- [ ] 所有测试通过
- [ ] 测试覆盖率达标（≥ 80%）
- [ ] 注释使用正确的标记（`//;` vs `//;@`）
- [ ] 所有 `//;@TODO` 和 `//;@FIXME` 都已记录

**推荐检查项**：
- [ ] 函数长度 ≤ 50 行
- [ ] 圈复杂度 ≤ 10
- [ ] 没有重复代码
- [ ] 错误处理完整

---

## 工具配置

### ESLint 配置

创建 `.eslintrc.js`：
```javascript
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
  ],
  plugins: ['@typescript-eslint'],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  env: {
    node: true,
    es2022: true,
    jest: true,
  },
  rules: {
    'no-console': 'warn',
    'no-unused-vars': 'error',
  },
};
```

### Prettier 配置

创建 `.prettierrc`：
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

---

## 总结

本编程标准的核心要点：

1. **注释区分**：
   - `//` - 纯代码注释
   - `//; ` - 功能注释（解释代码逻辑）
   - `//;@` - 元信息注释（TODO、FIXME、NOTE、HACK、OPTIMIZE、DEPRECATED、DEBUG、XXX）

2. **命名规范**：
   - 变量/函数：camelCase
   - 类/接口：PascalCase
   - 常量：UPPER_SNAKE_CASE
   - 文件：kebab-case 或 snake_case

3. **代码质量**：
   - 函数长度 ≤ 50 行
   - 圈复杂度 ≤ 10
   - 测试覆盖率 ≥ 80%

**参考资源**：
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
