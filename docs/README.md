# Claude Code Skills & Configuration System

> Centralized configuration hub, custom skills library, and development planning system for Claude Code across YJ-ANNO-SG-Y2025 projects.

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-green.svg)](https://claude.ai/code)

---

## 📖 Overview

This repository provides:

1. **Custom Skills** - Reusable automation workflows with `zco-` prefix
2. **Development Planning** - Structured task management system
3. **Configuration Management** - Shared Claude Code settings across projects
4. **Project Linking** - Symlink configuration to multiple repositories

**Part of**: [YJ-ANNO-SG-Y2025](../) - Annotation Services Platform (2D/3D)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.x
- Git
- Claude Code CLI

### Installation

```bash
# Clone or navigate to this repository
cd _.ai-claude-skills

# Link configuration to another project (optional)
./zco_claude_init.py /path/to/target/project

# Verify installation
ls -la .claude/
```

### First Steps

```bash
# 1. View available plans
ls docs/plans/

# 2. Execute a development plan
zco-plan 001

# 3. Create a new plan
zco-plan-new

# 4. Update documentation
zco-docs-update
```

---

## 📁 Repository Structure

```
_.ai-claude-skills/
├── .claude/                    # Active configuration (symlinked)
│   ├── hooks/                 # Git hooks
│   ├── rules/                 # Coding standards
│   ├── skills/                # Custom skills
│   └── settings.local.json    # Local settings
│
├── ClaudeSettings/            # Master templates
│   ├── skills/               # Skill definitions
│   │   ├── zco-plan/        # Execute plans
│   │   ├── zco-plan-new/    # Create plans
│   │   └── zco-docs-update/ # Update docs
│   ├── rules/               # Coding rules
│   ├── hooks/               # Automation
│   └── settings.json        # Team config
│
├── docs/plans/               # Task planning
│   ├── README.md            # Plan guide (630+ lines)
│   ├── plan.template.md     # Full template
│   └── plan.*.md            # Plan documents
│
├── zco_claude_init.py       # Linking script
├── setup.sh                 # Setup automation
├── CLAUDE.md                # Claude instructions
└── README.md                # This file
```

---

## 🎯 Key Features

### 1. Custom Skills System

All custom skills use the **zco-** prefix (Zhicheng Custom Operations).

| Skill | Command | Purpose |
|-------|---------|---------|
| **zco-plan** | `zco-plan {seq}` | Execute structured development plans |
| **zco-plan-new** | `zco-plan-new` | Create new development plan |
| **zco-docs-update** | `zco-docs-update` | Update CLAUDE.md metadata |

**Example**:
```bash
# Execute development plan 001
zco-plan 001

# Create a new plan
zco-plan-new

# Update Git metadata in CLAUDE.md
zco-docs-update
```

**Learn More**: [Skills Documentation](ClaudeSettings/skills/README.md)

### 2. Development Plan Management

Structured task planning with YAML metadata and Markdown content.

**Plan Format**: `plan.{seq}.{extra}.md`

**Example**:
```yaml
---
seq: 001
title: "Update project documentation"
status: "ongoing:2"
priority: "p2:中:可纳入后续迭代计划"
tags: [documentation, setup]
---

## 🎯 Goal
Update all project documentation files

## 📋 Detailed Requirements
1. Create CLAUDE.md
2. Create README.md
3. Summarize docs/

## ✅ Verification Standards
- [ ] CLAUDE.md created
- [ ] README.md created
- [ ] Documentation reviewed
```

**Workflow**:
```bash
# 1. Create plan from template
cp docs/plans/plan.template.md docs/plans/plan.002.260109.md

# 2. Edit plan
vim docs/plans/plan.002.260109.md

# 3. Execute plan
zco-plan 002

# 4. Status auto-updates: draft:0 → ongoing:2 → completed:3
```

**Learn More**: [Plan Management Guide](docs/plans/README.md) (630+ lines)

### 3. Project Linking System

Share Claude configuration across multiple projects via symlinks.

**Usage**:
```bash
./zco_claude_init.py /path/to/another/project
```

**What Gets Linked**:
- `.claude/rules/` → Coding standards
- `.claude/hooks/` → Git automation
- `.claude/skills/` → Custom skills

**Learn More**: See `zco_claude_init.py` source

---

## 📋 Documentation

### Core Documentation

| Document | Description | Size |
|----------|-------------|------|
| [README.md](README.md) | This file - project overview | - |
| [CLAUDE.md](CLAUDE.md) | Claude Code instructions | Comprehensive |
| [docs/plans/README.md](docs/plans/README.md) | Plan management guide | 630+ lines |
| [ClaudeSettings/README.md](ClaudeSettings/README.md) | Configuration guide | - |
| [ClaudeSettings/skills/README.md](ClaudeSettings/skills/README.md) | Skills development | 225+ lines |

### Skill Documentation

| Skill | Documentation | Lines |
|-------|---------------|-------|
| zco-plan | [SKILL.md](ClaudeSettings/skills/zco-plan/SKILL.md) | 400+ |
| zco-plan-new | [SKILL.md](ClaudeSettings/skills/zco-plan-new/SKILL.md) | - |
| zco-docs-update | [SKILL.md](ClaudeSettings/skills/zco-docs-update/SKILL.md) | - |

### Templates

| Template | Purpose | Lines |
|----------|---------|-------|
| [plan.template.md](docs/plans/plan.template.md) | Full plan template | 250+ |
| [plan.template.minimal.md](docs/plans/plan.template.minimal.md) | Minimal template | - |

---

## 🛠️ Common Tasks

### Working with Plans

```bash
# List all plans
ls docs/plans/

# View plan details
cat docs/plans/plan.001.*.md

# Execute a plan
zco-plan 001

# Create new plan manually
cp docs/plans/plan.template.md docs/plans/plan.003.$(date +%y%m%d).md
vim docs/plans/plan.003.260109.md

# Or use the skill
zco-plan-new
```

### Creating a New Skill

```bash
# 1. Create skill directory (must use zco- prefix)
mkdir -p ClaudeSettings/skills/zco-my-skill

# 2. Create SKILL.md
cat > ClaudeSettings/skills/zco-my-skill/SKILL.md << 'EOF'
---
name: zco-my-skill
description: Brief description of what this skill does
allowed-tools: Bash, Read, Glob, Write, Edit
---

# My Custom Skill

## 🎯 Skill Purpose
What this skill does...

## 📋 When to Use
Use this skill when...

## 🚀 Usage
Examples...
EOF

# 3. Test the skill
zco-my-skill
```

### Linking to Other Projects

```bash
# Link this configuration to another project
./zco_claude_init.py /path/to/another/project

# Verify the link
ls -la /path/to/another/project/.claude/

# Now you can use skills in that project
cd /path/to/another/project
zco-plan 001  # Works!
```

---

## 📚 Naming Conventions

### Skills

**Rule**: All custom skills **MUST** use `zco-` prefix.

✅ **Correct**:
```
zco-plan
zco-docs-update
zco-deploy
zco-backup
```

❌ **Incorrect**:
```
plan          # Missing prefix
my-skill      # Wrong prefix
update-docs   # Wrong prefix
```

### Plan Documents

**Format**: `plan.{seq}.{extra}.md`

- `{seq}`: Sequence number (any digits: 1, 02, 003, 0100)
- `{extra}`: Optional suffix (date YYMMDD or description)

✅ **Correct**:
```
plan.001.20260109.md       # seq=001, date
plan.002.用户鉴权.md       # seq=002, description
plan.0100.issue946.md      # seq=0100, issue reference
plan.1.md                  # seq=1, no extra
```

❌ **Incorrect**:
```
plan-002-20260109.md       # Uses - instead of .
task.002.20260109.md       # Wrong prefix
002.plan.md                # Wrong order
```

---

## 🔗 Integration with Parent Project

This repository is part of the **YJ-ANNO-SG-Y2025** annotation services platform.

**Parent Project**:
- **Location**: `../../YJ-ANNO-SG-Y2025/`
- **Type**: Dual-platform annotation system (2D images + 3D point clouds)
- **Tech Stack**: Go (Beego), MySQL, Redis, React
- **Documentation**: `../../CLAUDE.md`

**Shared Configuration**:
- Coding standards in `_.ai-claude/.claude/rules/`
- Go comment conventions (`//` vs `//;` vs `//;@TODO:`)
- Quality requirements (≥80% test coverage, ≤50 lines per function)

---

## 🎓 Tutorials

### Tutorial 1: Execute Your First Plan

```bash
# 1. View available plans
ls docs/plans/

# 2. Read plan content
cat docs/plans/plan.001.update_claude.md

# 3. Execute the plan
zco-plan 001

# 4. Claude will:
#    - Read the plan document
#    - Update status to "ongoing:2"
#    - Execute the tasks
#    - Update status to "completed:3"
```

### Tutorial 2: Create and Execute a New Plan

```bash
# 1. Copy template
cp docs/plans/plan.template.md docs/plans/plan.002.$(date +%y%m%d).md

# 2. Edit the plan
vim docs/plans/plan.002.260109.md
# Fill in:
#   - seq: 002
#   - title: "Your task title"
#   - Goal section
#   - Detailed requirements
#   - Verification standards

# 3. Execute
zco-plan 002

# 4. Verify completion
grep "status:" docs/plans/plan.002.260109.md
# Should show: status: "completed:3"
```

### Tutorial 3: Link to Another Project

```bash
# 1. Run linking script
./zco_claude_init.py /home/user/another-project

# 2. Verify symlinks created
ls -la /home/user/another-project/.claude/
# Should show:
#   hooks -> /path/to/_.ai-claude-skills/ClaudeSettings/hooks
#   rules -> /path/to/_.ai-claude-skills/ClaudeSettings/rules
#   skills -> /path/to/_.ai-claude-skills/ClaudeSettings/skills

# 3. Use skills in that project
cd /home/user/another-project
zco-plan 001  # Works!
```

---

## ⚙️ Configuration

### Team Settings

**File**: `ClaudeSettings/settings.json`

Shared team configuration (committed to Git):
- Permission rules
- Excluded paths
- Global settings

**Example**:
```json
{
  "permissions": {
    "deny": [
      "Read(./node_modules)",
      "Read(./node_modules/**)",
      "Read(./.git/**)"
    ]
  }
}
```

### Local Settings

**File**: `.claude/settings.local.json`

Personal settings (Git-ignored):
- Local overrides
- Personal preferences
- Machine-specific config

**Example**:
```json
{
  "permissions": {
    "deny": [
      "Read(./my-notes)",
      "Read(./my-notes/**)"
    ]
  }
}
```

---

## 🐛 Troubleshooting

### Issue: Skill Not Recognized

**Symptom**: Claude doesn't recognize `zco-my-skill`

**Solutions**:
1. ✅ Verify skill name uses `zco-` prefix
2. ✅ Check `SKILL.md` exists (case-sensitive)
3. ✅ Ensure YAML front matter is valid:
   ```yaml
   ---
   name: zco-my-skill
   description: ...
   allowed-tools: Bash, Read
   ---
   ```
4. ✅ Restart Claude Code session

### Issue: Plan Not Found

**Symptom**: `zco-plan 002` says "plan not found"

**Solutions**:
1. ✅ Check file exists:
   ```bash
   ls docs/plans/plan.002.*.md
   ```
2. ✅ Verify filename format: `plan.{seq}.{extra}.md`
3. ✅ Create from template if missing:
   ```bash
   cp docs/plans/plan.template.md docs/plans/plan.002.260109.md
   ```

### Issue: Symlinks Broken

**Symptom**: Linked project can't find skills/rules

**Solutions**:
1. ✅ Re-run linking script:
   ```bash
   ./zco_claude_init.py /path/to/project
   ```
2. ✅ Check source directories exist:
   ```bash
   ls -la ClaudeSettings/{skills,rules,hooks}
   ```
3. ✅ Verify symlink targets:
   ```bash
   ls -la /path/to/project/.claude/
   ```

### Issue: Python Script Fails

**Symptom**: `./zco_claude_init.py` errors

**Solutions**:
1. ✅ Check Python version:
   ```bash
   python3 --version  # Should be 3.x
   ```
2. ✅ Make script executable:
   ```bash
   chmod +x zco_claude_init.py
   ```
3. ✅ Check target path exists:
   ```bash
   ls -d /path/to/target
   ```

---

## 📊 Project Status

**Git Information**:
- **Branch**: master
- **Status**: Active development
- **Recent Commits**:
  - `e8cd900` - todo: fix zco_claude_init.py
  - `7005b57` - init: add claude settings sample v0.0.1

**Modified Files** (Current Session):
- `docs/plans/plan.001.update_claude.md`
- `setup.sh`
- `zco_claude_init.py`
- `CLAUDE.md` (newly created)
- `README.md` (this file)

---

## 🤝 Contributing

### Adding a New Skill

1. Create directory: `mkdir ClaudeSettings/skills/zco-{name}`
2. Write SKILL.md with proper YAML front matter
3. Test the skill: `zco-{name}`
4. Document in [skills/README.md](ClaudeSettings/skills/README.md)
5. Submit PR with description

### Updating Documentation

1. Edit relevant `.md` file
2. Maintain consistent formatting
3. Add examples where helpful
4. Update table of contents if needed
5. Run `zco-docs-update` to update metadata

### Reporting Issues

1. Check [Troubleshooting](#-troubleshooting) first
2. Gather diagnostic information:
   ```bash
   ls -la .claude/
   cat .claude/settings.local.json
   ls docs/plans/
   ```
3. Describe expected vs actual behavior
4. Include error messages

---

## 📞 Support

**Documentation Resources**:
- [CLAUDE.md](CLAUDE.md) - Complete Claude Code guide
- [docs/plans/README.md](docs/plans/README.md) - Plan management (630+ lines)
- [ClaudeSettings/skills/README.md](ClaudeSettings/skills/README.md) - Skills guide (225+ lines)

**Common Questions**:

<details>
<summary><b>How do I create a new plan?</b></summary>

```bash
# Method 1: Copy template
cp docs/plans/plan.template.md docs/plans/plan.{seq}.$(date +%y%m%d).md

# Method 2: Use skill (if available)
zco-plan-new

# Then edit the file to add your requirements
```
</details>

<details>
<summary><b>How do I share skills with other projects?</b></summary>

```bash
# Link configuration to target project
./zco_claude_init.py /path/to/target/project

# Skills are now available in that project
cd /path/to/target/project
zco-plan 001  # Works immediately
```
</details>

<details>
<summary><b>What's the difference between CLAUDE.md and README.md?</b></summary>

- **README.md**: Human-readable project overview and quick start guide
- **CLAUDE.md**: Instructions specifically for Claude Code AI to understand the project structure and conventions
</details>

<details>
<summary><b>Can I use a different prefix instead of zco-?</b></summary>

No. The `zco-` prefix is mandatory for all custom skills to:
- Distinguish custom skills from built-in ones
- Maintain consistency across projects
- Prevent naming conflicts
</details>

---

## 📄 License

Proprietary - Minieye Technology Co., Ltd.

**Maintainer**: Development Team
**Parent Project Lead**: ningrong@minieye.cc

---

## 🎯 Quick Reference

### Most Common Commands

```bash
# Plans
zco-plan {seq}              # Execute plan
zco-plan-new                # Create new plan
ls docs/plans/              # List all plans

# Documentation
zco-docs-update             # Update CLAUDE.md metadata
cat CLAUDE.md               # Read Claude instructions
cat README.md               # Read project overview

# Skills
ls ClaudeSettings/skills/   # List all skills
cat ClaudeSettings/skills/zco-plan/SKILL.md  # Read skill docs

# Linking
./zco_claude_init.py /path  # Link to another project
ls -la .claude/             # View symlinks
```

### Directory Quick Reference

```bash
ClaudeSettings/skills/      # Skill definitions
docs/plans/                 # Development plans
.claude/                    # Active configuration
_.zco_hist/              # Conversation history
```

### File Templates

```bash
docs/plans/plan.template.md           # Full plan template
docs/plans/plan.template.minimal.md   # Minimal template
ClaudeSettings/skills/zco-plan/SKILL.md  # Skill reference
```

---

**Version**: 1.0.0
**Last Updated**: 2026-01-09
**Status**: ✅ Documentation Complete

---

**🚀 Ready to Start?**

```bash
# Execute your first plan
zco-plan 001

# Or create a new one
zco-plan-new
```

For detailed guidance, see [CLAUDE.md](CLAUDE.md) or [docs/plans/README.md](docs/plans/README.md).
