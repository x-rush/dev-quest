# Go 数据类型速查手册

> **文档简介**: Go语言数据类型的完整参考手册，包含基本类型、复合类型和自定义类型的快速查阅
>
> **目标读者**: Go开发者，需要快速查阅Go数据类型语法的开发者
>
> **前置知识**: Go语言基础语法
>
> **预计时长**: 30分钟速查

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/language-concepts` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#数据类型` `#语法速查` `#Go基础` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 快速索引

### 基本数据类型
- [布尔值](#布尔值)
- [整数类型](#整数类型)
- [浮点数类型](#浮点数类型)
- [复数类型](#复数类型)
- [字符串类型](#字符串类型)

### 复合数据类型
- [数组](#数组)
- [切片](#切片)
- [映射](#映射)
- [结构体](#结构体)

### 引用类型
- [指针](#指针)
- [函数](#函数)
- [接口](#接口)
- [通道](#通道)

## 📖 基本数据类型

### 布尔值
```go
var isTrue bool = true
var isFalse bool = false
```

### 整数类型
```go
var i int     // 平台相关 (32位或64位)
var i8 int8   // 8位整数 (-128 到 127)
var i16 int16 // 16位整数 (-32768 到 32767)
var i32 int32 // 32位整数 (-2147483648 到 2147483647)
var i64 int64 // 64位整数

var u uint    // 平台相关无符号整数
var u8 uint8  // 8位无符号整数 (0 到 255)
var u16 uint16 // 16位无符号整数 (0 到 65535)
var u32 uint32 // 32位无符号整数 (0 到 4294967295)
var u64 uint64 // 64位无符号整数

var ptr uintptr // 指针大小的无符号整数
```

### 浮点数类型
```go
var f32 float32 // 32位浮点数
var f64 float64 // 64位浮点数 (默认)
```

### 复数类型
```go
var c64 complex64  // 32位实数和虚数
var c128 complex128 // 64位实数和虚数 (默认)
```

### 字符串类型
```go
var s string = "Hello, World!"
var raw string = `Raw string with
multiple lines`
```

## 📖 复合数据类型

### 数组
```go
// 固定长度的数组
var arr [5]int = [5]int{1, 2, 3, 4, 5}
var arr2 = [...]string{"a", "b", "c"} // 自动推断长度
```

### 切片
```go
// 动态长度的切片
var slice []int = []int{1, 2, 3}
slice := make([]int, 5, 10) // 长度5，容量10

// 切片操作
slice = append(slice, 4)    // 添加元素
subSlice := slice[1:3]     // 子切片
```

### 映射
```go
// 键值对集合
var m map[string]int
m = make(map[string]int)
m["key"] = 100

// 初始化时创建
m2 := map[string]int{
    "apple":  5,
    "banana": 3,
}
```

### 结构体
```go
type Person struct {
    Name string
    Age  int
    Email string
}

var p Person = Person{
    Name:  "John",
    Age:   30,
    Email: "john@example.com",
}
```

## 📖 引用类型

### 指针
```go
var x int = 42
var p *int = &x  // 指向x的指针
fmt.Println(*p) // 解引用，输出42

// 指针作为函数参数
func increment(p *int) {
    *p++
}
```

## 🔗 相关资源

- **深入学习**: [basics/03-variables-constants.md](../../basics/03-variables-constants.md)
- **相关文档**: [reference/language-concepts/01-go-keywords.md](01-go-keywords.md)
- **实践参考**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)

---

**更新日志**: 2025年10月 - 创建基础数据类型速查手册
