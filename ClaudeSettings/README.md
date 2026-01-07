# Claude Code 配置说明

本目录包含 Claude Code 的项目配置文件。

## 配置文件

### `settings.json`
项目级别的配置，包含了从以下文件转换而来的排除规则：
- 项目的 `.gitignore`
- 全局的 `~/.gitignore_global`

该配置确保 Claude Code 在分析代码时忽略：
- 构建产物和二进制文件
- IDE 配置文件 (.idea, .vscode, .DS_Store)
- 日志文件
- 临时文件和备份
- Python/Go 的依赖和缓存
- 敏感配置文件 (.env, conf/app.conf)
- 本地数据目录 (var, data, logs)

## 文件说明

| 文件 | 用途 | 是否提交到 Git |
|------|------|---------------|
| `settings.json` | 团队共享配置 | ✅ 是 |
| `settings.local.json` | 个人本地配置 | ❌ 否 (自动忽略) |

## 使用方法

配置已自动生效，无需额外操作。Claude Code 将自动读取此配置。

## 维护说明

### 当修改 .gitignore 时

由于 Claude Code 不会自动同步 `.gitignore` 的更改，当你更新项目的 `.gitignore` 或全局的 `~/.gitignore_global` 时，需要手动更新 `settings.json`。

可以使用以下方法：

1. **手动添加规则**
   在 `settings.json` 的 `permissions.deny` 数组中添加新规则：
   ```json
   "Read(./新增目录)",
   "Read(./新增目录/**)"
   ```

2. **请求 Claude 重新生成**
   告诉 Claude：
   ```
   请重新读取 .gitignore 和 ~/.gitignore_global，更新 .claude/settings.json
   ```

### 常见排除模式

```json
{
  "permissions": {
    "deny": [
      "Read(./单个文件.txt)",           // 排除单个文件
      "Read(./目录)",                   // 排除目录
      "Read(./目录/**)",                // 排除目录及所有子内容
      "Read(**/*.扩展名)",              // 排除所有该扩展名文件
      "Read(**/目录名)",                // 排除所有该名称的目录
      "Read(**/目录名/**)"              // 排除所有该名称目录的内容
    ]
  }
}
```

## 个人配置

如果你有个人专属的排除需求，创建 `settings.local.json`：

```bash
cat > .claude/settings.local.json << 'EOF'
{
  "permissions": {
    "deny": [
      "Read(./my-personal-notes)",
      "Read(./my-personal-notes/**)"
    ]
  }
}
EOF
```

该文件不会被提交到 Git（已在 .gitignore 中忽略）。

## 验证配置

测试配置是否生效：

```bash
# 在 Claude Code 会话中尝试读取被排除的文件
# 应该会被阻止
```

## 更新历史

- 2026-01-06: 初始配置，基于项目 .gitignore 和 ~/.gitignore_global
