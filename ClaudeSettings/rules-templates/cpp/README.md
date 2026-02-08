# C++ 编程规范

本目录包含 C++ 项目的编程标准和开发规范。

## 📚 规范文档

### 核心文档

- **[coding-standards.md](coding-standards.md)** - C++ 编程标准
  - 注释规范（`//` vs `//;` vs `//;@` 约定）
  - 命名规范（类、函数、变量、命名空间）
  - 代码组织（头文件、源文件、include 顺序）
  - 内存管理（RAII、智能指针）
  - 错误处理（异常、noexcept）
  - 并发编程（线程、互斥锁）
  - 现代 C++ 特性（auto、lambda、移动语义）
  - 模板编程
  - 性能优化

- **[cpp-testing.md](cpp-testing.md)** - C++ 测试规范
  - Google Test 框架使用
  - 测试组织和命名
  - Mock 对象
  - 测试覆盖率（≥ 80%）
  - 性能测试

## 🛠️ 工具脚本

### 代码质量检查

1. **`check-standards.sh`** - 全面的代码标准检查
   ```bash
   ./ClaudeSettings/rules/cpp/check-standards.sh
   ```

   检查项：
   - ✅ 代码格式（clang-format）
   - ✅ 静态分析（clang-tidy, cppcheck）
   - ✅ 测试通过率
   - ✅ 测试覆盖率（≥ 80%）
   - ✅ 注释规范统计

2. **`list-comments.sh`** - 列出所有非代码注释
   ```bash
   ./ClaudeSettings/rules/cpp/list-comments.sh
   ```

   显示：
   - 📋 TODO 列表
   - 🔧 FIXME 列表
   - ⚠️ HACK 列表
   - ⚡ OPTIMIZE 列表
   - 🗑️ DEPRECATED 列表
   - 📝 NOTE 列表

## 📋 配置模板

- **`.clang-format.template`** - 代码格式化配置
- **`.clang-tidy.template`** - 静态分析配置
- **`CMakeLists.txt.template`** - CMake 构建配置

## 💡 示例代码

- **`example.h`** - 头文件示例
- **`example.cpp`** - 源文件示例

展示了注释规范、命名规范、代码组织的实际应用。

## 🚀 快速开始

### 1. 安装必要工具

```bash
# Ubuntu/Debian
sudo apt-get install clang-format clang-tidy cppcheck

# macOS
brew install clang-format llvm cppcheck

# Google Test
sudo apt-get install libgtest-dev
```

### 2. 配置项目

```bash
# 复制配置模板到项目根目录
cp ClaudeSettings/rules/cpp/.clang-format.template .clang-format
cp ClaudeSettings/rules/cpp/.clang-tidy.template .clang-tidy
```

### 3. 运行代码检查

```bash
# 在项目根目录运行
./ClaudeSettings/rules/cpp/check-standards.sh
```

### 4. 在代码中使用注释约定

```cpp
// 标准代码注释 - 用于 API 文档
// Calculate the total price

//; 代码逻辑解释 - 给开发者看
//; Small orders don't get discounts

//;@TODO: Add email validation
//;@FIXME: Memory leak in destructor
//;@NOTE: Thread-safe implementation
//;@OPTIMIZE: Use move semantics
```

## 📊 质量标准

### 强制要求（MUST）

- ✅ 代码覆盖率 ≥ 80%
- ✅ 无编译警告（-Wall -Wextra -Werror）
- ✅ 所有测试通过
- ✅ 无内存泄漏（Valgrind 或 AddressSanitizer）
- ✅ 正确使用注释标记（`//` vs `//;` vs `//;@`）

### 推荐要求（SHOULD）

- ⭐ 函数长度 ≤ 50 行
- ⭐ 圈复杂度 ≤ 10
- ⭐ 参数数量 ≤ 5 个
- ⭐ 使用现代 C++ 特性（C++17+）
- ⭐ 无重复代码

## 🔗 参考资源

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [Effective Modern C++](https://www.oreilly.com/library/view/effective-modern-c/9781491908419/)

---

**维护者**: 开发团队
**最后更新**: 2026-02-05
