# C++ 项目编程标准

本文档定义了 C++ 项目的编程规范和最佳实践，旨在提高代码质量、可维护性和团队协作效率。

---

## 注释规范

### 注释类型区分（核心约定）

本项目使用不同的注释标记来区分注释的用途：

#### 1. 标准代码注释 `//`

**用途**：API 文档、函数说明、公共接口注释

**使用场景**：
- 类、函数、方法的文档注释
- 公共 API 的使用说明
- 复杂算法的整体说明
- 文件头部的版权和描述信息

#### 2. 代码逻辑解释 `//;`

**用途**：解释代码的功能、逻辑、算法，与纯代码注释 `//` 区分

**使用场景**：
- 解释复杂的业务逻辑
- 说明算法实现思路
- 阐述为什么这样写（设计决策）
- 解释不明显的代码行为

**示例**：

```cpp
// Calculate the discount based on order amount and user level
//
// Discount rules:
// - VIP users: 15% of order amount
// - Regular users: 10% of order amount
// - Orders < $100 don't qualify for discounts
//
// @param amount Order amount in dollars
// @param userLevel User membership level ("VIP" or "Regular")
// @return Discount amount in dollars
double calculateDiscount(double amount, const std::string& userLevel) {
    //; Small orders don't qualify for discount program
    if (amount < 100.0) {
        return 0.0;
    }

    //; Calculate discount rate based on user level
    double rate = 0.0;
    if (userLevel == "VIP") {
        rate = 0.15;
    } else {
        rate = 0.10;
    }

    return amount * rate;
}
```

#### 3. 非代码注释 `//;@`

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

```cpp
class OrderProcessor {
public:
    //; Process a single order
    void ProcessOrder(const Order& order);

    //;@TODO: Add support for batch order processing
    void ProcessBatch(const std::vector<Order>& orders);

    //;@FIXME: This method has a race condition when called concurrently
    void UpdateInventory(const Item& item);

    //;@HACK: Temporary workaround for legacy API compatibility
    //; Remove this once API v2 is deployed
    void ProcessLegacyPayment(const Payment& payment);

    //;@DEPRECATED: Use ProcessOrderAsync instead
    //; This method will be removed in v3.0
    void ProcessOrderSync(const Order& order);

    //;@NOTE: This cache is thread-safe but not persistent
    void EnableCache(bool enable);

private:
    //;@OPTIMIZE: Consider using a lock-free queue for better performance
    std::queue<Order> orderQueue_;

    //;@DEBUG: Remove this logging before release
    void DebugPrintState();
};
```

### 注释使用原则

**强制规则（MUST）**：

- ✅ 所有公共接口（头文件中的类、函数）必须有 `//` 文档注释
- ✅ 复杂的业务逻辑必须有 `//;` 解释注释
- ✅ 所有 TODO、FIXME、HACK 必须使用 `//;@` 前缀
- ✅ 代码应该自解释，简单清晰的代码不需要过度注释

**推荐规则（SHOULD）**：

- 注释应该解释"为什么"而不是"是什么"
- 注释应该与代码保持同步更新
- 避免 obvious comments（如 `i++  // increment i`）

**注释检查工具**：

```bash
# 查找所有逻辑解释注释
grep -rn "//;" --include="*.cpp" --include="*.h" .

# 查找所有 TODO
grep -rn "//;@TODO:" --include="*.cpp" --include="*.h" .

# 查找所有 FIXME
grep -rn "//;@FIXME:" --include="*.cpp" --include="*.h" .

# 使用 list-comments.sh 脚本（推荐）
./ClaudeSettings/rules/cpp/list-comments.sh
```

---

## 命名规范

### 命名空间（Namespace）

**规则**：使用小写字母，下划线分隔

```cpp
// ✅ 正确
namespace my_project { }
namespace file_processor { }
namespace utils { }

// ❌ 错误
namespace MyProject { }      // 大写
namespace fileProcessor { } // 驼峰
namespace File_Processor { } // 首字母大写
```

### 类（Class）

**规则**：使用 PascalCase（大驼峰）

```cpp
// ✅ 正确
class UserManager { };
class HttpRequest { };
class DatabaseConnection { };

// ❌ 错误
class user_manager { }     // 小写
class httpRequest { }       // 小驼峰
class databaseconnection { } // 无分隔
```

### 结构体（Struct）

**规则**：与类相同，使用 PascalCase

```cpp
// ✅ 正确
struct Point { double x, y; };
struct UserInfo { std::string name; int age; };
```

### 函数（Function）

**规则**：使用 camelCase（小驼峰）

```cpp
// ✅ 正确
void processOrder();
int calculateTotal();
std::string getUserName();

// ❌ 错误
void ProcessOrder();        // PascalCase
void process_order();       // 下划线
void PROCESS_ORDER();       // 全大写
```

**Getter/Setter 命名**：

```cpp
class User {
public:
    // Getter - 使用名词或 Get + 名词
    std::string name() const { return name_; }
    std::string getEmail() const { return email_; }

    // Setter - 使用 set + 名词
    void setName(const std::string& name) { name_ = name; }
    void setEmail(const std::string& email) { email_ = email; }

    // 布尔类型 - 使用 is/has/can/should 前缀
    bool isActive() const { return active_; }
    bool hasPermission() const { return permission_; }
    bool isValid() const { return valid_; }

private:
    std::string name_;
    std::string email_;
    bool active_;
    bool permission_;
    bool valid_;
};
```

### 变量（Variable）

**规则**：使用小写字母，下划线分隔

```cpp
// ✅ 正确
int order_count;
std::string user_name;
double total_amount;

// ❌ 错误
int orderCount;           // 驼峰
int OrderCount;           // PascalCase
int ORDER_COUNT;          // 全大写（常量使用）
```

**类成员变量**：使用后缀下划线

```cpp
class User {
private:
    std::string name_;
    int age_;
    std::shared_ptr<Database> db_;
};
```

### 常量（Constant）

**规则**：使用 k + PascalCase 或全大写下划线分隔

```cpp
// ✅ 正确 - Google Style
constexpr int kMaxConnections = 100;
constexpr double kPi = 3.1415926;
const std::string kDefaultConfigPath = "/etc/app.conf";

// ✅ 也正确 - 传统风格
constexpr int MAX_CONNECTIONS = 100;
constexpr double PI = 3.1415926;
```

### 宏（Macro）

**规则**：使用全大写，下划线分隔

```cpp
// ✅ 正确
#define DEBUG_MODE 1
#define BUFFER_SIZE 1024

// 尽量避免使用宏，优先使用 constexpr
constexpr int kBufferSize = 1024;
```

### 枚举（Enum）

**规则**：枚举类型使用 PascalCase，枚举值使用 k + PascalCase

```cpp
// C++11 强类型枚举（推荐）
enum class StatusCode {
    kOk = 200,
    kNotFound = 404,
    kInternalError = 500,
};

enum class Color {
    kRed,
    kGreen,
    kBlue,
};
```

---

## 代码组织

### 文件结构

#### 头文件（.h / .hpp）

**标准文件顺序**：

```cpp
// 1. 头文件保护
#pragma once

// 2. 系统头文件（<...>）
#include <string>
#include <vector>
#include <memory>

// 3. 第三方库头文件
#include <boost/asio.hpp>

// 4. 本项目头文件（"..."）
#include "myproject/utils.h"

// 5. 命名空间
namespace myproject {

// 6. 类/函数声明
class MyClass {
public:
    MyClass();
    void DoSomething();

private:
    int private_member_;
};

} // namespace myproject
```

#### 源文件（.cpp）

**标准文件顺序**：

```cpp
// 1. 对应的头文件（必须放在第一行）
#include "myproject/myclass.h"

// 2. 系统头文件
#include <iostream>
#include <algorithm>

// 3. 第三方库头文件
#include <fmt/format.h>

// 4. 命名空间
namespace myproject {

// 5. 匿名命名空间（文件内私有）
namespace {
    constexpr int kInternalBufferSize = 1024;
} // namespace

// 6. 函数实现
MyClass::MyClass() : private_member_(0) {}

void MyClass::DoSomething() {
    // ...
}

} // namespace myproject
```

### Include 顺序和分组

```cpp
// 组 1：对应的头文件
#include "myclass.h"

// 组 2：C 标准库
#include <cstddef>
#include <cstdint>

// 组 3：C++ 标准库
#include <algorithm>
#include <memory>
#include <vector>

// 组 4：第三方库
#include <boost/algorithm/string.hpp>

// 组 5：本项目头文件
#include "base/logging.h"
```

### 项目目录结构

```
myproject/
├── CMakeLists.txt
├── README.md
├── .clang-format
├── .clang-tidy
├── include/
│   └── myproject/
│       ├── core/
│       │   ├── engine.h
│       │   └── types.h
│       └── utils/
│           ├── logging.h
│           └── string_utils.h
├── src/
│   ├── core/
│   │   ├── engine.cpp
│   │   └── types.cpp
│   └── utils/
│       ├── logging.cpp
│       └── string_utils.cpp
├── tests/
│   ├── core/
│   │   └── engine_test.cpp
│   └── utils/
│       └── string_utils_test.cpp
└── docs/
    └── api.md
```

---

## 内存管理

### RAII 原则

**核心原则**：资源获取即初始化（Resource Acquisition Is Initialization）

```cpp
// ✅ 正确 - 使用 RAII
void ProcessFile(const std::string& path) {
    std::ifstream file(path);  // 文件在构造时打开
    if (!file) {
        throw std::runtime_error("Failed to open file");
    }

    std::string line;
    while (std::getline(file, line)) {
        ProcessLine(line);
    }

} // 文件在这里自动关闭

// ❌ 错误 - 手动管理资源
void ProcessFileBad(const std::string& path) {
    FILE* file = fopen(path.c_str(), "r");
    if (!file) return;

    // 容易遗漏 fclose，尤其是在异常发生时
    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), file)) {
        if (SomeCondition()) return;  // 忘记 fclose！
    }

    fclose(file);
}
```

### 智能指针

#### unique_ptr - 独占所有权

```cpp
// ✅ 正确 - 独占所有权
std::unique_ptr<User> CreateUser(const std::string& name) {
    return std::make_unique<User>(name);
}

void Process() {
    auto user = CreateUser("Alice");
    user->DoSomething();

    // 转移所有权
    auto new_owner = std::move(user);
}
```

#### shared_ptr - 共享所有权

```cpp
// ✅ 正确 - 共享所有权
class Node {
public:
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> parent;  // 避免循环引用

    void AddChild(std::shared_ptr<Node> child) {
        child->parent = shared_from_this();
        children_.push_back(std::move(child));
    }

private:
    std::vector<std::shared_ptr<Node>> children_;
};

// 创建 shared_ptr
auto node = std::make_shared<Node>();
```

**智能指针最佳实践**：

```cpp
// ✅ 优先使用 make_unique 和 make_shared
auto ptr1 = std::make_unique<MyClass>(arg1, arg2);
auto ptr2 = std::make_shared<MyClass>(arg1, arg2);

// ❌ 避免直接使用 new
std::unique_ptr<MyClass> ptr(new MyClass(arg1, arg2));
```

---

## 现代 C++ 特性

### auto 关键字

```cpp
// ✅ 正确 - 类型冗长时使用 auto
auto it = map.begin();
auto user = std::make_unique<User>("Alice");

// ❌ 错误 - 类型不明确时不应使用 auto
auto data = GetData();  // 不知道返回什么类型
```

### 范围 for 循环

```cpp
// ✅ 正确 - 范围 for 循环
std::vector<int> numbers = {1, 2, 3, 4, 5};

for (const auto& num : numbers) {  // 只读访问
    std::cout << num << " ";
}

for (auto& num : numbers) {  // 修改元素
    num *= 2;
}
```

### Lambda 表达式

```cpp
// ✅ 正确 - 简单回调
std::sort(vec.begin(), vec.end(),
          [](int a, int b) { return a > b; });

// ✅ 正确 - 捕获局部变量
int threshold = 10;
auto filtered = Filter(vec, [threshold](int x) {
    return x > threshold;
});
```

### 移动语义

```cpp
// ✅ 正确 - 实现移动构造函数
class Buffer {
public:
    Buffer(Buffer&& other) noexcept
        : data_(other.data_)
        , size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

private:
    char* data_ = nullptr;
    size_t size_ = 0;
};
```

### constexpr 和 consteval

```cpp
// ✅ 正确 - 编译期常量
constexpr int kMaxSize = 100;
constexpr double kPi = 3.14159265358979323846;

// ✅ 正确 - constexpr 函数
constexpr int Square(int x) {
    return x * x;
}

constexpr int result = Square(5);  // 编译期计算
```

### C++17 特性

```cpp
// ✅ 结构化绑定
auto [x, y] = GetPoint();

// ✅ if/switch 初始化语句
if (auto it = map.find(key); it != map.end()) {
    // 使用 it
}

// ✅ std::optional
std::optional<User> FindUser(int id);

if (auto user = FindUser(42); user.has_value()) {
    user->DoSomething();
}

// ✅ std::string_view（避免拷贝）
void ProcessString(std::string_view str);
```

---

## 错误处理

### 异常 vs 错误码

**使用异常的情况**：

```cpp
// ✅ 正确 - 异常情况使用异常
class FileNotFoundError : public std::runtime_error {
public:
    explicit FileNotFoundError(const std::string& path)
        : std::runtime_error("File not found: " + path), path_(path) {}

    const std::string& Path() const { return path_; }

private:
    std::string path_;
};

void ReadFile(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw FileNotFoundError(path);
    }
    // ...
}
```

### noexcept 使用

```cpp
// ✅ 正确 - 明确标记 noexcept
class MyClass {
public:
    // 析构函数应该总是 noexcept
    ~MyClass() noexcept = default;

    // 移动操作应该 noexcept
    MyClass(MyClass&& other) noexcept
        : data_(std::move(other.data_)) {}

    MyClass& operator=(MyClass&& other) noexcept {
        if (this != &other) {
            data_ = std::move(other.data_);
        }
        return *this;
    }

    // 简单查询函数
    size_t Size() const noexcept { return data_.size(); }
    bool Empty() const noexcept { return data_.empty(); }

private:
    std::vector<int> data_;
};
```

---

## 函数设计

### 函数长度

**规则**：单个函数 ≤ 50 行（推荐）

```cpp
// ❌ 函数过长
void ProcessOrder(const Order& order) {
    // 100+ 行代码...
}

// ✅ 拆分为多个小函数
void ProcessOrder(const Order& order) {
    ValidateOrder(order);
    auto total = CalculateTotal(order);
    ProcessPayment(order, total);
    UpdateInventory(order);
    SendConfirmation(order);
}
```

### 参数传递

```cpp
// ✅ 基本类型 - 按值传递
void SetAge(int age);
void SetFlag(bool enabled);

// ✅ 只读大对象 - 按 const 引用传递
void ProcessUser(const User& user);
void PrintConfig(const Config& config);

// ✅ 修改对象 - 按引用传递
void UpdateUser(User& user);

// ✅ 转移所有权 - 按值传递（移动语义）
void StoreData(std::vector<int> data);
```

---

## 类设计

### 单一职责原则

```cpp
// ✅ 正确 - 每个类只做一件事
class FileReader {
public:
    std::string Read(const std::string& path);
};

class DataParser {
public:
    Data Parse(const std::string& content);
};

// ❌ 错误 - 一个类做太多事
class GodClass {
public:
    std::string ReadFile(const std::string& path);
    Data ParseData(const std::string& content);
    Result ProcessData(const Data& data);
    void SaveToDatabase(const Result& result);
    // ...
};
```

### Rule of Zero/Three/Five

```cpp
// ✅ Rule of Zero - 所有成员都自动管理
class ModernClass {
public:
    // 编译器生成的默认构造、析构、拷贝、移动都正确

private:
    std::string name_;
    std::vector<int> data_;
    std::unique_ptr<Helper> helper_;
};

// ✅ Rule of Five - 自定义析构需要自定义所有特殊函数
class ResourceManager {
public:
    // 构造函数
    explicit ResourceManager(size_t size)
        : data_(new int[size]), size_(size) {}

    // 1. 析构函数
    ~ResourceManager() { delete[] data_; }

    // 2. 拷贝构造函数
    ResourceManager(const ResourceManager& other)
        : data_(new int[other.size_]), size_(other.size_) {
        std::copy(other.data_, other.data_ + size_, data_);
    }

    // 3. 拷贝赋值运算符
    ResourceManager& operator=(const ResourceManager& other);

    // 4. 移动构造函数
    ResourceManager(ResourceManager&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    // 5. 移动赋值运算符
    ResourceManager& operator=(ResourceManager&& other) noexcept;

private:
    int* data_;
    size_t size_;
};
```

### explicit 构造函数

```cpp
// ✅ 正确 - 单参数构造函数使用 explicit
class String {
public:
    explicit String(size_t length);
    explicit String(const char* str);
};

// ❌ 错误 - 允许隐式转换
void Process(const String& str);
Process(100);  // 意外：创建了长度为 100 的 String
```

### 虚函数和继承

```cpp
// ✅ 正确 - 基类虚析构函数
class Base {
public:
    virtual ~Base() = default;

    virtual void DoSomething() = 0;  // 纯虚函数
};

class Derived : public Base {
public:
    void DoSomething() override;  // 使用 override
};

// ❌ 错误 - 忘记 virtual 析构函数
class BadBase {
public:
    ~BadBase();  // 应该是 virtual！
};
```

---

## 并发编程

### 互斥锁

```cpp
// ✅ 正确 - 使用 lock_guard（简单场景）
class Counter {
public:
    void Increment() {
        std::lock_guard<std::mutex> lock(mutex_);
        ++count_;
    }

    int GetCount() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }

private:
    mutable std::mutex mutex_;
    int count_ = 0;
};
```

### 条件变量

```cpp
// ✅ 正确 - 使用条件变量
class TaskQueue {
public:
    void Push(Task task) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            queue_.push(std::move(task));
        }
        condition_.notify_one();
    }

    Task Pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        condition_.wait(lock, [this] {
            return !queue_.empty() || stop_;
        });

        if (queue_.empty()) return nullptr;

        Task task = std::move(queue_.front());
        queue_.pop();
        return task;
    }

private:
    std::mutex mutex_;
    std::condition_variable condition_;
    std::queue<Task> queue_;
    bool stop_ = false;
};
```

### 避免死锁

```cpp
// ✅ 正确 - 使用 std::scoped_lock（C++17）
void Transfer(Account& from, Account& to, double amount) {
    std::scoped_lock lock(from.mutex_, to.mutex_);  // 避免死锁

    from.Withdraw(amount);
    to.Deposit(amount);
}
```

---

## 性能优化

### 避免不必要的拷贝

```cpp
// ✅ 正确 - 使用 const 引用
void Process(const std::vector<int>& data);
void Process(const std::string& str);

// ❌ 错误 - 不必要的拷贝
void Process(std::vector<int> data);
void Process(std::string str);
```

### 预分配容器

```cpp
// ✅ 正确 - 预分配空间
std::vector<int> data;
data.reserve(10000);

for (int i = 0; i < 10000; ++i) {
    data.push_back(i);
}

// ✅ 正确 - emplace 避免临时对象
std::vector<std::pair<int, std::string>> vec;
vec.emplace_back(1, "one");
```

---

## 代码审查清单

### 提交前必须检查（MUST）

- [ ] **代码格式化**：通过 `clang-format` 检查
- [ ] **静态分析**：通过 `clang-tidy` 检查
- [ ] **编译**：无警告（`-Wall -Wextra -Werror`）
- [ ] **测试**：所有测试通过
- [ ] **覆盖率**：≥ 80%
- [ ] **内存**：无泄漏（Valgrind/AddressSanitizer）
- [ ] **注释规范**：正确使用 `//`、`//;`、`//;@` 前缀

### 推荐检查（SHOULD）

- [ ] **函数长度**：≤ 50 行
- [ ] **圈复杂度**：≤ 10
- [ ] **参数数量**：≤ 5 个
- [ ] **命名规范**：符合本标准
- [ ] **现代 C++**：使用 C++17 或更高特性

---

## 参考资源

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html)
- [cppreference.com](https://en.cppreference.com/)

**文档版本**: 1.0.0
**最后更新**: 2026-02-06
