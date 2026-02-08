# Node.js 测试规则

## 测试基础规范

### 文件命名

**规则：测试文件必须以 `.test.js` 或 `.spec.js` 结尾。**

```
user-service.js       → user-service.test.js
validator.js          → validator.spec.js
src/models/user.js    → src/models/user.test.js
```

### 测试函数命名

**规则：测试描述应该清晰表达测试意图。**

```javascript
// ✓ 正确
describe('UserService', () => {
  it('should create a new user successfully', () => {});
  it('should throw error when email already exists', () => {});
  it('should validate user data before saving', () => {});
});

// ❌ 错误
describe('UserService', () => {
  it('test1', () => {});  // 描述不清
  it('works', () => {});  // 太模糊
});
```

---

## Jest 基础

### 基本断言

```javascript
// 基本断言
expect(value).toBe(expected);           // 严格相等
expect(value).toEqual(expected);        // 深度相等
expect(value).toBeTruthy();             // 真值
expect(value).toBeFalsy();              // 假值
expect(value).toBeNull();               // null
expect(value).toBeUndefined();          // undefined
expect(value).toBeDefined();            // 已定义
expect(array).toContain(item);          // 包含元素
expect(string).toMatch(/regex/);        // 匹配正则
expect(fn).toThrow();                   // 抛出异常
expect(fn).toThrow('error message');    // 抛出特定异常

// 异步断言
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();
```

### 常用匹配器

```javascript
// 数字
expect(value).toBeGreaterThan(10);
expect(value).toBeGreaterThanOrEqual(10);
expect(value).toBeLessThan(10);
expect(value).toBeLessThanOrEqual(10);
expect(value).toBeCloseTo(0.3, 5);  // 浮点数比较

// 对象
expect(object).toHaveProperty('name');
expect(object).toHaveProperty('name', 'John');
expect(object).toMatchObject({ name: 'John' });

// 数组
expect(array).toHaveLength(3);
expect(array).toContain('item');
expect(array).toContainEqual({ id: 1 });
expect(array).toEqual(expect.arrayContaining(['a', 'b']));

// 函数
const mockFn = jest.fn();
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(1);
expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
expect(mockFn).toHaveBeenLastCalledWith('arg');
```

---

## 测试结构

### Describe 块组织

```javascript
describe('UserService', () => {
  // 外层描述类或模块
  
  describe('create', () => {
    // 内层描述方法或功能
    
    it('should create user with valid data', () => {
      // 测试用例
    });
    
    it('should throw error with invalid email', () => {
      // 测试用例
    });
  });
  
  describe('findById', () => {
    it('should return user when found', () => {});
    it('should return null when not found', () => {});
  });
});
```

### Setup 和 Teardown

```javascript
describe('DatabaseTests', () => {
  // 所有测试前执行一次
  beforeAll(async () => {
    await db.connect();
  });
  
  // 每个测试前执行
  beforeEach(async () => {
    await db.clear();
  });
  
  // 每个测试后执行
  afterEach(async () => {
    await db.rollback();
  });
  
  // 所有测试后执行一次
  afterAll(async () => {
    await db.disconnect();
  });
  
  it('test 1', () => {});
  it('test 2', () => {});
});
```

---

## Mock 和 Stub

### 函数 Mock

```javascript
// 基本 mock
const mockFn = jest.fn();
mockFn.mockReturnValue('default');
mockFn.mockResolvedValue({ data: [] });  // 异步
mockFn.mockRejectedValue(new Error('fail'));  // 异步错误

// 连续调用返回不同值
mockFn
  .mockReturnValueOnce('first')
  .mockReturnValueOnce('second')
  .mockReturnValue('default');

// 使用 mock 函数
test('mock function', () => {
  const result = mockFn('arg1', 'arg2');
  
  expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
  expect(mockFn).toHaveBeenCalledTimes(1);
  expect(result).toBe('default');
});
```

### 模块 Mock

```javascript
// 自动 mock 整个模块
jest.mock('../database');

// 手动 mock
jest.mock('../database', () => ({
  query: jest.fn().mockResolvedValue({ rows: [] }),
  connect: jest.fn(),
}));

// 部分 mock
jest.mock('../utils', () => ({
  ...jest.requireActual('../utils'),
  logger: jest.fn(),
}));
```

### Spy

```javascript
// 监视对象方法
const user = { save: () => 'saved' };
const spy = jest.spyOn(user, 'save');

user.save('data');

expect(spy).toHaveBeenCalledWith('data');
spy.mockRestore();  // 恢复原始实现

// 改变返回值
jest.spyOn(user, 'save').mockReturnValue('mocked');
```

### 定时器 Mock

```javascript
// 使用假定时器
jest.useFakeTimers();

// 测试 setTimeout
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

test('delay', async () => {
  const promise = delay(1000);
  
  jest.advanceTimersByTime(1000);
  
  await promise;
  expect(setTimeout).toHaveBeenCalledTimes(1);
});

// 恢复真定时器
jest.useRealTimers();
```

---

## 异步测试

### Promise 测试

```javascript
// 使用 async/await
test('async function', async () => {
  const result = await fetchData();
  expect(result).toEqual({ data: [] });
});

// 测试 Promise 解析
test('promise resolves', () => {
  return expect(fetchData()).resolves.toEqual({ data: [] });
});

// 测试 Promise 拒绝
test('promise rejects', async () => {
  await expect(fetchData()).rejects.toThrow('Network error');
});
```

### 回调测试

```javascript
// 传统回调函数
test('callback test', (done) => {
  fetchData((err, result) => {
    expect(err).toBeNull();
    expect(result).toEqual({ data: [] });
    done();  // 标记测试完成
  });
});
```

---

## 参数化测试

```javascript
// 使用 test.each
test.each([
  ['user@example.com', true],
  ['invalid', false],
  ['', false],
  [null, false],
])('validateEmail(%s) returns %s', (email, expected) => {
  expect(validateEmail(email)).toBe(expected);
});

// 使用 describe.each
describe.each([
  { name: 'Alice', age: 30 },
  { name: 'Bob', age: 25 },
])('User %s', ({ name, age }) => {
  it(`should have name ${name}`, () => {
    const user = createUser(name, age);
    expect(user.name).toBe(name);
  });
  
  it(`should have age ${age}`, () => {
    const user = createUser(name, age);
    expect(user.age).toBe(age);
  });
});
```

---

## 集成测试

### 数据库测试

```javascript
// 使用真实数据库（测试数据库）
describe('UserRepository Integration', () => {
  beforeAll(async () => {
    await db.connect(process.env.TEST_DATABASE_URL);
  });
  
  afterAll(async () => {
    await db.disconnect();
  });
  
  beforeEach(async () => {
    await db.truncate('users');
  });
  
  it('should save and retrieve user', async () => {
    const user = { name: 'John', email: 'john@example.com' };
    
    const saved = await userRepository.save(user);
    const found = await userRepository.findById(saved.id);
    
    expect(found).toMatchObject(user);
  });
});
```

### API 测试（Supertest）

```javascript
const request = require('supertest');
const app = require('../app');

describe('User API', () => {
  it('GET /users should return user list', async () => {
    const response = await request(app)
      .get('/users')
      .expect('Content-Type', /json/)
      .expect(200);
    
    expect(response.body).toBeInstanceOf(Array);
  });
  
  it('POST /users should create user', async () => {
    const userData = { name: 'John', email: 'john@example.com' };
    
    const response = await request(app)
      .post('/users')
      .send(userData)
      .expect(201);
    
    expect(response.body).toMatchObject(userData);
    expect(response.body).toHaveProperty('id');
  });
  
  it('should handle validation errors', async () => {
    const invalidData = { name: '' };
    
    await request(app)
      .post('/users')
      .send(invalidData)
      .expect(400);
  });
});
```

---

## 快照测试

```javascript
// 使用快照测试复杂对象
test('user object matches snapshot', () => {
  const user = createUser('John', 'john@example.com');
  expect(user).toMatchSnapshot();
});

// 行内快照
test('greeting message', () => {
  expect(generateGreeting('John')).toMatchInlineSnapshot(
    `"Hello, John!"`
  );
});

// 更新快照: npm test -- --updateSnapshot
```

---

## 测试覆盖率

### 配置

```json
// package.json
{
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{js,ts}",
      "!src/**/*.d.ts",
      "!src/**/index.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

### 生成报告

```bash
# 生成覆盖率报告
npm test -- --coverage

# 生成 HTML 报告
npm test -- --coverage --coverageReporters=html

# 只显示摘要
npm test -- --coverage --coverageReporters=text-summary
```

---

## 测试最佳实践

### AAA 模式

```javascript
test('should calculate discount correctly', () => {
  // Arrange (准备)
  const order = { amount: 200, userLevel: 'VIP' };
  const expectedDiscount = 30;
  
  // Act (执行)
  const result = calculateDiscount(order);
  
  // Assert (断言)
  expect(result).toBe(expectedDiscount);
});
```

### 测试独立性

```javascript
// ❌ 错误：测试间共享状态
let globalUser;

test('create user', () => {
  globalUser = createUser('test@example.com');
});

test('update user', () => {
  // 依赖上一个测试
  updateUser(globalUser, 'new@example.com');
});

// ✓ 正确：每个测试独立
test('update user', () => {
  const user = createUser('test@example.com');
  updateUser(user, 'new@example.com');
  expect(user.email).toBe('new@example.com');
});
```

### 避免过度 Mock

```javascript
// ❌ 错误：mock 太多实现细节
test('process order', () => {
  const mockValidate = jest.spyOn(orderService, 'validate');
  const mockSave = jest.spyOn(orderService, 'save');
  const mockNotify = jest.spyOn(orderService, 'notify');
  // ... 失去测试意义
});

// ✓ 正确：只 mock 外部依赖
test('process order with payment gateway', async () => {
  const mockPayment = jest.spyOn(paymentGateway, 'charge');
  mockPayment.mockResolvedValue({ success: true });
  
  const result = await orderService.process(order);
  
  expect(result).toBe('success');
  expect(mockPayment).toHaveBeenCalledWith(order.amount);
});
```

---

## Jest 命令

### 基本命令

```bash
# 运行所有测试
npm test

# 监视模式
npm test -- --watch

# 运行特定文件
npm test user.test.js

# 运行匹配模式的测试
npm test -- --testNamePattern="create user"

# 运行特定 describe 块
npm test -- --testPathPattern="user"

# 失败时停止
npm test -- --bail

# 显示详细输出
npm test -- --verbose
```

### 调试测试

```bash
# 使用 Node 调试器
node --inspect-brk node_modules/.bin/jest --runInBand

# 只运行失败的测试
npm test -- --onlyFailures

# 重新运行失败的测试
npm test -- --watch --onlyFailures
```

---

## 测试覆盖率目标

- **包级别**：≥ 80%
- **关键业务逻辑**：≥ 95%
- **公共 API**：100%
- **错误处理路径**：≥ 80%

## 质量检查清单

- [ ] 所有测试文件以 `.test.js` 或 `.spec.js` 结尾
- [ ] 测试描述清晰表达意图
- [ ] 使用 AAA 模式（Arrange-Act-Assert）
- [ ] 测试相互独立
- [ ] 适当使用 Mock，不过度 Mock
- [ ] 异步测试正确处理
- [ ] 覆盖率达标
- [ ] 测试执行快速
