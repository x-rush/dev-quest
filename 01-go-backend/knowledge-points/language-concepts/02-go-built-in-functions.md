# Go内置函数详解

Go语言提供了一些内置函数，这些函数无需导入任何包就可以直接使用。内置函数在Go编程中非常重要，它们提供了语言的核心功能。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `knowledge-points/language-concepts` |
| **难度** | ⭐⭐ |
| **标签** | `#内置函数` `#基础语法` `#语言概念` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 1. append() - 切片追加

**功能**：向切片追加元素并返回新的切片

**语法**：
```go
append(slice []T, elements ...T) []T
```

**示例**：
```go
// 基本追加
numbers := []int{1, 2, 3}
numbers = append(numbers, 4, 5)       // [1 2 3 4 5]

// 追加另一个切片
moreNumbers := []int{6, 7, 8}
numbers = append(numbers, moreNumbers...) // [1 2 3 4 5 6 7 8]

// 预分配容量
data := make([]int, 0, 10)  // 长度0，容量10
data = append(data, 1, 2, 3) // [1 2 3]，容量仍为10
```

**注意事项**：
- 当容量不足时，append会自动扩容并创建新的底层数组
- 使用...操作符可以展开切片作为参数

## 2. copy() - 切片复制

**功能**：将源切片复制到目标切片，返回复制的元素数量

**语法**：
```go
copy(dst, src []T) int
```

**示例**：
```go
// 基本复制
src := []int{1, 2, 3, 4, 5}
dst := make([]int, 3)
copied := copy(dst, src) // dst = [1 2 3], copied = 3

// 复制到更大目标
dst2 := make([]int, 10)
copied2 := copy(dst2, src) // dst2 = [1 2 3 4 5 0 0 0 0 0], copied2 = 5

// 切片内容交换
a := []int{1, 2, 3}
b := []int{4, 5, 6}
copy(a, b) // a = [4 5 6]
```

## 3. len() - 长度获取

**功能**：返回各种类型的长度

**语法**：
```go
len(v Type) int
```

**示例**：
```go
// 字符串长度
str := "Hello"
fmt.Println(len(str)) // 5

// 切片长度
slice := []int{1, 2, 3}
fmt.Println(len(slice)) // 3

// 数组长度
arr := [5]int{1, 2, 3, 4, 5}
fmt.Println(len(arr)) // 5

// 映射长度
m := map[string]int{"a": 1, "b": 2}
fmt.Println(len(m)) // 2

// 通道长度
ch := make(chan int, 10)
ch <- 1
fmt.Println(len(ch)) // 1
```

## 4. cap() - 容量获取

**功能**：返回切片、数组或通道的容量

**语法**：
```go
cap(v Type) int
```

**示例**：
```go
// 切片容量
slice := make([]int, 3, 10)
fmt.Println(len(slice)) // 3
fmt.Println(cap(slice)) // 10

// 数组容量等于长度
arr := [5]int{1, 2, 3, 4, 5}
fmt.Println(cap(arr)) // 5

// 通道容量
ch := make(chan int, 10)
fmt.Println(cap(ch)) // 10
```

## 5. make() - 内存分配

**功能**：分配并初始化引用类型（切片、映射、通道）

**语法**：
```go
make(Type, size... int) Type
```

**示例**：
```go
// 创建切片
slice1 := make([]int, 5)           // [0 0 0 0 0]，长度5，容量5
slice2 := make([]int, 3, 10)       // [0 0 0]，长度3，容量10

// 创建映射
m := make(map[string]int)          // 空映射
m2 := make(map[string]int, 100)    // 预分配100个桶

// 创建通道
ch1 := make(chan int)              // 无缓冲通道
ch2 := make(chan int, 10)         // 缓冲通道，容量10
ch3 := make(chan<- int)           // 只发送通道
ch4 := make(<-chan int)           // 只接收通道
```

## 6. new() - 内存分配

**功能**：分配内存并返回指针，值初始化为零值

**语法**：
```go
new(Type) *Type
```

**示例**：
```go
// 基本类型
pInt := new(int)
fmt.Println(*pInt) // 0
*pInt = 42
fmt.Println(*pInt) // 42

// 结构体
type Person struct {
    Name string
    Age  int
}
pPerson := new(Person)
fmt.Println(*pPerson) // { 0}
(*pPerson).Name = "Alice"
pPerson.Age = 25
fmt.Println(*pPerson) // {Alice 25}

// 切片（通常使用make）
pSlice := new([]int)
*pSlice = make([]int, 3)
(*pSlice)[0] = 1
```

## 7. delete() - 映射删除

**功能**：从映射中删除指定键值对

**语法**：
```go
delete(m map[Type1]Type2, key Type1)
```

**示例**：
```go
m := map[string]int{
    "apple":  1,
    "banana": 2,
    "orange": 3,
}

// 删除存在的键
delete(m, "banana") // 删除 "banana":2
fmt.Println(m)      // map[apple:1 orange:3]

// 删除不存在的键（安全操作）
delete(m, "grape") // 不会产生错误

// 检查键是否存在再删除
if val, exists := m["apple"]; exists {
    fmt.Println("apple exists:", val)
    delete(m, "apple")
}
```

## 8. close() - 通道关闭

**功能**：关闭通道，表示不会再发送更多数据

**语法**：
```go
close(c chan<- Type)
```

**示例**：
```go
// 基本关闭
ch := make(chan int, 3)
ch <- 1
ch <- 2
close(ch)

// 接收通道数据
for value := range ch {
    fmt.Println(value) // 1, 2
}

// 检查通道是否关闭
value, ok := <-ch
if !ok {
    fmt.Println("Channel is closed")
}

// panic if close nil channel or closed channel
// close(nil)        // panic
// close(closedCh)   // panic
```

## 9. complex() / real() / imag() - 复数操作

**功能**：创建和操作复数

**语法**：
```go
complex(real, imag float64) complex128
complex(real, imag float32) complex64
real(c complexType) floatType
imag(c complexType) floatType
```

**示例**：
```go
// 创建复数
c1 := complex(3.0, 4.0)    // complex128
c2 := complex(1.5, 2.5)    // complex64
fmt.Println(c1)             // (3+4i)

// 获取实部和虚部
fmt.Println(real(c1))       // 3.0
fmt.Println(imag(c1))       // 4.0

// 数学运算
c3 := complex(1, 2)
c4 := complex(3, 4)
sum := c3 + c4              // (4+6i)
product := c3 * c4          // (-5+10i)

// 复数类型
var c5 complex64 = complex(2.5, 3.5)
var c6 complex128 = complex(1.0, 2.0)
```

## 10. panic() / recover() - 异常处理

**功能**：panic引发运行时恐慌，recover恢复恐慌

**语法**：
```go
panic(v interface{})
recover() interface{}
```

**示例**：
```go
// 基本panic
func divide(a, b int) int {
    if b == 0 {
        panic("division by zero")
    }
    return a / b
}

// recover使用
func safeDivide(a, b int) (result int, err error) {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recovered:", r)
            err = fmt.Errorf("panic occurred: %v", r)
        }
    }()

    return divide(a, b), nil
}

// 使用recover
result, err := safeDivide(10, 0)
if err != nil {
    fmt.Println("Error:", err)
}

// panic的不同类型
panic(42)                    // int
panic("error message")       // string
panic(errors.New("custom error")) // error
```

## 11. print() / println() - 调试输出

**功能**：内置的调试输出函数（不推荐生产使用）

**语法**：
```go
print(args...Type)
println(args...Type)
```

**示例**：
```go
// 基本输出
print("Hello")              // Hello
println("World")           // World + 换行

// 多参数
print("Value:", 42, "Pi:", 3.14) // Value:42Pi:3.14
println("A", "B", "C")         // A B C + 换行

// 格式化有限
name := "Alice"
age := 25
print("Name:", name, "Age:", age) // Name:AliceAge:25

// 注意：这些函数主要用于调试，生产代码应使用fmt包
```

## 12. imag() / real() - 见复数操作

已在第9节复数操作中详细介绍

## 内置函数使用最佳实践

### 1. 性能考虑
```go
// 预分配切片容量避免频繁扩容
data := make([]int, 0, 1000) // 预分配容量
for i := 0; i < 1000; i++ {
    data = append(data, i)  // 不会触发扩容
}
```

### 2. 错误处理模式
```go
// 常见的错误处理模式
func processData(data []byte) error {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("Recovered from panic: %v", r)
        }
    }()

    // 处理可能panic的代码
    if len(data) == 0 {
        return errors.New("empty data")
    }

    return nil
}
```

### 3. 通道操作模式
```go
// 安全的通道关闭模式
func worker(ch chan int) {
    defer close(ch)

    for i := 0; i < 10; i++ {
        ch <- i
    }
}

// 检查通道关闭
func receiver(ch <-chan int) {
    for {
        select {
        case value, ok := <-ch:
            if !ok {
                return // 通道已关闭
            }
            fmt.Println("Received:", value)
        }
    }
}
```

## 内置函数总结表

| 函数 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| append() | 切片追加 | slice, elements... | []T |
| copy() | 切片复制 | dst, src | int |
| len() | 获取长度 | v Type | int |
| cap() | 获取容量 | v Type | int |
| make() | 分配引用类型 | Type, size... | Type |
| new() | 分配内存返回指针 | Type | *Type |
| delete() | 删除映射元素 | map, key | - |
| close() | 关闭通道 | chan<- Type | - |
| complex() | 创建复数 | real, imag | complexType |
| real() | 获取实部 | complexType | floatType |
| imag() | 获取虚部 | complexType | floatType |
| panic() | 引发恐慌 | v interface{} | - |
| recover() | 恢复恐慌 | - | interface{} |
| print() | 调试输出 | args... | - |
| println() | 调试输出+换行 | args... | - |

记住：
- 内置函数是Go语言的核心组成部分
- 理解内置函数的工作原理对编写高效的Go代码很重要
- 在生产代码中推荐使用fmt包而不是print/println
- 善用内置函数可以编写更简洁、更高效的Go代码