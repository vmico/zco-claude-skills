---
name: zco-plan-new
description: 创建新的项目开发计划。根据用户输入自动生成计划文档，自动分配序号和填充模板。
allowed-tools: Bash, Read, Write, Glob
---

# 创建新的项目开发计划

## 🎯 Skill 用途

快速创建新的项目计划文档，自动：
- **查找最大序号 + 1**：扫描现有计划，分配新序号
- **生成文件名**：`plan.{NewSeq}.A{yymmdd_HHMM}.md`（'A' = Auto-generated）
- **根据用户输入填充模板**：使用 `plan.template.minimal.md` 作为基础
- **由 Claude 分析并生成详细需求**：根据任务标题推断功能需求

## 📋 何时使用此 Skill

当用户需要创建新的计划文档时：

1. **明确创建计划**
   - "创建一个新计划：实现用户认证功能"
   - "/zco-plan-new 添加日志记录中间件"
   - "新建计划：优化数据库查询性能"

2. **快速任务规划**
   - "我想做一个...的功能"
   - "需要实现..."
   - "帮我规划一下...的开发"

## 📥 参数说明

**命令格式**：
```bash
zco-plan-new <简短任务描述>
```

**参数**：
- `<任务描述>` - 必需，用户的任务描述（一句话或简短描述）

**示例**：
```bash
zco-plan-new 实现用户认证功能
zco-plan-new 优化数据库查询性能
zco-plan-new 添加日志记录中间件
zco-plan-new 重构用户管理模块
```

## 🚀 执行流程

### Step 1: 查找最大序号

**扫描所有现有计划**：

```bash
# 扫描 docs/plans/ 目录
ls docs/plans/plan.*.md

# 提取序号（支持变长数字）
# plan.1.md → 1
# plan.002.md → 2
# plan.0100.md → 100

# 找到最大值
MAX_SEQ=100
NEW_SEQ=$((MAX_SEQ + 1))  # 101
```

**序号提取算法**：
```python
import re
from pathlib import Path

def find_max_seq(plans_dir: Path) -> int:
    max_seq = 0
    for plan_file in plans_dir.glob("plan.*.md"):
        # Extract seq from filename: plan.{seq}.*.md
        match = re.match(r'plan\.(\d+)\.', plan_file.name)
        if match:
            seq = int(match.group(1))  # Convert to int (removes leading zeros)
            max_seq = max(max_seq, seq)
    return max_seq

def next_new_seq(max_seq: int) -> str:
    """
    Calculate the next sequence number as a string, padding with zeros if necessary.

    :param max_seq: The maximum sequence number found so far.
    :return: The next sequence number as a string, padded to 3 digits.
    """
    return f"{max_seq + 1:03d}"  # Zero-fill to 3 digits
```

**边界情况**：
- 无现有计划 → 从 001 开始
- 最大序号 999 → 下一个为 1000（支持任意位数）

### Step 2: 生成文件名

**命名格式**：`plan.{NewSeq}.A{yymmdd_HHMM}.md`

**组成部分**：
- `plan.` - 固定前缀
- `{NewSeq}` - 新分配的序号（如果不足三位数, 则前缀补零，如 001、002、100, 1001）
- `.A` - "Auto-generated" 标记
- `{yymmdd_HHMM}` - 时间戳（年月日时分）
- `.md` - Markdown 扩展名

**示例**：
```
plan.101.A260109_1530.md
plan.1.A260109_1600.md
plan.050.A260110_0900.md
```

**时间戳格式**：
```bash
# 格式：yymmdd_HHMM
date +%y%m%d_%H%M

# 示例输出：260109_1530
```

### Step 3: 生成计划内容

**基于 `plan.template.minimal.md` 生成**：

```yaml
---
seq: {NEW_SEQ}
title: "{用户输入的任务描述}"
author: ""
status: "draft:0"
priority: "p2:中:可纳入后续迭代计划"
created_at: ""
updated_at: ""
tags: []
---

# 开发任务：{用户输入的任务描述}

## 🎯 目标

{用户输入的一句话描述}

## 📋 详细需求

### 功能描述

{由 Claude 根据任务标题推断并生成详细需求}

1. **功能点 1**：{推断的功能需求}
   - {子需求}

2. **功能点 2**：{推断的功能需求}
   - {子需求}

### 特殊要求

{根据任务类型推断的特殊要求}
- 性能要求
- 兼容性要求
- 安全要求

## ✅ 验证标准

- [ ] 功能实现并通过测试
- [ ] 代码通过 linter 检查
- [ ] 测试覆盖率 ≥ 80%
- [ ] 文档已更新

## 🧪 测试计划

### 单元测试
{根据功能推断的测试用例}

### 集成测试
{根据功能推断的集成场景}
```

**Claude 推断逻辑**：

根据任务标题关键词推断：

| 关键词 | 推断类型 | 优先级 | 示例标签 |
|--------|----------|--------|----------|
| 实现、添加、新增 | 新功能开发 | p1/p2 | feature, new |
| 优化、改进、提升 | 性能优化 | p2 | optimization, performance |
| 修复、Bug、问题 | Bug 修复 | p0/p1 | bugfix, fix |
| 重构、整理、清理 | 代码重构 | p2/p3 | refactor, cleanup |
| 测试、验证 | 测试相关 | p2 | test, qa |
| 文档、说明 | 文档更新 | p3 | docs, documentation |
| 用户、认证、权限 | 用户系统 | p1 | user, auth, security |
| 数据库、查询、存储 | 数据层 | p1/p2 | database, data |
| API、接口、服务 | 接口开发 | p1 | api, backend |
| 前端、UI、页面 | 前端开发 | p2 | frontend, ui |

### Step 4: 写入文件

**使用 Write 工具创建文件**：

```python
# 示例代码
plan_path = f"docs/plans/plan.{new_seq}.A{timestamp}.md"
Write(file_path=plan_path, content=generated_content)
```

**原子操作**：
- 检查文件是否已存在
- 如果存在，自动添加后缀：`-2`, `-3`, ...
- 写入成功后输出确认信息

### Step 5: 确认创建

**输出成功信息**：

```markdown
✅ 计划创建成功！

📄 文件路径：docs/plans/plan.101.A260109_1530.md
📋 计划序号：101
📝 任务标题：实现用户认证功能
📊 状态：draft:0（起稿中）
🏷️  标签：feature, auth, security

下一步操作：
1. 执行计划：zco-plan 101
2. 编辑计划：vim docs/plans/plan.101.A260109_1530.md
3. 查看内容：cat docs/plans/plan.101.A260109_1530.md
```

## 🔧 Implementation Details

### 序号检测完整实现

**处理各种序号格式**：

```python
import re
from pathlib import Path

def find_max_seq_number(plans_dir: Path = Path("docs/plans")) -> int:
    """
    Find maximum sequence number from existing plan files

    Handles:
    - plan.1.md → 1
    - plan.02.md → 2
    - plan.003.md → 3
    - plan.0100.md → 100

    Returns:
        int: Maximum sequence number (0 if no plans exist)
    """
    if not plans_dir.exists():
        plans_dir.mkdir(parents=True, exist_ok=True)
        return 0

    max_seq = 0
    pattern = re.compile(r'^plan\.(\d+)\.')

    for plan_file in plans_dir.glob("plan.*.md"):
        match = pattern.match(plan_file.name)
        if match:
            seq = int(match.group(1))  # Converts '001' to 1, '0100' to 100
            max_seq = max(max_seq, seq)

    return max_seq
```

### 内容生成策略

**基于任务描述生成内容**：

1. **分析任务标题**：
   - 提取关键词（动词、名词）
   - 识别技术领域
   - 判断任务类型

2. **推断优先级**：
   - 包含"紧急"、"Bug"、"修复" → p0/p1
   - 包含"实现"、"添加" → p1/p2
   - 包含"优化"、"重构" → p2
   - 包含"文档"、"整理" → p3

3. **生成标签**：
   - 任务类型标签（feature, bugfix, optimization, etc.）
   - 技术领域标签（backend, frontend, database, etc.）
   - 功能模块标签（auth, user, api, etc.）

4. **推断功能需求**：
   - 列出主要功能点（2-3 个）
   - 每个功能点包含子需求
   - 考虑特殊要求（性能、安全、兼容性）

5. **生成测试计划**：
   - 单元测试场景
   - 集成测试场景
   - 边界条件测试

### 错误处理

**常见错误及处理**：

1. **无参数错误**
   ```
   错误：缺少任务描述
   提示：用法：zco-plan-new <任务描述>
   示例：zco-plan-new 实现用户认证功能
   ```

2. **docs/plans/ 目录不存在**
   ```
   自动创建：mkdir -p docs/plans/
   提示：已创建 docs/plans/ 目录
   ```

3. **文件名冲突**
   ```
   检测：plan.101.A260109_1530.md 已存在
   处理：自动添加后缀 → plan.101.A260109_1530-2.md
   提示：文件名已存在，已添加后缀 -2
   ```

4. **写入权限问题**
   ```
   错误：无权限写入 docs/plans/
   提示：请检查目录权限：chmod +w docs/plans/
   ```

5. **任务描述过长**
   ```
   警告：任务描述超过 100 字符
   建议：简化为一句话描述，详细需求可在计划中补充
   ```

## 📋 使用示例

### 示例 1: 创建新功能计划

**用户输入**：
```bash
zco-plan-new 实现用户认证功能
```

**执行流程**：
1. 扫描现有计划：找到最大序号 100
2. 分配新序号：101
3. 生成文件名：`plan.101.A260109_1530.md`
4. 分析任务："实现" + "用户认证" → 新功能 + 用户模块
5. 推断优先级：p1（高优先级功能）
6. 生成标签：`[feature, auth, user, security]`
7. 生成内容（包含详细需求）
8. 写入文件
9. 输出确认信息

**生成的计划内容**：
```yaml
---
seq: 101
title: "实现用户认证功能"
author: ""
status: "draft:0"
priority: "p1:高:当前迭代/排期内重点解决"
created_at: ""
updated_at: ""
tags: [feature, auth, user, security]
---

# 开发任务：实现用户认证功能

## 🎯 目标

实现完整的用户认证系统，支持用户注册、登录、登出，以及基于 JWT 的身份验证。

## 📋 详细需求

### 功能描述

1. **用户注册**：新用户注册功能
   - 邮箱验证
   - 密码强度检查
   - 防重复注册

2. **用户登录**：用户登录功能
   - 邮箱/用户名登录
   - JWT Token 生成
   - 登录失败锁定机制

3. **会话管理**：用户会话管理
   - Token 刷新机制
   - 登出功能
   - 会话过期处理

### 特殊要求

- **安全要求**：
  - 密码加密存储（bcrypt）
  - SQL 注入防护
  - CSRF 防护
  - Rate limiting

- **性能要求**：
  - 登录响应时间 < 200ms
  - Token 验证 < 50ms

## ✅ 验证标准

- [ ] 用户注册功能实现并通过测试
- [ ] 用户登录功能实现并通过测试
- [ ] JWT Token 生成和验证正确
- [ ] 所有安全要求满足
- [ ] 代码通过 linter 检查
- [ ] 测试覆盖率 ≥ 80%
- [ ] API 文档已更新

## 🧪 测试计划

### 单元测试

**测试用例 1：用户注册**
```
输入：有效的邮箱和密码
预期：用户创建成功，返回用户 ID
```

**测试用例 2：重复注册**
```
输入：已存在的邮箱
预期：返回错误：邮箱已存在
```

**测试用例 3：密码强度**
```
输入：弱密码（如 "123456"）
预期：返回错误：密码强度不足
```

### 集成测试

**场景 1：完整认证流程**
```
步骤：
1. 用户注册
2. 用户登录
3. 验证 Token
4. 访问受保护资源
5. 登出

预期结果：整个流程正常运行
```
```

**输出**：
```
✅ 计划创建成功！

📄 文件路径：docs/plans/plan.101.A260109_1530.md
📋 计划序号：101
📝 任务标题：实现用户认证功能
📊 状态：draft:0（起稿中）
🏷️  标签：feature, auth, user, security

下一步操作：
1. 执行计划：zco-plan 101
2. 编辑计划：vim docs/plans/plan.101.A260109_1530.md
3. 查看内容：cat docs/plans/plan.101.A260109_1530.md
```

### 示例 2: 创建 Bug 修复计划

**用户输入**：
```bash
zco-plan-new 修复用户登录失败 500 错误
```

**推断结果**：
- 任务类型：Bug 修复
- 优先级：p0（紧急）
- 标签：`[bugfix, user, auth, critical]`

**生成的计划包含**：
- 问题描述
- 复现步骤
- 预期行为 vs 实际行为
- 可能原因分析
- 修复方案

### 示例 3: 创建优化计划

**用户输入**：
```bash
zco-plan-new 优化数据库查询性能
```

**推断结果**：
- 任务类型：性能优化
- 优先级：p2（中等）
- 标签：`[optimization, database, performance]`

**生成的计划包含**：
- 当前性能指标
- 优化目标
- 优化方案（索引、查询重写、缓存等）
- 性能测试计划

### 示例 4: 无现有计划（首次使用）

**用户输入**：
```bash
zco-plan-new 项目初始化
```

**执行流程**：
1. 扫描 docs/plans/：无现有计划
2. 分配序号：001
3. 自动创建目录：`mkdir -p docs/plans/`
4. 生成文件：`plan.001.A260109_1600.md`
5. 输出确认信息

## 🚨 注意事项

### 必须遵守的规则

1. **序号唯一性**：
   - 自动递增，避免冲突
   - 支持任意位数（1、02、003、0100）
   - 转换为整数比较（'002' == 2）

2. **文件命名规范**：
   - 格式：`plan.{seq}.A{timestamp}.md`
   - 时间戳精确到分钟（避免冲突）
   - 'A' 前缀标记自动生成

3. **内容完整性**：
   - 必须包含 YAML front matter
   - 至少包含：seq, title, status
   - 至少包含：目标、需求、验证标准

4. **默认值**：
   - status: `draft:0`
   - priority: `p2:中:可纳入后续迭代计划`
   - author: 空字符串（可后续填充）
   - tags: 由 Claude 生成

### 推荐做法

1. **任务描述简洁**：
   - 一句话描述核心功能
   - 避免过长描述（< 100 字符）
   - 关键词明确（动词 + 名词）

2. **创建后编辑**：
   - 生成计划后可编辑补充
   - 调整优先级和详细需求
   - 添加参考信息和依赖项

3. **配合 zco-plan 使用**：
   - 创建后立即执行：`zco-plan {seq}`
   - 或先编辑再执行

## 🔗 相关资源

### 相关文件

- **计划模板**: `docs/plans/plan.template.minimal.md`
- **完整模板**: `docs/plans/plan.template.md`
- **计划目录**: `docs/plans/`
- **zco-plan Skill**: `.claude/skills/zco-plan/SKILL.md`

### 相关 Skills

- **zco-plan**: 执行现有计划
- **zco-docs-update**: 更新文档元信息
- **zco-plan-new**: 创建新计划（本 Skill）

### 命名规范

所有自定义 skills 使用 `zco-` 前缀（Zhicheng Custom Operations）

---

**Skill 版本**: 1.0.0
**最后更新**: 2026-01-09
**维护者**: 开发团队
