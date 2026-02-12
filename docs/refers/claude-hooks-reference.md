# Claude Code Hooks 参考文档

## 概述

Claude Code 支持通过 hooks 机制在特定事件发生时执行自定义脚本。Hooks 以 JSON 格式通过 stdin 接收事件数据。

---

## 支持的 Hook 事件

| Hook 事件 | 触发时机 | 说明 |
|-----------|----------|------|
| `Start` | 会话开始时 | 新项目启动或恢复会话时触发 |
| `Stop` | 会话结束时 | 用户退出或会话终止时触发 |
| `UserPromptSubmit` | 用户提交消息时 | 用户输入并发送消息后触发 |

---

## 内置 Hooks

### 1. save_chat_cli_style - CLI 样式对话保存（推荐）

**文件**: `ClaudeSettings/hooks/save_chat_cli_style.py`

**功能**: 模拟终端显示效果，保存格式化后的对话，包含：
- 工具调用折叠面板（类似终端中的展开/收起）
- 消息角色图标（❯ User / ⬢ Claude）
- 自动截断过长的工具结果
- GitHub Flavored Markdown 格式

**启用方式**:
```bash
export ZCO_CHAT_SAVE_CLI=1
```

**环境变量**:
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ZCO_CHAT_SAVE_CLI` | - | 设置为 `1` 启用此 hook |
| `ZCO_CHAT_SAVE_DIR` | `_.zco_hist` | 输出目录（相对于 GIT_ROOT）|

**输出示例**:
```markdown
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

### 2. save_chat_plain - 简单对话保存

**文件**: `ClaudeSettings/hooks/save_chat_plain.py`

**功能**: 将会话内容保存为简洁的 Markdown 格式，仅包含纯文本对话。

**启用方式**:
```bash
export ZCO_CHAT_SAVE_PLAIN=1
```

**环境变量**:
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ZCO_CHAT_SAVE_PLAIN` | - | 设置为 `1` 启用此 hook |
| `ZCO_CHAT_SAVE_DIR` | `_.zco_hist` | 输出目录（相对于 GIT_ROOT）|

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

### 3. save_chat_spec - 增强对话保存

**文件**: `ClaudeSettings/hooks/save_chat_spec.py`

**功能**: 保存完整对话内容，包括工具调用、参考资源、使用统计等。

**启用方式**:
```bash
export ZCO_CHAT_SAVE_SPEC=1
```

**环境变量**:
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ZCO_CHAT_SAVE_SPEC` | - | 设置为 `1` 启用此 hook |
| `ZCO_CHAT_SAVE_DIR` | `_.zco_hist` | 输出目录（相对于 GIT_ROOT）|

**输出特性**:
- 按时间戳和关键词自动命名文件
- 提取并记录所有参考资源（URLs、文件路径）
- 统计工具使用次数
- 附录详细的工具调用 JSON

**输出文件**:
- `AiCode_log_YYMMDD_HHMMSS_{keywords}.md` - 主对话文件
- `AiCode_log_YYMMDD_HHMMSS_{keywords}_resources.txt` - 参考资源列表

---

## CHAT JSON 结构详解

### 外层事件对象 (Hook Input)

```python
class HookEvent(BaseModel):
    """Hook 事件根对象"""
    hook_event_name: str           # 事件类型: "Start" | "Stop" | "UserPromptSubmit"
    transcript_path: str           # 会话记录文件路径 (JSONL 格式)
    cwd: str                       # 当前工作目录
    session_id: str                # 会话唯一标识
    project_dir: Optional[str]     # 项目目录（Stop 事件）
    model: Optional[str]           # 当前使用的模型名（部分事件可能有）
```

---

### 获取当前模型名

**不同 Hook 事件的 model 字段支持情况：**

| Hook 事件 | model 字段 | 说明 |
|-----------|------------|------|
| `SessionStart` | ✅ 有 | 会话开始时提供 |
| `Stop` | ⚠️ 可能有 | 需实测确认 |
| `UserPromptSubmit` | ⚠️ 可能有 | 需实测确认 |

**在 hook 中获取模型名：**

```python
def main():
    input_data = json.load(sys.stdin)

    # 尝试从输入数据获取模型
    model = input_data.get('model')

    # 或者从环境变量获取（用户设置的默认模型）
    model_from_env = os.environ.get('ANTHROPIC_MODEL')

    print(f"当前模型: {model or model_from_env or 'unknown'}", file=sys.stderr)
```

**环境变量方式（备选）：**

```bash
# 用户可以在启动时设置模型
export ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# 然后在 hook 中读取
model = os.environ.get('ANTHROPIC_MODEL', 'default')
```

---

### 消息对象 (Message)

Claude Code 使用嵌套结构存储消息：

```python
class Message(BaseModel):
    """外层消息对象"""
    type: str                      # 消息类型: "user" | "assistant"
    message: InnerMessage          # 内层消息内容
    toolUseResult: Optional[ToolUseResult]  # 工具执行结果（仅 user 类型）


class InnerMessage(BaseModel):
    """内层消息对象"""
    role: str                      # 角色: "user" | "assistant"
    content: Union[str, List[ContentItem]]  # 消息内容


class ContentItem(BaseModel):
    """内容项（用于 assistant 的多段内容）"""
    type: str                      # 内容类型: "text" | "tool_use" | "tool_result"
    text: Optional[str]            # 文本内容（type="text" 时）
    name: Optional[str]            # 工具名称（type="tool_use" 时）
    input: Optional[Dict]          # 工具输入参数（type="tool_use" 时）
    id: Optional[str]              # 工具调用 ID（type="tool_use" 时）
    tool_use_id: Optional[str]     # 关联的工具 ID（type="tool_result" 时）
    content: Optional[Union[str, List]]  # 工具结果内容（type="tool_result" 时）


class ToolUseResult(BaseModel):
    """工具执行结果（外层字段）"""
    tool_use_id: str               # 工具调用 ID
    content: Union[str, List[TextContent]]  # 结果内容


class TextContent(BaseModel):
    """文本内容项"""
    type: str                      # "text"
    text: str                      # 文本内容
```

---

### 完整示例

#### 用户消息示例

```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": "请帮我读取 README.md 文件"
  }
}
```

#### Assistant 消息示例（纯文本）

```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": "我来帮您读取 README.md 文件。"
  }
}
```

#### Assistant 消息示例（含工具调用）

```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [
      {
        "type": "text",
        "text": "我来帮您读取 README.md 文件。"
      },
      {
        "type": "tool_use",
        "name": "Read",
        "input": {
          "file_path": "/path/to/README.md"
        },
        "id": "toolu_01ABC123"
      }
    ]
  }
}
```

#### 工具结果消息示例

```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_01ABC123",
        "content": [
          {
            "type": "text",
            "text": "# Project README\n\nThis is the project documentation..."
          }
        ]
      }
    ]
  },
  "toolUseResult": {
    "tool_use_id": "toolu_01ABC123",
    "content": [
      {
        "type": "text",
        "text": "# Project README\n\nThis is the project documentation..."
      }
    ]
  }
}
```

---

### Transcript 文件格式

Transcript 是 JSONL（JSON Lines）格式，每行是一个独立的 JSON 对象：

```jsonl
{"type": "user", "message": {"role": "user", "content": "你好"}}
{"type": "assistant", "message": {"role": "assistant", "content": "您好！有什么可以帮您的？"}}
{"type": "user", "message": {"role": "user", "content": "读取文件"}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "好的"}, {"type": "tool_use", "name": "Read", "input": {"file_path": "test.txt"}, "id": "toolu_01"}]}}
```

---

## Pydantic 模型定义（完整版）

```python
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel


class TextContent(BaseModel):
    """文本内容块"""
    type: str = "text"
    text: str


class ToolUseContent(BaseModel):
    """工具调用内容块"""
    type: str = "tool_use"
    name: str                      # 工具名称: Read, Write, Edit, Bash, Task, etc.
    input: Dict[str, Any]          # 工具输入参数
    id: str                        # 工具调用唯一 ID


class ToolResultContent(BaseModel):
    """工具结果内容块"""
    type: str = "tool_result"
    tool_use_id: str               # 关联的工具调用 ID
    content: Union[str, List[TextContent]]  # 工具返回内容
    is_error: Optional[bool] = None  # 是否错误结果


ContentItem = Union[TextContent, ToolUseContent, ToolResultContent]


class InnerMessage(BaseModel):
    """内层消息结构"""
    role: str                      # "user" | "assistant"
    content: Union[str, List[ContentItem]]


class ToolUseResult(BaseModel):
    """工具执行结果（外层）"""
    tool_use_id: str
    content: Union[str, List[TextContent]]


class Message(BaseModel):
    """外层消息结构（Transcript 中的每行）"""
    type: str                      # "user" | "assistant"
    message: InnerMessage
    toolUseResult: Optional[ToolUseResult] = None


class HookEvent(BaseModel):
    """Hook 事件输入"""
    hook_event_name: str           # "Start" | "Stop" | "UserPromptSubmit"
    transcript_path: str
    cwd: str
    session_id: str
    project_dir: Optional[str] = None


# 工具调用汇总（用于增强版保存）
class ToolCallSummary(BaseModel):
    """工具调用摘要"""
    name: str
    input: Dict[str, Any]
    id: str


class ReferenceResource(BaseModel):
    """参考资源"""
    type: str                      # "url" | "file" | "agent"
    value: str                     # 资源值
    icon: str                      # 显示图标
```

---

## 工具类型参考

| 工具名称 | 说明 | 常用输入参数 |
|----------|------|--------------|
| `Read` | 读取文件 | `file_path`, `offset`, `limit` |
| `Write` | 写入文件 | `file_path`, `content` |
| `Edit` | 编辑文件 | `file_path`, `old_string`, `new_string` |
| `Bash` | 执行命令 | `command`, `description`, `timeout` |
| `Task` | 启动子代理 | `prompt`, `subagent_type` |
| `Glob` | 文件匹配 | `pattern`, `path` |
| `Grep` | 内容搜索 | `pattern`, `path`, `output_mode` |
| `WebFetch` | 获取网页 | `url`, `prompt` |
| `WebSearch` | 网络搜索 | `query` |

---

## 调试 Hook 数据

### 使用 debug_hook.py 查看完整数据结构

**文件**: `ClaudeSettings/hooks/debug_hook.py`

**功能**: 打印 Hook 事件接收到的所有数据，用于查看实际可用的字段。

**使用方法**:

```bash
# 在 settings.json 中添加
{
  "hooks": {
    "Stop": ["/path/to/debug_hook.py"]
  }
}

# 或者临时启用
export CLAUDE_HOOK_DEBUG=1
```

**输出位置**: `_.zco_hist/hook_debug_{event_name}.json`

**输出示例**:
```json
{
  "timestamp": "2026-02-12T10:30:00",
  "hook_event_name": "Stop",
  "session_id": "abc123",
  "model": "claude-sonnet-4-5-20250929",
  "cwd": "/path/to/project",
  "transcript_path": "/tmp/...",
  "env": {
    "ANTHROPIC_MODEL": "claude-sonnet-4-5-20250929",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": null,
    ...
  },
  "full_input": { ... }
}
```

---

## 开发自定义 Hook

### 基础模板

```python
#!/usr/bin/env python3
"""自定义 Hook 模板"""
import json
import sys
from pydantic import BaseModel


class HookEvent(BaseModel):
    hook_event_name: str
    transcript_path: str
    cwd: str
    session_id: str


def main():
    # 读取 stdin 输入
    input_data = json.load(sys.stdin)
    event = HookEvent(**input_data)

    if event.hook_event_name == "Stop":
        # 处理会话结束事件
        print(f"Session {event.session_id} ended", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

### 配置 Hook

在 `settings.json` 中配置：

```json
{
  "hooks": {
    "Stop": [
      "/path/to/your/hook.py"
    ]
  }
}
```

---

## 相关文档

- `docs/plans/README.md` - 开发计划管理指南
- `ClaudeSettings/README.md` - Claude 配置系统说明
- `ClaudeSettings/skills/README.md` - Skills 开发指南
