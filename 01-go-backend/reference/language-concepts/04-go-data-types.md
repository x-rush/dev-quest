# Go 数据类型速查手册

> **文档简介**: Go语言数据类型的完整参考手册，包含基本类型、复合类型和自定义类型的快速查阅
>
> **目标读者**: Go开发者，需要快速查阅Go数据类型语法的开发者
>
> **前置知识**: Go语言基础语法
>
> **预计时长**: 30分钟速查

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/language-concepts` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#数据类型` `#语法速查` `#Go基础` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

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
slice = make([]int, 5, 10) // 长度5，容量10

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

### 函数

函数也是值，可作为参数或返回值。相同参数与返回类型组成同一种函数类型；未赋值的函数变量为 nil，调用会 panic。

```go
apply := func(x int, transform func(int) int) int { return transform(x) }
double := func(x int) int { return x * 2 }
fmt.Println(apply(3, double)) // 6；放入已导入 fmt 的 main 函数
```

### 接口

接口规定方法集合，具体类型满足集合即可隐式实现。接口值同时具有动态类型与动态值；装有 nil 指针的接口不等于 nil 接口。详见 [接口语义](13-interface-semantics.md)。

### 通道

channel 用于发送和接收有类型的值；`chan T` 可收发，`<-chan T` 只接收，`chan<- T` 只发送。方向约束表达 API 权限，不会复制底层通道。无缓冲通道需要发送与接收配对，缓冲通道满时发送阻塞；nil 通道的收发一直阻塞。关闭由负责发送生命周期的一方协调，接收方用 `value, ok := <-ch` 区分关闭后的零值。

<!-- full-library-explanation -->
## 值被复制时，哪些数据仍共享

前置是变量、赋值与函数参数。Go 的赋值和传参复制值；数组复制全部元素，切片复制描述底层存储的视图，指针复制地址。因此“传值”不能推出“修改永远互不影响”。本页原有代码是语法片段，含替代声明，不能直接串成一个 main 函数。

下面是完整程序，保存为 main.go，运行 go run main.go：

```go
package main
import "fmt"
func main() {
    a := [2]int{1, 2}
    b := a
    b[0] = 9
    s := a[:]
    s[0] = 7
    fmt.Println(a, b, s)
}
```

输出 `[7 2] [9 2] [7 2]`。b 与 a 是两个数组，s 则指向 a 的存储。练习：把 s 改为通过 make 和 copy 创建，a 应保留 `[1 2]`。另外，byte 是 uint8 别名，rune 是 int32 别名；string 存储字节，len 返回字节数，不保证等于文字数量。

## 🔗 相关资源

- **深入学习**: [basics/03-variables-constants.md](../../basics/03-variables-constants.md)
- **相关文档**: [reference/language-concepts/01-go-keywords.md](01-go-keywords.md)
- **实践参考**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)

---

**更新日志**: 2026年9月 - 创建基础数据类型速查手册


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
