# Go 错误处理机制

> **文档简介**: 掌握Go语言的错误处理机制，学会编写健壮的错误处理代码
>
> **目标读者**: Go语言初学者，希望学习Go错误处理最佳实践的开发者
>
> **前置知识**: Go基础语法、函数基础、接口基础
>
> **预计时长**: 2-3小时学习 + 1小时实践

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/error-handling` |
| **难度** | ⭐⭐⭐ (3/5) |
| **标签** | `#错误处理` `#Go特色` `#健壮性` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

通过本章学习，您将能够：

1. **理解Go错误处理哲学**
   - 了解Go为何不使用异常
   - 掌握error接口的设计理念
   - 理解显式错误处理的优势

2. **掌握基本错误处理**
   - 创建和使用错误
   - 处理函数返回的错误
   - 使用fmt.Errorf包装错误

3. **学习高级错误处理**
   - 自定义错误类型
   - 错误链和包装
   - panic和recover的使用

## 📋 内容大纲

### 1. Go错误处理基础
- [ ] error接口介绍
- [ ] 基本错误处理模式
- [ ] 创建和返回错误
- [ ] 错误检查最佳实践

### 2. 标准库错误处理
- [ ] fmt.Errorf错误包装
- [ ] errors包的使用
- [ ] 标准库常见错误类型

### 3. 自定义错误类型
- [ ] 实现error接口
- [ ] 结构体错误类型
- [ ] 错误类型断言

### 4. 错误链和包装
- [ ] 错误包装技术
- [ ] 错误链追溯
- [ ] Unwrap方法

### 5. Panic和Recover
- [ ] panic的使用场景
- [ ] recover机制
- [ ] defer+recover模式

## 🛠️ 代码示例

### 基本错误处理
```go
package main

import (
    "errors"
    "fmt"
    "os"
)

func readFile(filename string) ([]byte, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        // 包装错误，添加上下文信息
        return nil, fmt.Errorf("failed to read file %s: %w", filename, err)
    }
    return data, nil
}

func main() {
    data, err := readFile("nonexistent.txt")
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }
    fmt.Printf("File content: %s\n", data)
}
```

### 自定义错误类型
```go
package main

import (
    "fmt"
)

// 自定义错误类型
type ValidationError struct {
    Field   string
    Message string
}

func (e ValidationError) Error() string {
    return fmt.Sprintf("validation failed for field '%s': %s", e.Field, e.Message)
}

func validateAge(age int) error {
    if age < 0 {
        return ValidationError{
            Field:   "age",
            Message: "age cannot be negative",
        }
    }
    if age > 150 {
        return ValidationError{
            Field:   "age",
            Message: "age seems unrealistic",
        }
    }
    return nil
}
```

### Panic和Recover
```go
package main

import (
    "fmt"
    "log"
)

func riskyOperation() {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("Recovered from panic: %v", r)
        }
    }()
    
    // 模拟panic
    panic("something went wrong")
}

func main() {
    fmt.Println("Starting risky operation...")
    riskyOperation()
    fmt.Println("Operation completed")
}
```

## 🎯 最佳实践

### 1. 错误处理原则
- 总是检查函数返回的错误
- 尽早处理错误，避免深层嵌套
- 使用fmt.Errorf添加上下文信息

### 2. 错误信息设计
- 错误信息要清晰明确
- 包含足够的上下文信息
- 避免暴露敏感信息

### 3. 错误分类
- 区分可恢复和不可恢复错误
- 对不同类型的错误采用不同处理策略

## 🔗 相关资源

- **深入学习**: [knowledge-points/language-concepts/03-go-programming-essentials.md](../knowledge-points/language-concepts/03-go-programming-essentials.md)
- **相关文档**: [basics/04-functions-methods.md](04-functions-methods.md)
- **实践参考**: [frameworks/01-gin-framework-basics.md](../frameworks/01-gin-framework-basics.md)

---

**更新日志**: 2025年10月 - 创建Go错误处理机制教程
