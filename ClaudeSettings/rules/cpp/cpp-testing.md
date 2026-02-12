# C++ 测试规范

本文档定义了 C++ 项目的测试标准和最佳实践。

---

## 测试基础规范

### 测试文件命名

**规则**：测试文件必须以 `_test.cpp` 或 `_unittest.cpp` 结尾

```
user_service.cpp       → user_service_test.cpp
validator.cpp          → validator_test.cpp
core/engine.cpp        → core/engine_test.cpp
```

### 测试函数命名

**规则**：测试函数使用 `TEST` 或 `TEST_F` 宏，名称清晰描述测试场景

```cpp
// ✅ 正确
TEST(UserServiceTest, RegisterUserValidInput)
TEST(UserServiceTest, RegisterUserDuplicateEmail)
TEST(UserServiceTest, RegisterUserInvalidPassword)

// ❌ 错误
TEST(Test1, TestCase1)  // 名称不清晰
```

### 包组织

**规则**：测试文件放在 `tests/` 目录中，与源代码结构对应

```
tests/
├── CMakeLists.txt
├── core/
│   ├── engine_test.cpp
│   └── types_test.cpp
├── utils/
│   ├── logging_test.cpp
│   └── string_utils_test.cpp
└── testdata/
    ├── valid_users.json
    └── invalid_users.json
```

---

## 测试框架选择

### Google Test（推荐）

**特点**：
- 功能丰富，社区活跃
- 支持死亡测试、值参数化测试
- 与 Google Mock 集成
- 良好的 IDE 支持

**安装**：

```bash
# Ubuntu/Debian
sudo apt-get install libgtest-dev

# macOS
brew install googletest

# 或使用 FetchContent（CMake）
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        release-1.12.1
)
FetchContent_MakeAvailable(googletest)
```

### Catch2（轻量级选择）

**特点**：
- 仅头文件，易于集成
- BDD 风格测试支持
- 现代 C++ 设计

### Boost.Test（Boost 项目）

**特点**：
- 与 Boost 库集成
- 丰富的断言集

---

## Google Test 基础

### 基本断言

```cpp
#include <gtest/gtest.h>

TEST(BasicAssertions, Demo) {
    // 相等性断言
    EXPECT_EQ(1 + 1, 2);        // 期待相等
    EXPECT_NE(1 + 1, 3);        // 期待不等
    EXPECT_LT(1, 2);            // 期待小于
    EXPECT_LE(1, 1);            // 期待小于等于
    EXPECT_GT(2, 1);            // 期待大于
    EXPECT_GE(1, 1);            // 期待大于等于

    // 布尔断言
    EXPECT_TRUE(true);
    EXPECT_FALSE(false);

    // 浮点数比较
    EXPECT_DOUBLE_EQ(0.1 + 0.2, 0.3);           // 精确相等
    EXPECT_NEAR(0.1 + 0.2, 0.3, 0.0001);        // 在误差范围内相等

    // 字符串比较
    EXPECT_STREQ("hello", "hello");             // C 字符串相等
    EXPECT_EQ(std::string("hello"), "hello");   // std::string 相等

    // 空检查
    EXPECT_NULL(nullptr);
    EXPECT_NOT_NULL(ptr);
}
```

### EXPECT vs ASSERT

```cpp
TEST(ExpectVsAssert, Demo) {
    auto user = CreateUser("test@example.com");

    // EXPECT_* 失败继续执行
    EXPECT_NE(user, nullptr);           // 如果失败，继续执行
    EXPECT_EQ(user->Email(), "test@example.com");

    // ASSERT_* 失败立即返回
    ASSERT_NE(user, nullptr);           // 如果失败，测试结束
    ASSERT_EQ(user->Email(), "test@example.com");
}
```

**原则**：
- 使用 `EXPECT_*` 进行多属性检查
- 使用 `ASSERT_*` 当后续代码依赖前面的条件

### 简单测试示例

```cpp
#include <gtest/gtest.h>
#include "myproject/utils.h"

// 被测函数
double CalculateDiscount(double amount, const std::string& level) {
    if (amount < 100.0) return 0.0;
    double rate = (level == "VIP") ? 0.15 : 0.10;
    return amount * rate;
}

// 测试
TEST(CalculateDiscountTest, SmallOrderNoDiscount) {
    EXPECT_DOUBLE_EQ(CalculateDiscount(50.0, "normal"), 0.0);
    EXPECT_DOUBLE_EQ(CalculateDiscount(99.99, "VIP"), 0.0);
}

TEST(CalculateDiscountTest, NormalUserDiscount) {
    EXPECT_DOUBLE_EQ(CalculateDiscount(100.0, "normal"), 10.0);
    EXPECT_DOUBLE_EQ(CalculateDiscount(200.0, "normal"), 20.0);
}

TEST(CalculateDiscountTest, VIPUserDiscount) {
    EXPECT_DOUBLE_EQ(CalculateDiscount(100.0, "VIP"), 15.0);
    EXPECT_DOUBLE_EQ(CalculateDiscount(200.0, "VIP"), 30.0);
}
```

---

## 测试夹具（Test Fixtures）

### 基本用法

```cpp
class DatabaseTest : public ::testing::Test {
protected:
    // 每个测试前执行
    void SetUp() override {
        db_ = std::make_unique<Database>(":memory:");
        db_->Connect();
        db_->Execute("CREATE TABLE users (id INT, name TEXT)");
    }

    // 每个测试后执行
    void TearDown() override {
        db_->Disconnect();
        db_.reset();
    }

    // 辅助函数
    void InsertUser(int id, const std::string& name) {
        db_->Execute("INSERT INTO users VALUES (" +
                     std::to_string(id) + ", '" + name + "')");
    }

    std::unique_ptr<Database> db_;
};

// 使用 TEST_F 代替 TEST
TEST_F(DatabaseTest, InsertUser) {
    InsertUser(1, "Alice");

    auto result = db_->Query("SELECT * FROM users WHERE id = 1");
    EXPECT_EQ(result->GetString("name"), "Alice");
}

TEST_F(DatabaseTest, DeleteUser) {
    InsertUser(1, "Alice");
    db_->Execute("DELETE FROM users WHERE id = 1");

    auto result = db_->Query("SELECT * FROM users WHERE id = 1");
    EXPECT_TRUE(result->IsEmpty());
}
```

### 参数化测试

```cpp
class DiscountTest :
    public ::testing::TestWithParam<std::tuple<double, std::string, double>> {
};

TEST_P(DiscountTest, CalculateDiscount) {
    auto [amount, level, expected] = GetParam();
    EXPECT_DOUBLE_EQ(CalculateDiscount(amount, level), expected);
}

// 测试参数
INSTANTIATE_TEST_SUITE_P(
    DiscountCases,
    DiscountTest,
    ::testing::Values(
        std::make_tuple(50.0, "normal", 0.0),      // 小额订单无折扣
        std::make_tuple(99.99, "VIP", 0.0),        // 小额订单无折扣
        std::make_tuple(100.0, "normal", 10.0),    // 普通用户 10%
        std::make_tuple(100.0, "VIP", 15.0),       // VIP 用户 15%
        std::make_tuple(200.0, "normal", 20.0),    // 普通用户 10%
        std::make_tuple(200.0, "VIP", 30.0)        // VIP 用户 15%
    )
);
```

---

## 测试辅助函数

### 命名规范

```cpp
// ✅ 正确 - 辅助函数以下划线开头
class UserTest : public ::testing::Test {
protected:
    User _CreateTestUser(const std::string& email = "test@example.com") {
        User user;
        user.setEmail(email);
        user.setName("Test User");
        return user;
    }

    void _CleanUpDatabase() {
        db_.Execute("DELETE FROM users WHERE email LIKE '%test%'");
    }

    Database db_;
};
```

### Setup 和 Teardown

```cpp
class FileTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 创建临时目录
        temp_dir_ = std::filesystem::temp_directory_path() / "test";
        std::filesystem::create_directories(temp_dir_);
    }

    void TearDown() override {
        // 清理临时目录
        std::filesystem::remove_all(temp_dir_);
    }

    std::filesystem::path temp_dir_;
};
```

---

## Mock 对象

### Google Mock 基础

```cpp
#include <gmock/gmock.h>

// 定义接口
class PaymentGateway {
public:
    virtual ~PaymentGateway() = default;
    virtual bool Charge(const std::string& card, double amount) = 0;
    virtual void Refund(const std::string& transaction_id) = 0;
};

// 创建 Mock 类
class MockPaymentGateway : public PaymentGateway {
public:
    MOCK_METHOD(bool, Charge, (const std::string& card, double amount), (override));
    MOCK_METHOD(void, Refund, (const std::string& transaction_id), (override));
};

// 使用 Mock
using ::testing::_;
using ::testing::Return;
using ::testing::Throw;

TEST(OrderServiceTest, ProcessPayment) {
    MockPaymentGateway mock_gateway;

    // 设置期望
    EXPECT_CALL(mock_gateway, Charge("4111111111111111", 100.0))
        .WillOnce(Return(true));

    OrderService service(&mock_gateway);
    auto result = service.ProcessPayment("4111111111111111", 100.0);

    EXPECT_TRUE(result.success);
}

TEST(OrderServiceTest, PaymentFailure) {
    MockPaymentGateway mock_gateway;

    EXPECT_CALL(mock_gateway, Charge(_, _))
        .WillOnce(Return(false));

    OrderService service(&mock_gateway);
    auto result = service.ProcessPayment("invalid", 100.0);

    EXPECT_FALSE(result.success);
}
```

### 验证调用次数

```cpp
TEST(OrderServiceTest, ChargeExactlyOnce) {
    MockPaymentGateway mock_gateway;

    // 期望恰好调用一次
    EXPECT_CALL(mock_gateway, Charge(_, _))
        .Times(1)
        .WillOnce(Return(true));

    OrderService service(&mock_gateway);
    service.ProcessPayment("4111111111111111", 100.0);
}

TEST(OrderServiceTest, RefundAtMostOnce) {
    MockPaymentGateway mock_gateway;

    // 期望最多调用一次
    EXPECT_CALL(mock_gateway, Refund(_))
        .Times(::testing::AtMost(1));

    OrderService service(&mock_gateway);
    service.CancelOrder("order123");
}
```

---

## C++ 特定测试技巧

### 测试异常

```cpp
TEST(ExceptionTest, ThrowsException) {
    // 期待抛出异常
    EXPECT_THROW(
        Divide(1, 0),
        std::invalid_argument
    );
}

TEST(ExceptionTest, ThrowsWithMessage) {
    // 期待抛出异常并检查消息
    try {
        Divide(1, 0);
        FAIL() << "Expected std::invalid_argument";
    } catch (const std::invalid_argument& e) {
        EXPECT_STREQ(e.what(), "Division by zero");
    }
}

TEST(ExceptionTest, NoException) {
    // 期待不抛出异常
    EXPECT_NO_THROW(Divide(4, 2));
}
```

### 测试模板

```cpp
template<typename T>
class ContainerTest : public ::testing::Test {
protected:
    Container<T> container_;
};

using TestTypes = ::testing::Types<int, float, double>;
TYPED_TEST_SUITE(ContainerTest, TestTypes);

TYPED_TEST(ContainerTest, PushAndPop) {
    using T = TypeParam;

    this->container_.Push(T(1));
    this->container_.Push(T(2));

    EXPECT_EQ(this->container_.Pop(), T(2));
    EXPECT_EQ(this->container_.Pop(), T(1));
}
```

### 测试移动语义

```cpp
TEST(MoveSemanticsTest, MoveConstructor) {
    Buffer original(1024);
    original.Fill('A');

    Buffer moved(std::move(original));

    EXPECT_EQ(moved.Size(), 1024);
    EXPECT_EQ(original.Data(), nullptr);  // 原对象应为空
}

TEST(MoveSemanticsTest, MoveAssignment) {
    Buffer original(1024);
    Buffer target(512);

    target = std::move(original);

    EXPECT_EQ(target.Size(), 1024);
    EXPECT_EQ(original.Data(), nullptr);
}
```

### 测试线程安全

```cpp
TEST(ThreadSafetyTest, ConcurrentIncrement) {
    Counter counter;

    std::vector<std::thread> threads;
    for (int i = 0; i < 10; ++i) {
        threads.emplace_back([&counter]() {
            for (int j = 0; j < 1000; ++j) {
                counter.Increment();
            }
        });
    }

    for (auto& t : threads) {
        t.join();
    }

    EXPECT_EQ(counter.GetCount(), 10000);
}
```

---

## 基准测试

### Google Benchmark

```cpp
#include <benchmark/benchmark.h>

static void BM_StringConcatenation(benchmark::State& state) {
    for (auto _ : state) {
        std::string s;
        for (int i = 0; i < 100; ++i) {
            s += "x";
        }
    }
}
BENCHMARK(BM_StringConcatenation);

static void BM_StringReserve(benchmark::State& state) {
    for (auto _ : state) {
        std::string s;
        s.reserve(100);
        for (int i = 0; i < 100; ++i) {
            s += "x";
        }
    }
}
BENCHMARK(BM_StringReserve);

// 参数化基准测试
static void BM_VectorPushBack(benchmark::State& state) {
    int n = state.range(0);
    for (auto _ : state) {
        std::vector<int> v;
        for (int i = 0; i < n; ++i) {
            v.push_back(i);
        }
    }
}
BENCHMARK(BM_VectorPushBack)->Range(8, 8<<10);

BENCHMARK_MAIN();
```

---

## 测试覆盖率

### 生成覆盖率报告

```cmake
# CMakeLists.txt
option(ENABLE_COVERAGE "Enable coverage reporting" OFF)

if(ENABLE_COVERAGE)
    target_compile_options(mylib PRIVATE --coverage -O0 -g)
    target_link_options(mylib PRIVATE --coverage)

    find_program(LCOV_PATH lcov)
    find_program(GENHTML_PATH genhtml)

    if(LCOV_PATH AND GENHTML_PATH)
        add_custom_target(coverage
            COMMAND ${LCOV_PATH} --capture --directory . --output-file coverage.info
            COMMAND ${LCOV_PATH} --remove coverage.info '/usr/*' --output-file coverage.info
            COMMAND ${GENHTML_PATH} coverage.info --output-directory coverage_report
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
            COMMENT "Generating coverage report"
        )
    endif()
endif()
```

### 运行覆盖率检查

```bash
# 1. 配置时启用覆盖率
cmake -B build -DENABLE_COVERAGE=ON

# 2. 构建
cmake --build build

# 3. 运行测试
ctest --test-dir build

# 4. 生成报告
cd build && make coverage

# 5. 查看报告
firefox coverage_report/index.html
```

### 覆盖率要求

| 组件 | 目标覆盖率 |
|------|-----------|
| 核心业务逻辑 | ≥ 90% |
| 公共 API | ≥ 85% |
| 工具函数 | ≥ 80% |
| 错误处理路径 | ≥ 70% |

---

## 测试命令

### 基本命令

```bash
# 运行所有测试
./myproject_test

# 运行特定测试套件
./myproject_test --gtest_filter=UserServiceTest.*

# 运行特定测试
./myproject_test --gtest_filter=UserServiceTest.RegisterUserValidInput

# 排除特定测试
./myproject_test --gtest_filter=-*StressTest.*

# 重复运行
./myproject_test --gtest_repeat=10

# 随机顺序
./myproject_test --gtest_shuffle

# 显示详细输出
./myproject_test --gtest_also_run_disabled_tests

# 输出 XML 报告
./myproject_test --gtest_output=xml:report.xml
```

### CTest 集成

```bash
# 运行所有测试
ctest

# 详细输出
ctest -V

# 并行运行
ctest -j4

# 运行特定测试
ctest -R UserService

# 排除特定测试
ctest -E StressTest

# 失败时停止
ctest --stop-on-failure
```

---

## 测试组织最佳实践

### 目录结构

```
tests/
├── CMakeLists.txt          # 测试配置
├── unit/                   # 单元测试
│   ├── core/
│   │   ├── engine_test.cpp
│   │   └── types_test.cpp
│   └── utils/
│       └── string_utils_test.cpp
├── integration/            # 集成测试
│   ├── database_test.cpp
│   └── api_test.cpp
├── benchmark/              # 性能测试
│   └── engine_benchmark.cpp
└── fixtures/               # 共享测试夹具
    ├── database_fixture.h
    └── mock_factories.h
```

### 测试分类标记

```cpp
// 慢速测试
TEST(SlowTest, DataProcessing) {
    // ...
}

// 需要外部依赖的测试
TEST(NetworkTest, ExternalAPI) {
    // ...
}

// 使用 DISABLED_ 前缀禁用测试
TEST(DISABLED_TempTest, BrokenFeature) {
    // ...
}
```

---

## 常见陷阱

### ❌ 陷阱 1：共享状态

```cpp
// ❌ 错误 - 测试间共享状态
static int counter = 0;

TEST(CounterTest, Increment) {
    counter++;
    EXPECT_EQ(counter, 1);
}

TEST(CounterTest, IncrementAgain) {
    counter++;  // 依赖上一个测试！
    EXPECT_EQ(counter, 2);  // 可能失败
}

// ✅ 正确 - 每个测试独立
class CounterTest : public ::testing::Test {
protected:
    int counter_ = 0;
};

TEST_F(CounterTest, Increment) {
    counter_++;
    EXPECT_EQ(counter_, 1);
}
```

### ❌ 陷阱 2：硬编码路径

```cpp
// ❌ 错误
TEST(FileTest, ReadFile) {
    auto content = ReadFile("/home/user/test/data.txt");  // 硬编码路径
}

// ✅ 正确
TEST_F(FileTest, ReadFile) {
    auto path = GetTestDataDir() / "data.txt";
    auto content = ReadFile(path.string());
}
```

### ❌ 陷阱 3：忽略资源清理

```cpp
// ❌ 错误
TEST(DatabaseTest, Insert) {
    Database db("localhost");
    db.Connect();
    db.Insert("test_data");
    // 没有断开连接！
}

// ✅ 正确
class DatabaseTest : public ::testing::Test {
protected:
    void SetUp() override {
        db_ = std::make_unique<Database>("localhost");
        db_->Connect();
    }

    void TearDown() override {
        db_->Disconnect();
    }

    std::unique_ptr<Database> db_;
};
```

### ❌ 陷阱 4：测试过多

```cpp
// ❌ 错误 - 一个测试检查太多
TEST(UserTest, Everything) {
    User user;

    // 测试设置名称
    user.SetName("Alice");
    EXPECT_EQ(user.GetName(), "Alice");

    // 测试设置邮箱
    user.SetEmail("alice@example.com");
    EXPECT_EQ(user.GetEmail(), "alice@example.com");

    // 测试验证
    EXPECT_TRUE(user.IsValid());

    // 测试保存
    EXPECT_TRUE(user.Save());

    // 测试加载
    auto loaded = User::Load(user.GetId());
    EXPECT_EQ(loaded.GetName(), "Alice");
}

// ✅ 正确 - 拆分为多个小测试
TEST(UserTest, SetName) { /* ... */ }
TEST(UserTest, SetEmail) { /* ... */ }
TEST(UserTest, ValidateValidUser) { /* ... */ }
TEST(UserTest, SaveAndLoad) { /* ... */ }
```

---

## 质量检查清单

### 单元测试标准

- [ ] 每个公共函数都有对应的测试
- [ ] 测试覆盖正常路径和错误路径
- [ ] 测试使用描述性名称
- [ ] 测试相互独立
- [ ] 测试运行快速（< 1 秒）
- [ ] 使用适当的断言（EXPECT vs ASSERT）

### 测试代码质量

- [ ] 测试代码与生产代码同等重要
- [ ] 避免测试代码中的重复
- [ ] 使用辅助函数减少重复
- [ ] 测试夹具正确清理资源
- [ ] Mock 对象验证预期调用

### 覆盖率目标

- [ ] 行覆盖率 ≥ 80%
- [ ] 分支覆盖率 ≥ 75%
- [ ] 函数覆盖率 ≥ 90%
- [ ] 关键业务逻辑 100% 覆盖

---

## 参考资源

- [Google Test Documentation](https://google.github.io/googletest/)
- [Google Mock Cookbook](https://google.github.io/googletest/gmock_cook_book.html)
- [Google Benchmark](https://github.com/google/benchmark)
- [Modern C++ Testing](https://github.com/catchorg/Catch2)

**文档版本**: 1.0.0
**最后更新**: 2026-02-06
