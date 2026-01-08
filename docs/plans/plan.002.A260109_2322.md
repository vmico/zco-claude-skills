---
seq: 002
title: "新增 ClaudeSkill: zco-week-summary - 周工作总结生成工具"
author: ""
status: "draft:0"
priority: "p2:中:可纳入后续迭代计划"
created_at: ""
updated_at: ""
tags: [feature, skill, automation, documentation, productivity]
---

# 开发任务：新增 ClaudeSkill: zco-week-summary - 周工作总结生成工具

## 🎯 目标

创建一个自动化工具，用于分析最近一周的工作记录（Git 提交、计划执行、文档变更等），生成结构化的周工作总结报告。

## 📋 详细需求

### 功能描述

1. **数据源收集**：从多个来源收集一周内的工作数据
   - Git 提交记录（commit message, 文件变更统计）
   - 已完成的开发计划（docs/plans/ 中 status=completed 的计划）
   - 文档更新记录（CLAUDE.md, README.md 等关键文档的变更）
   - Claude 对话历史（如果可访问 _.claude_hist/）

2. **数据分析与分类**：智能分类工作内容
   - 按类型分类：新功能开发、Bug 修复、性能优化、文档更新、重构等
   - 按模块分类：识别涉及的项目模块（如 yj2d-anno-server, yj3d-anno-server, yjxd-anno-libs 等）
   - 统计代码量：新增/修改/删除的行数
   - 识别关键成果：重要功能上线、重大 Bug 修复

3. **生成结构化报告**：输出 Markdown 格式的周总结
   - 时间范围：明确起止日期
   - 工作概览：本周完成的主要任务数量统计
   - 详细内容：按分类列出具体工作项
   - 技术亮点：本周技术难点和解决方案
   - 遗留问题：未完成的任务和下周计划
   - 统计数据：提交次数、代码行数、文件变更数等

4. **可配置选项**：支持灵活配置
   - 时间范围：默认最近 7 天，可自定义（如最近 14 天）
   - 输出路径：默认 `docs/summaries/week-{YYMMDD}.md`
   - 数据源选择：可选择包含/排除特定数据源
   - 语言：支持中文/英文输出

### 特殊要求

- **自动化程度**：
  - 一键生成，无需手动输入
  - 自动识别时间范围（如果今天是周五，自动统计本周一到周五）
  - 自动去重（避免同一工作被重复统计）

- **智能分析**：
  - 使用 Claude 分析 commit message，识别任务类型
  - 自动关联 Git 提交和开发计划
  - 识别跨项目的关联工作

- **可读性**：
  - Markdown 格式美观
  - 使用表格、列表、emoji 增强可读性
  - 关键数据可视化（如代码量柱状图的文本表示）

- **性能要求**：
  - 处理时间 < 30 秒（对于正常一周的工作量）
  - 支持大型代码库（1000+ 提交/周）

### 输入/输出规格

**输入参数**：
```bash
# 默认：最近 7 天
zco-week-summary

# 自定义时间范围
zco-week-summary --days 14

# 指定起止日期
zco-week-summary --from 2026-01-06 --to 2026-01-12

# 仅分析特定项目
zco-week-summary --project yj2d-anno-server

# 指定输出路径
zco-week-summary --output docs/summaries/custom-summary.md
```

**输出格式示例**：
```markdown
# 周工作总结 (2026-01-06 ~ 2026-01-12)

## 📊 工作概览

| 指标 | 数量 |
|------|------|
| Git 提交次数 | 23 |
| 完成开发计划 | 3 |
| 新增代码行数 | +1,245 |
| 删除代码行数 | -567 |
| 文件变更数 | 45 |
| 涉及项目 | 3 |

## ✅ 主要成果

### 新功能开发 (2 项)

1. **用户认证系统重构** (plan.101)
   - 实现 JWT Token 刷新机制
   - 添加登录失败锁定功能
   - 提交: e8cd900, 7005b57
   - 代码量: +456 -123 行

2. **日志记录中间件** (plan.102)
   - 实现请求/响应日志记录
   - 添加性能监控
   - 提交: 0b118e1
   - 代码量: +234 -45 行

### Bug 修复 (3 项)

1. Redis 连接超时问题
   - 添加重试机制和连接池
   - 提交: abc1234

2. ...

### 性能优化 (1 项)

1. 数据库查询优化
   - 添加索引，查询速度提升 60%
   - 提交: def5678

### 文档更新 (2 项)

1. 更新 CLAUDE.md，添加 Skills 使用说明
2. 完善 API 文档

## 🔧 技术亮点

1. **JWT Token 刷新机制**
   - 问题：原有 Token 过期后需要重新登录
   - 方案：实现滑动窗口刷新策略
   - 效果：用户体验提升，会话保持时间延长

2. **数据库查询优化**
   - 问题：订单列表查询耗时 2s+
   - 方案：添加复合索引 + 查询重写
   - 效果：查询时间降至 0.8s，提升 60%

## ⚠️ 遗留问题与下周计划

### 待完成任务

- [ ] plan.103: 实现缓存预热机制 (进行中，完成 60%)
- [ ] 修复 WebSocket 断线重连问题

### 下周计划

1. 完成缓存预热机制开发
2. 开始性能测试和压力测试
3. 整理本周代码，提交 Code Review

## 📈 工作统计

### 提交时间分布

```
周一: ████████ (8 commits)
周二: ██████ (6 commits)
周三: ████ (4 commits)
周四: ██ (2 commits)
周五: ██████ (3 commits)
```

### 涉及项目

- yj2d-anno-server (15 commits)
- yjxd-anno-libs (5 commits)
- _.ai-claude-skills (3 commits)

---

**生成时间**: 2026-01-12 18:30:00
**数据来源**: Git (23 commits), Plans (3 completed), Docs (2 updated)
```

## ✅ 验证标准

- [ ] 能够正确收集 Git 提交记录（最近 7 天）
- [ ] 能够读取并分析已完成的开发计划
- [ ] 能够检测文档变更
- [ ] 生成的 Markdown 格式正确且美观
- [ ] 智能分类准确率 ≥ 85%
- [ ] 支持自定义时间范围参数
- [ ] 代码通过 linter 检查
- [ ] SKILL.md 文档完整（包含用法示例）
- [ ] 在测试环境验证生成效果

## 🧪 测试计划

### 单元测试

**测试用例 1：Git 提交解析**
```
输入：Git log 输出（最近 7 天）
预期：正确解析 commit hash, message, author, date, stats
```

**测试用例 2：Commit 分类**
```
输入：
- "feat: 添加用户认证功能"
- "fix: 修复登录 500 错误"
- "perf: 优化数据库查询"

预期：
- 分类为 "新功能开发"
- 分类为 "Bug 修复"
- 分类为 "性能优化"
```

**测试用例 3：时间范围过滤**
```
输入：--days 14
预期：仅包含最近 14 天的提交
```

**测试用例 4：计划关联**
```
输入：Commit message 包含 "plan.101"
预期：自动关联到 docs/plans/plan.101.*.md
```

### 集成测试

**场景 1：完整周总结生成**
```
步骤：
1. 在测试仓库创建模拟提交（包含各种类型）
2. 创建已完成的开发计划
3. 运行 zco-week-summary
4. 验证生成的报告内容

预期结果：
- 所有提交被正确统计
- 分类准确
- Markdown 格式正确
- 统计数据准确
```

**场景 2：空工作周**
```
步骤：
1. 在没有任何提交的仓库运行
2. 验证输出

预期结果：
- 不报错
- 输出提示信息："本周暂无工作记录"
```

**场景 3：跨项目总结**
```
步骤：
1. 在包含多个子项目的仓库运行
2. 验证按项目分类

预期结果：
- 正确识别各子项目
- 按项目分组显示
```

### 边界测试

1. **大量提交**：模拟 1000+ 提交/周，验证性能
2. **中文 commit message**：验证中文解析正确
3. **特殊字符**：验证 Markdown 特殊字符转义
4. **时区问题**：验证跨时区提交的时间计算

## 📚 参考信息

### 相关技术

- **Git 命令**：
  ```bash
  # 获取最近 7 天的提交
  git log --since="7 days ago" --pretty=format:"%H|%an|%ae|%ad|%s" --date=iso --numstat

  # 统计代码变更
  git diff --shortstat HEAD~7..HEAD
  ```

- **文件读取**：使用 Read tool 读取计划文档
- **Markdown 生成**：使用 Write tool 写入报告

### 现有实现参考

- **zco-plan**: 读取计划文档的逻辑
- **zco-docs-update**: 更新文档元信息的逻辑
- **zco-plan-new**: 生成 Markdown 文档的逻辑

### 类似工具

- `git-summary`: 统计 Git 仓库信息
- `git-quick-stats`: 快速查看 Git 统计数据

## 🎨 实现建议

### 文件结构

```
ClaudeSettings/skills/zco-week-summary/
├── SKILL.md              # Skill 定义和使用说明
└── templates/            # 可选：报告模板
    └── report.template.md
```

### 核心逻辑

1. **参数解析**：解析命令行参数（时间范围、输出路径等）
2. **数据收集**：
   - 调用 Bash 工具执行 `git log`
   - 读取 docs/plans/ 中的计划文档
   - 检查关键文档的变更
3. **数据分析**：
   - 解析 commit message（正则匹配关键词）
   - 关联 commit 和 plan（匹配 "plan.XXX"）
   - 统计代码量（解析 --numstat 输出）
4. **报告生成**：
   - 构建 Markdown 内容
   - 使用 Write 工具写入文件
5. **输出确认**：显示生成的报告路径和摘要

### 关键函数

```python
def parse_git_log(since_days: int) -> list[Commit]:
    """解析 Git 提交记录"""

def classify_commit(message: str) -> str:
    """分类 commit（基于关键词）"""

def find_completed_plans(since_date: str) -> list[Plan]:
    """查找已完成的计划"""

def generate_summary_report(data: dict) -> str:
    """生成 Markdown 报告"""
```

---

**计划创建时间**: 2026-01-09 23:22
**估计工作量**: 4-6 小时
**优先级**: p2（可纳入后续迭代）
**依赖项**: 无
