# 项目开发规范

本目录包含项目的编程标准和开发规范。

## 📚 规范文档

### Go 语言规范

- **[coding-standards.md](go/coding-standards.md)** - Go 项目编程标准
  - 注释规范（`//` vs `//;` 约定）
  - 命名规范
  - 代码组织
  - 错误处理
  - 并发编程
  - 测试规范
  - 性能优化

## 🛠️ 工具脚本

### Go 项目工具

1. **`check-standards.sh`** - 全面的代码标准检查
   ```bash
   # 在项目根目录运行
   ./.claude/rules/go/check-standards.sh
   ```

   检查项：
   - ✅ 代码格式（gofmt）
   - ✅ Imports 顺序（goimports）
   - ✅ 测试通过率
   - ✅ 测试覆盖率（≥ 80%）
   - ✅ 竞态条件检测
   - ✅ Linter 检查
   - ✅ 注释规范统计

2. **`list-comments.sh`** - 列出所有非代码注释
   ```bash
   # 在项目根目录运行
   ./.claude/rules/go/list-comments.sh
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
# 安装 golangci-lint
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin

# 安装 goimports
go install golang.org/x/tools/cmd/goimports@latest
```

### 2. 配置项目

在项目根目录创建 `.golangci.yml`：

```yaml
linters:
  enable:
    - gofmt
    - goimports
    - govet
    - errcheck
    - staticcheck
    - unused
    - gosimple
    - ineffassign
    - deadcode
    - typecheck
    - gocyclo
    - funlen

linters-settings:
  gocyclo:
    min-complexity: 10
  funlen:
    lines: 50
    statements: 40
```

### 3. 设置 Git Hooks（可选）

创建 `.git/hooks/pre-commit`：

```bash
#!/bin/bash
./.claude/rules/go/check-standards.sh
```

```bash
chmod +x .git/hooks/pre-commit
```

### 4. 在代码中使用注释约定

```go
package main

// Add 计算两个整数的和
// 这是标准的代码注释，使用 //
func Add(a, b int) int {
    //; TODO: 添加溢出检查
    //; NOTE: 这个函数会在 v2.0 中支持浮点数
    return a + b
}

//; DEPRECATED: 使用 Add 函数替代
//; 此函数将在 v2.0 移除
func AddLegacy(a, b int) int {
    return a + b
}
```

## 📋 注释规范速查

| 前缀 | 用途 | 示例 |
|------|------|------|
| `//` | 代码功能注释 | `// CalculateTotal 计算订单总金额` |
| `//; TODO:` | 待实现功能 | `//; TODO: 添加参数验证` |
| `//; FIXME:` | 需要修复的问题 | `//; FIXME: Redis 连接超时问题` |
| `//; HACK:` | 临时解决方案 | `//; HACK: 等待 API v2 升级后移除` |
| `//; OPTIMIZE:` | 性能优化点 | `//; OPTIMIZE: 可以使用批量查询` |
| `//; DEPRECATED:` | 已废弃代码 | `//; DEPRECATED: 使用 NewAPI 替代` |
| `//; NOTE:` | 开发者备注 | `//; NOTE: 这里需要考虑并发安全` |
| `//; DEBUG:` | 调试信息 | `//; DEBUG: 临时日志，发布前删除` |

## 🎯 质量标准

### 强制要求（MUST）

- ✅ 代码覆盖率 ≥ 80%
- ✅ 无编译错误和 linter 错误
- ✅ 所有测试通过
- ✅ 无竞态条件
- ✅ 正确使用注释标记（`//` vs `//;`）

### 推荐要求（SHOULD）

- ⭐ 函数长度 ≤ 50 行
- ⭐ 圈复杂度 ≤ 10
- ⭐ 参数数量 ≤ 5 个
- ⭐ 无重复代码

## 📖 使用示例

### 示例 1：检查代码标准

```bash
# 运行完整检查
$ ./.claude/rules/go/check-standards.sh

🔍 开始检查 Go 编程标准...

📝 [1/7] 检查代码格式...
✓ 代码格式正确

📦 [2/7] 检查 imports 顺序...
✓ Imports 顺序正确

🧪 [3/7] 运行测试...
✓ 所有测试通过

📊 [4/7] 检查测试覆盖率...
✓ 测试覆盖率: 87.5% (≥ 80%)

🏃 [5/7] 检查竞态条件...
✓ 无竞态条件

🔍 [6/7] 运行 linter...
✓ Linter 检查通过

💬 [7/7] 检查注释规范...
   - TODO: 3 项
   - FIXME: 1 项
   - HACK: 0 项
   - DEPRECATED: 0 项

================================
✓ 所有检查通过！
```

### 示例 2：查看待办事项

```bash
# 列出所有非代码注释
$ ./.claude/rules/go/list-comments.sh

💬 Go 项目非代码注释列表
======================================

📋 TODO 列表:
./service/user.go:45://; TODO: 添加邮箱验证
./handler/order.go:78://; TODO: 实现订单取消功能

🔧 FIXME 列表:
./cache/redis.go:23://; FIXME: Redis 连接偶尔超时

⚠️  HACK 列表:
   (无)

======================================
📊 统计信息:
   TODO:       2 项
   FIXME:      1 项
   HACK:       0 项
```

## 🔧 集成到 IDE

### VS Code

创建 `.vscode/settings.json`：

```json
{
  "go.lintTool": "golangci-lint",
  "go.lintOnSave": "package",
  "go.formatTool": "gofmt",
  "editor.formatOnSave": true
}
```

### GoLand / IntelliJ IDEA

1. Settings → Tools → File Watchers
2. 添加 gofmt 和 goimports
3. Settings → Editor → Inspections → Go
4. 启用所有推荐的检查项

## 📝 提交代码前检查清单

在提交代码前，确保：

- [ ] 运行 `check-standards.sh` 并全部通过
- [ ] 使用 `list-comments.sh` 检查是否有未完成的 TODO/FIXME
- [ ] 所有新增代码都有单元测试
- [ ] 所有导出的函数都有文档注释（使用 `//`）
- [ ] 所有 TODO、FIXME 等使用 `//;` 前缀
- [ ] 代码已通过 code review

## 🤝 贡献规范更新

如果需要更新或改进这些规范：

1. 修改对应的 `.md` 文件
2. 如有必要，更新检查脚本
3. 在团队中讨论并达成共识
4. 提交 PR 并说明修改原因

## 📚 参考资源

- [Effective Go](https://golang.org/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Uber Go Style Guide](https://github.com/uber-go/guide)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)

---

**维护者**: 开发团队
**最后更新**: 2026-01-06
