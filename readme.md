
# ClaudeSettings 配置扩展包

[![PyPI version](https://badge.fury.io/py/zco-claude.svg)](https://badge.fury.io/py/zco-claude)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Claude Code 配置管理工具 - 快速初始化项目的 `.claude` 配置目录

## 安装

### 方式一：通过 pip 安装（推荐）

```bash
pip install zco-claude
```

### 方式二：本地安装

```bash
git clone <repository-url>
cd zco-claude-skills
pip install -e .
```

### 方式三：使用 Makefile

```bash
make install   # 复制安装
make link      # 软链接安装（开发推荐）
make uninstall # 卸载
```

## 使用方法

### 初始化项目

```bash
# 初始化当前目录
zco-claude init

# 初始化指定目录
zco-claude init /path/to/project

# 使用自定义模板
zco-claude init /path/to/project --tpl /custom/template
```

### 管理已链接项目

```bash
# 列出所有已链接的项目
zco-claude list-linked-repos

# 修复所有项目的软链接
zco-claude fix-linked-repos

# 删除不存在的项目记录
zco-claude fix-linked-repos --remove-not-found

# 修复指定项目
zco-claude fix /path/to/project
```

### 生成全局配置

```bash
# 仅生成全局配置
zco-claude
```

## 支持的命令

| 命令 | 说明 |
|------|------|
| `init [path] [--tpl]` | 初始化项目配置 |
| `list-linked-repos` | 列出已链接项目 |
| `fix-linked-repos [--remove-not-found]` | 修复所有项目软链接 |
| `fix [path] [--tpl]` | 修复指定项目软链接 |

## zco-plan 工作流程

### 1. 安装工具

```bash
pip install zco-claude
```

### 2. 初始化项目

```bash
cd /path/to/your/project
zco-claude init
```

### 3. 启动 Claude Code

```bash
claude .
```

### 4. 执行计划

```
/zco-plan 001
```

### 5. 创建新计划

```
/zco-plan-new 实现用户认证功能
```

## 项目结构

```
.
├── src/
│   └── zco_claude/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py              # 主命令行工具
│       └── ClaudeSettings/     # 配置模板
│           ├── commands/
│           ├── hooks/
│           ├── rules/
│           ├── skills/
│           └── zco-scripts/
├── docs/
│   └── plans/                  # 计划文档
├── pyproject.toml              # 包配置
├── setup.py                    # 安装脚本
└── Makefile                    # 快捷命令
```

## 开发

### 构建包

```bash
python setup.py sdist bdist_wheel
```

### 本地测试安装

```bash
pip install -e .
```

### 上传到 PyPI

```bash
# 安装工具
pip install twine

# 上传
python -m twine upload dist/*
```

## 许可证

MIT License

