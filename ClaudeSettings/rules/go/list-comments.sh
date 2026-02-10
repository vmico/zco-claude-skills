#!/bin/bash

# 列出所有非代码注释的脚本

# 颜色定义
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "💬 Go 项目非代码注释列表"
echo "======================================"
echo ""

# 检查是否在 Go 项目中
if ! ls *.go > /dev/null 2>&1 && ! find . -name "*.go" -type f | grep -q .; then
    echo -e "${RED}错误: 当前目录不是 Go 项目${NC}"
    exit 1
fi

# 1. TODO 列表
echo -e "${CYAN}📋 TODO 列表:${NC}"
if grep -rn "//;@TODO:" . --include="*.go" --color=always 2>/dev/null; then
    echo ""
else
    echo "   (无)"
    echo ""
fi

# 2. FIXME 列表
echo -e "${RED}🔧 FIXME 列表:${NC}"
if grep -rn "//;@FIXME:" . --include="*.go" --color=always 2>/dev/null; then
    echo ""
else
    echo "   (无)"
    echo ""
fi

# 3. HACK 列表
echo -e "${YELLOW}⚠️  HACK 列表:${NC}"
if grep -rn "//;@HACK:" . --include="*.go" --color=always 2>/dev/null; then
    echo ""
else
    echo "   (无)"
    echo ""
fi

# 4. OPTIMIZE 列表
echo -e "${GREEN}⚡ OPTIMIZE 列表:${NC}"
if grep -rn "//;@OPTIMIZE:" . --include="*.go" --color=always 2>/dev/null; then
    echo ""
else
    echo "   (无)"
    echo ""
fi

# 5. DEPRECATED 列表
echo -e "${RED}🗑️  DEPRECATED 列表:${NC}"
if grep -rn "//;@DEPRECATED:" . --include="*.go" --color=always 2>/dev/null; then
    echo ""
else
    echo "   (无)"
    echo ""
fi

# 6. NOTE 列表
echo -e "${CYAN}📝 NOTE 列表:${NC}"
if grep -rn "//;@NOTE:" . --include="*.go" --color=always 2>/dev/null; then
    echo ""
else
    echo "   (无)"
    echo ""
fi

# 7. 统计
echo "======================================"
echo -e "${CYAN}📊 统计信息:${NC}, comment with //@NOTE:"
echo "   TODO:       $(grep -r "TODO:" . --include="*.go" 2>/dev/null | wc -l) 项"
echo "   FIXME:      $(grep -r "FIXME:" . --include="*.go" 2>/dev/null | wc -l) 项"
echo "   HACK:       $(grep -r "HACK:" . --include="*.go" 2>/dev/null | wc -l) 项"
echo "   OPTIMIZE:   $(grep -r "OPTIMIZE:" . --include="*.go" 2>/dev/null | wc -l) 项"
echo "   DEPRECATED: $(grep -r "DEPRECATED:" . --include="*.go" 2>/dev/null | wc -l) 项"
echo "   NOTE:       $(grep -r "NOTE:" . --include="*.go" 2>/dev/null | wc -l) 项"
echo ""
