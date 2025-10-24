# 函数定义与方法调用

> **文档简介**: 全面掌握Go语言函数的定义、调用和方法的使用，理解函数与方法的概念差异和应用场景

> **目标读者**: Go初学者，需要掌握Go函数编程的学习者

> **前置知识**: 已掌握变量、常量和基础数据类型

> **预计时长**: 2-3小时学习 + 实践

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#函数` `#方法` `#参数` `#返回值` `#作用域` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

通过本文档学习，您将能够：
- 掌握Go函数的定义和调用方式
- 理解函数参数和返回值的使用
- 学会函数的作用域和变量遮蔽
- 区分函数和方法的区别
- 掌握多返回值和命名返回值

## 📝 函数基础

### 1. 函数定义语法

```go
// 基本函数定义
func functionName(parameter1 type1, parameter2 type2) returnType {
    // 函数体
    return value
}

// 无参数函数
func sayHello() {
    fmt.Println("Hello, World!")
}

// 带参数函数
func greet(name string) {
    fmt.Printf("Hello, %s!\n", name)
}

// 带返回值函数
func add(a, b int) int {
    return a + b
}
```

### 2. 函数调用

```go
package main

import "fmt"

// 定义一些示例函数
func add(a, b int) int {
    return a + b
}

func multiply(x, y float64) float64 {
    return x * y
}

func printMessage(msg string) {
    fmt.Println(msg)
}

func main() {
    // 调用无返回值函数
    printMessage("程序开始")

    // 调用有返回值函数
    sum := add(10, 20)
    fmt.Printf("10 + 20 = %d\n", sum)

    product := multiply(3.5, 2.0)
    fmt.Printf("3.5 × 2.0 = %.2f\n", product)

    // 直接使用函数返回值
    fmt.Printf("5 + 3 = %d\n", add(5, 3))

    printMessage("程序结束")
}
```

## 📊 函数参数

### 1. 值参数

```go
// 值传递 - 函数内修改不影响外部变量
func modifyValue(x int) {
    x = 100  // 只影响函数内的副本
    fmt.Printf("函数内: x = %d\n", x)
}

func main() {
    num := 10
    fmt.Printf("调用前: num = %d\n", num)
    modifyValue(num)
    fmt.Printf("调用后: num = %d\n", num)  // 仍然是10
}
```

### 2. 引用参数（指针）

```go
// 指针传递 - 可以修改外部变量
func modifyByReference(ptr *int) {
    *ptr = 100  // 修改指针指向的值
    fmt.Printf("函数内: *ptr = %d\n", *ptr)
}

func main() {
    num := 10
    fmt.Printf("调用前: num = %d\n", num)
    modifyByReference(&num)  // 传递地址
    fmt.Printf("调用后: num = %d\n", num)  // 变为100
}
```

### 3. 可变参数

```go
// 可变参数函数
func sum(numbers ...int) int {
    total := 0
    for _, num := range numbers {
        total += num
    }
    return total
}

// 混合参数
func greetAll(greeting string, names ...string) {
    for _, name := range names {
        fmt.Printf("%s, %s!\n", greeting, name)
    }
}

func main() {
    // 可变参数调用
    result1 := sum(1, 2, 3, 4, 5)
    fmt.Printf("1+2+3+4+5 = %d\n", result1)

    result2 := sum(10, 20)
    fmt.Printf("10+20 = %d\n", result2)

    // 混合参数调用
    greetAll("你好", "张三", "李四", "王五")
}
```

## 🔄 返回值

### 1. 单个返回值

```go
// 返回单个值
func getPI() float64 {
    return 3.14159
}

func isEven(num int) bool {
    return num%2 == 0
}
```

### 2. 多个返回值

```go
// 返回多个值
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("除数不能为0")
    }
    return a / b, nil
}

// 返回多个不同类型的值
func getUserInfo(id int) (string, int, bool) {
    // 模拟数据库查询
    if id == 1 {
        return "张三", 25, true
    } else if id == 2 {
        return "李四", 30, true
    }
    return "", 0, false
}

func main() {
    // 多返回值接收
    name, age, found := getUserInfo(1)
    if found {
        fmt.Printf("用户: %s, 年龄: %d\n", name, age)
    }

    // 错误处理
    result, err := divide(10, 2)
    if err != nil {
        fmt.Printf("错误: %v\n", err)
    } else {
        fmt.Printf("结果: %.2f\n", result)
    }
}
```

### 3. 命名返回值

```go
// 命名返回值 - 可以直接使用return语句
func calculate(a, b int) (sum, diff int) {
    sum = a + b
    diff = a - b
    return  // 等价于 return sum, diff
}

// 命名返回值可以在函数内直接使用
func process(name string) (result string, err error) {
    if name == "" {
        err = errors.New("姓名不能为空")
        return  // 返回空字符串和错误
    }

    result = "处理成功: " + name
    return  // 返回结果和nil错误
}

func main() {
    sum, diff := calculate(10, 3)
    fmt.Printf("和: %d, 差: %d\n", sum, diff)

    result, err := process("张三")
    if err != nil {
        fmt.Printf("错误: %v\n", err)
    } else {
        fmt.Printf("结果: %s\n", result)
    }
}
```

## 🏛️ 函数作为值

### 1. 函数类型

```go
// 定义函数类型
type Calculator func(int, int) int

// 定义函数
func add(a, b int) int {
    return a + b
}

func subtract(a, b int) int {
    return a - b
}

// 接受函数作为参数
func calculate(a, b int, op Calculator) int {
    return op(a, b)
}

func main() {
    // 将函数作为参数传递
    result1 := calculate(10, 5, add)
    fmt.Printf("10 + 5 = %d\n", result1)

    result2 := calculate(10, 5, subtract)
    fmt.Printf("10 - 5 = %d\n", result2)
}
```

### 2. 匿名函数

```go
func main() {
    // 匿名函数赋值给变量
    add := func(a, b int) int {
        return a + b
    }

    result := add(3, 4)
    fmt.Printf("3 + 4 = %d\n", result)

    // 在其他函数中使用匿名函数
    numbers := []int{1, 2, 3, 4, 5}
    filtered := filter(numbers, func(n int) bool {
        return n%2 == 0  // 只保留偶数
    })
    fmt.Printf("偶数: %v\n", filtered)
}

// 过滤函数
func filter(numbers []int, predicate func(int) bool) []int {
    var result []int
    for _, num := range numbers {
        if predicate(num) {
            result = append(result, num)
        }
    }
    return result
}
```

## 🎯 闭包

```go
// 返回函数的函数
func makeAdder(x int) func(int) int {
    return func(y int) int {
        return x + y  // 闭包：访问外部变量x
    }
}

// 计数器工厂
func makeCounter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

func main() {
    // 闭包示例1
    add5 := makeAdder(5)
    add10 := makeAdder(10)

    fmt.Printf("5 + 3 = %d\n", add5(3))   // 8
    fmt.Printf("10 + 7 = %d\n", add10(7))  // 17

    // 闭包示例2 - 计数器
    counter1 := makeCounter()
    counter2 := makeCounter()

    fmt.Printf("计数器1: %d\n", counter1())  // 1
    fmt.Printf("计数器1: %d\n", counter1())  // 2
    fmt.Printf("计数器2: %d\n", counter2())  // 1 (独立状态)
    fmt.Printf("计数器1: %d\n", counter1())  // 3
}
```

## 🔧 方法

### 1. 方法定义

方法是与特定类型关联的函数：

```go
// 定义结构体
type Rectangle struct {
    Width  float64
    Height float64
}

// 定义方法 - 值接收者
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 定义方法 - 指针接收者（可以修改结构体）
func (r *Rectangle) SetDimensions(width, height float64) {
    r.Width = width
    r.Height = height
}

func (r Rectangle) String() string {
    return fmt.Sprintf("Rectangle{Width: %.1f, Height: %.1f}", r.Width, r.Height)
}

func main() {
    // 创建结构体实例
    rect := Rectangle{Width: 10.0, Height: 5.0}

    // 调用方法
    area := rect.Area()
    fmt.Printf("面积: %.2f\n", area)

    // 调用指针接收者方法
    rect.SetDimensions(20.0, 10.0)
    area = rect.Area()
    fmt.Printf("新面积: %.2f\n", area)

    // String()方法会被fmt.Printf自动调用
    fmt.Printf("矩形: %s\n", rect)
}
```

### 2. 值接收者 vs 指针接收者

```go
type Counter struct {
    count int
}

// 值接收者方法 - 不能修改原始值
func (c Counter) Increment() {
    c.count++
    fmt.Printf("值接收者内部: %d\n", c.count)
}

// 指针接收者方法 - 可以修改原始值
func (c *Counter) IncrementPtr() {
    c.count++
    fmt.Printf("指针接收者内部: %d\n", c.count)
}

func main() {
    counter := Counter{count: 0}

    fmt.Printf("初始值: %d\n", counter.count)

    // 调用值接收者方法
    counter.Increment()
    fmt.Printf("值接收者调用后: %d\n", counter.count)  // 仍然是0

    // 调用指针接收者方法
    counter.IncrementPtr()
    fmt.Printf("指针接收者调用后: %d\n", counter.count)  // 变为1
}
```

## 🎯 实际应用示例

### 示例1: 数学工具库

```go
package main

import (
    "fmt"
    "math"
)

// 数学操作函数
func power(base, exponent float64) float64 {
    return math.Pow(base, exponent)
}

func sqrt(number float64) (float64, error) {
    if number < 0 {
        return 0, fmt.Errorf("不能计算负数的平方根")
    }
    return math.Sqrt(number), nil
}

// 批量计算函数
func batchCalculate(numbers []float64, operation func(float64) float64) []float64 {
    results := make([]float64, len(numbers))
    for i, num := range numbers {
        results[i] = operation(num)
    }
    return results
}

func main() {
    // 基本数学运算
    result := power(2, 3)
    fmt.Printf("2³ = %.0f\n", result)

    // 错误处理
    sqrtResult, err := sqrt(16)
    if err != nil {
        fmt.Printf("错误: %v\n", err)
    } else {
        fmt.Printf("√16 = %.2f\n", sqrtResult)
    }

    // 批量计算
    numbers := []float64{1, 4, 9, 16, 25}
    squareRoots := batchCalculate(numbers, math.Sqrt)
    fmt.Printf("平方根: %v\n", squareRoots)
}
```

### 示例2: 字符串处理工具

```go
package main

import (
    "fmt"
    "strings"
    "unicode"
)

// 字符串处理函数
func reverseString(s string) string {
    runes := []rune(s)
    for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
        runes[i], runes[j] = runes[j], runes[i]
    }
    return string(runes)
}

func isPalindrome(s string) bool {
    // 转换为小写并移除非字母字符
    cleaned := strings.Map(func(r rune) rune {
        if unicode.IsLetter(r) {
            return unicode.ToLower(r)
        }
        return -1
    }, s)

    return cleaned == reverseString(cleaned)
}

// 高阶函数 - 字符串处理管道
func StringPipeline(s string, operations ...func(string) string) string {
    result := s
    for _, op := range operations {
        result = op(result)
    }
    return result
}

func main() {
    // 字符串反转
    original := "Hello, World!"
    reversed := reverseString(original)
    fmt.Printf("原字符串: %s\n", original)
    fmt.Printf("反转字符串: %s\n", reversed)

    // 回文检测
    testWords := []string{"level", "hello", "racecar", "world"}
    for _, word := range testWords {
        fmt.Printf("%s 是回文: %t\n", word, isPalindrome(word))
    }

    // 字符串处理管道
    text := "  Hello, World!  "
    operations := []func(string) string{
        strings.TrimSpace,     // 移除前后空格
        strings.ToLower,       // 转小写
        strings.ReplaceAll(",", " "), // 替换逗号
    }
    processed := StringPipeline(text, operations...)
    fmt.Printf("处理后: '%s'\n", processed)
}
```

### 示例3: 验证工具

```go
package main

import (
    "fmt"
    "regexp"
    "unicode"
)

// 验证函数类型
type Validator func(string) bool

// 常用验证函数
func ValidateEmail(email string) bool {
    pattern := `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
    matched, _ := regexp.MatchString(pattern, email)
    return matched
}

func ValidatePhone(phone string) bool {
    pattern := `^1[3-9]\d{9}$`  // 简单的中国手机号验证
    matched, _ := regexp.MatchString(pattern, phone)
    return matched
}

func ValidatePassword(password string) bool {
    if len(password) < 8 {
        return false
    }

    var hasUpper, hasLower, hasDigit, hasSpecial bool
    for _, char := range password {
        switch {
        case unicode.IsUpper(char):
            hasUpper = true
        case unicode.IsLower(char):
            hasLower = true
        case unicode.IsDigit(char):
            hasDigit = true
        case unicode.IsPunct(char) || unicode.IsSymbol(char):
            hasSpecial = true
        }
    }

    return hasUpper && hasLower && hasDigit && hasSpecial
}

// 组合验证器
func ValidateAll(input string, validators ...Validator) bool {
    for _, validator := range validators {
        if !validator(input) {
            return false
        }
    }
    return true
}

func main() {
    // 单个验证
    email := "user@example.com"
    fmt.Printf("邮箱 %s 有效: %t\n", email, ValidateEmail(email))

    phone := "13812345678"
    fmt.Printf("手机号 %s 有效: %t\n", phone, ValidatePhone(phone))

    password := "SecurePass123!"
    fmt.Printf("密码强度满足要求: %t\n", ValidatePassword(password))

    // 组合验证 - 验证用户输入
    userInput := struct {
        email    string
        phone    string
        password string
    }{
        email:    "test@example.com",
        phone:    "13987654321",
        password: "MySecure123!",
    }

    isValid := ValidateAll(
        userInput.email,
        ValidateEmail,
        ValidatePhone,
        userInput.password,
        ValidatePassword,
    )

    fmt.Printf("用户输入验证: %t\n", isValid)
}
```

## 🔍 函数设计最佳实践

### 1. 单一职责原则

```go
// ✅ 好的设计 - 每个函数只做一件事
func calculateTax(income float64) float64 {
    return income * 0.2  // 简单的税收计算
}

func formatCurrency(amount float64) string {
    return fmt.Sprintf("¥%.2f", amount)
}

// ❌ 不好的设计 - 一个函数做太多事
func calculateAndFormatTax(income float64) string {
    tax := income * 0.2
    return fmt.Sprintf("¥%.2f", tax)
}
```

### 2. 纯函数

```go
// ✅ 纯函数 - 相同输入总是产生相同输出
func add(a, b int) int {
    return a + b
}

// ❌ 非纯函数 - 有副作用
func addAndPrint(a, b int) int {
    result := a + b
    fmt.Printf("结果: %d\n", result)  // 副作用
    return result
}
```

### 3. 错误处理

```go
// ✅ 好的错误处理
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("除数不能为0")
    }
    return a / b, nil
}

// 使用错误处理
result, err := divide(10, 2)
if err != nil {
    log.Printf("除法错误: %v", err)
    return
}
fmt.Printf("结果: %.2f", result)
```

## 🔗 文档交叉引用

### 相关文档
- 📄 **[第一个程序]**: [02-first-program.md](02-first-program.md) - Go程序基础结构
- 📄 **[变量和常量]**: [03-variables-constants.md](03-variables-constants.md) - Go数据类型和变量
- 📄 **[控制结构]**: [05-control-structures.md](05-control-structures.md) - 条件语句和循环

### 参考资源
- 📖 **[Go函数文档]**: https://golang.org/ref/spec#Functions
- 📖 **[Go方法文档]**: https://golang.org/ref/spec#Method_declarations
- 📖 **[Go闭包文档]**: https://golang.org/ref/spec#Function_literals

## 📝 总结

### 核心要点回顾
1. **函数定义**: 掌握函数语法和参数传递方式
2. **返回值**: 理解单返回值、多返回值和命名返回值
3. **方法使用**: 区分函数和方法，掌握接收者概念
4. **高阶函数**: 学会使用闭包和函数作为参数

### 实践练习
- [ ] 编写不同参数类型的函数
- [ ] 创建返回多个值的函数
- [ ] 实现带错误处理的函数
- [ ] 定义结构体并创建相关方法

---

**文档状态**: ✅ 已完成
**最后更新**: 2025年10月
**版本**: v1.0.0

---

> 💡 **学习建议**:
> - 多练习函数的定义和调用，熟悉Go的语法特性
> - 理解值传递和引用传递的区别，合理选择使用场景
> - 掌握Go的多返回值特性，用于替代异常处理
> - 学会使用闭包创建工厂函数和状态管理