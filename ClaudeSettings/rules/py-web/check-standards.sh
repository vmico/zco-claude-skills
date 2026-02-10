#!/bin/bash

## Python 编程标准检查脚本

set -e

echo "🔍 开始检查 Python 编程标准..."
echo ""

## 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' ## No Color

FAILED=0

## 1. 检查代码格式
echo "📝 [1/7] 检查代码格式..."
if command -v autopep8 &> /dev/null; then
    if autopep8 --diff .; then
        echo -e "${GREEN}✓ 代码格式正确${NC}"
    else
        echo -e "${RED}✗ 代码格式不正确，运行 'autopep8 --in-place .' 修复${NC}"
        FAILED=1
    fi
elif command -v ruff &> /dev/null; then
    if ruff format --check .; then
        echo -e "${GREEN}✓ 代码格式正确${NC}"
    else
        echo -e "${RED}✗ 代码格式不正确，运行 'ruff format .' 修复${NC}"
        FAILED=1
    fi
elif command -v black &> /dev/null; then
    if black --check .; then
        echo -e "${GREEN}✓ 代码格式正确${NC}"
    else
        echo -e "${RED}✗ 代码格式不正确，运行 'black .' 修复${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠ ruff/black 未安装，跳过格式检查${NC}"
fi
echo ""

## 2. 检查 imports
echo "📦 [2/7] 检查 imports 顺序..."
if command -v ruff &> /dev/null; then
    if ruff check --select I .; then
        echo -e "${GREEN}✓ Imports 顺序正确${NC}"
    else
        echo -e "${RED}✗ Imports 顺序不正确${NC}"
        FAILED=1
    fi
elif command -v isort &> /dev/null; then
    if isort --check-only .; then
        echo -e "${GREEN}✓ Imports 顺序正确${NC}"
    else
        echo -e "${RED}✗ Imports 顺序不正确${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠ ruff/isort 未安装，跳过检查${NC}"
fi
echo ""

## 3. 运行 linter
echo "🔍 [3/7] 运行 linter..."
if command -v ruff &> /dev/null; then
    if ruff check .; then
        echo -e "${GREEN}✓ Linter 检查通过${NC}"
    else
        echo -e "${RED}✗ Linter 检查失败${NC}"
        FAILED=1
    fi
elif command -v pylint &> /dev/null; then
    if pylint **/*.py; then
        echo -e "${GREEN}✓ Linter 检查通过${NC}"
    else
        echo -e "${RED}✗ Linter 检查失败${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠ ruff/pylint 未安装，跳过检查${NC}"
    echo "   安装命令: pip install ruff"
fi
echo ""

## 4. 运行类型检查
echo "🔍 [4/7] 运行类型检查..."
if command -v mypy &> /dev/null; then
    if mypy .; then
        echo -e "${GREEN}✓ 类型检查通过${NC}"
    else
        echo -e "${YELLOW}⚠ 类型检查发现问题${NC}"
        ## 类型检查失败不标记为 FAILED，只警告
    fi
else
    echo -e "${YELLOW}⚠ mypy 未安装，跳过类型检查${NC}"
    echo "   安装命令: pip install mypy"
fi
echo ""

## 5. 运行测试
echo "🧪 [5/7] 运行测试..."
if command -v pytest &> /dev/null; then
    if pytest -q; then
        echo -e "${GREEN}✓ 所有测试通过${NC}"
    else
        echo -e "${RED}✗ 测试失败${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠ pytest 未安装，跳过测试${NC}"
fi
echo ""

## 6. 检查测试覆盖率
echo "📊 [6/7] 检查测试覆盖率..."
if command -v pytest &> /dev/null && command -v coverage &> /dev/null; then
    COVERAGE_OUTPUT=$(pytest --cov=. --cov-report=term-missing -q 2>&1 || true)
    COVERAGE=$(echo "$COVERAGE_OUTPUT" | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
    
    if [ -z "$COVERAGE" ]; then
        echo -e "${YELLOW}⚠ 无法计算覆盖率${NC}"
    else
        COVERAGE_INT=${COVERAGE%.*}
        if [ "$COVERAGE_INT" -ge 80 ]; then
            echo -e "${GREEN}✓ 测试覆盖率: ${COVERAGE}% (≥ 80%)${NC}"
        else
            echo -e "${RED}✗ 测试覆盖率: ${COVERAGE}% (< 80%)${NC}"
            FAILED=1
        fi
    fi
else
    echo -e "${YELLOW}⚠ pytest-cov 未安装，跳过覆盖率检查${NC}"
fi
echo ""

## 7. 检查注释规范
echo "💬 [7/7] 检查注释规范..."
echo "   查找所有非代码注释 (##;@):"

## 统计各类非代码注释
TODO_COUNT=$(grep -r "##;@TODO:" . --include="*.py" 2>/dev/null | wc -l || echo 0)
FIXME_COUNT=$(grep -r "##;@FIXME:" . --include="*.py" 2>/dev/null | wc -l || echo 0)
HACK_COUNT=$(grep -r "##;@HACK:" . --include="*.py" 2>/dev/null | wc -l || echo 0)
DEPRECATED_COUNT=$(grep -r "##;@DEPRECATED:" . --include="*.py" 2>/dev/null | wc -l || echo 0)

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

## 8. 总结
echo "================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 检查失败，请修复上述问题${NC}"
    exit 1
fi
