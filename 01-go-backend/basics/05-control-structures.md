# Go 控制流程详解 - 从PHP视角理解

## 📚 概述

Go的控制流程结构比PHP更简洁，但提供了强大的控制能力。作为PHP开发者，理解Go的控制流程差异对于编写高效的Go代码至关重要。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐⭐ |
| **标签** | `#控制流程` `#条件语句` `#循环` `#错误处理` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

### 🎯 学习目标
- 掌握Go的条件语句和循环语句
- 理解Go的switch语句和延迟调用
- 学会Go的错误处理模式
- 熟悉Go的控制流程与PHP的差异

## 🔄 Go vs PHP 控制流程对比

### 条件语句对比

#### PHP 条件语句
```php
<?php
// if-else语句
$age = 25;
if ($age >= 18) {
    echo "成年人";
} elseif ($age >= 13) {
    echo "青少年";
} else {
    echo "儿童";
}

// 三元运算符
$status = $age >= 18 ? "成年" : "未成年";

// switch语句
$day = "Monday";
switch ($day) {
    case "Monday":
        echo "星期一";
        break;
    case "Tuesday":
        echo "星期二";
        break;
    default:
        echo "其他";
}
```

#### Go 条件语句
```go
// if-else语句
age := 25
if age >= 18 {
    fmt.Println("成年人")
} else if age >= 13 {
    fmt.Println("青少年")
} else {
    fmt.Println("儿童")
}

// if语句中的变量声明
if userAge := getUserAge(); userAge >= 18 {
    fmt.Println("成年人")
}

// switch语句
day := "Monday"
switch day {
case "Monday":
    fmt.Println("星期一")
case "Tuesday":
    fmt.Println("星期二")
default:
    fmt.Println("其他")
}

// switch without condition (替代长if-else链)
score := 85
switch {
case score >= 90:
    fmt.Println("优秀")
case score >= 80:
    fmt.Println("良好")
case score >= 60:
    fmt.Println("及格")
default:
    fmt.Println("不及格")
}
```

### 循环语句对比

#### PHP 循环语句
```php
<?php
// for循环
for ($i = 0; $i < 5; $i++) {
    echo $i;
}

// while循环
$count = 0;
while ($count < 5) {
    echo $count;
    $count++;
}

// do-while循环
$count = 0;
do {
    echo $count;
    $count++;
} while ($count < 5);

// foreach循环
$fruits = ["苹果", "香蕉", "橙子"];
foreach ($fruits as $fruit) {
    echo $fruit;
}

foreach ($fruits as $index => $fruit) {
    echo $index . ": " . $fruit;
}
```

#### Go 循环语句
```go
// for循环 (Go中只有for循环)
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

// while风格的for循环
count := 0
for count < 5 {
    fmt.Println(count)
    count++
}

// 无限循环
for {
    fmt.Println("无限循环")
    if someCondition() {
        break
    }
}

// range遍历
fruits := []string{"苹果", "香蕉", "橙子"}
for index, fruit := range fruits {
    fmt.Printf("%d: %s\n", index, fruit)
}

// 遍历映射
person := map[string]interface{}{
    "name": "张三",
    "age":  25,
}
for key, value := range person {
    fmt.Printf("%s: %v\n", key, value)
}

// 遍历字符串 (Unicode字符)
for index, char := range "你好" {
    fmt.Printf("%d: %c\n", index, char)
}
```

## 📝 Go 控制流程详解

### 1. 条件语句

#### if-else 语句
```go
// 基本if-else
age := 25
if age >= 18 {
    fmt.Println("成年人")
} else {
    fmt.Println("未成年")
}

// if-else if-else
score := 85
if score >= 90 {
    fmt.Println("优秀")
} else if score >= 80 {
    fmt.Println("良好")
} else if score >= 60 {
    fmt.Println("及格")
} else {
    fmt.Println("不及格")
}

// if语句中的变量声明
if user, err := getUser(); err == nil {
    fmt.Printf("用户: %s\n", user.Name)
} else {
    fmt.Printf("获取用户失败: %v\n", err)
}

// 嵌套if
if age >= 18 {
    if hasLicense := checkDriverLicense(); hasLicense {
        fmt.Println("可以开车")
    } else {
        fmt.Println("需要驾照")
    }
}
```

#### switch 语句
```go
// 基本switch
day := "Monday"
switch day {
case "Monday":
    fmt.Println("星期一")
case "Tuesday":
    fmt.Println("星期二")
case "Wednesday":
    fmt.Println("星期三")
default:
    fmt.Println("其他")
}

// 多值匹配
day := "Monday"
switch day {
case "Monday", "Tuesday", "Wednesday", "Thursday", "Friday":
    fmt.Println("工作日")
case "Saturday", "Sunday":
    fmt.Println("周末")
default:
    fmt.Println("未知")
}

// 条件switch
score := 85
switch {
case score >= 90:
    fmt.Println("优秀")
    fallthrough // 继续执行下一个case
case score >= 80:
    fmt.Println("良好")
case score >= 60:
    fmt.Println("及格")
default:
    fmt.Println("不及格")
}

// 类型switch
var value interface{} = "hello"
switch v := value.(type) {
case string:
    fmt.Printf("字符串: %s\n", v)
case int:
    fmt.Printf("整数: %d\n", v)
case bool:
    fmt.Printf("布尔值: %t\n", v)
default:
    fmt.Printf("未知类型: %T\n", v)
}
```

### 2. 循环语句

#### for 循环
```go
// 标准for循环
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

// 省略init语句
i := 0
for ; i < 5; i++ {
    fmt.Println(i)
}

// 省略post语句
for i := 0; i < 5; {
    fmt.Println(i)
    i++
}

// 省略init和post语句 (while循环)
i := 0
for i < 5 {
    fmt.Println(i)
    i++
}

// 无限循环
for {
    fmt.Println("无限循环")
    if shouldBreak() {
        break
    }
}
```

#### range 循环
```go
// 遍历切片
numbers := []int{1, 2, 3, 4, 5}
for index, value := range numbers {
    fmt.Printf("索引 %d: 值 %d\n", index, value)
}

// 遍历映射
person := map[string]interface{}{
    "name": "张三",
    "age":  25,
    "email": "zhangsan@example.com",
}
for key, value := range person {
    fmt.Printf("%s: %v\n", key, value)
}

// 遍历字符串 (Unicode)
text := "Hello, 世界"
for index, char := range text {
    fmt.Printf("索引 %d: 字符 %c\n", index, char)
}

// 遍历通道
ch := make(chan int)
go func() {
    ch <- 1
    ch <- 2
    ch <- 3
    close(ch)
}()

for value := range ch {
    fmt.Println(value)
}
```

#### 循环控制
```go
// break语句
for i := 0; i < 10; i++ {
    if i == 5 {
        break // 跳出循环
    }
    fmt.Println(i)
}

// continue语句
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue // 跳过当前迭代
    }
    fmt.Println(i)
}

// 带标签的break
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == 1 && j == 1 {
            break outer // 跳出外层循环
        }
        fmt.Printf("%d, %d\n", i, j)
    }
}

// 带标签的continue
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if j == 1 {
            continue outer // 继续外层循环的下一次迭代
        }
        fmt.Printf("%d, %d\n", i, j)
    }
}
```

### 3. 延迟调用 (defer)

#### defer 基础
```go
// defer语句会在函数返回前执行
func example() {
    defer fmt.Println("第一条defer语句")
    defer fmt.Println("第二条defer语句")
    defer fmt.Println("第三条defer语句")

    fmt.Println("函数主体")
}

// 输出顺序:
// 函数主体
// 第三条defer语句
// 第二条defer语句
// 第一条defer语句
```

#### defer 实际应用
```go
// 文件操作
func readFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close() // 确保文件关闭

    // 读取文件内容
    data, err := ioutil.ReadAll(file)
    if err != nil {
        return err
    }

    fmt.Printf("文件内容: %s\n", string(data))
    return nil
}

// 数据库连接
func processUser(userID int) error {
    db, err := sql.Open("mysql", "user:password@/dbname")
    if err != nil {
        return err
    }
    defer db.Close()

    // 执行查询
    row := db.QueryRow("SELECT name, email FROM users WHERE id = ?", userID)
    var name, email string
    err = row.Scan(&name, &email)
    if err != nil {
        return err
    }

    fmt.Printf("用户: %s, 邮箱: %s\n", name, email)
    return nil
}

// HTTP请求
func fetchAPI(url string) error {
    resp, err := http.Get(url)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("HTTP请求失败: %s", resp.Status)
    }

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        return err
    }

    fmt.Printf("API响应: %s\n", string(body))
    return nil
}
```

### 4. 错误处理

#### Go错误处理模式
```go
// 基本错误处理
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("除数不能为零")
    }
    return a / b, nil
}

// 使用函数
func main() {
    result, err := divide(10, 2)
    if err != nil {
        fmt.Printf("错误: %v\n", err)
        return
    }
    fmt.Printf("结果: %f\n", result)

    // 错误处理
    result, err = divide(10, 0)
    if err != nil {
        fmt.Printf("错误: %v\n", err)
        return
    }
    fmt.Printf("结果: %f\n", result)
}

// 自定义错误类型
type DivisionError struct {
    Dividend float64
    Divisor  float64
    Message  string
}

func (e *DivisionError) Error() string {
    return fmt.Sprintf("除法错误: %s (被除数: %.2f, 除数: %.2f)",
        e.Message, e.Dividend, e.Divisor)
}

func divideWithError(a, b float64) (float64, error) {
    if b == 0 {
        return 0, &DivisionError{
            Dividend: a,
            Divisor:  b,
            Message:  "除数不能为零",
        }
    }
    return a / b, nil
}

// 错误包装
func processData(data string) error {
    if len(data) == 0 {
        return fmt.Errorf("processData failed: %w",
            fmt.Errorf("empty data provided"))
    }
    // 处理数据...
    return nil
}

// panic和recover
func riskyOperation() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Printf("捕获到panic: %v\n", r)
        }
    }()

    // 可能导致panic的代码
    panic("这是一个panic")
}
```

## 🧪 实践练习

### 练习1: 条件语句和循环
```go
package main

import "fmt"

func main() {
    // 1. 判断成绩等级
    score := 85
    var grade string

    switch {
    case score >= 90:
        grade = "优秀"
    case score >= 80:
        grade = "良好"
    case score >= 60:
        grade = "及格"
    default:
        grade = "不及格"
    }

    fmt.Printf("成绩 %d 对应等级: %s\n", score, grade)

    // 2. 循环输出1-100的奇数
    fmt.Println("1-100的奇数:")
    for i := 1; i <= 100; i += 2 {
        fmt.Printf("%d ", i)
    }
    fmt.Println()

    // 3. 遍历切片
    fruits := []string{"苹果", "香蕉", "橙子", "葡萄"}
    for index, fruit := range fruits {
        fmt.Printf("%d: %s\n", index, fruit)
    }
}
```

### 练习2: defer和错误处理
```go
package main

import (
    "fmt"
    "os"
)

func processFile(filename string) error {
    // 打开文件
    file, err := os.Open(filename)
    if err != nil {
        return fmt.Errorf("无法打开文件: %w", err)
    }
    defer file.Close()

    // 检查文件是否存在
    if _, err := os.Stat(filename); os.IsNotExist(err) {
        return fmt.Errorf("文件不存在: %s", filename)
    }

    // 读取文件信息
    fileInfo, err := file.Stat()
    if err != nil {
        return fmt.Errorf("无法获取文件信息: %w", err)
    }

    fmt.Printf("文件名: %s\n", fileInfo.Name())
    fmt.Printf("文件大小: %d 字节\n", fileInfo.Size())
    fmt.Printf("文件权限: %v\n", fileInfo.Mode())

    return nil
}

func main() {
    filename := "example.txt"

    err := processFile(filename)
    if err != nil {
        fmt.Printf("处理文件失败: %v\n", err)
    } else {
        fmt.Println("文件处理成功")
    }
}
```

### 练习3: 复杂的控制流
```go
package main

import "fmt"

// 斐波那契数列
func fibonacci(n int) []int {
    if n <= 0 {
        return []int{}
    }

    fib := make([]int, n)
    fib[0] = 0
    if n > 1 {
        fib[1] = 1
    }

    for i := 2; i < n; i++ {
        fib[i] = fib[i-1] + fib[i-2]
    }

    return fib
}

// 判断质数
func isPrime(num int) bool {
    if num <= 1 {
        return false
    }
    if num == 2 {
        return true
    }
    if num%2 == 0 {
        return false
    }

    for i := 3; i*i <= num; i += 2 {
        if num%i == 0 {
            return false
        }
    }

    return true
}

func main() {
    // 1. 斐波那契数列
    fmt.Println("斐波那契数列前10项:")
    fib := fibonacci(10)
    for i, num := range fib {
        fmt.Printf("F(%d) = %d\n", i, num)
    }

    // 2. 找出1-100的质数
    fmt.Println("\n1-100的质数:")
    for i := 1; i <= 100; i++ {
        if isPrime(i) {
            fmt.Printf("%d ", i)
        }
    }
    fmt.Println()

    // 3. 九九乘法表
    fmt.Println("\n九九乘法表:")
    for i := 1; i <= 9; i++ {
        for j := 1; j <= i; j++ {
            fmt.Printf("%d×%d=%-2d ", j, i, i*j)
        }
        fmt.Println()
    }
}
```

## 📋 检查清单

- [ ] 掌握Go的if-else条件语句
- [ ] 理解Go的switch语句和类型switch
- [ ] 学会Go的for循环的各种形式
- [ ] 掌握range循环的使用方法
- [ ] 理解defer语句的执行机制
- [ ] 学会Go的错误处理模式
- [ ] 掌握panic和recover的使用
- [ ] 理解Go控制流程与PHP的差异

## 🚀 下一步

掌握控制流程后，你可以继续学习：
- **面向对象编程**: Go的OOP实现方式
- **并发编程**: Goroutine和Channel
- **标准库**: 常用包的使用方法
- **Web开发**: Gin框架和REST API

---

**学习提示**: Go的控制流程虽然比PHP简洁，但提供了更强大的控制能力。特别是defer语句和错误处理模式，是Go编程的重要组成部分。多练习这些特性，你会发现Go代码的可读性和可维护性都很高。

*最后更新: 2025年9月*