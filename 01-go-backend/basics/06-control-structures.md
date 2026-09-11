# 条件语句与循环控制

> **文档简介**: 全面掌握Go语言的条件语句和循环控制结构，学会编写逻辑清晰的程序控制流程

> **目标读者**: Go初学者，需要掌握Go程序控制流程的学习者

> **前置知识**: 已掌握函数定义和调用基础

> **预计时长**: 2-3小时学习 + 实践

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#控制结构` `#条件语句` `#循环` `#switch` `#goto` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

通过本文档学习，您将能够：
- 掌握if-else条件语句的使用
- 理解switch多路选择结构
- 学会for循环的各种形式
- 掌握while风格的循环实现
- 了解defer语句的作用和应用

## 🔄 条件语句

### 1. if-else语句

#### 基本语法
```go
if condition {
    // 条件为真时执行
} else {
    // 条件为假时执行
}
```

#### 简单示例
```go
package main

import "fmt"

func checkAge(age int) {
    if age >= 18 {
        fmt.Printf("%d岁是成年人\n", age)
    } else {
        fmt.Printf("%d岁是未成年人\n", age)
    }
}

func main() {
    checkAge(16)
    checkAge(18)
    checkAge(25)
}
```

#### if-else if-else
```go
func getGrade(score int) string {
    if score >= 90 {
        return "优秀"
    } else if score >= 80 {
        return "良好"
    } else if score >= 70 {
        return "中等"
    } else if score >= 60 {
        return "及格"
    } else {
        return "不及格"
    }
}

func main() {
    scores := []int{95, 85, 75, 65, 55}
    for _, score := range scores {
        fmt.Printf("分数: %d, 等级: %s\n", score, getGrade(score))
    }
}
```

### 2. 带初始化的if语句

```go
func main() {
    // if语句中的短变量声明
    if x := 10; x > 5 {
        fmt.Printf("x = %d, 大于5\n", x)
    }

    // if-else中的短变量声明
    if name := "张三"; name != "" {
        fmt.Printf("姓名: %s\n", name)
    } else {
        fmt.Println("姓名为空")
    }
}
```

## 🔀 switch语句

### 1. 基本switch

```go
func dayOfWeek(day int) string {
    switch day {
    case 1:
        return "星期一"
    case 2:
        return "星期二"
    case 3:
        return "星期三"
    case 4:
        return "星期四"
    case 5:
        return "星期五"
    case 6:
        return "星期六"
    case 7:
        return "星期日"
    default:
        return "无效的日期"
    }
}

func main() {
    for i := 1; i <= 8; i++ {
        fmt.Printf("第%d天是%s\n", i, dayOfWeek(i))
    }
}
```

### 2. switch的表达式形式

```go
func checkNumber(num int) string {
    switch {
    case num < 0:
        return "负数"
    case num == 0:
        return "零"
    case num > 0 && num < 10:
        return "个位数"
    case num >= 10 && num < 100:
        return "两位数"
    default:
        return "多位数"
    }
}

func main() {
    numbers := []int{-5, 0, 7, 15, 123}
    for _, num := range numbers {
        fmt.Printf("%d是%s\n", num, checkNumber(num))
    }
}
```

### 3. fallthrough的使用

```go
func checkTrafficLight(light string) {
    fmt.Printf("交通灯: %s - ", light)
    switch light {
    case "红灯":
        fmt.Println("停止")
    case "黄灯":
        fmt.Println("准备")
        fallthrough
    case "绿灯":
        fmt.Println("通行")
    default:
        fmt.Println("无效信号")
    }
}

func main() {
    lights := []string{"红灯", "黄灯", "绿灯", "蓝灯"}
    for _, light := range lights {
        checkTrafficLight(light)
    }
}
```

### 4. 类型switch

```go
func printType(value interface{}) {
    switch v := value.(type) {
    case int:
        fmt.Printf("整数: %d\n", v)
    case string:
        fmt.Printf("字符串: %s\n", v)
    case bool:
        fmt.Printf("布尔值: %t\n", v)
    case []int:
        fmt.Printf("整数数组: %v\n", v)
    default:
        fmt.Printf("未知类型: %T\n", v)
    }
}

func main() {
    values := []interface{}{42, "Hello", true, []int{1, 2, 3}, 3.14}
    for _, value := range values {
        printType(value)
    }
}
```

## 🔄 循环结构

### 1. for循环 - 三种形式

#### 标准for循环
```go
func printNumbers(n int) {
    fmt.Printf("1到%d的数字:\n", n)
    for i := 1; i <= n; i++ {
        fmt.Printf("%d ", i)
    }
    fmt.Println()
}

func main() {
    printNumbers(5)
}
```

#### while风格的for循环
```go
func readInputUntilStop() {
    var input string
    count := 0

    for {
        fmt.Scanln(&input)
        if input == "stop" {
            break
        }
        count++
        fmt.Printf("输入 %d: %s\n", count, input)
    }

    fmt.Printf("共输入了%d个有效输入\n", count)
}

func main() {
    fmt.Println("输入内容，输入'stop'结束:")
    readInputUntilStop()
}
```

#### 无限for循环
```go
func main() {
    // 无限循环（需要break退出）
    count := 0
    for {
        fmt.Printf("计数: %d\n", count)
        count++
        if count >= 5 {
            break
        }
    }
    fmt.Println("循环结束")
}
```

### 2. range循环

#### 遍历数组/切片
```go
func main() {
    numbers := []int{10, 20, 30, 40, 50}

    // 遍历数组元素和索引
    fmt.Println("遍历数组元素:")
    for i, num := range numbers {
        fmt.Printf("索引 %d: %d\n", i, num)
    }

    // 只遍历元素
    fmt.Println("\n只遍历元素:")
    for _, num := range numbers {
        fmt.Printf("%d ", num)
    }
    fmt.Println()
}
```

#### 遍历映射
```go
func main() {
    scores := map[string]int{
        "张三": 85,
        "李四": 92,
        "王五": 78,
    }

    // 遍历映射的键值对
    fmt.Println("学生成绩:")
    for name, score := range scores {
        fmt.Printf("%s: %d分\n", name, score)
    }
}
```

#### 遍历字符串
```go
func main() {
    text := "Hello, 世界!"

    // 遍历字符串的字节（UTF-8编码）
    fmt.Println("字节遍历:")
    for i, b := range []byte(text) {
        fmt.Printf("位置 %d: %c\n", i, b)
    }

    // 遍历字符串的字符（Unicode码点）
    fmt.Println("\n字符遍历:")
    for i, r := range text {
        fmt.Printf("位置 %d: %c (码点: %d)\n", i, r, r)
    }
}
```

### 3. 嵌套循环

#### 多重循环
```go
func printMultiplicationTable(n int) {
    fmt.Printf("%d乘法表:\n", n)
    for i := 1; i <= n; i++ {
        for j := 1; j <= n; j++ {
            fmt.Printf("%dx%d=%-3d ", i, j, i*j)
        }
        fmt.Println()
    }
}

func main() {
    printMultiplicationTable(5)
}
```

#### 循环中的标签和break/continue
```go
func searchInMatrix(matrix [][]int, target int) (row, col int, found bool) {
OuterLoop:
    for r, rowSlice := range matrix {
        for c, value := range rowSlice {
            if value == target {
                return r, c, true
            }
            if value > target {
                // 跳出当前行循环，继续下一行
                continue OuterLoop
            }
        }
    }
    return -1, -1, false
}

func main() {
    matrix := [][]int{
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9},
        {10, 11, 12},
    }

    row, col, found := searchInMatrix(matrix, 8)
    if found {
        fmt.Printf("找到目标值8在位置[%d][%d]\n", row, col)
    } else {
        fmt.Println("未找到目标值")
    }
}
```

## ⚡ defer语句

### 1. defer的基本用法

```go
func demonstrateDefer() {
    fmt.Println("函数开始")

    defer fmt.Println("函数结束 (1)")
    defer fmt.Println("函数结束 (2)")
    defer fmt.Println("函数结束 (3)")

    fmt.Println("函数执行中...")
}

func main() {
    demonstrateDefer()
    fmt.Println("main函数继续执行")
}
```

**输出顺序**：
```
函数开始
函数执行中...
main函数继续执行
函数结束 (3)
函数结束 (2)
函数结束 (1)
```

### 2. defer的实际应用

#### 资源清理
```go
import "os"

func processFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()  // 确保文件被关闭

    // 读取文件内容
    content := make([]byte, 1024)
    n, err := file.Read(content)
    if err != nil {
        return err
    }

    fmt.Printf("读取了%d个字节\n", n)
    return nil
}

func main() {
    err := processFile("example.txt")
    if err != nil {
        fmt.Printf("处理文件错误: %v\n", err)
    }
}
```

#### panic恢复
```go
func safeOperation() (result string) {
    defer func() {
        if r := recover(); r != nil {
            result = fmt.Sprintf("操作失败，已恢复: %v", r)
        }
    }()

    // 模拟可能失败的操作
    // panic("模拟错误")
    result = "操作成功"
    return
}

func main() {
    result := safeOperation()
    fmt.Printf("结果: %s\n", result)
}
```

## 🎯 实际应用示例

### 示例1: 用户输入验证

```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "strconv"
    "strings"
)

func validateInput(input string) (bool, string) {
    // 去除前后空格
    input = strings.TrimSpace(input)

    if input == "" {
        return false, "输入不能为空"
    }

    if len(input) > 100 {
        return false, "输入过长（最多100字符）"
    }

    return true, "输入有效"
}

func getUserInput(prompt string) string {
    reader := bufio.NewReader(os.Stdin)
    fmt.Print(prompt)

    input, _ := reader.ReadString('\n')
    return strings.TrimSpace(input)
}

func main() {
    fmt.Println("=== 用户输入验证系统 ===")

    for {
        input := getUserInput("请输入内容（输入'quit'退出）: ")

        if input == "quit" {
            break
        }

        valid, message := validateInput(input)
        if valid {
            fmt.Printf("✅ %s\n", message)
        } else {
            fmt.Printf("❌ %s\n", message)
        }
    }

    fmt.Println("程序结束")
}
```

### 示例2: 菜单驱动程序

```go
package main

import "fmt"

func displayMenu() {
    fmt.Println("=== 计算器菜单 ===")
    fmt.Println("1. 加法")
    fmt.Println("2. 减法")
    fmt.Println("3. 乘法")
    fmt.Println("4. 除法")
    fmt.Println("5. 退出")
    fmt.Print("请选择操作 (1-5): ")
}

func getNumbers() (float64, float64) {
    var a, b float64
    fmt.Print("请输入第一个数字: ")
    fmt.Scanln(&a)
    fmt.Print("请输入第二个数字: ")
    fmt.Scanln(&b)
    return a, b
}

func main() {
    var choice int
    var a, b float64

    for {
        displayMenu()
        fmt.Scanln(&choice)

        if choice == 5 {
            fmt.Println("感谢使用，再见！")
            break
        }

        if choice < 1 || choice > 5 {
            fmt.Println("无效选择，请重新输入")
            continue
        }

        a, b = getNumbers()

        switch choice {
        case 1:
            fmt.Printf("%.2f + %.2f = %.2f\n", a, b, a+b)
        case 2:
            fmt.Printf("%.2f - %.2f = %.2f\n", a, b, a-b)
        case 3:
            fmt.Printf("%.2f × %.2f = %.2f\n", a, b, a*b)
        case 4:
            if b != 0 {
                fmt.Printf("%.2f ÷ %.2f = %.2f\n", a, b, a/b)
            } else {
                fmt.Println("错误：除数不能为0")
            }
        }

        fmt.Println() // 空行分隔
    }
}
```

### 示例3: 数据处理管道

```go
package main

import (
    "fmt"
    "strings"
)

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

// 映射函数
func mapNumbers(numbers []int, transform func(int) int) []int {
    result := make([]int, len(numbers))
    for i, num := range numbers {
        result[i] = transform(num)
    }
    return result
}

// 规约函数
func reduce(numbers []int, operation func(int, int) int) int {
    if len(numbers) == 0 {
        return 0
    }

    result := numbers[0]
    for _, num := range numbers[1:] {
        result = operation(result, num)
    }
    return result
}

// 数据处理管道
func processNumbers(numbers []int) []int {
    // 管道: 过滤偶数 → 平方 → 求和
    pipeline := func(nums []int) []int {
        // 步骤1: 过滤偶数
        evens := filter(nums, func(n int) bool {
            return n%2 == 0
        })

        // 步骤2: 平方每个偶数
        squares := mapNumbers(evens, func(n int) int {
            return n * n
        })

        // 步骤3: 计算总和
        total := reduce(squares, func(a, b int) int {
            return a + b
        })

        return []int{total}
    }

    return pipeline(numbers)
}

func main() {
    data := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

    fmt.Printf("原始数据: %v\n", data)
    result := processNumbers(data)
    fmt.Printf("偶数平方和: %v\n", result)

    // 验证结果
    sum := 0
    for _, num := range data {
        if num%2 == 0 {
            sum += num * num
        }
    }
    fmt.Printf("验证结果: %d\n", sum)
}
```

## 🔍 常见错误和注意事项

### 1. 无限循环
```go
// ❌ 错误 - 忘须有退出条件
func badLoop() {
    count := 0
    for {
        count++
        // 没有break或return，会无限循环
    }
}

// ✅ 正确 - 有明确的退出条件
func goodLoop(n int) {
    for i := 0; i < n; i++ {
        // 循环条件明确
    }
}
```

### 2. switch缺少break
```go
// ❌ 错误 - 没有break会继续执行下一个case
func checkGrade(grade string) string {
    switch grade {
    case "A":
        return "优秀"
    case "B":
        return "良好"  // 缺少fallthrough可能是意外的
    case "C":
        return "及格"
    }
}

// ✅ 正确 - 明确控制执行流程
func checkGradeFixed(grade string) string {
    switch grade {
    case "A":
        return "优秀"
    case "B":
        fallthrough  // 明确使用fallthrough
    case "C":
        return "良好"
    default:
        return "需要改进"
    }
}
```

### 3. defer在循环中的使用
```go
// ❌ 谨试时的陷阱
func badDeferInLoop() {
    for i := 0; i < 3; i++ {
        defer fmt.Printf("循环结束: %d\n", i)
        // 所有defer会在函数结束时执行，不是每次循环结束时
    }
}

// ✅ 正确的方式 - 匿名函数创建defer
func goodDeferInLoop() {
    for i := 0; i < 3; i++ {
        func(id int) {
            defer fmt.Printf("循环结束: %d\n", id)
        }(i)
    }
}
```

## 📈 性能优化提示

### 1. 循环优化
```go
// ❌ 效率低 - 每次都计算长度
func slowSum(numbers []int) int {
    sum := 0
    for i := 0; i < len(numbers); i++ {
        sum += numbers[i]  // 每次都调用len()
    }
    return sum
}

// ✅ 效率高 - 预先计算长度
func fastSum(numbers []int) int {
    sum := 0
    length := len(numbers)  // 预先计算
    for i := 0; i < length; i++ {
        sum += numbers[i]
    }
    return sum
}
```

### 2. 避免不必要的循环
```go
// ❌ 不必要的循环
func containsValue(slice []int, target int) bool {
    for _, v := range slice {
        if v == target {
            return true
        }
    }
    return false
}

// ✅ 使用map查找（适合大数据集）
func containsValueMap(set map[int]struct{}) bool {
    _, exists := set[target]
    return exists
}
```

## 🔗 文档交叉引用

### 相关文档
- 📄 **[第一个程序]**: [02-first-program.md](02-first-program.md) - Go程序基础结构
- 📄 **[变量和常量]**: [03-variables-constants.md](03-variables-constants.md) - Go数据类型和变量
- 📄 **[函数和方法]**: [05-functions-methods.md](05-functions-methods.md) - 函数定义和方法调用
- 📄 **[错误处理]**: [08-error-handling.md](08-error-handling.md) - Go错误处理机制

### 参考资源
- 📖 **[Go控制流文档]**: https://golang.org/ref/spec#Statements
- 📖 **[Go for循环文档]**: https://golang.org/ref/spec#For_statements
- 📖 **[Go switch文档]**: https://golang.org/ref/spec#Switch_statements

## 📝 总结

### 核心要点回顾
1. **条件语句**: 掌握if-else和switch的使用
2. **循环结构**: 理解for循环的各种形式和range循环
3. **defer语句**: 学会使用defer进行资源清理
4. **控制流程**: 组合使用各种控制结构

### 实践练习
- [ ] 编写包含多种条件判断的程序
- [ ] 使用switch替代复杂的if-else链
- [ ] 实现嵌套循环和标签控制
- [ ] 使用defer处理资源清理
- [ ] 创建交互式菜单驱动程序

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0

---

> 💡 **学习建议**:
> - 理解Go控制流程的简洁性和安全性
> - 善用switch语句替代复杂的if-else结构
> - 掌握range循环，避免手动的索引管理
> - 使用defer确保资源的正确释放
> - 避免无限循环，始终提供明确的退出条件