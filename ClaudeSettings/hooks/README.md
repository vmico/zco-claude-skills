# Claude Code 对话自动保存 Hooks

自动保存 Claude Code 对话记录到 Markdown 文件。

## 📦 可用脚本

### 1. `save-conversation-simple.py` - 简洁版 ⭐推荐

**特点**:
- 只保存核心对话内容（用户提问 + Claude 回答）
- 格式简洁，接近终端输出体验
- 适合日常快速回顾

**文件名**: `claude_log_YYMMDD_HHMMSS_simple.md`

### 2. `save-conversation-enhanced.py` - 增强版

**特点**:
- 包含工具使用统计（如 Bash 14次、Edit 7次）
- 提取参考资源列表（读取的文件、访问的 URL）
- 附带详细的工具调用参数
- 适合深度分析和复盘

**文件名**: `YYMMDDHH_{关键词}.md` + `YYMMDDHH_{关键词}_resources.txt`

### 3. `install-to-project.sh` - 一键安装脚本

快速将 hooks 部署到其他项目。

## 🚀 快速安装到其他项目

```bash
# 方法 1: 使用安装脚本（推荐）
./.claude/hooks/install-to-project.sh /path/to/your-project

# 方法 2: 手动复制
mkdir -p /path/to/project/.claude/hooks
cp .claude/hooks/save-conversation-*.py /path/to/project/.claude/hooks/
```

然后在目标项目创建 `.claude/settings.local.json`：
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/save-conversation-simple.py"
      }]
    }]
  }
}
```

## 🔧 跨项目使用说明

### ✅ 关键点

**不需要配置的内容**：
- ✅ `python3` 路径：已在系统 PATH 中，不需要绝对路径
- ✅ 项目路径：脚本自动从 hook 输入数据中获取 `cwd`
- ✅ transcript 路径：由 Claude Code 自动传递

**环境变量**：
- `$CLAUDE_PROJECT_DIR`：Claude Code 自动设置，指向当前项目根目录
- 可以在 `command` 中使用这个变量引用脚本

### 三种部署方案

#### 方案 1：每个项目独立（推荐）

```bash
# 安装
./install-to-project.sh /path/to/project-A
./install-to-project.sh /path/to/project-B

# 每个项目都有自己的配置和脚本副本
project-A/.claude/hooks/save-conversation-*.py
project-B/.claude/hooks/save-conversation-*.py
```

**优点**：每个项目可以独立定制脚本

#### 方案 2：全局共享

```bash
# 1. 创建全局 hooks 目录
mkdir -p ~/.claude/shared-hooks
cp .claude/hooks/save-conversation-*.py ~/.claude/shared-hooks/

# 2. 在各项目的 .claude/settings.local.json 中引用
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/shared-hooks/save-conversation-simple.py"
      }]
    }]
  }
}
```

**优点**：所有项目共享一份脚本，便于统一维护

#### 方案 3：符号链接

```bash
# 创建中央仓库
mkdir -p ~/code/claude-hooks
cp .claude/hooks/save-conversation-*.py ~/code/claude-hooks/

# 在各项目中创建符号链接
mkdir -p /path/to/project/.claude/hooks
ln -s ~/code/claude-hooks/save-conversation-simple.py \
      /path/to/project/.claude/hooks/
```

**优点**：便于版本控制和同步更新

## 工作原理

1. **用户提问** → Claude 回答 → 对话进行中...
2. **对话结束** → 触发 `Stop` Hook
3. **脚本执行**:
   - 读取会话文件（`transcript_path`）
   - 解析 JSONL 格式的对话记录
   - 提取用户提问和 Claude 回答
   - 生成 Markdown 格式
   - 保存到 `_.claude_hist/`

## 查看保存的对话

```bash
# 查看最近的对话记录
ls -lt _.claude_hist/ | head -10

# 查看今天的对话
ls _.claude_hist/$(date +%y%m%d)*.md

# 搜索包含特定关键词的对话
grep -l "API" _.claude_hist/*.md
```

## 手动保存对话

如果自动保存未触发，可以手动运行脚本：

```bash
# 需要知道会话文件路径
python3 .claude/hooks/save-conversation.py << EOF
{
  "hook_event_name": "Stop",
  "transcript_path": "~/.claude/projects/项目路径/sessions/会话ID.jsonl",
  "cwd": "$(pwd)"
}
EOF
```

## 禁用自动保存

如果需要临时禁用自动保存，编辑 `.claude/settings.json`，注释掉 `hooks.Stop` 部分：

```json
{
  "hooks": {
    // "Stop": [...]  // 注释掉这行即可禁用
  }
}
```

## 自定义配置

### 修改关键词提取数量

编辑 `save-conversation.py`，找到 `extract_keywords` 函数：

```python
def extract_keywords(text: str, max_keywords: int = 3):  # 改为你想要的数量
```

### 修改文件名格式

编辑 `save-conversation.py`，找到文件名生成部分：

```python
timestamp = datetime.now().strftime('%y%m%d%H')  # 自定义时间格式
filename = f"{timestamp}_{keywords}.md"          # 自定义文件名格式
```

### 添加更多元数据

在 Markdown 头部添加更多信息：

```python
lines.append(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
lines.append(f"**项目**: {project_dir}\n")  # 添加项目路径
lines.append(f"**会话ID**: {session_id}\n")  # 添加会话ID
```

## 故障排查

### 对话没有自动保存

1. 检查脚本是否可执行：
   ```bash
   ls -la .claude/hooks/save-conversation.py
   # 应该有 x 权限
   ```

2. 检查 hooks 配置：
   ```bash
   cat .claude/settings.json | grep -A 10 "hooks"
   ```

3. 查看错误日志（如果有）：
   ```bash
   # Claude Code 的日志通常在控制台输出
   ```

### 文件名中的关键词不准确

这是正常的，关键词提取是基于简单的算法。你可以：
1. 手动重命名文件
2. 修改 `extract_keywords` 函数的逻辑
3. 添加更多停用词

### Python 3 未安装

确保系统安装了 Python 3：

```bash
python3 --version
# 应该显示 Python 3.x.x
```

如果未安装：
```bash
# Ubuntu/Debian
sudo apt install python3

# macOS
brew install python3
```

## 维护

- **定期清理**: `_.claude_hist/` 目录可能会积累大量文件，建议定期归档
- **备份**: 重要对话建议备份到其他位置
- **版本控制**: 可以选择将对话记录提交到 Git（但建议使用 `.gitignore` 排除）

## 更新日志

- 2026-01-06: 初始版本，支持自动保存对话为 Markdown 格式