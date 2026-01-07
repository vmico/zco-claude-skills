#!/bin/bash

# Go 编程标准检查脚本

set -e

echo "🔍 开始检查 Go 编程标准..."
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# 1. 检查代码格式
echo "📝 [1/7] 检查代码格式..."
if ! gofmt -l . | grep -q ".go"; then
    echo -e "${GREEN}✓ 代码格式正确${NC}"
else
    echo -e "${RED}✗ 以下文件格式不正确:${NC}"
    gofmt -l .
    FAILED=1
fi
echo ""

# 2. 检查 imports
echo "📦 [2/7] 检查 imports 顺序..."
if command -v goimports &> /dev/null; then
    if ! goimports -l . | grep -q ".go"; then
        echo -e "${GREEN}✓ Imports 顺序正确${NC}"
    else
        echo -e "${RED}✗ 以下文件 imports 顺序不正确:${NC}"
        goimports -l .
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠ goimports 未安装，跳过检查${NC}"
fi
echo ""

# 3. 运行测试
echo "🧪 [3/7] 运行测试..."
if go test ./... -v; then
    echo -e "${GREEN}✓ 所有测试通过${NC}"
else
    echo -e "${RED}✗ 测试失败${NC}"
    FAILED=1
fi
echo ""

# 4. 检查测试覆盖率
echo "📊 [4/7] 检查测试覆盖率..."
COVERAGE=$(go test ./... -cover -coverprofile=coverage.out 2>&1 | grep "coverage:" | awk '{sum+=$NF; count++} END {if (count>0) print sum/count; else print 0}' | sed 's/%//')

if [ -z "$COVERAGE" ]; then
    echo -e "${YELLOW}⚠ 无法计算覆盖率${NC}"
else
    if (( $(echo "$COVERAGE >= 80" | bc -l) )); then
        echo -e "${GREEN}✓ 测试覆盖率: ${COVERAGE}% (≥ 80%)${NC}"
    else
        echo -e "${RED}✗ 测试覆盖率: ${COVERAGE}% (< 80%)${NC}"
        FAILED=1
    fi
fi
echo ""

# 5. 检查竞态条件
echo "🏃 [5/7] 检查竞态条件..."
if go test -race ./... > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 无竞态条件${NC}"
else
    echo -e "${RED}✗ 检测到竞态条件${NC}"
    FAILED=1
fi
echo ""

# 6. 运行 linter
echo "🔍 [6/7] 运行 linter..."
if command -v golangci-lint &> /dev/null; then
    if golangci-lint run ./...; then
        echo -e "${GREEN}✓ Linter 检查通过${NC}"
    else
        echo -e "${RED}✗ Linter 检查失败${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠ golangci-lint 未安装，跳过检查${NC}"
    echo "   安装命令: curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b \$(go env GOPATH)/bin"
fi
echo ""

# 7. 检查注释规范
echo "💬 [7/7] 检查注释规范..."
echo "   查找所有功能注释 (//@NOTE:):"

# 统计各类非代码注释
TODO_COUNT=$(grep -r "TODO:" . --include="*.go" 2>/dev/null | wc -l || echo 0)
FIXME_COUNT=$(grep -r "FIXME:" . --include="*.go" 2>/dev/null | wc -l || echo 0)
HACK_COUNT=$(grep -r "HACK:" . --include="*.go" 2>/dev/null | wc -l || echo 0)
DEPRECATED_COUNT=$(grep -r "DEPRECATED:" . --include="*.go" 2>/dev/null | wc -l || echo 0)

echo "   - TODO: $TODO_COUNT 项"
echo "   - FIXME: $FIXME_COUNT 项"
echo "   - HACK: $HACK_COUNT 项"
echo "   - DEPRECATED: $DEPRECATED_COUNT 项"

if [ "$FIXME_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ 有 $FIXME_COUNT 个 FIXME 需要修复${NC}"
fi

if [ "$DEPRECATED_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ 有 $DEPRECATED_COUNT 个废弃代码需要清理${NC}"
fi

echo ""

# 8. 总结
echo "================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 检查失败，请修复上述问题${NC}"
    exit 1
fi
