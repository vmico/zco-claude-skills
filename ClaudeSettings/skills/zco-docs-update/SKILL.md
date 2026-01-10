---
name: zco-docs-update
description: 更新 CLAUDE.md 文档的 Git 元信息（提交 ID、分支、最新提交等）。当用户需要同步项目文档、维护代码库文档，或明确要求更新 CLAUDE.md 时使用此 Skill。
allowed-tools: Bash, Read, Glob
---

# 更新 CLAUDE.md 文档元信息

## 🎯 Skill 用途

自动更新项目根目录下 `CLAUDE.md` 文件中的 Git 相关元信息，保持项目文档与代码仓库同步。

**更新内容包括**：
- **Git Commit ID**（完整哈希 + 短版本）
- **当前 Git 分支**
- **最新提交信息**（消息、作者、时间）
- **应用版本**（从 main.go 自动提取）
- **文档更新时间戳**

## 📋 何时使用此 Skill

当以下情况发生时，Claude 会自动提议使用此 Skill（或您也可以手动请求）：

1. **用户明确请求**
   - "更新 CLAUDE.md 的 Git 信息"
   - "同步项目文档"
   - "运行 co-docs-update 脚本"

2. **代码提交后**
   - 完成重要功能开发后
   - 准备提交代码前
   - 发布新版本前

3. **分支切换后**
   - 从一个分支切换到另一个分支
   - 需要确认当前环境信息

4. **定期维护**
   - 每日/每周的文档维护
   - Code Review 前的文档检查

## 🚀 使用步骤

### Step 1: 查看当前状态

首先，我会显示 CLAUDE.md 当前的元信息状态：

```bash
# 查看当前文档元信息
head -20 CLAUDE.md
```

### Step 2: 执行更新脚本

运行项目的文档更新脚本：

```bash
# 执行更新
bash .claude/zco-scripts/co-docs-update.sh
```

**脚本执行流程**：
1. ✅ 验证当前目录是 Git 仓库
2. ✅ 检查 CLAUDE.md 文件是否存在
3. ✅ 创建备份文件（格式：`CLAUDE.md._.YYMMDD_HHMM`）
4. ✅ 收集 Git 元信息（commit、branch、author 等）
5. ✅ 从 main.go 提取应用版本
6. ✅ 使用 sed 更新文档中的对应字段
7. ✅ 显示更新前后的差异
8. ✅ 询问是否删除备份文件

### Step 3: 查看更新结果

我会展示更新后的差异，并确认更新是否成功：

```bash
# 查看更新后的元信息
head -20 CLAUDE.md

# 查看 Git 状态
git status CLAUDE.md
```

### Step 4: 提交更改（可选）

如果需要，我会帮您提交更改到 Git：

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md metadata"
```

## 📝 更新的字段说明

脚本会精确更新 CLAUDE.md 中以下字段（位于 "文档元信息" 部分）：

| 字段 | 说明 | 示例 |
|------|------|------|
| **更新时间** | 当前时间戳 | `2026-01-08 16:30:45` |
| **Git Commit** | 短哈希 + 完整哈希 | `` `280e2ba` (280e2bae6...) `` |
| **Git Branch** | 当前分支名 | `` `server_idc_alpha` `` |
| **最新提交** | 提交信息 + 作者 + 时间 | `ignore: ai-forge (by 宁蓉, 2026-01-06 23:01:23 +0800)` |
| **应用版本** | 从 main.go 提取 | `25.12.31` |
| **最后更新** | 文档底部时间戳 | `2026-01-08 16:30:45` |

## 🔧 脚本功能详解

### 自动备份机制

```bash
# 备份文件命名规则
CLAUDE.md._.YYMMDD_HHMM

# 示例
CLAUDE.md._.260108_1630
```

- ✅ 更新前自动创建备份
- ✅ 时间戳命名，易于追溯
- ✅ 更新失败时可快速回滚
- ✅ 更新成功后可选择保留或删除

### Git 信息采集

脚本使用以下 Git 命令采集信息：

```bash
# 完整 Commit 哈希
git log -1 --pretty=format:"%H"

# 短 Commit 哈希
git log -1 --pretty=format:"%h"

# 提交消息
git log -1 --pretty=format:"%s"

# 作者
git log -1 --pretty=format:"%an"

# 提交时间
git log -1 --pretty=format:"%ad" --date=iso

# 当前分支
git rev-parse --abbrev-ref HEAD
```

### 版本提取逻辑

从 `main.go` 中提取版本号：

```go
// main.go 中的版本定义
const version string = "25.12.31"

// 脚本提取命令
grep -E 'const version string = "' main.go | sed -E 's/.*"(.*)".*/\1/'
```

### 安全的文本替换

使用 `sed` 进行精确的正则替换，确保只更新目标字段：

```bash
sed -e "s|^- \*\*更新时间\*\*:.*|- **更新时间**: $CURRENT_TIME|" \
    -e "s|^- \*\*Git Commit\*\*:.*|- **Git Commit**: \`$GIT_COMMIT_SHORT\` ($GIT_COMMIT_FULL)|" \
    ...
```

## ⚠️ 注意事项

### 前置条件

- ✅ 必须在 Git 仓库根目录或子目录运行
- ✅ 项目根目录必须存在 `CLAUDE.md` 文件
- ✅ 脚本必须有执行权限（`chmod +x .claude/zco-scripts/co-docs-update.sh`）
- ✅ main.go 中需要有 `const version string = "..."` 定义

### 安全性

- ✅ 更新前自动创建备份，防止数据丢失
- ✅ 使用 `sed` 替换特定行，不影响其他内容
- ✅ 显示更新差异，允许用户审查
- ✅ 出错时自动退出，不破坏文档

### 兼容性

- ✅ 支持 Linux 和 macOS
- ⚠️ Windows 需要 Git Bash 或 WSL 环境
- ✅ 需要 bash 4.0+、sed、git 命令

## 🐛 失败排查

### 错误 1: "未找到 Git 仓库"

**原因**：不在 Git 项目目录中

**解决方案**：
```bash
# 进入项目根目录
cd /path/to/yj3d-anno-server

# 验证 Git 仓库
git status
```

### 错误 2: "CLAUDE.md 文件不存在"

**原因**：项目根目录缺少 CLAUDE.md

**解决方案**：
```bash
# 方式 1: 手动创建（如果已经创建过）
ls CLAUDE.md

# 方式 2: 重新生成文档
# 请求 Claude 重新创建 CLAUDE.md
```

### 错误 3: 版本显示 "unknown"

**原因**：main.go 中没有 `const version string` 定义

**解决方案**：
```bash
# 检查 main.go
grep "const version" main.go

# 如果没有，添加版本定义：
# const version string = "XX.YY.ZZ"
```

### 错误 4: 权限不足

**原因**：脚本没有执行权限

**解决方案**：
```bash
# 添加执行权限
chmod +x .claude/zco-scripts/co-docs-update.sh

# 验证权限
ls -l .claude/zco-scripts/co-docs-update.sh
```

### 错误 5: sed 命令失败

**原因**：CLAUDE.md 格式被手动修改，导致正则不匹配

**解决方案**：
```bash
# 查看备份文件
ls CLAUDE.md._.*.md

# 检查元信息部分格式
head -20 CLAUDE.md

# 确保元信息格式为：
# - **更新时间**: YYYY-MM-DD HH:MM:SS
# - **Git Commit**: `short` (full)
# ...
```

## 📚 使用示例

### 示例 1: 日常更新

**用户请求**：
```
更新一下 CLAUDE.md 的 Git 信息
```

**Claude 执行**：
1. 运行 `bash .claude/zco-scripts/co-docs-update.sh`
2. 显示更新前后的差异
3. 询问是否保留备份
4. 确认更新成功

### 示例 2: 提交前检查

**用户请求**：
```
我准备提交代码了，帮我同步一下项目文档
```

**Claude 执行**：
1. 运行文档更新脚本
2. 显示 Git 状态
3. 建议是否一起提交 CLAUDE.md
4. 提供提交命令

### 示例 3: 发布新版本

**用户请求**：
```
我们要发布 v26.01.08 版本，更新所有文档
```

**Claude 执行**：
1. 确认 main.go 中的版本号已更新
2. 运行文档更新脚本
3. 验证版本号正确提取
4. 建议创建版本标签

## 🔗 相关资源

### 项目文件

- **文档位置**: `CLAUDE.md`（项目根目录）
- **脚本位置**: `scripts/co-docs-update.sh`
- **版本定义**: `main.go:21`（`const version string = "..."`）

### 相关 Skills

如果您有其他文档相关的 Skills，可以组合使用：

- `zco-docs-update`: 更新 CLAUDE.md 元信息（本 Skill）
- `/init`: 初始化新的 CLAUDE.md 文档（如果存在）
- 其他自定义 `zco-*` 命令（按您的命名规范）

### 团队协作

- ✅ 将此 Skill 提交到 Git，团队共享
- ✅ 在 CI/CD 中集成自动更新（可选）
- ✅ 定期运行保持文档最新

## 💡 最佳实践

### 1. 定期更新

建议在以下时机更新文档：
- 每次重要 feature 完成后
- 每天工作结束前
- 提交 Pull Request 前
- 发布新版本前

### 2. 与 Git 工作流集成

```bash
# Git Pre-commit Hook 示例
# .git/hooks/pre-commit
#!/bin/bash
if [ -f "CLAUDE.md" ]; then
    bash .claude/zco-scripts/co-docs-update.sh -y  # 自动更新
    git add CLAUDE.md
fi
```

### 3. CI/CD 集成

在 `.gitlab-ci.yml` 中添加文档检查：

```yaml
check-docs:
  stage: test
  script:
    - bash .claude/zco-scripts/co-docs-update.sh
    - git diff --exit-code CLAUDE.md || (echo "文档需要更新" && exit 1)
```

## 🎓 技术细节

### Skill 调用逻辑

1. **自动触发**：当用户请求与文档更新相关时，Claude 自动调用
2. **工具限制**：仅允许使用 Bash、Read、Glob 工具（安全性）
3. **上下文感知**：Claude 会检查当前项目状态，决定是否合适运行

### 脚本输出格式

脚本使用彩色输出，便于阅读：

- 🔵 蓝色 `[INFO]` - 信息提示
- 🟢 绿色 `[SUCCESS]` - 成功消息
- 🟡 黄色 `[WARN]` - 警告信息
- 🔴 红色 `[ERROR]` - 错误信息

---

**Skill 版本**: 1.0.0
**最后更新**: 2026-01-08
**维护者**: 开发团队
