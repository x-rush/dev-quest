# Go 环境搭建和工具配置

> **阅读准备**：会创建文件、打开终端并理解命令退出状态即可；本章不要求先掌握 Go 语法，安装后用最小程序验证工具链。

## 先理解，再动手

安装编译器、让终端找到命令、让项目找到依赖是三件事。go version 成功只证明第一条链路，不证明当前目录已经是模块。

**本节自测**：分别在项目目录运行 go version、go env GOMOD，再运行一个 main。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

应能指出编译器版本、当前模块文件和程序输出；GOMOD 指向空设备时要检查目录或初始化模块。

</details>

## 📚 概述

作为PHP开发者，第一次接触Go需要了解Go的开发环境和工具链配置。Go的开发环境与PHP有显著不同，主要体现在编译型语言特性和工具链设计上。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐ (1/5) |
| **标签** | `#环境配置` `#开发工具` `#go-modules` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

### 🎯 学习目标
- 完成Go开发环境的搭建
- 理解Go的工作区和模块系统
- 配置常用的开发工具
- 编写并运行第一个Go程序

## 🛠️ 环境搭建

### 1. 安装Go SDK

#### 下载和安装
- **官方网站**: [go.dev/dl](https://go.dev/dl/)
- **推荐版本**: Go 1.27+（当前稳定版本，详见 README 技术基线区块）
- **安装方式**:
  - **Windows**: 下载msi安装包，按向导安装
  - **macOS**: 使用Homebrew: `brew install go`
  - **Linux**: 下载tar.gz包或使用包管理器

#### 验证安装
```bash
go version
# 输出示例: go version go1.27.1 darwin/amd64

go env
# 查看Go环境变量
```

### 2. 理解Go环境变量

#### 核心环境变量
```bash
# GOROOT - Go安装目录
export GOROOT=/usr/local/go

# GOPATH - Go工作区 (Go 1.11+后主要用于第三方包)
export GOPATH=$HOME/go

# GOBIN - 可执行文件目录
export GOBIN=$GOPATH/bin

# PATH - 添加Go可执行文件到PATH
export PATH=$PATH:$GOROOT/bin:$GOBIN

# Go代理设置 (国内用户推荐)
export GOPROXY=https://goproxy.cn,direct
export GOSUMDB=off
```

#### 与PHP的对比
| PHP | Go |
|-----|-----|
| 解释型语言，无需编译 | 编译型语言，需要编译 |
| php.ini配置文件 | 环境变量配置 |
| Composer包管理 | Go Modules |
| 即时运行 | 编译后运行 |

### 3. Go Modules (Go 1.11+)

#### 初始化模块
```bash
# 创建项目目录
mkdir hello-go
cd hello-go

# 初始化Go模块
go mod init github.com/your-username/hello-go

# 项目结构
hello-go/
├── go.mod          # 模块定义文件
├── go.sum          # 依赖版本锁定
├── main.go         # 主程序文件
└── README.md       # 项目说明
```

#### 依赖管理
```bash
# 添加依赖
go get github.com/gin-gonic/gin

# 添加特定版本
go get github.com/gin-gonic/gin@latest

# 移除依赖
go get github.com/gin-gonic/gin@none

# 整理依赖
go mod tidy

# 查看依赖图
go mod graph
```

## 🛠️ 开发工具配置

### 1. VS Code 配置

#### 编辑器支持

VS Code 的 Go 扩展用于把诊断、跳转、格式化和测试等能力接入编辑器。先确保终端中的 `go version` 与 `go test ./...` 能工作，再检查编辑器是否使用同一套工具链；扩展不能替代 Go 安装。其他测试面板或结构浏览扩展按需选择，不是完成本课程的必需条件。

#### 推荐配置 (settings.json)
```json
{
    "go.useLanguageServer": true,
    "go.autocompleteUnimportedPackages": true,
    "go.docsTool": "godoc",
    "go.inferGopath": false,
    "go.lintTool": "golangci-lint",
    "go.lintOnSave": "workspace",
    "go.formatTool": "goimports",
    "go.formatOnSave": true,
    "go.testTimeout": "30s",
    "go.testFlags": ["-v"]
}
```

### 2. GoLand 配置

#### 项目设置
1. **GOPATH**: 设置为 `$HOME/go`
2. **Go Modules**: 启用Go Modules支持
3. **File Watchers**: 配置go fmt和go imports
4. **Terminal**: 使用Go enabled terminal

### 3. 常用Go工具

#### 开发工具
```bash
# 格式化代码
go fmt ./...

# 导入包整理
goimports -w .

# 静态检查
go vet ./...

# 代码检查 (golangci-lint)
golangci-lint run

# 依赖检查
go mod why github.com/gin-gonic/gin
```

#### 调试工具
```bash
# 编译
go build -o hello main.go

# 运行
go run main.go

# 安装二进制文件
go install github.com/your-username/hello-go

# 交叉编译
GOOS=linux GOARCH=amd64 go build -o hello-linux main.go
GOOS=windows GOARCH=amd64 go build -o hello.exe main.go
```

## 🎯 第一个Go程序

### 1. Hello World 程序

<!-- doc-verify:go-environment-toolchain-hello -->
```go
// main.go
package main

import "fmt"

func main() {
    fmt.Println("hello-go toolchain-ready")
}
```

这个程序只验证编译器能编译并运行当前模块中的 `main.go`；还应在同一目录运行 `go env GOMOD`，确认输出是该目录下的 `go.mod`，而不是空设备。它不安装 SDK，也不下载依赖。

预期输出：

```text
hello-go toolchain-ready
```

### 2. 编译和运行

```bash
# 直接运行 (开发阶段)
go run main.go
# Hello, Go!
# 我是从PHP转来的开发者

# 编译为可执行文件
go build -o hello main.go

# 运行编译后的文件
./hello
# Hello, Go!
# 我是从PHP转来的开发者
```

### 3. 与PHP的对比

#### PHP版本
```php
<?php
echo "Hello, PHP!\n";
echo "我是PHP开发者\n";
```

#### 关键差异
1. **包声明**: Go需要`package main`
2. **导入语句**: 使用`import`而不是`require/include`
3. **入口函数**: 必须有`main()`函数
4. **分号**: Go的分号是可选的（编译器自动添加）
5. **编译运行**: Go需要编译，PHP解释执行

## 🧪 实践练习

### 练习1: 环境验证
```bash
# 创建练习项目
mkdir go-practice
cd go-practice
go mod init github.com/your-username/go-practice

# 创建main.go
cat > main.go << 'EOF'
package main

import "fmt"

func main() {
    fmt.Println("Go环境配置成功!")
}
EOF

# 运行程序
go run main.go
```

### 练习2: 包管理实践

> 💡 这是预览练习：Web 服务部分用到了 gin 框架，超出 basics 范围，详见 [../frameworks/01-gin-framework-basics.md](../frameworks/01-gin-framework-basics.md)。

```bash
# 添加一个Web框架依赖
go get github.com/gin-gonic/gin

# 查看go.mod文件
cat go.mod

# 创建简单的Web服务
cat > web.go << 'EOF'
package main

import (
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "message": "Hello from Gin!",
        })
    })
    r.Run(":8080")
}
EOF

# 运行Web服务
go run web.go
```

## 📋 检查清单

- [ ] Go SDK安装成功 (go version)
- [ ] 环境变量配置正确 (go env)
- [ ] Go Modules工作正常 (go mod init)
- [ ] 开发工具配置完成 (VS Code/GoLand)
- [ ] 第一个Go程序运行成功
- [ ] 包管理基本操作掌握
- [ ] 常用开发工具命令熟悉

## 🚀 下一步

完成环境搭建后，你可以继续学习：
- **Go基础语法**: 变量、函数、数据类型
- **控制流程**: 条件语句、循环语句
- **数据结构**: 数组、切片、映射、结构体
- **面向对象**: Go的OOP实现方式

---

**学习提示**: Go的环境配置相比PHP更复杂一些，但一旦配置完成，后续的开发体验会非常流畅。建议花时间熟悉Go的工具链，这将大大提高你的开发效率。

*最后更新: 2025年9月*

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
