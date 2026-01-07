# 项目开发计划管理指南

## 📖 简介

本目录用于管理项目的结构化开发计划。每个计划都是一个独立的 Markdown 文档，包含任务目标、详细需求、验证标准等信息。通过 **zco-plan** skill，Claude 可以自动读取并执行这些计划。

## 🎯 核心概念

### 什么是开发计划？

开发计划是对单个任务或功能的完整描述，包括：
- **目标**：要实现什么
- **需求**：具体做什么
- **验证**：如何确认完成
- **测试**：如何验证正确性

### 为什么使用计划文档？

✅ **标准化**：统一的任务描述格式
✅ **可追溯**：完整记录任务信息和执行历史
✅ **自动化**：一条命令即可执行（`zco-plan {seq}`）
✅ **协作友好**：易于版本控制和团队共享
✅ **AI 友好**：结构化信息便于 Claude 理解和执行

## 📁 目录结构

```
docs/plans/
├── README.md           # 本文件 - 使用指南
├── plan.template.md    # 计划文档标准模板
├── plan.001.260107.md  # 计划 001 - 配置同步功能
├── plan.002.260108.md  # 计划 002 - .claudeignore 生成
└── plan.003.260108.md  # 计划 003 - 用户认证实现
```

## 📝 文档命名规范

### 标准格式

```
plan.{seq}.{date}.md
```

**参数说明**：
- `{seq}` - 计划序号，3 位数字（001-999）
- `{date}` - 创建日期，YYMMDD 格式

### 命名示例

```
✅ plan.001.260107.md  # 计划 001，2026 年 1 月 7 日
✅ plan.002.260108.md  # 计划 002，2026 年 1 月 8 日
✅ plan.010.260115.md  # 计划 010，2026 年 1 月 15 日

❌ plan.1.260108.md    # 错误：seq 不足 3 位
❌ plan.002.md         # 错误：缺少日期
❌ plan-002-260108.md  # 错误：使用了 - 而非 .
```

### 版本管理

同一个序号可以有多个日期版本：

```
plan.002.260105.md  # 计划 002 的旧版本
plan.002.260108.md  # 计划 002 的新版本（最新）
```

**规则**：执行 `zco-plan 002` 时，自动选择日期最新的版本（260108）

## 🚀 快速开始

### 1. 创建新计划

**方式 A：复制模板（推荐）**

```bash
# 1. 确定序号（例如 003）
ls docs/plans/  # 查看现有计划，避免重复

# 2. 复制模板
cp docs/plans/plan.template.md docs/plans/plan.003.$(date +%y%m%d).md

# 3. 编辑计划文档
vim docs/plans/plan.003.260108.md

# 4. 填写必需信息
#    - YAML front matter（seq、date、title、author 等）
#    - 目标、详细需求、验证标准
```

**方式 B：手动创建**

```bash
# 创建新文件
touch docs/plans/plan.003.260108.md

# 添加 YAML front matter 和内容
# 参考 plan.template.md 的结构
```

### 2. 执行计划

```bash
# 方式 1：在 Claude CLI 中执行
zco-plan 003

# 方式 2：在对话中请求
"执行计划 003"
"按照 plan.003 实施任务"
```

### 3. 查看所有计划

```bash
# 方式 1：列出文件
ls docs/plans/

# 方式 2：使用 zco-plan（无参数）
zco-plan
```

## 📋 计划文档结构

### YAML Front Matter（必需）

文档开头的元数据部分，使用 YAML 格式：

```yaml
---
seq: 003                          # 计划序号（3 位数字）
date: 20260108                    # 创建日期（YYMMDD）
title: "实现用户认证功能"         # 任务标题
author: "张三"                    # 作者/负责人
status: pending                   # 任务状态
priority: high                    # 优先级
created: 2026-01-08 10:30:00      # 创建时间戳
updated: 2026-01-08 10:30:00      # 最后更新时间
tags: [feature, backend, auth]    # 标签列表
---
```

**字段说明**：

| 字段 | 类型 | 必需 | 说明 | 可选值 |
|------|------|------|------|--------|
| `seq` | 数字 | ✅ | 计划序号 | 001-999 |
| `date` | 字符串 | ✅ | 创建日期 | YYMMDD 格式 |
| `title` | 字符串 | ✅ | 任务标题 | 简洁描述（≤50 字） |
| `author` | 字符串 | ✅ | 作者姓名 | 真实姓名或用户名 |
| `status` | 字符串 | ✅ | 任务状态 | `pending` / `in-progress` / `completed` / `cancelled` |
| `priority` | 字符串 | ✅ | 优先级 | `low` / `medium` / `high` |
| `created` | 时间戳 | ✅ | 创建时间 | `YYYY-MM-DD HH:MM:SS` |
| `updated` | 时间戳 | ✅ | 更新时间 | `YYYY-MM-DD HH:MM:SS` |
| `tags` | 数组 | ⏸️ | 标签列表 | `[tag1, tag2]` |

### Markdown 内容（必需部分）

#### 🎯 目标

简洁描述任务的核心目标（1-2 句话）

```markdown
## 🎯 目标

实现基于 JWT 的用户认证系统，支持用户注册、登录、登出功能。
```

#### 📋 详细需求

详细说明功能需求、特殊要求、输入输出规范

```markdown
## 📋 详细需求

### 功能描述
1. **用户注册**：邮箱 + 密码注册，发送验证邮件
2. **用户登录**：邮箱/用户名 + 密码登录，返回 JWT token
3. **用户登出**：使 token 失效

### 特殊要求
- 密码使用 bcrypt 加密存储
- JWT token 有效期 7 天
- 支持刷新 token

### 输入/输出
**注册接口**：
- 输入：`POST /api/auth/register { email, password }`
- 输出：`{ user_id, email, created_at }`
```

#### ✅ 验证标准

明确的完成标准清单，所有条目必须满足

```markdown
## ✅ 验证标准

### 功能验证
- [ ] 用户注册功能实现并通过测试
- [ ] 用户登录功能实现并通过测试
- [ ] Token 刷新功能实现并通过测试

### 质量验证
- [ ] 代码通过 linter 检查
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过
```

#### 🧪 测试计划

测试用例和验证场景

```markdown
## 🧪 测试计划

### 单元测试
- 测试密码加密/验证
- 测试 JWT token 生成/解析
- 测试输入参数验证

### 集成测试
- 完整的注册 → 登录 → 访问受保护资源流程
- Token 过期自动刷新流程
```

### Markdown 内容（可选部分）

#### 🏗️ 实施步骤

如果任务复杂，可以列出详细的实施步骤

```markdown
## 🏗️ 实施步骤

### 阶段 1：数据模型
1. [ ] 设计用户表结构
2. [ ] 实现用户模型

### 阶段 2：核心功能
1. [ ] 实现注册逻辑
2. [ ] 实现登录逻辑
```

#### 📚 参考信息

相关文档、现有实现、技术选型依据

```markdown
## 📚 参考信息

### 相关文档
- [JWT 规范](https://jwt.io/)
- [Bcrypt 使用指南](https://example.com/bcrypt)

### 技术选型
- JWT 库：`github.com/golang-jwt/jwt/v5`
- 密码加密：`golang.org/x/crypto/bcrypt`
```

## 🔄 任务状态管理

### 状态类型

| 状态 | 说明 | 使用场景 |
|------|------|----------|
| `pending` | 待开始 | 计划已创建，尚未开始执行 |
| `in-progress` | 进行中 | 正在执行任务 |
| `completed` | 已完成 | 任务完成并验证通过 |
| `cancelled` | 已取消 | 任务不再需要或被其他方案替代 |

### 状态转换流程

```
pending → in-progress → completed
   ↓             ↓
cancelled    cancelled
```

### 更新状态

**方式 1：手动更新**

```yaml
# 编辑计划文档的 YAML front matter
status: pending → in-progress
updated: 2026-01-08 14:30:00
```

**方式 2：版本控制（推荐）**

```bash
# 1. 任务完成后，创建新版本
cp docs/plans/plan.003.260108.md docs/plans/plan.003.completed.260110.md

# 2. 更新新版本的状态
status: completed
updated: 2026-01-10 18:00:00

# 3. 提交到 Git
git add docs/plans/
git commit -m "docs: complete plan 003 - user authentication"
```

## 💡 最佳实践

### 1. 计划编写

**清晰的目标**：
- ✅ 目标明确，一句话说清楚
- ❌ 目标模糊，包含多个不相关任务

**详细的需求**：
- ✅ 功能点细分，每个点都可验证
- ❌ 需求笼统，无法判断是否完成

**明确的验证标准**：
- ✅ 使用清单格式（`- [ ]`），标准可量化
- ❌ 标准模糊，主观判断

**示例**：

```markdown
✅ 好的目标：
实现用户认证系统，支持注册、登录、登出功能

❌ 不好的目标：
实现用户相关功能，包括认证、权限、个人资料等

✅ 好的验证标准：
- [ ] 用户注册功能通过 10 个单元测试
- [ ] API 响应时间 < 200ms

❌ 不好的验证标准：
- [ ] 功能基本完成
- [ ] 性能还不错
```

### 2. 序号管理

**连续编号**：
```bash
# ✅ 推荐：按顺序编号
plan.001.md
plan.002.md
plan.003.md

# ⚠️ 可接受：跳号（但不推荐）
plan.001.md
plan.005.md  # 跳过了 002-004
plan.010.md
```

**预留空间**：
```bash
# 不同类型任务使用不同的序号段
001-099: 基础功能开发
100-199: 性能优化任务
200-299: 重构任务
300-399: 文档和工具
```

### 3. 版本控制

**提交计划文档**：

```bash
# 创建新计划时
git add docs/plans/plan.003.260108.md
git commit -m "docs: add plan 003 - user authentication"

# 更新计划时
git add docs/plans/plan.003.260108.md
git commit -m "docs: update plan 003 - add test plan"

# 完成计划时
git add docs/plans/plan.003.260108.md
git commit -m "docs: complete plan 003"
```

**Code Review**：
- 新建计划时，请团队成员 review 需求描述
- 确保验证标准清晰、可执行
- 讨论技术选型和潜在风险

### 4. 团队协作

**分工明确**：
```yaml
# 在 YAML front matter 中指定负责人
author: "张三"
reviewers: ["李四", "王五"]
```

**定期同步**：
- 每日/每周回顾计划执行情况
- 更新计划状态
- 识别阻塞因素

**知识共享**：
- 计划文档作为知识库的一部分
- 完成的计划可作为未来任务的参考
- 记录技术选型和踩过的坑

## 🛠️ 常用命令

### 创建计划

```bash
# 自动使用当前日期
cp docs/plans/plan.template.md docs/plans/plan.$(printf "%03d" {seq}).$(date +%y%m%d).md

# 示例：创建计划 005
cp docs/plans/plan.template.md docs/plans/plan.005.$(date +%y%m%d).md
```

### 查看计划

```bash
# 列出所有计划
ls -l docs/plans/plan.*.md

# 按日期排序
ls -lt docs/plans/plan.*.md

# 查看特定计划
cat docs/plans/plan.003.260108.md

# 查看计划元信息（仅 YAML）
head -n 15 docs/plans/plan.003.260108.md
```

### 执行计划

```bash
# 在 Claude CLI 中执行
zco-plan 003

# 或在对话中请求
"执行计划 003"
"运行 plan 003"
```

### 搜索计划

```bash
# 按标题搜索
grep "title:" docs/plans/plan.*.md

# 按状态搜索
grep "status: pending" docs/plans/plan.*.md

# 按作者搜索
grep "author: 张三" docs/plans/plan.*.md

# 全文搜索
grep -r "用户认证" docs/plans/
```

## 📊 计划统计

### 查看计划概览

```bash
# 统计计划总数
ls docs/plans/plan.*.md | wc -l

# 按状态统计
grep -h "^status:" docs/plans/plan.*.md | sort | uniq -c

# 示例输出：
#   5 status: pending
#   3 status: in-progress
#   12 status: completed
#   1 status: cancelled
```

### 生成计划列表

```bash
# 生成简单列表
for file in docs/plans/plan.*.md; do
  seq=$(grep "^seq:" "$file" | awk '{print $2}')
  title=$(grep "^title:" "$file" | sed 's/title: "//;s/"$//')
  status=$(grep "^status:" "$file" | awk '{print $2}')
  echo "[$seq] $title - $status"
done

# 示例输出：
# [001] 配置同步功能 - completed
# [002] .claudeignore 生成 - in-progress
# [003] 用户认证实现 - pending
```

## 🔍 故障排查

### 问题 1：zco-plan 找不到计划

**症状**：
```
zco-plan 003
未找到计划 003
```

**排查步骤**：
```bash
# 1. 检查文件是否存在
ls docs/plans/plan.003.*.md

# 2. 检查文件名格式
#    必须是 plan.{seq}.{date}.md
#    seq 必须是 3 位数字

# 3. 如果文件不存在，创建它
cp docs/plans/plan.template.md docs/plans/plan.003.$(date +%y%m%d).md
```

### 问题 2：YAML 解析错误

**症状**：
Claude 无法正确理解计划元数据

**排查步骤**：
```bash
# 1. 检查 YAML 格式
head -n 15 docs/plans/plan.003.260108.md

# 2. 确保格式正确：
#    - 以 --- 开始和结束
#    - 键值对格式：key: value
#    - 字符串使用双引号
#    - 数组使用方括号

# 3. 验证 YAML 语法（可选）
# 使用在线工具：https://www.yamllint.com/
```

### 问题 3：多个同序号计划，不确定使用哪个

**症状**：
```
docs/plans/plan.002.260105.md
docs/plans/plan.002.260108.md
```

**解决方案**：
```bash
# zco-plan 会自动选择日期最新的（260108）

# 如果要手动选择：
# 1. 重命名旧版本（添加后缀）
mv docs/plans/plan.002.260105.md docs/plans/plan.002.260105.old.md

# 2. 或移动到归档目录
mkdir -p docs/plans/archive
mv docs/plans/plan.002.260105.md docs/plans/archive/
```

## 📚 示例计划

### 示例 1：简单功能实现

参考 `plan.001.260107.md`（配置同步功能）：
- 清晰的目标
- 4 个具体功能点
- 输入输出示例
- 测试用例

### 示例 2：复杂任务拆分

参考 `plan.002.260108.md`（.claudeignore 生成）：
- 逻辑拆分为多个步骤
- 特殊格式要求
- 测试场景定义

## 🚀 进阶功能（未来）

### 计划依赖关系

```yaml
---
seq: 005
depends_on: [003, 004]  # 依赖计划 003 和 004
---
```

### 计划归档

```bash
# 完成的计划自动归档
docs/plans/plan.003.260108.md
→ docs/plans/archive/2026/01/plan.003.260108.md
```

### 计划模板库

```
docs/plans/templates/
├── feature.md     # 新功能开发模板
├── bugfix.md      # Bug 修复模板
├── refactor.md    # 重构任务模板
└── research.md    # 技术研究模板
```

## 🤝 贡献指南

如果需要改进计划管理流程：

1. 修改模板：编辑 `plan.template.md`
2. 更新文档：编辑本 `README.md`
3. 提交 PR：说明修改原因和收益
4. 团队讨论：达成共识后合并

## 📞 获取帮助

**文档资源**：
- 计划模板：`docs/plans/plan.template.md`
- Skill 定义：`.claude/skills/zco-plan/SKILL.md`
- 项目文档：`CLAUDE.md`

**常见问题**：
- 如何创建计划？→ 参考"快速开始"章节
- 如何执行计划？→ 运行 `zco-plan {seq}`
- 如何查看所有计划？→ 运行 `zco-plan` 或 `ls docs/plans/`

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-08
**维护者**: 开发团队
