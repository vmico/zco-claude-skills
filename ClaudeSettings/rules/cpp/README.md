# C++ 项目开发规范

本目录包含 C++ 项目的编程标准和开发规范。

## 📚 规范文档

### C++ 语言规范

- **[coding-standards.md](coding-standards.md)** - C++ 项目编程标准
  - 注释规范（`//` vs `//;` 约定）
  - 命名规范（命名空间、类、函数、变量、常量）
  - 代码组织（头文件、源文件、include 顺序）
  - 内存管理（RAII、智能指针）
  - 现代 C++ 特性（C++11/14/17/20）
  - 错误处理（异常、noexcept）
  - 并发编程（线程、互斥锁）
  - 测试规范
  - 性能优化

- **[cpp-testing.md](cpp-testing.md)** - C++ 测试规范
  - 测试框架选择（Google Test、Catch2）
  - 测试文件组织
  - 单元测试编写规范
  - Mock 对象使用（Google Mock）
  - 测试覆盖率要求（≥80%）
  - 性能测试（Benchmark）

## 🛠️ 工具脚本

### C++ 项目工具

1. **`check-standards.sh`** - 全面的代码标准检查
   ```bash
   # 在项目根目录运行
   ./ClaudeSettings/rules/cpp/check-standards.sh
   ```

   检查项：
   - ✅ 代码格式（clang-format）
   - ✅ 静态分析（clang-tidy、cppcheck）
   - ✅ 构建检查（CMake）
   - ✅ 测试运行（CTest）
   - ✅ 测试覆盖率（≥ 80%）
   - ✅ 注释规范统计

2. **`list-comments.sh`** - 列出所有非代码注释
   ```bash
   # 在项目根目录运行
   ./ClaudeSettings/rules/cpp/list-comments.sh
   ```

   显示：
   - 📋 TODO 列表
   - 🔧 FIXME 列表
   - ⚠️ HACK 列表
   - ⚡ OPTIMIZE 列表
   - 🗑️ DEPRECATED 列表
   - 📝 NOTE 列表

## 🚀 快速开始

### 1. 安装必要工具

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    clang-format \
    clang-tidy \
    cppcheck \
    cmake \
    g++ \
    lcov

# macOS
brew install \
    llvm \
    cppcheck \
    cmake \
    lcov

# 安装 Google Test
# Ubuntu/Debian
sudo apt-get install libgtest-dev

# macOS
brew install googletest
```

### 2. 配置项目

复制配置模板到项目根目录：

```bash
# 代码格式化配置
cp ClaudeSettings/rules/cpp/.clang-format.template .clang-format

# 静态分析配置
cp ClaudeSettings/rules/cpp/.clang-tidy.template .clang-tidy

# CMake 配置（参考模板）
cp ClaudeSettings/rules/cpp/CMakeLists.txt.template CMakeLists.txt
```

### 3. 设置 Git Hooks（可选）

创建 `.git/hooks/pre-commit`：

```bash
#!/bin/bash
./ClaudeSettings/rules/cpp/check-standards.sh
```

```bash
chmod +x .git/hooks/pre-commit
```

### 4. 在代码中使用注释约定

```cpp
#pragma once

#include <string>

namespace myproject {

//; User 表示系统用户
//; 包含用户的基本信息和认证数据
class User {
public:
    //; 构造函数，验证邮箱格式
    explicit User(const std::string& email);

    //;@TODO: 添加密码哈希功能
    //;@NOTE: 这里需要考虑线程安全
    void setPassword(const std::string& password);

private:
    std::string email_;
    std::string password_;  //;@FIXME: 应该存储哈希值而不是明文
};

//;@DEPRECATED: 使用 User 类构造函数替代
//; 此函数将在 v2.0 移除
User* CreateUserLegacy(const char* email);

} // namespace myproject
```

## 📋 注释规范速查

| 前缀 | 用途 | 示例 |
|------|------|------|
| `//` | 代码功能注释 | `// Calculate total price` |
| `//;` | 代码逻辑解释 | `//; Small orders don't get discounts` |
| `//;@TODO:` | 待实现功能 | `//;@TODO: Add email validation` |
| `//;@FIXME:` | 需要修复的问题 | `//;@FIXME: Memory leak in destructor` |
| `//;@HACK:` | 临时解决方案 | `//;@HACK: Remove after API v2` |
| `//;@OPTIMIZE:` | 性能优化点 | `//;@OPTIMIZE: Use move semantics` |
| `//;@DEPRECATED:` | 已废弃代码 | `//;@DEPRECATED: Use NewAPI instead` |
| `//;@NOTE:` | 开发者备注 | `//;@NOTE: Thread-safe implementation` |
| `//;@DEBUG:` | 调试信息 | `//;@DEBUG: Temporary log, remove before release` |

## 🎯 质量标准

### 强制要求（MUST）

- ✅ 代码覆盖率 ≥ 80%
- ✅ 无编译错误和警告（-Wall -Wextra -Werror）
- ✅ 所有测试通过
- ✅ 无内存泄漏（Valgrind/AddressSanitizer）
- ✅ 正确使用注释标记（`//` vs `//;`）
- ✅ 通过 clang-tidy 检查

### 推荐要求（SHOULD）

- ⭐ 函数长度 ≤ 50 行
- ⭐ 圈复杂度 ≤ 10
- ⭐ 参数数量 ≤ 5 个
- ⭐ 无重复代码
- ⭐ 使用现代 C++ 特性（C++17 或更高）

## 🔧 集成到 IDE

### VS Code

安装扩展：
- C/C++ (Microsoft)
- C/C++ Extension Pack
- Clang-Format
- CMake Tools

创建 `.vscode/settings.json`：

```json
{
  "C_Cpp.formatting": "clangFormat",
  "C_Cpp.clang_format_style": "file",
  "C_Cpp.codeAnalysis.clangTidy.enabled": true,
  "C_Cpp.codeAnalysis.clangTidy.config": "file",
  "editor.formatOnSave": true,
  "C_Cpp.default.cppStandard": "c++17"
}
```

### CLion

1. Settings → Editor → Code Style → C/C++
2. 选择 "Project" 方案
3. 导入 `.clang-format` 配置

Settings → Languages & Frameworks → C/C++ → Clang-Tidy
- 启用 "Use .clang-tidy config"

### Vim/Neovim

使用 ALE 插件：

```vim
" .vimrc
let g:ale_linters = {'cpp': ['clangtidy', 'cppcheck']}
let g:ale_fixers = {'cpp': ['clang-format']}
let g:ale_fix_on_save = 1
```

## 📝 提交代码前检查清单

在提交代码前，确保：

- [ ] 运行 `check-standards.sh` 并全部通过
- [ ] 使用 `list-comments.sh` 检查是否有未完成的 TODO/FIXME
- [ ] 所有新增代码都有单元测试
- [ ] 所有导出的函数都有文档注释（使用 `//`）
- [ ] 所有 TODO、FIXME 等使用 `//;@` 前缀
- [ ] 代码已通过 code review
- [ ] 无内存泄漏（运行 Valgrind 或 AddressSanitizer）

## 🤝 贡献规范更新

如果需要更新或改进这些规范：

1. 修改对应的 `.md` 文件
2. 如有必要，更新检查脚本
3. 在团队中讨论并达成共识
4. 提交 PR 并说明修改原因

## 📚 参考资源

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html)
- [Effective Modern C++](https://www.oreilly.com/library/view/effective-modern-c/9781491908419/)
- [cppreference.com](https://en.cppreference.com/)

---

**维护者**: 开发团队
**最后更新**: 2026-02-06
