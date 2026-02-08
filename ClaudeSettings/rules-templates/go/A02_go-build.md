# 🐹 Go 项目版本管理与构建规范

## 1. 核心协议：二进制自携带元数据

- ✅ **必须**：所有 Go 二进制文件必须支持 `-version` 和 `-show-info` 参数。
- ✅ **目的**：确保线上运行的二进制文件可溯源（Commit ID、构建时间、CI 流水线）。

---

## 2. 代码实现规范

### 2.1 变量声明

在 `main` 包中定义以下包级变量。**❌ 严禁**在代码中硬编码这些值。

```go
var (
    AppName    string = "unnamed"
    GitCommit  string = "unset"
    GitBranch  string = "unset"
    BuildTime  string = "unset"
    CI_JOB_URL string = "unset"
    Version    string = "1.0.0" // 基础版本号
)

```

### 2.2 Flag 绑定

- ✅ **原则**：`flag.Parse()` 全局仅允许调用一次。
- ✅ **实现**：推荐封装 `co_parse_flag()` 函数并在 `main` 入口最早期执行。

```go
func co_parse_flag() {
    versionFlag := flag.Bool("version", false, "打印版本号并退出")
    verboseFlag := flag.Bool("show-info", false, "打印详细构建信息并退出")

    // ##; 注意：如果业务有其他 flag，请在此处一并定义
    flag.Parse()

    if *versionFlag {
        fmt.Printf("%s version: %s\n", AppName, Version)
        os.Exit(0)
    }

    if *verboseFlag {
        info := fmt.Sprintf(
            "App Name:    %s\nVersion:     %s\nCommit ID:   %s\nBranch:      %s\nBuild Time:  %s\nCI Job:      %s\n",
            AppName, Version, GitCommit, GitBranch, BuildTime, CI_JOB_URL,
        )
        fmt.Print(info)
        os.Exit(0)
    }
}

```

---

## 3. 动态编译规范 (Makefile)

### 3.1 注入指令

- ✅ **强约束**：必须在 `Makefile` 中通过 `-ldflags` 注入元数据。
- ✅ **参数含义**：
- `-s -w`: 压缩体积，移除符号表（生产环境推荐）。
- `-X`: 动态修改变量值。

### 3.2 标准 Makefile 模板

```makefile
##; 获取元数据
DIST_GitCommit := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
DIST_GitBranch := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
DIST_BuildTime := $(shell date +'%Y%m%d_%H%M%S')
DIST_AppName   := $(shell basename $(PWD))

LDFLAGS := -s -w \
    -X 'main.AppName=${DIST_AppName}' \
    -X 'main.GitCommit=${DIST_GitCommit}' \
    -X 'main.GitBranch=${DIST_GitBranch}' \
    -X 'main.BuildTime=${DIST_BuildTime}' \
    -X 'main.CI_JOB_URL=${CI_JOB_URL}'

build:
	@echo "🏗️ Building ${DIST_AppName}..."
	CGO_ENABLED=0 go build -ldflags="$(LDFLAGS)" -o bin/${DIST_AppName} main.go

```

---

## 4. 质量检查清单

- [MUST] **✅ 检查项**：运行 `strings <binary_file> | grep "2026"` 是否能看到注入的时间？
- [MUST] **✅ 检查项**：`-version` 输出是否简洁？
- [MUST] **⚠️ 注意**：如果项目使用 `go-zero` 或 `go-beego` 等框架，请确保框架自带的 Flag 解析不与此冲突（统一使用标准库 `flag` 或框架推荐的解析方式）。

---
