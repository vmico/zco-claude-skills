# GoBuild  动态编译版本管理

## 说明
go释放的二进制文件, 应该自携带版本信息

## 实现步骤

#### 1.  定义全局变量并绑定到  flag

将版本信息变量声明为包级变量：

```go
package main

import flag
import fmt
import os

var (
	xBuildDesc string
	AppName    string = "{AppName}"
	GitCommit  string = "unset" // 默认 Commit，编译时覆盖
	GitBranch  string = "unset" // 默认 分支，编译时覆盖
	BuildTime  string = "unset" // 默认构建时间，编译时覆盖
	CI_JOB_URL string = "unset" // 默认 CI Job URL，编译时覆盖
)

func co_parse_flag() {
    //@NOTE: 绑定版本信息到 flag, 注意 flag.Parse() 只能执行一次
    versionFlag := flag.Bool("version", false, "Print version and exit")
	verboseFlag := flag.Bool("show-info", false, "Print verbose info and exit")
    helpFlag := flag.Bool("h", false, "Display this help message")
    flag.Parse()

	if *versionFlag {
		fmt.Fprint(os.Stdout, version)
		os.Exit(0)
	}

	xBuildDesc := fmt.Sprintf(" AppName: %s \n Version: %s \n CommitID: %s \n Branch: %s \n BuildTime: %s \n CI_JOB_URL:%s \n",
		AppName, version, GitCommit, GitBranch, BuildTime, CI_JOB_URL,
	)

	if *verboseFlag {
		fmt.Fprint(os.Stdout, xBuildDesc)
		os.Exit(0)
	}

    if *helpFlag {
		flag.Usage()
		os.Exit(0)
	}
}

func main(){
    //; 如果有其他自定义的 flag 配置需要前置
    //flag.StringVar(&configFilePath, "c", "conf/app.conf", "Path to config file")
    //; 注意 flag.Parse() 全局只能执行一次
    co_parse_flag()

    //; 后续是原业务逻辑代码
}
```

#### 2.  编译时动态注入值

在编译命令中使用  `-ldflags`  覆盖全局变量值：(Makefile), 参考如下是

```Makefile
DIST_GitCommit ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "commit_id")
DIST_GitBranch ?= $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "branch")
DIST_CI_JOB_URL ?= $(shell echo ${CI_JOB_URL:-"unset"})
# DIST_BuildTime := $(shell date +'%Y-%m-%dT%H%M%S%Z')
DIST_BuildTime := $(shell date +'%Y%m%d_%H%M%S')
DIST_AppName := "AppName"

build:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w \
    -X 'main.GitCommit=${DIST_GitCommit}' \
    -X 'main.GitBranch=${DIST_GitBranch}' \
    -X 'main.BuildTime=${DIST_BuildTime}' \
	-X 'main.CI_JOB_URL=${DIST_CI_JOB_URL}' " \
    -o ${BINARY}
#    // ...  自定义更多的参数
```

- **效果**：`Version`、`GitCommit`、`BuildTime`  会被编译时注入的值覆盖。

#### 3.  测试

```shell
make build
./{BINARY} -version
./{BINARY} -show-info
```
