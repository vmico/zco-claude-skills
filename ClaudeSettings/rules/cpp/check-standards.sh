#!/bin/bash
#
# check-standards.sh - C++ 代码标准检查脚本
#
# 使用方法:
#   ./check-standards.sh [选项]
#
# 选项:
#   -h, --help      显示帮助信息
#   -v, --verbose   显示详细输出
#   -q, --quiet     静默模式（只显示错误）
#   --no-format     跳过格式检查
#   --no-tidy       跳过静态分析
#   --no-build      跳过构建检查
#   --no-test       跳过测试检查
#   --no-coverage   跳过覆盖率检查
#
# 退出码:
#   0 - 所有检查通过
#   1 - 有检查失败

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
VERBOSE=0
QUIET=0
CHECK_FORMAT=1
CHECK_TIDY=1
CHECK_BUILD=1
CHECK_TEST=1
CHECK_COVERAGE=1
CHECK_COMMENTS=1

# 统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "C++ Code Standards Check Script"
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -h, --help      Show this help message"
            echo "  -v, --verbose   Show verbose output"
            echo "  -q, --quiet     Quiet mode (only show errors)"
            echo "  --no-format     Skip format check"
            echo "  --no-tidy       Skip static analysis"
            echo "  --no-build      Skip build check"
            echo "  --no-test       Skip test check"
            echo "  --no-coverage   Skip coverage check"
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -q|--quiet)
            QUIET=1
            shift
            ;;
        --no-format)
            CHECK_FORMAT=0
            shift
            ;;
        --no-tidy)
            CHECK_TIDY=0
            shift
            ;;
        --no-build)
            CHECK_BUILD=0
            shift
            ;;
        --no-test)
            CHECK_TEST=0
            shift
            ;;
        --no-coverage)
            CHECK_COVERAGE=0
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# 打印函数
print_header() {
    if [ $QUIET -eq 0 ]; then
        echo -e "\n${BLUE}══════════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}  $1${NC}"
        echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    fi
}

print_step() {
    if [ $QUIET -eq 0 ]; then
        echo -e "\n${YELLOW}[${1}/${2}]${NC} $3"
    fi
}

print_success() {
    if [ $QUIET -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    fi
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    if [ $QUIET -eq 0 ]; then
        echo -e "${YELLOW}⚠${NC} $1"
    fi
}

print_info() {
    if [ $VERBOSE -eq 1 ]; then
        echo -e "${BLUE}ℹ${NC} $1"
    fi
}

# 检查工具是否存在
check_tool() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 运行检查并记录结果
run_check() {
    local name=$1
    local command=$2

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if eval "$command" > /dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        print_success "$name"
        return 0
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        print_error "$name"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════
# 主程序开始
# ═══════════════════════════════════════════════════════════════

print_header "C++ Code Standards Check"

# 检查是否在项目根目录
if [ ! -f "CMakeLists.txt" ] && [ ! -f "Makefile" ]; then
    print_warning "No CMakeLists.txt or Makefile found. Some checks may be skipped."
fi

# ═══════════════════════════════════════════════════════════════
# [1/7] 代码格式检查
# ═══════════════════════════════════════════════════════════════
if [ $CHECK_FORMAT -eq 1 ]; then
    print_step "1" "7" "🔍 Code Formatting Check (clang-format)"

    if check_tool clang-format; then
        # 查找所有 C++ 源文件
        CPP_FILES=$(find . -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.hpp" \) \
            -not -path "*/build/*" \
            -not -path "*/.git/*" \
            -not -path "*/third_party/*" \
            -not -path "*/external/*" 2>/dev/null || true)

        if [ -n "$CPP_FILES" ]; then
            # 检查格式
            FORMAT_ERRORS=0
            for file in $CPP_FILES; do
                if ! clang-format --dry-run --Werror "$file" > /dev/null 2>&1; then
                    FORMAT_ERRORS=$((FORMAT_ERRORS + 1))
                    if [ $VERBOSE -eq 1 ]; then
                        print_error "Formatting issues in: $file"
                        clang-format --dry-run "$file" 2>&1 | head -20
                    fi
                fi
            done

            if [ $FORMAT_ERRORS -eq 0 ]; then
                run_check "All files are properly formatted" "true"
            else
                run_check "Code formatting ($FORMAT_ERRORS files need formatting)" "false"
                print_info "Run 'clang-format -i <file>' to fix formatting issues"
            fi
        else
            print_warning "No C++ files found"
        fi
    else
        print_warning "clang-format not found, skipping format check"
    fi
else
    print_info "Skipping format check (--no-format)"
fi

# ═══════════════════════════════════════════════════════════════
# [2/7] 静态分析检查
# ═══════════════════════════════════════════════════════════════
if [ $CHECK_TIDY -eq 1 ]; then
    print_step "2" "7" "🔍 Static Analysis (clang-tidy)"

    if check_tool clang-tidy; then
        # 查找所有 C++ 源文件
        CPP_FILES=$(find . -type f \( -name "*.cpp" -o -name "*.cc" \) \
            -not -path "*/build/*" \
            -not -path "*/.git/*" \
            -not -path "*/third_party/*" \
            -not -path "*/external/*" \
            -not -path "*/test*/*" \
            -not -name "*_test.cpp" 2>/dev/null || true)

        if [ -n "$CPP_FILES" ]; then
            TIDY_ERRORS=0
            for file in $CPP_FILES; do
                if ! clang-tidy "$file" -- -std=c++17 > /dev/null 2>&1; then
                    TIDY_ERRORS=$((TIDY_ERRORS + 1))
                    if [ $VERBOSE -eq 1 ]; then
                        print_error "Issues in: $file"
                    fi
                fi
            done

            if [ $TIDY_ERRORS -eq 0 ]; then
                run_check "Static analysis passed" "true"
            else
                run_check "Static analysis ($TIDY_ERRORS files with issues)" "false"
            fi
        else
            print_warning "No C++ source files found"
        fi
    else
        print_warning "clang-tidy not found, skipping static analysis"
    fi
else
    print_info "Skipping static analysis (--no-tidy)"
fi

# ═══════════════════════════════════════════════════════════════
# [3/7] 构建检查
# ═══════════════════════════════════════════════════════════════
if [ $CHECK_BUILD -eq 1 ]; then
    print_step "3" "7" "🔨 Build Check"

    if [ -f "CMakeLists.txt" ]; then
        # 创建构建目录
        if [ ! -d "build" ]; then
            mkdir -p build
        fi

        # 配置
        print_info "Configuring with CMake..."
        if cmake -B build -DCMAKE_BUILD_TYPE=Release > /dev/null 2>&1; then
            # 构建
            print_info "Building..."
            if cmake --build build -j$(nproc) > /dev/null 2>&1; then
                run_check "Build successful" "true"
            else
                run_check "Build failed" "false"
            fi
        else
            run_check "CMake configuration failed" "false"
        fi
    elif [ -f "Makefile" ]; then
        if make -j$(nproc) > /dev/null 2>&1; then
            run_check "Build successful" "true"
        else
            run_check "Build failed" "false"
        fi
    else
        print_warning "No build system found, skipping build check"
    fi
else
    print_info "Skipping build check (--no-build)"
fi

# ═══════════════════════════════════════════════════════════════
# [4/7] 测试运行
# ═══════════════════════════════════════════════════════════════
if [ $CHECK_TEST -eq 1 ]; then
    print_step "4" "7" "🧪 Test Execution"

    if [ -d "build" ] && [ -f "build/CTestTestfile.cmake" ]; then
        # 使用 CTest
        if cd build && ctest --output-on-failure > /dev/null 2>&1; then
            run_check "All tests passed" "true"
        else
            run_check "Some tests failed" "false"
        fi
        cd ..
    elif [ -d "build" ] && find build -name "*_test" -type f > /dev/null 2>&1; then
        # 直接运行测试
        TEST_FAILED=0
        for test in build/*_test build/test/*_test; do
            if [ -f "$test" ]; then
                if ! "$test" > /dev/null 2>&1; then
                    TEST_FAILED=1
                fi
            fi
        done

        if [ $TEST_FAILED -eq 0 ]; then
            run_check "All tests passed" "true"
        else
            run_check "Some tests failed" "false"
        fi
    else
        print_warning "No tests found, skipping test check"
    fi
else
    print_info "Skipping test check (--no-test)"
fi

# ═══════════════════════════════════════════════════════════════
# [5/7] 覆盖率检查
# ═══════════════════════════════════════════════════════════════
if [ $CHECK_COVERAGE -eq 1 ]; then
    print_step "5" "7" "📊 Coverage Check (≥80%)"

    if [ -f "build/coverage.info" ] || [ -d "build/coverage_report" ]; then
        # 检查覆盖率报告
        if [ -f "build/coverage.info" ]; then
            # 使用 lcov 提取覆盖率
            if check_tool lcov; then
                COVERAGE=$(lcov --summary build/coverage.info 2>&1 | \
                          grep "lines" | grep -oP '\d+\.?\d*%' | head -1 | tr -d '%')

                if [ -n "$COVERAGE" ]; then
                    COVERAGE_INT=${COVERAGE%.*}
                    if [ "$COVERAGE_INT" -ge 80 ]; then
                        run_check "Code coverage: ${COVERAGE}% (≥80%)" "true"
                    else
                        run_check "Code coverage: ${COVERAGE}% (<80%)" "false"
                    fi
                else
                    print_warning "Could not parse coverage data"
                fi
            else
                print_warning "lcov not found, skipping coverage check"
            fi
        fi
    else
        print_info "No coverage data found, skipping coverage check"
        print_info "Enable coverage with: cmake -DENABLE_COVERAGE=ON"
    fi
else
    print_info "Skipping coverage check (--no-coverage)"
fi

# ═══════════════════════════════════════════════════════════════
# [6/7] 注释规范统计
# ═══════════════════════════════════════════════════════════════
if [ $CHECK_COMMENTS -eq 1 ]; then
    print_step "6" "7" "💬 Comment Statistics"

    # 统计各类注释
    TODO_COUNT=$(grep -r "//;@TODO:" --include="*.cpp" --include="*.h" --include="*.hpp" . 2>/dev/null | wc -l)
    FIXME_COUNT=$(grep -r "//;@FIXME:" --include="*.cpp" --include="*.h" --include="*.hpp" . 2>/dev/null | wc -l)
    HACK_COUNT=$(grep -r "//;@HACK:" --include="*.cpp" --include="*.h" --include="*.hpp" . 2>/dev/null | wc -l)
    OPTIMIZE_COUNT=$(grep -r "//;@OPTIMIZE:" --include="*.cpp" --include="*.h" --include="*.hpp" . 2>/dev/null | wc -l)
    DEPRECATED_COUNT=$(grep -r "//;@DEPRECATED:" --include="*.cpp" --include="*.h" --include="*.hpp" . 2>/dev/null | wc -l)

    print_info "TODO: $TODO_COUNT"
    print_info "FIXME: $FIXME_COUNT"
    print_info "HACK: $HACK_COUNT"
    print_info "OPTIMIZE: $OPTIMIZE_COUNT"
    print_info "DEPRECATED: $DEPRECATED_COUNT"

    if [ $FIXME_COUNT -gt 0 ]; then
        print_warning "$FIXME_COUNT FIXME(s) found"
    fi

    if [ $HACK_COUNT -gt 0 ]; then
        print_warning "$HACK_COUNT HACK(s) found"
    fi

    run_check "Comment statistics collected" "true"
fi

# ═══════════════════════════════════════════════════════════════
# [7/7] 总结
# ═══════════════════════════════════════════════════════════════
print_step "7" "7" "📋 Summary"

echo -e "\n══════════════════════════════════════════════════════════════"
echo -e "  Total checks:  $TOTAL_CHECKS"
echo -e "  ${GREEN}Passed:${NC}        $PASSED_CHECKS"
echo -e "  ${RED}Failed:${NC}        $FAILED_CHECKS"
echo -e "══════════════════════════════════════════════════════════════"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "\n${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some checks failed. Please fix the issues above.${NC}"
    exit 1
fi
