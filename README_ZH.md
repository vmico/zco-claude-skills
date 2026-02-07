# ZCO Claude - Claude Code 配置管理工具

[![PyPI version](https://badge.fury.io/py/zco-claude.svg)](https://badge.fury.io/py/zco-claude)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ZCO Claude** 是一个 Claude Code 配置管理工具，帮助你快速初始化项目的 `.claude` 配置目录，共享自定义技能(Skill)、编码规范(Rules)和自动化脚本。

---

## ✨ 功能特性

- 🔗 **项目链接** - 通过软链接将 ClaudeSettings 配置共享到多个项目
- 🧩 **自定义技能** - 提供 `zco-plan`、`zco-plan-new`、`zco-help` 等扩展技能
- 📋 **开发计划管理** - 结构化的任务规划和执行系统
- 📝 **编码规范** - 内置 Go/Python 等语言的编码标准和最佳实践
- 🔧 **自动修复** - 检测并修复损坏的软链接配置

---

## 📦 安装

### 方式一：通过 pip 安装（推荐）

```bash
pip install zco-claude
```

### 方式二：本地开发安装

```bash
git clone <repository-url>
cd zco-claude-skills
pip install -e .
```

### 方式三：使用 Makefile

```bash
make install   # 复制安装到 ~/.local/bin
make link      # 软链接安装（开发推荐）
make uninstall # 卸载
```

---

## 🚀 快速开始

### 1. 初始化项目

```bash
# 初始化当前目录
zco-claude init

# 初始化指定项目
zco-claude init /path/to/project

# 使用自定义模板
zco-claude init /path/to/project --tpl /custom/template
```

初始化后，项目会创建 `.claude/` 目录，包含以下软链接：
- `.claude/rules/` → 编码规范
- `.claude/hooks/` → Git 钩子
- `.claude/commands/` → 自定义命令
- `.claude/skills/` → 扩展技能

### 2. 启动 Claude Code

```bash
cd /path/to/project
claude .
```

### 3. 使用扩展技能

```bash
# 查看所有可用工具
/zco-help

# 执行开发计划
/zco-plan 001

# 创建新计划
/zco-plan-new 实现用户认证功能
```

---

## 📚 核心技能

| 技能 | 命令 | 说明 |
|------|------|------|
| **zco-plan** | `zco-plan {seq}` | 执行结构化开发计划 |
| **zco-plan-new** | `zco-plan-new <描述>` | 创建新的开发计划 |
| **zco-docs-update** | `zco-docs-update` | 更新 CLAUDE.md Git 元信息 |
| **zco-help** | `zco-help [filter]` | 显示可用的 Claude 工具 |

---

## 🛠️ CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `init [path] [--tpl]` | 初始化项目配置 | `zco-claude init .` |
| `list-linked-repos` | 列出已链接的所有项目 | `zco-claude list-linked-repos` |
| `fix-linked-repos [--remove-not-found]` | 修复所有项目的软链接 | `zco-claude fix-linked-repos` |
| `fix [path] [--tpl]` | 修复指定项目配置 | `zco-claude fix /path/to/project` |

---

## 📁 项目结构

```
zco-claude-init/
├── ClaudeSettings/          # 主配置模板
│   ├── skills/              # 自定义技能 (zco-* 前缀)
│   │   ├── zco-plan/        # 执行开发计划
│   │   ├── zco-plan-new/    # 创建新计划
│   │   ├── zco-docs-update/ # 更新文档元信息
│   │   └── zco-help/        # 显示帮助信息
│   ├── rules/               # 编码规范
│   ├── hooks/               # Git 钩子
│   ├── commands/            # 自定义命令
│   ├── settings.json        # 团队共享设置
│   └── README.md            # 配置指南
│
├── docs/plans/              # 结构化开发计划
│   ├── plan.template.md     # 计划模板
│   └── plan.{seq}.{date}.md # 具体计划文档
│
├── zco_claude_init.py       # 项目链接脚本
├── pyproject.toml           # 包配置
├── setup.py                 # 安装脚本
└── Makefile                 # 快捷命令
```

---

## 🔧 开发计划管理

### 创建计划

```bash
# 使用技能创建
zco-plan-new 实现用户登录功能

# 或手动复制模板
cp docs/plans/plan.template.md docs/plans/plan.002.$(date +%y%m%d).md
```

### 执行计划

```bash
zco-plan 002
```

计划文档使用 YAML front matter 定义元数据，包含状态追踪、优先级、验证标准等。

---

## 🏗️ 开发

### 构建包

```bash
# 本地构建和检查
make twine-pypi-local

# 上传到 PyPI
make twine-pypi-upload
```

### 创建新技能

1. 创建技能目录：
   ```bash
   mkdir -p ClaudeSettings/skills/zco-{your-skill}
   ```

2. 创建 SKILL.md：
   ```markdown
   ---
   name: zco-your-skill
   description: 技能描述
   allowed-tools: Bash, Read, Glob
   ---
   # 技能文档...
   ```

3. 测试技能：
   ```bash
   zco-help zco-your-skill
   ```

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**维护者**: NicoNing (vmico@outlook.com)  
**项目主页**: https://github.com/zco-team/zco-claude
