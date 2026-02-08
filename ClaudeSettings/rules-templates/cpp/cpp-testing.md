这份 `cpp-testing.md` 针对 C++ 的严谨性进行了优化，特别强调了 **Google Test (GTest)** 的工程化实践，并引入了 C++ 开发者最关心的内存安全与性能基准测试。

---

# 🧪 C++ 测试与质量保证规范

## 1. 核心测试框架 (Google Test)

本项目统一使用 **Google Test (GTest)** 作为单元测试框架，**Google Mock (GMock)** 作为打桩工具。

### 1.1 测试组织结构

* ✅ **文件位置**: 测试文件必须位于项目根目录的 `tests/` 文件夹内，并与 `src/` 结构对应。
* ✅ **文件名**: 必须以 `_test.cc` 或 `_unittest.cc` 结尾。
* 示例：`src/auth/manager.cc` -> `tests/auth/manager_test.cc`


* ✅ **命名空间**: 测试代码应包裹在 `namespace { ... }` (匿名命名空间) 中，防止符号污染。

---

## 2. 测试命名与语义

利用 GTest 的宏，确保测试输出具有极高的可读性。

### 2.1 命名约定

* **TestSuiteName**: 使用被测类名（如 `UserManagerTest`）。
* **TestName**: 遵循 `Condition_Result` 模式。
* ✅ `Login_WithEmptyPassword_ReturnsFalse`
* ❌ `TestLogin1`



### 2.2 断言选择

* ✅ 优先使用 `EXPECT_*` (如 `EXPECT_EQ`): 失败后继续执行，能暴露更多错误。
* ✅ 关键路径使用 `ASSERT_*`: 失败后立即终止当前测试（如指针判空）。
* ✅ 浮点数比较：必须使用 `EXPECT_NEAR` 或 `EXPECT_FLOAT_EQ`，严禁使用 `EXPECT_EQ`。

---

## 3. Mock 对象 (GMock) 规范

为了实现单元隔离，必须对外部依赖（DB、Network、Hardware）进行 Mock。

* ✅ **虚析构函数**: 被 Mock 的基类必须拥有 `virtual ~Base() = default;`。
* ✅ **宏定义**: 使用 `MOCK_METHOD(ReturnType, MethodName, (Args...), (Specs...))`。
* ❌ **严格度**: 默认使用 `NiceMock` 以减少无关调用干扰，关键逻辑使用 `StrictMock`。

```cpp
##; 示例：Mock 数据库接口
class MockDatabase : public Database {
 public:
  MOCK_METHOD(bool, Connect, (const std::string& url), (override));
};

```

---

## 4. 内存安全检查 (Critical)

C++ 测试如果不跑内存检查，则测试无效。

* ✅ **Valgrind / ASan**: 所有单元测试必须在开启 **AddressSanitizer (ASan)** 的情况下通过。
* ✅ **内存泄露**: 确保 `tests` 运行结束后的退出码为 0，且无 `memory leak` 报错。

---

## 5. 性能测试 (Benchmark)

针对高性能组件，必须提供基准测试。

* ✅ **框架**: 推荐使用 `google/benchmark`。
* ✅ **要求**:
* 关键算法（如排序、解析）必须有 `BM_` 前缀的性能测试。
* 必须在 `Release` 模式下运行基准测试。


* ❌ **禁忌**: 严禁在单元测试（GTest）中使用 `std::chrono` 手动计算耗时作为通过标准。

---

## 6. 测试覆盖率与 CI 约束

* 📈 **覆盖率指标**: 单元测试覆盖率必须 **≥ 80%**。
* 📈 **核心逻辑**: 涉及金融、协议解析、内存管理的模块覆盖率必须 **≥ 95%**。
* ✅ **检查命令**:
```bash
## 使用 gcov/lcov 生成报告
make test && lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory out

```



---

## 7. 代码自检清单 (❌/✅)

* ✅ 是否为每个 `public` 方法编写了至少一个测试用例？
* ✅ 是否测试了边界条件（空指针、溢出、最大/最小值）？
* ✅ Mock 对象的预期调用 (`EXPECT_CALL`) 是否在 `Action` 发生之前定义的？
* ❌ 严禁在测试代码中使用 `sleep()` 等待异步任务，必须使用 `Condition Variable` 或 `Future`。

---

### 给 Nico 的特别建议：

作为 **Platform Architect**，你在 C++ 项目中可以利用 `zco init` 自动生成一个带 `CMakeLists.txt` 的项目，该文件应默认集成：

1. `FetchContent` 自动拉取 GTest 和 Google Benchmark。
2. 预设好 `enable_testing()`。
3. 开启 `-fsanitize=address` 编译选项。

