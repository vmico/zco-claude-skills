---
seq: 004
title: "增强 zco_claude_init.py 支持多命令模式"
author: ""
status: "draft:0"
priority: "p2:中:可纳入后续迭代计划"
created_at: ""
updated_at: ""
tags: [feature, enhancement, cli, tooling]
---

# 开发任务：增强 zco_claude_init.py 支持多命令模式

## 🎯 目标

将 `zco_claude_init.py` 从单一功能脚本重构为支持多命令的 CLI 工具，新增 `init`、`list-linked-repos`、`fix-linked-repos` 三个子命令，提升项目配置管理的灵活性和可维护性。

## 📋 详细需求

### 功能描述

#### 1. **命令行架构重构**
   - 从单一参数模式改为子命令模式
   - 使用 `argparse` 的 `subparsers` 实现多命令支持
   - 保持向后兼容（可选）

#### 2. **子命令 1: `init` - 初始化当前项目**
   - **功能**：初始化当前工作目录的 `.claude/` 配置
   - **用法**：`./zco_claude_init.py init`
   - **行为**：
     - 自动检测当前目录（`os.getcwd()`）
     - 执行与原有 `main()` 相同的初始化流程
     - 创建软链接、生成配置文件、生成 `.claudeignore`
     - 记录到 `ZCO_CLAUDE_RECORD_FILE`

#### 3. **子命令 2: `list-linked-repos` - 列出已链接项目**
   - **功能**：打印所有已初始化的项目列表
   - **用法**：`./zco_claude_init.py list-linked-repos`
   - **输出格式**：
     ```
     [linked_time] [target_path]
     ```
   - **示例输出**：
     ```
     [2026-01-09 15:30:45] /home/user/project1
     [2026-01-10 09:15:22] /home/user/project2
     [2026-02-05 12:27:00] /home/user/project3
     ```
   - **数据来源**：读取 `ZCO_CLAUDE_RECORD_FILE` (默认 `~/.claude/zco-linked-projects.json`)
   - **边界情况**：
     - 文件不存在 → 提示 "无已链接项目"
     - 文件为空 → 提示 "无已链接项目"
     - JSON 解析失败 → 显示错误信息

#### 4. **子命令 3: `fix-linked-repos` - 修复已链接项目**
   - **功能**：检查并修复所有已链接项目的软链接
   - **用法**：`./zco_claude_init.py fix-linked-repos`
   - **执行流程**：
     1. 读取 `ZCO_CLAUDE_RECORD_FILE` 获取所有已链接项目
     2. 对每个项目执行检查：
        - 检查 `.claude/rules/*` 软链接是否有效
        - 检查 `.claude/hooks/*` 软链接是否有效
        - 检查 `.claude/skills/*` 软链接是否有效
        - 检查 `.claude/commands/*` 软链接是否有效
        - 检查 `.claude/zco-scripts` 软链接是否有效
     3. 对无效软链接执行修复：
        - 删除失效的软链接
        - 重新创建指向当前 `ZCO_CLAUDE_TPL_DIR` 的软链接
     4. 更新 `ZCO_CLAUDE_RECORD_FILE` 中的 `linked_time`
   - **输出示例**：
     ```
     检查项目: /home/user/project1
       ✓ .claude/rules/go → 有效
       ✗ .claude/hooks/save_chat_plain.py → 失效，已修复
       ✓ .claude/skills/zco-plan → 有效

     检查项目: /home/user/project2
       ✓ 所有软链接有效

     修复完成：
       - 检查项目数: 2
       - 修复软链接数: 1
     ```

### 特殊要求

#### 软链接检查逻辑
```python
def is_valid_symlink(link_path: Path, expected_source: Path) -> bool:
    """
    检查软链接是否有效

    Args:
        link_path: 软链接路径
        expected_source: 期望的源路径

    Returns:
        bool: True 表示有效，False 表示无效
    """
    if not link_path.exists():
        return False

    if not link_path.is_symlink():
        return False

    # 检查软链接是否指向正确的源
    actual_source = link_path.resolve()
    return actual_source == expected_source.resolve()
```

#### 命令行参数设计
```python
parser = argparse.ArgumentParser(
    description="Claude Code 配置管理工具",
    formatter_class=argparse.RawDescriptionHelpFormatter
)

subparsers = parser.add_subparsers(dest='command', help='可用命令')

# 子命令: init
parser_init = subparsers.add_parser('init', help='初始化当前项目的 .claude/ 配置')

# 子命令: list-linked-repos
parser_list = subparsers.add_parser('list-linked-repos', help='列出所有已链接的项目')

# 子命令: fix-linked-repos
parser_fix = subparsers.add_parser('fix-linked-repos', help='修复已链接项目的软链接')

# 保留原有行为（向后兼容）
parser.add_argument(
    "target_path",
    nargs='?',
    default=None,
    help="目标项目路径（兼容旧版用法）"
)
```

#### 向后兼容性
- 如果用户直接运行 `./zco_claude_init.py /path/to/project`，保持原有行为
- 如果用户运行 `./zco_claude_init.py init`，初始化当前目录
- 优先检查子命令，如果没有子命令则检查 `target_path` 参数

## ✅ 验证标准

- [ ] 子命令 `init` 正常工作，能初始化当前目录
- [ ] 子命令 `list-linked-repos` 正确显示所有已链接项目
- [ ] 子命令 `fix-linked-repos` 能检测并修复失效软链接
- [ ] 向后兼容：`./zco_claude_init.py /path/to/project` 仍然有效
- [ ] 所有子命令都有 `--help` 帮助信息
- [ ] 代码通过 Python linter 检查（pylint/flake8）
- [ ] 注释使用正确的前缀（`##;` 用于逻辑说明）
- [ ] 错误处理完善（文件不存在、权限问题、JSON 解析失败等）
- [ ] 更新 README.md 文档说明新用法

## 🧪 测试计划

### 单元测试

**测试用例 1：`init` 命令**
```bash
# 准备：创建测试目录
mkdir -p /tmp/test-project
cd /tmp/test-project

# 执行
./zco_claude_init.py init

# 验证
ls -la .claude/
# 预期：存在 rules, hooks, skills, commands, zco-scripts 软链接
```

**测试用例 2：`list-linked-repos` 命令（有数据）**
```bash
# 执行
./zco_claude_init.py list-linked-repos

# 预期输出：
# [2026-01-09 15:30:45] /home/user/project1
# [2026-01-10 09:15:22] /home/user/project2
```

**测试用例 3：`list-linked-repos` 命令（无数据）**
```bash
# 准备：删除记录文件
rm ~/.claude/zco-linked-projects.json

# 执行
./zco_claude_init.py list-linked-repos

# 预期输出：
# 无已链接项目
```

**测试用例 4：`fix-linked-repos` 命令（有失效链接）**
```bash
# 准备：手动删除一个软链接
rm /tmp/test-project/.claude/hooks/save_chat_plain.py

# 执行
./zco_claude_init.py fix-linked-repos

# 验证
ls -la /tmp/test-project/.claude/hooks/save_chat_plain.py
# 预期：软链接已恢复
```

**测试用例 5：向后兼容性**
```bash
# 执行旧版用法
./zco_claude_init.py /tmp/another-project

# 验证
ls -la /tmp/another-project/.claude/
# 预期：正常初始化
```

### 集成测试

**场景 1：完整工作流**
```bash
# 1. 初始化项目 A
cd /tmp/project-a
./zco_claude_init.py init

# 2. 初始化项目 B
cd /tmp/project-b
./zco_claude_init.py init

# 3. 列出已链接项目
./zco_claude_init.py list-linked-repos
# 预期：显示 project-a 和 project-b

# 4. 手动破坏 project-a 的软链接
rm /tmp/project-a/.claude/rules/go

# 5. 修复所有项目
./zco_claude_init.py fix-linked-repos
# 预期：project-a 的软链接被修复

# 6. 验证修复结果
ls -la /tmp/project-a/.claude/rules/go
# 预期：软链接存在且有效
```

### 边界条件测试

1. **记录文件不存在**
   - `list-linked-repos` → 提示 "无已链接项目"
   - `fix-linked-repos` → 提示 "无已链接项目"

2. **记录文件损坏（JSON 格式错误）**
   - 显示友好的错误信息
   - 不崩溃

3. **目标项目已被删除**
   - `fix-linked-repos` 跳过不存在的项目
   - 可选：从记录中移除

4. **权限问题**
   - 无法创建软链接 → 显示错误信息
   - 无法写入记录文件 → 显示错误信息

## 📚 参考信息

### 相关文件
- `zco_claude_init.py` - 当前脚本（需要修改）
- `~/.claude/zco-linked-projects.json` - 链接记录文件
- `ClaudeSettings/` - 配置模板目录

### 相关函数
- `record_linked_project()` - 记录链接项目（已存在）
- `make_symlink()` - 创建软链接（已存在）
- `make_links_for_subs()` - 批量创建子目录软链接（已存在）

### 技术栈
- Python 3.x
- `argparse` - 命令行参数解析
- `pathlib.Path` - 路径操作
- `json` - JSON 文件读写

### 代码风格
- 使用 `##;` 前缀标记逻辑说明注释
- 使用 `##;@TODO:` 标记待办事项
- 使用 `##;@NOTE:` 标记重要说明
- 函数使用 docstring 说明参数和返回值

## 🔄 实现步骤建议

### Step 1: 重构命令行参数解析
- 添加 `subparsers`
- 定义三个子命令
- 保留 `target_path` 参数用于向后兼容

### Step 2: 实现 `init` 命令
- 提取当前 `main()` 中的初始化逻辑
- 创建 `cmd_init()` 函数
- 使用 `os.getcwd()` 作为目标路径

### Step 3: 实现 `list-linked-repos` 命令
- 创建 `cmd_list_linked_repos()` 函数
- 读取 `ZCO_CLAUDE_RECORD_FILE`
- 格式化输出

### Step 4: 实现 `fix-linked-repos` 命令
- 创建 `cmd_fix_linked_repos()` 函数
- 实现软链接检查逻辑
- 实现软链接修复逻辑
- 更新记录文件

### Step 5: 更新 `main()` 函数
- 根据 `args.command` 分发到不同的子命令函数
- 处理向后兼容逻辑

### Step 6: 测试和文档
- 执行所有测试用例
- 更新 README.md
- 更新 `--help` 信息

## 💡 实现提示

### 软链接检查示例代码
```python
def check_and_fix_symlinks(target_path: Path, source_dir: Path) -> dict:
    """
    检查并修复项目的软链接

    Returns:
        dict: 统计信息 {'checked': 5, 'fixed': 2, 'valid': 3}
    """
    stats = {'checked': 0, 'fixed': 0, 'valid': 0}

    subdirs = ['rules', 'hooks', 'skills', 'commands']

    for subdir in subdirs:
        target_subdir = target_path / '.claude' / subdir
        source_subdir = source_dir / subdir

        if not target_subdir.exists():
            continue

        for item in target_subdir.iterdir():
            stats['checked'] += 1

            if is_valid_symlink(item, source_subdir / item.name):
                stats['valid'] += 1
                print(f"  ✓ {subdir}/{item.name} → 有效")
            else:
                # 删除失效链接
                if item.is_symlink() or item.exists():
                    item.unlink()

                # 重新创建
                source_item = source_subdir / item.name
                if source_item.exists():
                    item.symlink_to(source_item)
                    stats['fixed'] += 1
                    print(f"  ✗ {subdir}/{item.name} → 失效，已修复")

    return stats
```

---

**计划版本**: 1.0.0
**创建时间**: 2026-02-05 12:27
**预计工作量**: 2-3 小时
