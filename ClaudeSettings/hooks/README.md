# Claude Code 对话自动保存 Hooks

自动保存 Claude Code 对话记录到 Markdown 文件。

---

## 📦 可用脚本

| 脚本                     | 环境变量                | 特点                     | 推荐场景    |
| ------------------------ | ----------------------- | ------------------------ | ----------- |
| `save_chat_cli_style.py` | `ZCO_CHAT_SAVE_CLI=1`   | CLI 样式，折叠面板，图标 | ⭐ 日常使用 |
| `save_chat_plain.py`     | `ZCO_CHAT_SAVE_PLAIN=1` | 纯文本，最简洁           | 快速查看    |
| `save_chat_spec.py`      | `ZCO_CHAT_SAVE_SPEC=1`  | 完整信息，工具统计       | 深度分析    |
| `debug_hook.py`          | -                       | 调试 hook，查看数据结构  | 开发调试    |

---

## 🚀 快速开始

### 方案 1：环境变量控制（推荐）

通过环境变量启用不同的保存方式：

```bash
# 方式 1：CLI 样式（带折叠面板，最接近终端效果）
export ZCO_CHAT_SAVE_CLI=1

# 方式 2：简洁纯文本
export ZCO_CHAT_SAVE_PLAIN=1

# 方式 3：增强版（含工具统计和参考资源）
export ZCO_CHAT_SAVE_SPEC=1

# 启动 Claude Code
claude
```

**可选配置**：

```bash
# 自定义输出目录（默认：_.zco_hist）
export ZCO_CHAT_SAVE_DIR=my_logs
```

---

### 方案 2：Settings.json 配置

编辑 `.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/save_chat_cli_style.py"
          }
        ]
      }
    ]
  }
}
```

---

## 📄 脚本详细说明

### 1. save_chat_cli_style.py - CLI 样式版 ⭐推荐

**文件**: `ClaudeSettings/hooks/save_chat_cli_style.py`

**功能**: 模拟终端显示效果，包含：

- 工具调用折叠面板（类似终端中的展开/收起）
- 消息角色图标（❯ User / ⬢ Claude）
- 自动截断过长的工具结果
- 支持模型名记录（如果可用）
- GitHub Flavored Markdown 格式

**启用**:

```bash
export ZCO_CHAT_SAVE_CLI=1
```

**输出示例**:

````markdown
### ❯ **User**

请读取 README.md 文件

### ⬢ **Claude**

我来帮您读取文件。

<details>
<summary>📄 <b>Read</b> /path/to/README.md</summary>

```json
{
  "file_path": "/path/to/README.md"
}
```
````

</details>

<details>
<summary>◗ <b>Read</b> 结果</summary>

```
# Project README
...
```

</details>
```

---

### 2. save_chat_plain.py - 简洁版

**文件**: `ClaudeSettings/hooks/save_chat_plain.py`

**功能**: 只保存核心对话内容，纯文本格式，最简洁。

**启用**:

```bash
export ZCO_CHAT_SAVE_PLAIN=1
```

**输出格式**:

```markdown
# AI Code Conversation

**Time**: 2026-02-12 10:30:00
**Session ID**: xxx

---

**User**:
用户提问内容

**AiCode**:
AI 回答内容
```

---

### 3. save_chat_spec.py - 增强版

**文件**: `ClaudeSettings/hooks/save_chat_spec.py`

**功能**: 保存完整对话内容，包括：

- 工具调用统计（如 Bash 14次、Edit 7次）
- 参考资源列表（URLs、文件路径、Agent 调用）
- 详细的工具调用 JSON 参数
- 独立的资源列表文件

**启用**:

```bash
export ZCO_CHAT_SAVE_SPEC=1
```

**输出文件**:

- `AiCode_log_YYMMDD_HHMMSS_{keywords}.md` - 主对话文件
- `AiCode_log_YYMMDD_HHMMSS_{keywords}_resources.txt` - 参考资源列表

---

### 4. debug_hook.py - 调试工具

**文件**: `ClaudeSettings/hooks/debug_hook.py`

**功能**: 打印 Hook 事件接收到的所有数据，用于查看实际可用的字段（如 model、session_id 等）。

**使用**:

```bash
# 临时添加到 settings.json
{
  "hooks": {
    "Stop": [
      "ClaudeSettings/hooks/debug_hook.py",
      "ClaudeSettings/hooks/save_chat_cli_style.py"
    ]
  }
}
```

**输出位置**: `_.zco_hist/hook_debug_Stop.json`

---

## 🔧 跨项目使用说明

### 方案 1：每个项目独立（推荐）

```bash
# 使用 zco_claude_init.py 链接配置
./zco_claude_init.py /path/to/project

# 或手动复制
mkdir -p /path/to/project/.claude/hooks
cp ClaudeSettings/hooks/save_chat_*.py /path/to/project/.claude/hooks/
```

### 方案 2：全局共享

```bash
# 1. 创建全局 hooks 目录
mkdir -p ~/.config/claude/hooks
cp ClaudeSettings/hooks/save_chat_*.py ~/.config/claude/hooks/

# 2. 设置环境变量
export ZCO_CHAT_SAVE_CLI=1
# 或添加到 ~/.bashrc / ~/.zshrc
```

### 方案 3：符号链接

```bash
# 创建中央仓库
mkdir -p ~/code/claude-hooks
cp ClaudeSettings/hooks/save_chat_*.py ~/code/claude-hooks/

# 在各项目中创建符号链接
mkdir -p /path/to/project/.claude/hooks
ln -s ~/code/claude-hooks/save_chat_cli_style.py \
      /path/to/project/.claude/hooks/
```

---

## 📊 查看保存的对话

```bash
# 查看最近的对话记录
ls -lt _.zco_hist/*.md | head -10

# 查看今天的对话
ls _.zco_hist/$(date +%y%m%d)*.md 2>/dev/null || echo "今天没有对话"

# 搜索包含特定关键词的对话
grep -l "API" _.zco_hist/*.md

# 查看统计
echo "总对话数: $(ls _.zco_hist/*.md 2>/dev/null | wc -l)"
echo "今日对话: $(ls _.zco_hist/$(date +%y%m%d)*.md 2>/dev/null | wc -l)"
```

---

## ⚙️ 自定义配置

### 修改关键词提取数量

编辑 `save_chat_spec.py`，找到 `extract_keywords` 函数：

```python
def extract_keywords(text: str, max_keywords: int = 3):  # 改为你想要的数量
```

### 修改文件名格式

编辑任意脚本，找到文件名生成部分：

```python
# save_chat_cli_style.py
timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
filename = f"log_{timestamp}_cli_style.md"

# save_chat_spec.py
timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
base_filename = f"log_{timestamp}_spec"
```

### 添加更多元数据

在 Markdown 头部添加更多信息：

```python
lines.append(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
lines.append(f"**项目**: {project_dir}\n")
lines.append(f"**会话ID**: {session_id}\n")
lines.append(f"**模型**: {model}\n")  # 如果有的话
```

---

## 🐛 故障排查

### 对话没有自动保存

1. 检查环境变量是否设置：

   ```bash
   echo $ZCO_CHAT_SAVE_CLI
   # 应该显示 1
   ```

2. 检查脚本是否可执行：

   ```bash
   ls -la .claude/hooks/save_chat_*.py
   # 应该有 x 权限
   ```

3. 检查输出目录是否存在：

   ```bash
   ls -la _.zco_hist/
   ```

4. 使用 debug_hook 查看错误：
   ```bash
   # 添加 debug hook 后查看输出
   cat _.zco_hist/hook_debug_Stop.json
   ```
   <!--

### 文件名中的关键词不准确

这是正常的，关键词提取是基于简单的算法。你可以：

1. 手动重命名文件
2. 修改 `extract_keywords` 函数的逻辑
3. 使用固定文件名格式（去掉关键词） -->

### Python 3 未安装

```bash
python3 --version

# Ubuntu/Debian
sudo apt install python3

# macOS
brew install python3
```

---

## 🔒 隐私和安全

- 对话记录保存在本地项目目录（`_.zco_hist/`）
- 建议将 `_.zco_hist/` 添加到 `.gitignore`
- 敏感信息（密码、token）可能会被记录，请谨慎分享

---

## 📝 维护建议

- **定期清理**: `_.zco_hist/` 目录可能积累大量文件

  ```bash
  # 删除 30 天前的记录
  find _.zco_hist/ -name "*.md" -mtime +30 -delete
  ```

- **备份**: 重要对话建议备份

  ```bash
  tar czf zco_hist_backup_$(date +%Y%m%d).tar.gz _.zco_hist/
  ```

- **归档**: 按月份归档
  ```bash
  mkdir -p _.zco_hist/archive_2026_01
  mv _.zco_hist/2601*.md _.zco_hist/archive_2026_01/
  ```

---

## 📚 相关文档

- `docs/refers/claude-hooks-reference.md` - Hook 技术参考（含 Pydantic 模型）
- `ClaudeSettings/skills/zco-plan/SKILL.md` - 开发计划 Skill
- `ClaudeSettings/README.md` - Claude 配置系统说明

---

## 🔄 更新日志

参见 [CHANGELOG.md](./CHANGELOG.md)
