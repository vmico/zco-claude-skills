# Hooks 变更日志

## 2026-01-06 - 增强版发布

### 新增功能

#### save-conversation-enhanced.py（增强版）

相比标准版，新增以下功能：

1. **📚 参考资源记录**
   - 自动提取并记录所有引用的资源
   - 支持的资源类型：
     - 🌐 网络 URLs（WebFetch、WebSearch）
     - 📄 本地文件路径（Read 工具）
     - 🤖 Agent 调用（Task 工具）

2. **🔧 工具调用统计**
   - 记录使用了哪些工具
   - 统计每个工具的调用次数
   - 在文档头部显示摘要

3. **📋 详细的工具调用记录**
   - 在附录中记录每个工具的完整调用参数
   - JSON 格式展示，便于调试和回溯

4. **🗂️ 独立的资源列表文件**
   - 为每次对话生成独立的资源列表文件
   - 文件名：`{timestamp}_{keywords}_resources.txt`
   - 便于批量处理和检索

### 文件对比

| 功能 | 标准版 | 增强版 |
|------|--------|--------|
| 保存对话内容 | ✅ | ✅ |
| 提取关键词 | ✅ | ✅ |
| 记录参考资源 | ❌ | ✅ |
| 工具使用统计 | ❌ | ✅ |
| 工具调用详情 | ❌ | ✅ |
| 独立资源列表 | ❌ | ✅ |
| 性能开销 | 低 | 中等 |

### 输出示例

#### 对话文件（26010614_API文档_生成.md）

```markdown
# Claude Code 对话记录

**时间**: 2026-01-06 14:30:00

## 📚 参考资源

- 🤖 Agent: claude-code-guide
- 🤖 Agent: Explore
- 📄 /path/to/routers/router.go
- 📄 /path/to/models/auth/jwt.go

**使用工具**: 8 次
  - Read: 5 次
  - Task: 2 次
  - Bash: 1 次

---

## 👤 用户提问 #1

请为我遍历项目的 API 接口...

## 🤖 Claude 回答 #1

好的！我来帮你遍历...

---

## 📋 附录：工具调用详情

### 工具 1: Task
```json
{
  "subagent_type": "Explore",
  "prompt": "探索项目 API 结构..."
}
```

---
*自动生成于 2026-01-06 14:30:00*
```

#### 资源列表文件（26010614_API文档_生成_resources.txt）

```
# 参考资源
# 生成时间: 2026-01-06 14:30:00
# 对话文件: 26010614_API文档_生成.md

🤖 Agent: Explore
🤖 Agent: claude-code-guide
📄 /home/lane/.../routers/router.go
📄 /home/lane/.../models/auth/jwt.go
```

### 如何切换版本

编辑 `.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            // 标准版：
            // "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/save-conversation.py"

            // 增强版（当前）：
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/save-conversation-enhanced.py"
          }
        ]
      }
    ]
  }
}
```

### 性能说明

- **标准版**: 处理时间 < 100ms，适合频繁对话
- **增强版**: 处理时间 100-300ms，适合需要详细记录的场景

### 推荐使用场景

#### 标准版适合：
- 日常快速对话
- 不需要追溯参考资源
- 注重性能

#### 增强版适合：
- 技术研究和学习
- 需要记录资料来源
- 团队协作和知识分享
- 生成可审计的对话记录

---

## 历史版本

### v1.0 - 2026-01-06
- 初始版本：save-conversation.py
- 功能：基础对话保存

### v2.0 - 2026-01-06（当前）
- 增强版：save-conversation-enhanced.py
- 新增：参考资源记录、工具调用统计、详细调用记录
