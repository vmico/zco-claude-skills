---
seq: 003
title: "新增 zco-help Skill - 显示项目 Claude 工具帮助信息"
author: "Claude"
status: "completed:3"
priority: "p2:中:可纳入后续迭代计划"
created_at: "2026-01-13 14:45:00"
updated_at: "2026-01-13 14:50:00"
tags: [feature, skill, documentation, help, tooling]
---

# 开发任务：新增 zco-help Skill - 显示项目 Claude 工具帮助信息

## 🎯 目标

创建一个 `zco-help` skill，用于快速查看当前项目中可用的 Claude Code 工具（skills、commands、rules）及其用途和使用方式。

## 📋 详细需求

### 功能描述

1. **扫描工具目录**
   - 扫描 `.claude/skills/` 目录下的所有 skill
   - 扫描 `.claude/commands/` 目录（如果存在）
   - 扫描 `.claude/rules/` 目录下的规则文档

2. **提取工具信息**
   - 从 `SKILL.md` 的 YAML front matter 提取：
     - `name`: Skill 名称
     - `description`: 简短描述
     - `allowed-tools`: 允许使用的工具（可选）
   - 从 Markdown 内容提取：
     - 用途说明（"## 🎯 Skill 用途" 章节）
     - 使用示例（"## 📋 使用示例" 或命令格式）

3. **分类展示**
   - **Skills**: 自定义技能（zco-* 前缀）
   - **Commands**: 命令脚本（如果存在）
   - **Rules**: 编码规范和开发规则
   - 按字母顺序排列

4. **输出格式**
   - 清晰的分类标题
   - 表格形式展示（名称、描述、用法）
   - 彩色输出（可选，如果支持）
   - 链接到详细文档

### 特殊要求

- **兼容性**：支持符号链接（symlinks）
- **错误处理**：优雅处理缺失的目录或文件
- **性能**：快速扫描和输出（< 1s）
- **可扩展性**：易于添加新的工具类型

### 输入输出

**输入**：
```bash
zco-help                    # 显示所有工具
zco-help skills             # 只显示 skills
zco-help rules              # 只显示 rules
zco-help zco-plan           # 显示特定 skill 的详细信息
```

**输出示例**：
```
🔧 Claude Code 工具帮助

📁 当前项目：zco-claude-init
📂 配置目录：.claude/

================================================================================
📚 Skills (自定义技能)
================================================================================

名称             | 描述                                    | 用法
-----------------|----------------------------------------|----------------------
zco-plan         | 执行结构化开发计划                      | zco-plan {seq}
zco-plan-new     | 创建新的开发计划                        | zco-plan-new <描述>
zco-docs-update  | 更新 CLAUDE.md Git 元信息               | zco-docs-update
zco-help         | 显示 Claude 工具帮助信息                | zco-help [类型]

详细文档：cat .claude/skills/{skill-name}/SKILL.md

================================================================================
📋 Commands (命令脚本)
================================================================================

暂无自定义命令

================================================================================
📖 Rules (编码规范)
================================================================================

名称                        | 描述
----------------------------|------------------------------------------
go/coding-standards.md      | Go 项目编程标准（注释规范、命名等）
go/go-testing.md            | Go 测试规范（测试文件组织、表驱动测试）
go/check-standards.sh       | 代码标准检查脚本
go/list-comments.sh         | 列出所有非代码注释

详细文档：cat .claude/rules/{rule-path}

================================================================================
💡 提示
================================================================================

- 查看 skill 详情：zco-help {skill-name}
- 查看所有计划：ls docs/plans/
- 执行计划：zco-plan {seq}
- 创建计划：zco-plan-new <任务描述>

📚 更多信息：cat CLAUDE.md
```

## ✅ 验证标准

- [ ] 能够扫描 `.claude/skills/`、`.claude/commands/`、`.claude/rules/` 目录
- [ ] 正确提取 YAML front matter 和 Markdown 内容
- [ ] 支持过滤参数（skills、rules、特定 skill 名称）
- [ ] 输出格式清晰、易读
- [ ] 处理符号链接（symlinks）正确
- [ ] 优雅处理缺失的目录或文件
- [ ] 创建 `SKILL.md` 文档完整
- [ ] 在 CLAUDE.md 中添加相关说明

## 🧪 测试计划

### 单元测试

**测试用例 1：扫描所有 skills**
```bash
输入：zco-help skills
预期：列出所有 zco-* skills 及其描述
```

**测试用例 2：显示特定 skill**
```bash
输入：zco-help zco-plan
预期：显示 zco-plan 的详细信息（从 SKILL.md 提取）
```

**测试用例 3：扫描 rules**
```bash
输入：zco-help rules
预期：列出所有编码规范文档
```

**测试用例 4：缺失目录**
```bash
场景：.claude/commands/ 不存在
预期：提示 "暂无自定义命令"，不报错
```

### 集成测试

**场景 1：完整使用流程**
```
步骤：
1. 用户运行 zco-help
2. 查看所有可用工具
3. 选择 zco-plan 查看详情
4. 执行 zco-plan 001

预期结果：用户能够快速了解并使用工具
```

**场景 2：新项目（首次链接）**
```
步骤：
1. 新项目通过 zco_claude_init.py 链接配置
2. 运行 zco-help
3. 查看链接的 skills 和 rules

预期结果：正确显示符号链接的工具
```

## 📚 参考信息

### 相关文件

- `.claude/skills/*/SKILL.md` - Skill 定义文档
- `.claude/rules/` - 编码规范目录
- `CLAUDE.md` - 项目主文档
- `ClaudeSettings/skills/README.md` - Skills 开发指南

### 相关 Skills

- `zco-plan` - 执行开发计划
- `zco-plan-new` - 创建新计划
- `zco-docs-update` - 更新文档

### 技术要点

1. **YAML 解析**：提取 front matter
2. **Markdown 解析**：提取章节内容
3. **文件系统遍历**：扫描目录和文件
4. **符号链接处理**：正确处理 symlinks
5. **格式化输出**：表格对齐、分隔符

### 实现建议

**Skill 文件位置**：
```
ClaudeSettings/skills/zco-help/
└── SKILL.md
```

**核心逻辑**：
1. 使用 `Glob` 工具扫描目录
2. 使用 `Read` 工具读取 SKILL.md
3. 解析 YAML front matter（正则或简单解析）
4. 格式化输出（使用 Markdown 表格）

**YAML 解析示例**：
```bash
# 提取 YAML front matter
sed -n '/^---$/,/^---$/p' SKILL.md | grep 'name:' | cut -d: -f2 | xargs
```

**Markdown 章节提取**：
```bash
# 提取 "## 🎯 Skill 用途" 章节
sed -n '/^## 🎯 Skill 用途/,/^##/p' SKILL.md | head -n -1
```

## 🏗️ 实现步骤

### Step 1: 创建 Skill 目录和文档

```bash
mkdir -p ClaudeSettings/skills/zco-help
vim ClaudeSettings/skills/zco-help/SKILL.md
```

### Step 2: 编写 SKILL.md

包含以下章节：
- YAML front matter（name, description, allowed-tools）
- 🎯 Skill 用途
- 📋 何时使用此 Skill
- 📥 参数说明
- 🚀 执行流程
- 📋 使用示例
- 🚨 注意事项

### Step 3: 实现核心逻辑

- 扫描 `.claude/skills/` 目录
- 提取每个 skill 的信息
- 扫描 `.claude/rules/` 目录
- 格式化输出

### Step 4: 测试

```bash
# 测试基本功能
zco-help

# 测试过滤
zco-help skills
zco-help rules

# 测试特定 skill
zco-help zco-plan
```

### Step 5: 更新文档

- 在 `CLAUDE.md` 中添加 zco-help 说明
- 更新 Skills 表格
- 添加使用示例

## 🔄 后续改进

- [ ] 支持彩色输出（如果终端支持）
- [ ] 添加搜索功能（按关键词搜索）
- [ ] 生成 HTML 版本的帮助文档
- [ ] 支持 JSON 输出格式（便于脚本解析）
- [ ] 添加使用统计（记录最常用的工具）

---

**计划创建时间**: 2026-01-13 14:45
**预计工作量**: 2-3 小时
**依赖项**: 无
