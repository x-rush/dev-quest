# Go语言25个关键字详解

## 概述
Go语言共有25个关键字，这些关键字都是预定义的保留字，不能用作标识符（变量名、函数名等）。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `knowledge-points/language-concepts` |
| **难度** | ⭐⭐ |
| **标签** | `#关键字` `#语法基础` `#语言概念` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 1. var - 变量声明

### 描述
`var`用于声明变量，可以指定类型或让编译器推断类型。

### 语法和示例
```go
// 基本声明
var name string = "John"
var age int = 25
var isActive bool = true

// 类型推断
var city = "Beijing"        // 自动推断为string
var salary = 50000.50        // 自动推断为float64

// 批量声明
var (
    username string
    email    string
    age      int
    active   bool
)

// 函数内部声明
func main() {
    var message string = "Hello, World!"
    var count = 10
    println(message, count)
}
```

## 2. const - 常量声明

### 描述
`const`用于声明常量，常量的值在编译时确定，运行时不能修改。

### 语法和示例
```go
// 基本常量
const PI = 3.14159
const AppName = "MyApp"
const MaxUsers = 1000

// 批量常量声明
const (
    StatusActive   = 1
    StatusInactive = 0
    StatusPending  = 2
)

// 枚举常量 (iota)
const (
    Sunday = iota    // 0
    Monday           // 1
    Tuesday          // 2
    Wednesday        // 3
    Thursday         // 4
    Friday           // 5
    Saturday         // 6
)

// 带表达式的常量
const (
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024
)
```

## 3. func - 函数声明

### 描述
`func`用于声明函数，Go语言是一等公民函数。

### 语法和示例
```go
// 基本函数
func add(a int, b int) int {
    return a + b
}

// 多返回值函数
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// 命名返回值
func calculateRectangle(width, height float64) (area float64, perimeter float64) {
    area = width * height
    perimeter = 2 * (width + height)
    return
}

// 函数作为参数
func processNumbers(numbers []int, processor func(int) int) []int {
    result := make([]int, len(numbers))
    for i, num := range numbers {
        result[i] = processor(num)
    }
    return result
}

// 闭包函数
func multiplier(factor int) func(int) int {
    return func(x int) int {
        return x * factor
    }
}

// 使用示例
func main() {
    double := multiplier(2)
    triple := multiplier(3)

    println(double(5))  // 10
    println(triple(5))  // 15
}
```

## 4. package - 包声明

### 描述
`package`用于声明包，每个Go文件都必须以包声明开始。

### 语法和示例
```go
// main包是程序的入口点
package main

// 自定义包
package utils
package models
package controllers

// 子包
package database/mysql
package api/v1
```

## 5. import - 导入包

### 描述
`import`用于导入其他包的功能。

### 语法和示例
```go
// 基本导入
import "fmt"
import "math"

// 分组导入
import (
    "fmt"
    "math"
    "strings"
    "net/http"
)

// 别名导入
import (
    str "strings"        // 给strings起别名str
    httpclient "net/http" // 给net/http起别名httpclient
)

// 相对导入 (Go 1.22+)
import (
    "./utils"
    "../models"
    "./internal/config"
)

// 忽略导入 (只执行init函数)
import _ "database/sql"

// 点导入 (导入所有公开成员，不推荐)
import . "fmt"

func main() {
    Println("Hello") // 不需要fmt.Println
}
```

## 6. if - 条件语句

### 描述
`if`用于条件判断，可以包含初始化语句。

### 语法和示例
```go
// 基本if
if age >= 18 {
    println("Adult")
}

// if-else
if age >= 18 {
    println("Adult")
} else {
    println("Minor")
}

// if-else if-else
if score >= 90 {
    println("A")
} else if score >= 80 {
    println("B")
} else if score >= 70 {
    println("C")
} else {
    println("F")
}

// 带初始化语句的if
if value, err := someFunction(); err != nil {
    println("Error:", err)
} else {
    println("Value:", value)
}

// 复杂条件
if (age >= 18 && hasID) || (age >= 16 && hasParentalConsent) {
    println("Can register")
}
```

## 7. else - 条件语句

### 描述
`else`与`if`配合使用，处理条件不满足的情况。

### 语法和示例
```go
// 基本else
if condition {
    // true分支
} else {
    // false分支
}

// if-else if-else链
if score >= 90 {
    grade = "A"
} else if score >= 80 {
    grade = "B"
} else if score >= 70 {
    grade = "C"
} else {
    grade = "F"
}
```

## 8. for - 循环语句

### 描述
`for`是Go语言唯一的循环语句，有多种使用方式。

### 语法和示例
```go
// 基本for循环
for i := 0; i < 10; i++ {
    println(i)
}

// 类似while的for循环
i := 0
for i < 10 {
    println(i)
    i++
}

// 无限循环
for {
    println("This will run forever")
    // break 或 return 来退出
}

// for-range遍历数组/切片
numbers := []int{1, 2, 3, 4, 5}
for index, value := range numbers {
    println(index, value)
}

// for-range遍历map
person := map[string]string{
    "name": "John",
    "age":  "25",
}
for key, value := range person {
    println(key, value)
}

// for-range遍历字符串
for index, char := range "Hello" {
    println(index, char)
}

// for-range遍历通道
ch := make(chan int, 3)
ch <- 1
ch <- 2
ch <- 3
close(ch)

for value := range ch {
    println(value)
}
```

## 9. switch - 选择语句

### 描述
`switch`提供多路分支，比多个if-else更清晰。

### 语法和示例
```go
// 基本switch
day := "Monday"
switch day {
case "Monday":
    println("Work day")
case "Saturday", "Sunday":
    println("Weekend")
default:
    println("Unknown day")
}

// switch表达式 (Go 1.22+)
message := switch score {
case 90, 100:
    "Excellent"
case 80, 89:
    "Good"
case 70, 79:
    "Fair"
default:
    "Need improvement"
}

// 无表达式的switch
switch {
case score >= 90:
    grade = "A"
case score >= 80:
    grade = "B"
case score >= 70:
    grade = "C"
default:
    grade = "F"
}

// fallthrough关键字
switch i {
case 1:
    println("1")
    fallthrough
case 2:
    println("2") // 会执行，因为fallthrough
default:
    println("default")
}

// 类型switch
var i interface{} = "hello"
switch v := i.(type) {
case int:
    println("Integer:", v)
case string:
    println("String:", v)
case bool:
    println("Boolean:", v)
default:
    println("Unknown type")
}
```

## 10. case - switch分支

### 描述
`case`用于定义`switch`语句的分支条件。

### 语法和示例
```go
// 单值case
switch day {
case "Monday":
    println("Monday")
}

// 多值case
switch day {
case "Monday", "Tuesday", "Wednesday", "Thursday", "Friday":
    println("Weekday")
case "Saturday", "Sunday":
    println("Weekend")
}

// 表达式case
switch x {
case 1, 2, 3:
    println("Small number")
case 4, 5, 6:
    println("Medium number")
default:
    println("Large number")
}
```

## 11. default - 默认分支

### 描述
`default`用于`switch`语句中的默认分支。

### 语法和示例
```go
switch day {
case "Monday", "Tuesday", "Wednesday", "Thursday", "Friday":
    println("Weekday")
case "Saturday", "Sunday":
    println("Weekend")
default:
    println("Invalid day")
}

// 类型switch中的default
switch v := i.(type) {
case int:
    println("Integer")
case string:
    println("String")
default:
    println("Other type")
}
```

## 12. break - 跳出循环

### 描述
`break`用于立即跳出循环或switch语句。

### 语法和示例
```go
// 跳出for循环
for i := 0; i < 10; i++ {
    if i == 5 {
        break
    }
    println(i)
}
// 输出: 0 1 2 3 4

// 跳出switch
switch x {
case 1:
    println("One")
    if someCondition {
        break
    }
    println("This won't execute if break happens")
}

// 带标签的break
OuterLoop:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == 1 && j == 1 {
            break OuterLoop
        }
        println(i, j)
    }
}
```

## 13. continue - 跳过本次循环

### 描述
`continue`用于跳过当前循环迭代，继续下一次迭代。

### 语法和示例
```go
// 基本continue
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue
    }
    println(i) // 只输出奇数
}

// 带标签的continue
OuterLoop:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == 1 && j == 1 {
            continue OuterLoop
        }
        println(i, j)
    }
}
```

## 14. return - 返回值

### 描述
`return`用于从函数返回值或提前结束函数执行。

### 语法和示例
```go
// 返回单个值
func add(a, b int) int {
    return a + b
}

// 返回多个值
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// 提前返回
func process(data []int) error {
    if len(data) == 0 {
        return errors.New("empty data")
    }

    // 处理数据
    for _, item := range data {
        if item < 0 {
            return errors.New("negative value found")
        }
    }

    return nil
}

// 命名返回值的return
func calculate(a, b int) (sum int, product int) {
    sum = a + b
    product = a * b
    return // 自动返回sum和product
}

// defer中的return
func example() (result int) {
    defer func() {
        result *= 2 // 会在return后执行
    }()
    return 5 // 最终返回10
}
```

## 15. defer - 延迟执行

### 描述
`defer`用于延迟函数的执行，通常用于资源清理。

### 语法和示例
```go
// 基本defer
func readFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close() // 函数返回前执行

    // 读取文件内容
    return nil
}

// 多个defer的执行顺序 (LIFO)
func example() {
    defer println("Third")
    defer println("Second")
    defer println("First")
}
// 输出: First, Second, Third

// defer与return的交互
func deferExample() int {
    result := 1

    defer func() {
        result *= 2
    }()

    return result // 返回2
}

// defer与闭包
func deferWithClosure(x int) int {
    defer func() {
        println(x) // 10
    }()

    x = 10
    return x
}

// defer在错误处理中的应用
func transactionExample() error {
    tx, err := db.Begin()
    if err != nil {
        return err
    }
    defer func() {
        if err != nil {
            tx.Rollback()
        } else {
            tx.Commit()
        }
    }()

    // 执行事务操作
    if err = tx.Exec("INSERT INTO..."); err != nil {
        return err
    }

    return nil
}
```

## 16. go - 启动goroutine

### 描述
`go`用于启动一个新的goroutine（轻量级线程）。

### 语法和示例
```go
// 基本goroutine
func sayHello() {
    println("Hello from goroutine")
}

func main() {
    go sayHello() // 启动goroutine
    println("Hello from main")

    // 等待goroutine完成
    time.Sleep(1 * time.Second)
}

// 匿名函数goroutine
func main() {
    go func() {
        println("Anonymous goroutine")
    }()

    // 带参数的goroutine
    go func(msg string) {
        println(msg)
    }("Hello from parameterized goroutine")

    time.Sleep(1 * time.Second)
}

// 多个goroutine
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        println("worker", id, "processing job", j)
        time.Sleep(time.Second)
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动3个worker goroutines
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    // 发送5个jobs
    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)

    // 收集results
    for a := 1; a <= 5; a++ {
        <-results
    }
}
```

## 17. select - 多路复用

### 描述
`select`用于等待多个通道操作，类似于switch语句。

### 语法和示例
```go
// 基本select
func example1() {
    ch1 := make(chan int)
    ch2 := make(chan int)

    go func() {
        time.Sleep(1 * time.Second)
        ch1 <- 1
    }()

    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- 2
    }()

    select {
    case msg1 := <-ch1:
        println("Received from ch1:", msg1)
    case msg2 := <-ch2:
        println("Received from ch2:", msg2)
    }
}

// 带超时的select
func example2() {
    ch := make(chan int)

    select {
    case msg := <-ch:
        println("Received:", msg)
    case <-time.After(3 * time.Second):
        println("Timeout after 3 seconds")
    }
}

// 非阻塞select
func example3() {
    ch := make(chan int)

    select {
    case msg := <-ch:
        println("Received:", msg)
    default:
        println("No message received")
    }
}

// 多个case的select
func example4() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() { ch1 <- "one" }()
    go func() { ch2 <- "two" }()

    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            println("Received ch1:", msg1)
        case msg2 := <-ch2:
            println("Received ch2:", msg2)
        }
    }
}

// 关闭通道的select
func example5() {
    ch := make(chan int)
    close(ch)

    select {
    case value, ok := <-ch:
        if ok {
            println("Received:", value)
        } else {
            println("Channel closed")
        }
    default:
        println("No data available")
    }
}
```

## 18. struct - 结构体定义

### 描述
`struct`用于定义结构体类型，是Go中实现复杂数据结构的方式。

### 语法和示例
```go
// 基本结构体
type Person struct {
    Name string
    Age  int
    Email string
}

// 嵌套结构体
type Address struct {
    Street  string
    City    string
    Country string
}

type Person struct {
    Name    string
    Age     int
    Address Address // 嵌套结构体
}

// 匿名字段嵌入
type Employee struct {
    Person  // 嵌入Person结构体
    Position string
    Salary   float64
}

// 带标签的结构体
type User struct {
    ID        int    `json:"id"`
    Name      string `json:"name" validate:"required"`
    Email     string `json:"email" validate:"email"`
    CreatedAt time.Time `json:"created_at"`
}

// 结构体方法
func (p Person) Greet() string {
    return fmt.Sprintf("Hello, my name is %s", p.Name)
}

func (p *Person) SetAge(age int) {
    p.Age = age
}

// 结构体使用示例
func main() {
    // 创建结构体实例
    person1 := Person{
        Name: "John",
        Age:  30,
        Email: "john@example.com",
    }

    // 使用new关键字
    person2 := new(Person)
    person2.Name = "Alice"
    person2.Age = 25

    // 嵌套结构体
    person3 := Person{
        Name: "Bob",
        Age:  35,
        Address: Address{
            Street:  "123 Main St",
            City:    "New York",
            Country: "USA",
        },
    }

    // 嵌入结构体
    emp := Employee{
        Person: Person{
            Name: "Charlie",
            Age:  28,
        },
        Position: "Developer",
        Salary:   75000.00,
    }

    // 调用方法
    println(person1.Greet())
    person1.SetAge(31)

    // 访问嵌入字段
    println(emp.Name) // 直接访问Person的Name字段
}
```

## 19. interface - 接口定义

### 描述
`interface`用于定义接口，Go中的接口是隐式实现的。

### 语法和示例
```go
// 基本接口
type Writer interface {
    Write([]byte) (int, error)
}

type Reader interface {
    Read([]byte) (int, error)
}

// 组合接口
type ReadWriter interface {
    Reader
    Writer
}

// 空接口 (任何类型都实现了空接口)
type EmptyInterface interface{}

// 带方法的接口
type Shape interface {
    Area() float64
    Perimeter() float64
}

// 接口实现 (隐式)
type Rectangle struct {
    Width  float64
    Height float64
}

func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

// 接口使用示例
func printShapeInfo(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\n", s.Area(), s.Perimeter())
}

func main() {
    rect := Rectangle{Width: 10, Height: 5}
    circle := Circle{Radius: 7}

    printShapeInfo(rect)
    printShapeInfo(circle)

    // 类型断言
    var i interface{} = "hello"
    if str, ok := i.(string); ok {
        println("String value:", str)
    }

    // 类型switch
    switch v := i.(type) {
    case string:
        println("String:", v)
    case int:
        println("Integer:", v)
    default:
        println("Unknown type")
    }
}
```

## 20. type - 类型定义

### 描述
`type`用于定义新类型或类型别名。

### 语法和示例
```go
// 定义新类型
type ID int
type Name string
type Age int

// 定义函数类型
type Processor func(int) int
type Validator func(string) bool

// 定义结构体类型
type Person struct {
    Name string
    Age  int
}

// 定义接口类型
type Writer interface {
    Write([]byte) (int, error)
}

// 定义通道类型
type MessageChannel chan string

// 定义map类型
type StringMap map[string]string

// 定义slice类型
type IntSlice []int

// 类型别名 (Go 1.9+)
type ByteString = []byte

// 带方法的类型
type Meter float64

func (m Meter) Feet() float64 {
    return float64(m) * 3.28084
}

func (m Meter) String() string {
    return fmt.Sprintf("%.2fm", m)
}

// 使用示例
func main() {
    var id ID = 123
    var name Name = "John"
    var age Age = 25

    var processor Processor = func(x int) int {
        return x * 2
    }

    var validator Validator = func(s string) bool {
        return len(s) > 0
    }

    var distance Meter = 5.5
    println(distance.Feet()) // 18.04462
    println(distance.String()) // 5.50m

    // 类型检查
    if validator(string(name)) {
        println("Valid name")
    }

    result := processor(int(id))
    println("Processed:", result)
}
```

## 21. map - 映射类型

### 描述
`map`是Go中的内置映射类型，类似于其他语言的字典或哈希表。

### 语法和示例
```go
// 基本map声明和使用
func basicMapExample() {
    // 声明map
    var m1 map[string]int
    m2 := make(map[string]int)
    m3 := map[string]int{
        "apple":  1,
        "banana": 2,
        "orange": 3,
    }

    // 添加元素
    m2["grape"] = 4
    m2["melon"] = 5

    // 访问元素
    value := m3["apple"]
    println(value) // 1

    // 检查key是否存在
    if value, exists := m2["grape"]; exists {
        println("Grape:", value)
    }

    // 删除元素
    delete(m3, "orange")

    // 遍历map
    for key, value := range m2 {
        println(key, ":", value)
    }

    // 获取map长度
    println("Map size:", len(m2))
}

// 复杂map示例
func complexMapExample() {
    // map of structs
    type Person struct {
        Name string
        Age  int
    }

    people := map[string]Person{
        "john": {Name: "John", Age: 30},
        "jane": {Name: "Jane", Age: 25},
    }

    // map of slices
    groups := map[string][]string{
        "fruits":  {"apple", "banana", "orange"},
        "colors": {"red", "green", "blue"},
    }

    // map of functions
    operations := map[string]func(int, int) int{
        "add":      func(a, b int) int { return a + b },
        "subtract": func(a, b int) int { return a - b },
        "multiply": func(a, b int) int { return a * b },
    }

    result := operations["add"](5, 3)
    println("5 + 3 =", result)
}

// map作为函数参数
func countWords(text string) map[string]int {
    words := strings.Fields(text)
    counts := make(map[string]int)

    for _, word := range words {
        counts[word]++
    }

    return counts
}

// map的最佳实践
func mapBestPractices() {
    // 1. 使用make初始化map
    m := make(map[string]int)

    // 2. 检查key是否存在
    if value, exists := m["key"]; exists {
        println("Key exists:", value)
    }

    // 3. 处理零值
    value := m["nonexistent"] // 返回int的零值0
    println("Nonexistent key:", value)

    // 4. 并发安全的map (使用sync.Map)
    var safeMap sync.Map
    safeMap.Store("key", "value")
    if val, ok := safeMap.Load("key"); ok {
        println(val.(string))
    }
}
```

## 22. chan - 通道类型

### 描述
`chan`用于声明通道，是Go中实现goroutine间通信的主要方式。

### 语法和示例
```go
// 基本通道操作
func basicChannelExample() {
    // 创建无缓冲通道
    ch := make(chan int)

    // 创建有缓冲通道
    bufferedCh := make(chan int, 3)

    // 发送和接收
    go func() {
        ch <- 42 // 发送
        value := <-ch // 接收
        println("Received:", value)
    }()

    // 关闭通道
    close(ch)
}

// 通道方向
func channelDirectionExample() {
    // 只发送通道
    var sendOnly chan<- int = make(chan int)

    // 只接收通道
    var receiveOnly <-chan int = make(chan int)

    // 双向通道
    var bidirectional chan int = make(chan int)

    // 函数参数中的通道方向
    func producer(ch chan<- int) {
        ch <- 100
    }

    func consumer(ch <-chan int) {
        value := <-ch
        println("Consumed:", value)
    }
}

// 多goroutine通道通信
func workerExample() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动worker
    go func() {
        for job := range jobs {
            println("Processing job:", job)
            time.Sleep(time.Second)
            results <- job * 2
        }
        close(results)
    }()

    // 发送jobs
    for i := 1; i <= 5; i++ {
        jobs <- i
    }
    close(jobs)

    // 收集results
    for result := range results {
        println("Result:", result)
    }
}

// select与通道
func selectExample() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(1 * time.Second)
        ch1 <- "from ch1"
    }()

    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "from ch2"
    }()

    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            println("Received:", msg1)
        case msg2 := <-ch2:
            println("Received:", msg2)
        case <-time.After(3 * time.Second):
            println("Timeout")
        }
    }
}

// 通道的同步作用
func synchronizationExample() {
    done := make(chan bool)

    go func() {
        println("Worker starting")
        time.Sleep(2 * time.Second)
        println("Worker finished")
        done <- true
    }()

    println("Main waiting for worker")
    <-done // 等待worker完成
    println("Main continuing")
}
```

## 23. range - 遍历

### 描述
`range`用于遍历数组、切片、字符串、map、通道等。

### 语法和示例
```go
// 遍历数组和切片
func rangeSliceExample() {
    numbers := []int{1, 2, 3, 4, 5}

    // 带索引的遍历
    for index, value := range numbers {
        println(index, ":", value)
    }

    // 只需要值
    for _, value := range numbers {
        println(value)
    }

    // 只需要索引
    for index := range numbers {
        println(index)
    }
}

// 遍历map
func rangeMapExample() {
    person := map[string]string{
        "name":  "John",
        "age":   "30",
        "email": "john@example.com",
    }

    for key, value := range person {
        println(key, ":", value)
    }

    // map的遍历顺序不保证
    for key := range person {
        println(key)
    }
}

// 遍历字符串
func rangeStringExample() {
    str := "Hello, 世界"

    // range会正确处理Unicode字符
    for index, runeValue := range str {
        println(index, ":", runeValue, string(runeValue))
    }
}

// 遍历通道
func rangeChannelExample() {
    ch := make(chan int, 3)
    ch <- 1
    ch <- 2
    ch <- 3
    close(ch)

    // range会一直读取直到通道关闭
    for value := range ch {
        println(value)
    }
}

// 遍历多维数据
func rangeMultiDimExample() {
    matrix := [][]int{
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9},
    }

    for i, row := range matrix {
        for j, value := range row {
            println("matrix[", i, "][", j, "] =", value)
        }
    }
}

// range的陷阱和注意事项
func rangePitfallsExample() {
    // 陷阱1: range返回的是副本
    type Person struct {
        Name string
        Age  int
    }

    people := []Person{
        {"Alice", 25},
        {"Bob", 30},
    }

    // 这样修改不会影响原slice
    for _, person := range people {
        person.Age = 100 // 修改的是副本
    }

    // 正确的修改方式
    for i := range people {
        people[i].Age = 100 // 修改原元素
    }

    // 陷阱2: 在循环中使用闭包
    funcs := []func(){}

    for i := 0; i < 3; i++ {
        // 错误: 所有闭包都引用同一个i
        funcs = append(funcs, func() {
            println(i)
        })
    }

    // 正确方式: 创建局部变量
    for i := 0; i < 3; i++ {
        i := i // 创建新的局部变量
        funcs = append(funcs, func() {
            println(i)
        })
    }
}
```

## 24. goto - 跳转语句

### 描述
`goto`用于无条件跳转到指定标签，在现代Go编程中很少使用。

### 语法和示例
```go
// 基本goto
func gotoExample() {
    i := 0

    START:
    if i < 5 {
        println(i)
        i++
        goto START
    }
}

// goto用于错误处理
func errorHandlingExample() {
    err := doSomething()
    if err != nil {
        goto ERROR_HANDLER
    }

    err = doSomethingElse()
    if err != nil {
        goto ERROR_HANDLER
    }

    println("All operations completed successfully")
    return

ERROR_HANDLER:
    println("Error occurred:", err)
}

// goto用于资源清理
func resourceCleanupExample() {
    file, err := os.Open("file.txt")
    if err != nil {
        goto DONE
    }

    defer func() {
        if file != nil {
            file.Close()
        }
    }()

    // 处理文件
    _, err = file.WriteString("Hello")
    if err != nil {
        goto DONE
    }

    println("File processed successfully")

DONE:
    println("Operation completed")
}

// goto的限制: 不能跳过变量声明
func gotoLimitationsExample() {
    goto LABEL // 错误: 跳过了x的声明

    x := 10

LABEL:
    println(x)

    // 正确方式: 跳转到声明之后
    y := 20
    goto LABEL2

LABEL2:
    println(y)
}
```

## 25. fallthrough - 贯穿执行

### 描述
`fallthrough`用于在`switch`语句中强制执行下一个`case`。

### 语法和示例
```go
// 基本fallthrough
func fallthroughExample() {
    switch num := 2; num {
    case 1:
        println("One")
        fallthrough
    case 2:
        println("Two")
        fallthrough
    case 3:
        println("Three")
    default:
        println("Default")
    }
    // 输出: Two, Three
}

// fallthrough与条件
func fallthroughWithCondition() {
    score := 85

    switch {
    case score >= 90:
        println("A")
    case score >= 80:
        println("B")
        fallthrough
    case score >= 70:
        println("C")
    default:
        println("F")
    }
    // 如果score是85，输出: B, C
}

// fallthrough的限制
func fallthroughLimitations() {
    switch day {
    case "Monday":
        println("Monday")
        fallthrough
    case "Tuesday":
        println("Tuesday")
        // fallthrough不能是最后一个case
        // fallthrough // 编译错误
    }

    // fallthrough不能跳转到下一个带条件的case
    switch x {
    case 1:
        println("One")
        fallthrough
    case x > 5: // 编译错误: cannot fallthrough to final case
        println("Greater than 5")
    }
}

// 实际应用场景
func processRequest(request string) {
    switch request {
    case "GET":
        println("Processing GET request")
        fallthrough
    case "POST":
        println("Validating request")
        fallthrough
    case "PUT":
        println("Processing data")
        fallthrough
    case "DELETE":
        println("Logging operation")
        fallthrough
    default:
        println("Common cleanup")
    }
}
```

## 总结

Go语言的25个关键字可以分为以下几类：

1. **声明相关**: `var`, `const`, `func`, `package`, `import`, `type`, `struct`, `interface`
2. **控制流程**: `if`, `else`, `for`, `switch`, `case`, `default`, `break`, `continue`, `return`, `goto`, `fallthrough`
3. **并发相关**: `go`, `select`, `chan`, `defer`
4. **数据类型**: `map`, `range`

这些关键字构成了Go语言的核心语法，掌握它们的使用方法对于成为Go语言开发者至关重要。