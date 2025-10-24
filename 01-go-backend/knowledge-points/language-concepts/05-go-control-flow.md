# Go 控制流程速查手册

> **文档简介**: Go语言控制流程的完整参考手册，包含条件语句、循环、跳转语句的快速查阅
>
> **目标读者**: Go开发者，需要快速查阅Go控制流程语法的开发者
>
> **前置知识**: Go语言基础语法、数据类型
>
> **预计时长**: 30分钟速查

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `knowledge-points/language-concepts` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#控制流程` `#语法速查` `#条件语句` `#循环` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 快速索引

### 条件语句
- [if语句](#if语句)
- [switch语句](#switch语句)
- [类型断言](#类型断言)

### 循环语句
- [for循环](#for循环)
- [range循环](#range循环)
- [循环控制](#循环控制)

### 跳转语句
- [break](#break)
- [continue](#continue)
- [goto](#goto)
- [defer](#defer)

## 📖 条件语句

### if语句
```go
// 基本if语句
if x > 10 {
    fmt.Println("x is greater than 10")
}

// if-else语句
if x > 10 {
    fmt.Println("greater")
} else {
    fmt.Println("less or equal")
}

// if-else if-else语句
if x > 100 {
    fmt.Println("very large")
} else if x > 10 {
    fmt.Println("large")
} else {
    fmt.Println("small")
}

// 带初始化的if语句
if y := x * 2; y > 50 {
    fmt.Println("y is large:", y)
}
```

### switch语句
```go
// 基本switch
switch day {
case "Monday":
    fmt.Println("Start of week")
case "Friday":
    fmt.Println("End of week")
default:
    fmt.Println("Middle of week")
}

// switch表达式
switch {
case x < 0:
    fmt.Println("negative")
case x == 0:
    fmt.Println("zero")
case x > 0:
    fmt.Println("positive")
}

// 多个case值
switch grade {
case "A", "B":
    fmt.Println("Excellent")
case "C":
    fmt.Println("Good")
default:
    fmt.Println("Need improvement")
}
```

## 📖 循环语句

### for循环
```go
// 基本for循环
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// 类似while循环
for x < 100 {
    x *= 2
}

// 无限循环
for {
    if condition {
        break
    }
}
```

### range循环
```go
// 遍历切片
nums := []int{1, 2, 3, 4, 5}
for i, num := range nums {
    fmt.Printf("Index: %d, Value: %d\n", i, num)
}

// 遍历映射
m := map[string]int{"a": 1, "b": 2}
for key, value := range m {
    fmt.Printf("Key: %s, Value: %d\n", key, value)
}

// 遍历字符串
for i, char := range "hello" {
    fmt.Printf("Index: %d, Char: %c\n", i, char)
}
```

## 📖 跳转语句

### break
```go
// 跳出循环
for i := 0; i < 10; i++ {
    if i == 5 {
        break
    }
    fmt.Println(i)
}

// 跳出switch
switch x {
case 1:
    fmt.Println("one")
    break
case 2:
    fmt.Println("two")
    break
}
```

### continue
```go
// 跳过当前迭代
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue
    }
    fmt.Println(i) // 只打印奇数
}
```

### defer
```go
// 延迟执行函数
func readFile() {
    file, err := os.Open("test.txt")
    if err != nil {
        return
    }
    defer file.Close() // 函数结束时执行
    
    // 使用文件...
}
```

## 🔗 相关资源

- **深入学习**: [basics/05-control-structures.md](../../basics/05-control-structures.md)
- **相关文档**: [knowledge-points/language-concepts/04-go-data-types.md](04-go-data-types.md)
- **实践参考**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)

---

**更新日志**: 2025年10月 - 创建控制流程速查手册
