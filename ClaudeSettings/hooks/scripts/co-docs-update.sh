#!/bin/bash

#
# co-docs-update.sh - 自动更新 CLAUDE.md 文档元信息
#
# 用途：
#   - 更新 Git Commit ID、Branch、最新提交信息
#   - 更新文档修改时间
#   - 保持文档与代码同步
#
# 使用方法：
#   bash scripts/co-docs-update.sh
#
# 作者：Claude Code
# 日期：2026-01-07
#

set -e # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
	echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
	echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
	echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
	echo -e "${RED}[ERROR]${NC} $1"
}

# 获取项目根目录
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$PROJECT_ROOT" ]; then
	log_error "未找到 Git 仓库，请在 Git 项目中运行此脚本"
	exit 1
fi

CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"

log_info "项目根目录: $PROJECT_ROOT"
log_info "CLAUDE.md 路径: $CLAUDE_MD"

# 检查 CLAUDE.md 是否存在
if [ ! -f "$CLAUDE_MD" ]; then
	log_error "CLAUDE.md 文件不存在: $CLAUDE_MD"
	log_info "请先创建 CLAUDE.md 文件"
	exit 1
fi

## 创建备份
#BACKUP_FILE="${CLAUDE_MD}._.$(date +%y%m%d_%H%M).md"
BACKUP_FILE="$PROJECT_ROOT/CLAUDE._.v$(date +%y%m%d_%H%M).md"
cp "$CLAUDE_MD" "$BACKUP_FILE"
log_info "已创建备份: $BACKUP_FILE"

# 收集 Git 信息
log_info "收集 Git 信息..."

# 当前时间
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Git Commit 信息
GIT_COMMIT_FULL=$(git log -1 --pretty=format:"%H" 2>/dev/null || echo "unknown")
GIT_COMMIT_SHORT=$(git log -1 --pretty=format:"%h" 2>/dev/null || echo "unknown")
GIT_COMMIT_MSG=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "unknown")
GIT_AUTHOR=$(git log -1 --pretty=format:"%an" 2>/dev/null || echo "unknown")
GIT_DATE=$(git log -1 --pretty=format:"%ad" --date=iso 2>/dev/null || echo "unknown")

# Git Branch
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# 应用版本（从 main.go 中提取）
MAIN_GO="$PROJECT_ROOT/main.go"
APP_VERSION="unknown"
if [ -f "$MAIN_GO" ]; then
	APP_VERSION=$(grep -E 'const version string = "' "$MAIN_GO" | sed -E 's/.*const version string = "(.*)".*/\1/' || echo "unknown")
fi

log_info "  - 更新时间: $CURRENT_TIME"
log_info "  - Git Commit: $GIT_COMMIT_SHORT ($GIT_COMMIT_FULL)"
log_info "  - Git Branch: $GIT_BRANCH"
log_info "  - 最新提交: $GIT_COMMIT_MSG"
log_info "  - 提交作者: $GIT_AUTHOR"
log_info "  - 提交时间: $GIT_DATE"
log_info "  - 应用版本: $APP_VERSION"

# 使用 sed 更新 CLAUDE.md 中的元信息
log_info "更新 CLAUDE.md 元信息..."

# 临时文件
TEMP_FILE=$(mktemp)

# 更新各个字段
sed -e "s|^- \*\*更新时间\*\*:.*|- **更新时间**: $CURRENT_TIME|" \
	-e "s|^- \*\*Git Commit\*\*:.*|- **Git Commit**: \`$GIT_COMMIT_SHORT\` ($GIT_COMMIT_FULL)|" \
	-e "s|^- \*\*Git Branch\*\*:.*|- **Git Branch**: \`$GIT_BRANCH\`|" \
	-e "s|^- \*\*最新提交\*\*:.*|- **最新提交**: $GIT_COMMIT_MSG (by $GIT_AUTHOR, $GIT_DATE)|" \
	-e "s|^- \*\*应用版本\*\*:.*|- **应用版本**: $APP_VERSION|" \
	"$CLAUDE_MD" >"$TEMP_FILE"

# 更新文档底部的最后更新时间
sed -i "s|^\*\*最后更新\*\*:.*|\*\*最后更新\*\*: $CURRENT_TIME|" "$TEMP_FILE"

# 替换原文件
mv "$TEMP_FILE" "$CLAUDE_MD"

log_success "CLAUDE.md 元信息更新完成！"

# 显示差异
echo ""
log_info "更新内容对比："
echo "----------------------------------------"
git diff --no-index --color=always "$BACKUP_FILE" "$CLAUDE_MD" | tail -n +5 || true
echo "----------------------------------------"

# 询问是否删除备份
echo ""
read -p "$(echo -e ${YELLOW}是否删除备份文件？ [y/N]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
	rm -f "$BACKUP_FILE"
	log_success "备份文件已删除"
else
	log_info "备份文件保留在: $BACKUP_FILE"
fi

# 显示文档状态
echo ""
log_success "✅ 文档更新完成！"
echo ""
log_info "下一步操作："
log_info "  1. 查看文档: cat CLAUDE.md"
log_info "  2. 提交更改: git add CLAUDE.md && git commit -m 'docs: update CLAUDE.md metadata'"
log_info "  3. 验证 Claude Code 加载: claude code"
echo ""

exit 0
