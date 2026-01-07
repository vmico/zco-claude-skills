# Go 语言测试规则

## Go 测试基础规范

### 文件命名

**规则：测试文件必须以 `_test.go` 结尾。**

```
user.go       → user_test.go
validator.go  → validator_test.go
service.go    → service_test.go
```

### 测试函数签名

**规则：测试函数必须符合 Go 测试规范。**

```go
// ✓ 正确
func TestRegisterUser(t *testing.T) {
    // ...
}

func TestRegisterUser_ValidInput(t *testing.T) {
    // ...
}

// ❌ 错误
func testRegisterUser(t *testing.T) {  // 小写开头
    // ...
}

func TestRegisterUser() {  // 缺少 *testing.T 参数
    // ...
}
```

### 包声明

**规则：测试文件可以使用相同包名或添加 `_test` 后缀。**

```go
// 方式 1：黑盒测试（推荐用于测试公共 API）
package user_test

import (
    "testing"
    "myapp/internal/user"
)

func TestRegisterUser(t *testing.T) {
    u, err := user.Register("test@example.com", "Pass123!")
    // 只能访问公共 API
}

// 方式 2：白盒测试（用于测试内部逻辑）
package user

import "testing"

func TestValidateEmail(t *testing.T) {
    err := validateEmail("test@example.com")
    // 可以访问私有函数
}
```

**选择建议：**
- 优先使用黑盒测试（`package xxx_test`）
- 只在必须测试私有函数时使用白盒测试
- 一个包可以同时有两种测试文件

## Go 测试工具

### 使用 testing 包

```go
import "testing"

func TestExample(t *testing.T) {
    // t.Error/t.Errorf - 报告错误但继续执行
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }

    // t.Fatal/t.Fatalf - 报告错误并停止测试
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }

    // t.Log/t.Logf - 记录信息（只在失败或 -v 时显示）
    t.Logf("Processing user: %s", user.Email)

    // t.Skip/t.Skipf - 跳过测试
    if runtime.GOOS == "windows" {
        t.Skip("skipping test on Windows")
    }
}
```

### 推荐使用 testify/assert

**安装：**
```bash
go get github.com/stretchr/testify/assert
```

**使用：**
```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestRegisterUser(t *testing.T) {
    user, err := RegisterUser("test@example.com", "Pass123!")

    // 更清晰的断言
    assert.NoError(t, err)
    assert.NotNil(t, user)
    assert.Equal(t, "test@example.com", user.Email)
    assert.NotEmpty(t, user.ID)
    assert.True(t, len(user.ID) > 0)
    assert.Contains(t, user.Email, "@")
}
```

### 推荐使用 testify/mock（如果需要 mock）

```go
import (
    "github.com/stretchr/testify/mock"
)

type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) Save(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}

func (m *MockUserRepository) FindByEmail(email string) (*User, error) {
    args := m.Called(email)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

// 在测试中使用
func TestRegisterUser_EmailExists_ReturnsError(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("FindByEmail", "existing@example.com").
        Return(&User{Email: "existing@example.com"}, nil)

    service := NewUserService(mockRepo)
    _, err := service.RegisterUser("existing@example.com", "Pass123!")

    assert.Error(t, err)
    mockRepo.AssertExpectations(t)
}
```

## 表驱动测试（Table-Driven Tests）

**Go 推荐的测试模式，适合测试多个相似场景。**

### 基本结构

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string        // 测试名称
        email   string        // 输入
        wantErr bool          // 期望是否有错误
    }{
        {
            name:    "有效邮箱",
            email:   "user@example.com",
            wantErr: false,
        },
        {
            name:    "缺少@符号",
            email:   "userexample.com",
            wantErr: true,
        },
        {
            name:    "空邮箱",
            email:   "",
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateEmail(tt.email)

            if tt.wantErr {
                assert.Error(t, err, "Expected error for %s", tt.name)
            } else {
                assert.NoError(t, err, "Unexpected error for %s", tt.name)
            }
        })
    }
}
```

### 子测试（Subtests）

**使用 t.Run 创建子测试，提供更好的组织和错误报告。**

```go
func TestUserService(t *testing.T) {
    t.Run("注册用户", func(t *testing.T) {
        t.Run("有效输入", func(t *testing.T) {
            user, err := service.RegisterUser("user@example.com", "Pass123!")
            assert.NoError(t, err)
            assert.NotNil(t, user)
        })

        t.Run("无效邮箱", func(t *testing.T) {
            _, err := service.RegisterUser("invalid", "Pass123!")
            assert.Error(t, err)
        })
    })

    t.Run("登录用户", func(t *testing.T) {
        // ...
    })
}
```

**运行特定子测试：**
```bash
go test -run TestUserService/注册用户/有效输入
```

## 测试辅助函数

### Setup 和 Teardown

**使用辅助函数进行测试准备和清理。**

```go
// 测试级别的 setup
func setupTest(t *testing.T) (*UserService, *MockRepository) {
    mockRepo := new(MockRepository)
    service := NewUserService(mockRepo)
    return service, mockRepo
}

// 包级别的 setup/teardown
func TestMain(m *testing.M) {
    // 全局 setup
    setupDatabase()

    // 运行测试
    code := m.Run()

    // 全局 teardown
    teardownDatabase()

    os.Exit(code)
}

// 使用 t.Cleanup（推荐）
func TestWithCleanup(t *testing.T) {
    // 创建临时资源
    tmpFile := createTempFile()

    // 注册清理函数
    t.Cleanup(func() {
        os.Remove(tmpFile)
    })

    // 测试逻辑
    // ...
}
```

### 测试辅助函数命名

**辅助函数应以 `test` 开头（小写），避免被识别为测试函数。**

```go
// ✓ 正确：辅助函数
func testCreateUser(t *testing.T, email string) *User {
    t.Helper()  // 标记为辅助函数，错误时显示调用者的行号
    user, err := CreateUser(email, "Pass123!")
    if err != nil {
        t.Fatalf("failed to create user: %v", err)
    }
    return user
}

// 在测试中使用
func TestUserOperations(t *testing.T) {
    user := testCreateUser(t, "test@example.com")
    // ...
}
```

## Go 特定的测试技巧

### 1. 使用接口进行 Mock

**定义接口以便于测试时替换实现。**

```go
// 定义接口
type UserRepository interface {
    Save(user *User) error
    FindByEmail(email string) (*User, error)
}

// 生产实现
type PostgresUserRepository struct {
    db *sql.DB
}

func (r *PostgresUserRepository) Save(user *User) error {
    // 真实数据库操作
}

// 测试实现
type InMemoryUserRepository struct {
    users map[string]*User
}

func (r *InMemoryUserRepository) Save(user *User) error {
    r.users[user.Email] = user
    return nil
}

// 服务依赖接口，不依赖具体实现
type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}
```

### 2. 测试并发代码

**测试涉及 goroutine 的代码。**

```go
func TestConcurrentAccess(t *testing.T) {
    counter := NewSafeCounter()

    // 使用 WaitGroup 等待所有 goroutine
    var wg sync.WaitGroup
    goroutines := 100
    increments := 1000

    for i := 0; i < goroutines; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := 0; j < increments; j++ {
                counter.Increment()
            }
        }()
    }

    wg.Wait()

    expected := goroutines * increments
    assert.Equal(t, expected, counter.Value())
}

// 检测竞态条件
// go test -race ./...
```

### 3. 测试 Panic

```go
func TestDivide_ByZero_Panics(t *testing.T) {
    assert.Panics(t, func() {
        Divide(10, 0)
    }, "Divide by zero should panic")
}

// 或者使用 recover
func TestDivide_ByZero_Panics_Manual(t *testing.T) {
    defer func() {
        if r := recover(); r == nil {
            t.Error("Expected panic but didn't get one")
        }
    }()

    Divide(10, 0)
}
```

### 4. 测试 HTTP Handler

```go
import (
    "net/http"
    "net/http/httptest"
)

func TestUserHandler_Register(t *testing.T) {
    // 创建请求
    reqBody := `{"email":"user@example.com","password":"Pass123!"}`
    req := httptest.NewRequest("POST", "/api/users/register",
        strings.NewReader(reqBody))
    req.Header.Set("Content-Type", "application/json")

    // 创建响应记录器
    rr := httptest.NewRecorder()

    // 调用 handler
    handler := NewUserHandler(mockService)
    handler.ServeHTTP(rr, req)

    // 断言
    assert.Equal(t, http.StatusCreated, rr.Code)
    assert.Contains(t, rr.Body.String(), "user@example.com")
}
```

### 5. 使用 Testdata 目录

**Go 约定：测试数据放在 `testdata` 目录中。**

```
mypackage/
├── user.go
├── user_test.go
└── testdata/
    ├── valid_user.json
    ├── invalid_user.json
    └── test_config.yaml
```

```go
func TestLoadUser(t *testing.T) {
    data, err := os.ReadFile("testdata/valid_user.json")
    assert.NoError(t, err)

    var user User
    err = json.Unmarshal(data, &user)
    assert.NoError(t, err)
    assert.Equal(t, "user@example.com", user.Email)
}
```

## 基准测试（Benchmarks）

**测试性能时使用基准测试。**

```go
func BenchmarkValidateEmail(b *testing.B) {
    email := "user@example.com"

    b.ResetTimer()  // 重置计时器，忽略 setup 时间

    for i := 0; i < b.N; i++ {
        ValidateEmail(email)
    }
}

// 运行基准测试
// go test -bench=. -benchmem
```

## 示例测试（Examples）

**可作为文档的示例测试。**

```go
func ExampleRegisterUser() {
    user, err := RegisterUser("user@example.com", "SecurePass123!")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }

    fmt.Println("User created:", user.Email)
    // Output:
    // User created: user@example.com
}
```

## Go 测试命令

### 基本命令

```bash
# 运行所有测试
go test ./...

# 运行并显示详细输出
go test -v ./...

# 运行特定包的测试
go test ./internal/user

# 运行特定测试
go test -run TestRegisterUser

# 运行匹配正则的测试
go test -run "TestRegister.*"

# 运行子测试
go test -run TestUserService/注册用户
```

### 覆盖率

```bash
# 显示覆盖率
go test -cover ./...

# 生成覆盖率报告
go test -coverprofile=coverage.out ./...

# 查看覆盖率详情
go tool cover -func=coverage.out

# 生成 HTML 报告
go tool cover -html=coverage.out
```

### 其他有用参数

```bash
# 检测竞态条件
go test -race ./...

# 运行基准测试
go test -bench=. ./...

# 查看内存分配
go test -bench=. -benchmem ./...

# 设置超时
go test -timeout 30s ./...

# 并行运行测试
go test -parallel 4 ./...

# 短测试模式（跳过耗时测试）
go test -short ./...
```

## 测试组织最佳实践

### 1. 文件组织

```
mypackage/
├── user.go              # 实现代码
├── user_test.go         # 黑盒测试
├── user_internal_test.go # 白盒测试（如果需要）
├── mock_repository.go   # Mock 对象
└── testdata/            # 测试数据
    └── users.json
```

### 2. 测试分类

**使用 build tags 分类测试。**

```go
// +build integration

package user_test

func TestDatabaseIntegration(t *testing.T) {
    // 集成测试
}
```

```bash
# 只运行单元测试（默认）
go test ./...

# 运行集成测试
go test -tags=integration ./...
```

### 3. 测试命名层次

```go
func TestUserService(t *testing.T) {
    t.Run("Register", func(t *testing.T) {
        t.Run("ValidInput", func(t *testing.T) {
            t.Run("CreatesUser", func(t *testing.T) {
                // ...
            })
            t.Run("ReturnsUserID", func(t *testing.T) {
                // ...
            })
        })
        t.Run("InvalidEmail", func(t *testing.T) {
            // ...
        })
    })
}
```

## 常见陷阱

### ❌ 陷阱 1：共享状态

```go
// ❌ 错误：测试间共享状态
var testUser *User

func TestCreateUser(t *testing.T) {
    testUser = CreateUser("test@example.com")
}

func TestUpdateUser(t *testing.T) {
    UpdateUser(testUser, "new@example.com")  // 依赖上一个测试
}

// ✓ 正确：每个测试独立
func TestUpdateUser(t *testing.T) {
    user := CreateUser("test@example.com")
    UpdateUser(user, "new@example.com")
}
```

### ❌ 陷阱 2：忽略错误

```go
// ❌ 错误
func TestCreateUser(t *testing.T) {
    user, _ := CreateUser("test@example.com")  // 忽略错误
    assert.NotNil(t, user)
}

// ✓ 正确
func TestCreateUser(t *testing.T) {
    user, err := CreateUser("test@example.com")
    assert.NoError(t, err)
    assert.NotNil(t, user)
}
```

### ❌ 陷阱 3：不使用 t.Helper()

```go
// ❌ 错误：辅助函数不标记 Helper
func createTestUser(t *testing.T) *User {
    user, err := CreateUser("test@example.com")
    if err != nil {
        t.Fatal(err)  // 错误会显示这一行，而不是调用者
    }
    return user
}

// ✓ 正确
func createTestUser(t *testing.T) *User {
    t.Helper()  // 标记为辅助函数
    user, err := CreateUser("test@example.com")
    if err != nil {
        t.Fatal(err)  // 错误会显示调用者的行号
    }
    return user
}
```

## 测试覆盖率目标

- **包级别**：≥ 80%
- **关键业务逻辑**：≥ 90%
- **公共 API**：100%
- **错误处理路径**：≥ 80%

## 质量检查清单

- [ ] 所有测试文件以 `_test.go` 结尾
- [ ] 测试函数以 `Test` 开头
- [ ] 使用表驱动测试处理多个场景
- [ ] 使用 `t.Run` 组织子测试
- [ ] 辅助函数使用 `t.Helper()`
- [ ] 不忽略错误返回值
- [ ] 测试相互独立
- [ ] 运行 `go test -race` 无竞态条件
- [ ] 覆盖率达标
- [ ] 测试执行快速
