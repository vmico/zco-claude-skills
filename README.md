# ZCO Claude - Claude Code Configuration Manager

[![PyPI version](https://badge.fury.io/py/zco-claude.svg)](https://badge.fury.io/py/zco-claude)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ZCO Claude** is a Claude Code configuration management tool that helps you quickly initialize `.claude` configuration directories for your projects, sharing custom skills, coding standards, and automation scripts.

[中文文档](README_ZH.md)

---

## ✨ Features

- 🔗 **Project Linking** - Share ClaudeSettings configurations across multiple projects via symlinks
- 🧩 **Custom Skills** - Provides extended skills like `zco-plan`, `zco-plan-new`, `zco-help`
- 📋 **Development Plan Management** - Structured task planning and execution system
- 📝 **Coding Standards** - Built-in coding standards and best practices for Go/Python
- 🔧 **Auto Repair** - Detect and fix broken symlink configurations

---

## 📦 Installation

### Option 1: Install via pip (Recommended)

```bash
pip install zco-claude
```

### Option 2: Local Development Install/Uninstall

```bash
git clone <repository-url>
cd <project-directory>
##; method A: Copy install to ~/.local/bin
make install   
##; method B: Symlink install (recommended for development)
make link
##; Uninstall
make uninstall 
```

---

## 🚀 Quick Start

### 1. Initialize a Project

```bash
# Initialize current directory
zco-claude init

# Initialize a specific project
zco-claude init /path/to/project

# Use custom template
zco-claude init /path/to/project --tpl /custom/template
```

After initialization, the project will have a `.claude/` directory with the following symlinks:
- `.claude/rules/` → Coding standards
- `.claude/hooks/` → Git hooks
- `.claude/commands/` → Custom commands
- `.claude/skills/` → Extended skills

### 2. Start Claude Code

```bash
cd /path/to/project
claude .
```

### 3. Use Extended Skills

```bash
# View all available tools
/zco-help

# Execute a development plan
/zco-plan 001

# Create a new plan
/zco-plan-new {describe your requirement in any language}
```

---

## 📚 Core Skills

| Skill | Command | Description |
|-------|---------|-------------|
| **zco-plan** | `zco-plan {seq}` | Execute structured development plans |
| **zco-plan-new** | `zco-plan-new <description>` | Create a new development plan |
| **zco-docs-update** | `zco-docs-update` | Update CLAUDE.md Git metadata |
| **zco-help** | `zco-help [filter]` | Display available Claude tools |

---

## 🛠️ CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init [path] [--tpl]` | Initialize project configuration | `zco-claude init .` |
| `list-linked-repos` | List all linked projects | `zco-claude list-linked-repos` |
| `fix-linked-repos [--remove-not-found]` | Fix symlinks for all projects | `zco-claude fix-linked-repos` |
| `fix [path] [--tpl]` | Fix specific project configuration | `zco-claude fix /path/to/project` |

---

## 📁 Project Structure

```
zco-claude-init/
├── ClaudeSettings/          # Master configuration templates
│   ├── skills/              # Custom skills (zco-* prefix)
│   │   ├── zco-plan/        # Execute development plans
│   │   ├── zco-plan-new/    # Create new plans
│   │   ├── zco-docs-update/ # Update document metadata
│   │   └── zco-help/        # Display help information
│   ├── rules/               # Coding standards
│   ├── hooks/               # Git hooks
│   ├── commands/            # Custom commands
│   ├── settings.json        # Team-shared settings
│   └── README.md            # Configuration guide
│
├── docs/plans/              # Structured development plans
│   ├── plan.template.md     # Plan template
│   └── plan.{seq}.{date}.md # Specific plan documents
│
├── zco_claude_init.py       # Project linking script
├── pyproject.toml           # Package configuration
├── setup.py                 # Installation script
└── Makefile                 # Shortcut commands
```

---

## 🔧 Development Plan Management

### Create a Plan

```bash
# using skill in claude code
/zco-plan-new {describe your requirement in any language}

# Or manually copy template
cp docs/plans/plan.template.md docs/plans/plan.002.$(date +%y%m%d).md
```

### Execute a Plan

```bash
# using skill in claude code
/zco-plan 002
```

Plan documents use YAML front matter to define metadata, including status tracking, priority, verification criteria, etc.

---

## 🏗️ Development

### Build Package

```bash
# Local build and check
make twine-pypi-local

# Upload to PyPI
make twine-pypi-upload
```

### Create a New Skill

1. Create skill directory:
   ```bash
   mkdir -p ClaudeSettings/skills/zco-{your-skill}
   ```

2. Create SKILL.md:
   ```markdown
   ---
   name: zco-your-skill
   description: Skill description
   allowed-tools: Bash, Read, Glob
   ---
   # Skill documentation...
   ```

3. Test the skill:
   ```bash
   zco-help zco-your-skill
   ```

---

## 📄 License

[MIT License](LICENSE)

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**Maintainer**: NicoNing (vmico@outlook.com)  
**Homepage**: https://github.com/zco-team/zco-claude
