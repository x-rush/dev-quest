# Go标准库详解

Go标准库提供了丰富的包，涵盖了从基础数据结构到网络编程的各个方面。本文档详细介绍Go 1.21+版本中最重要的标准库包。

## 1. fmt - 格式化I/O

**功能**：格式化输入输出，类似C语言的printf/scanf

**主要功能**：
- 字符串格式化
- 终端输出
- 文件格式化读写

**示例**：
```go
package main

import (
    "fmt"
    "os"
)

func main() {
    // 基本输出
    fmt.Print("Hello, ")      // 无换行
    fmt.Println("World!")     // 带换行
    fmt.Printf("Pi = %.2f\n", 3.14159) // 格式化输出

    // 格式化动词
    name := "Alice"
    age := 25
    fmt.Printf("Name: %s, Age: %d\n", name, age)

    // 不同进制输出
    num := 42
    fmt.Printf("Decimal: %d, Binary: %b, Hex: %x, Octal: %o\n", num, num, num, num)

    // 格式化到字符串
    s := fmt.Sprintf("User: %s (%d years old)", name, age)
    fmt.Println(s)

    // 从字符串解析
    var s2 string
    var i int
    fmt.Sscanf("Hello 123", "%s %d", &s2, &i)
    fmt.Printf("Parsed: s=%s, i=%d\n", s2, i)

    // 错误输出
    fmt.Fprintln(os.Stderr, "Error: something went wrong")
}
```

## 2. strings - 字符串操作

**功能**：字符串的常用操作函数

**主要功能**：
- 字符串查找、替换、分割
- 大小写转换
- 去除空白字符
- 字符串比较和包含检查

**示例**：
```go
package main

import (
    "fmt"
    "strings"
    "unicode"
)

func main() {
    // 基本操作
    str := "Hello, World!"

    // 查找和包含
    fmt.Println(strings.Contains(str, "World"))    // true
    fmt.Println(strings.HasPrefix(str, "Hello"))   // true
    fmt.Println(strings.HasSuffix(str, "!"))       // true
    fmt.Println(strings.Index(str, "World"))       // 7

    // 大小写转换
    fmt.Println(strings.ToLower(str))               // hello, world!
    fmt.Println(strings.ToUpper(str))               // HELLO, WORLD!
    fmt.Println(strings.Title("hello world"))       // Hello World

    // 去除空白
    trimmed := "   spaces   "
    fmt.Printf("'%s' -> '%s'\n", trimmed, strings.TrimSpace(trimmed))

    // 分割和连接
    csv := "apple,banana,orange"
    fruits := strings.Split(csv, ",")
    fmt.Println(fruits) // [apple banana orange]

    joined := strings.Join(fruits, "; ")
    fmt.Println(joined) // apple; banana; orange

    // 替换
    fmt.Println(strings.Replace(str, "World", "Go", 1)) // Hello, Go!
    fmt.Println(strings.ReplaceAll(str, "l", "L"))     // HeLLo, WorLd!

    // 重复和计数
    fmt.Println(strings.Repeat("Go", 3))               // GoGoGo
    fmt.Println(strings.Count("hello world", "l"))     // 3

    // 字符串处理函数
    fmt.Println(strings.Map(func(r rune) rune {
        if unicode.IsUpper(r) {
            return unicode.ToLower(r)
        }
        return r
    }, "Hello WORLD")) // hello world

    // 修剪字符
    html := "<div>Hello</div>"
    fmt.Println(strings.Trim(html, "<div>")) // Hello
}
```

## 3. strconv - 字符串转换

**功能**：字符串与基本类型之间的转换

**主要功能**：
- 字符串与数值类型转换
- 布尔值转换
- 引用和转义处理

**示例**：
```go
package main

import (
    "fmt"
    "strconv"
)

func main() {
    // 整数转换
    str := "123"
    num, err := strconv.Atoi(str)
    if err != nil {
        fmt.Println("转换错误:", err)
    } else {
        fmt.Printf("转换结果: %d, 类型: %T\n", num, num)
    }

    // 字符串转整数（指定进制）
    num2, err := strconv.ParseInt("FF", 16, 64)
    if err == nil {
        fmt.Printf("十六进制转换: %d\n", num2) // 255
    }

    // 整数转字符串
    fmt.Println(strconv.Itoa(42))               // "42"
    fmt.Println(strconv.FormatInt(255, 16))    // "ff"

    // 浮点数转换
    f, err := strconv.ParseFloat("3.14159", 64)
    if err == nil {
        fmt.Printf("浮点数: %f\n", f)
    }

    fmt.Println(strconv.FormatFloat(3.14159, 'f', 2, 64)) // "3.14"

    // 布尔值转换
    b, err := strconv.ParseBool("true")
    if err == nil {
        fmt.Printf("布尔值: %t\n", b)
    }

    fmt.Println(strconv.FormatBool(true)) // "true"

    // 引用和转义
    quoted := strconv.Quote("Hello\nWorld")
    fmt.Println(quoted) // "Hello\nWorld"

    unquoted, err := strconv.Unquote(quoted)
    if err == nil {
        fmt.Println(unquoted) // Hello
                              // World
    }

    // 附加字符串
    fmt.Println(strconv.AppendBool([]byte("Value: "), true))
    fmt.Println(strconv.AppendInt([]byte("Number: "), 42, 10))
    fmt.Println(strconv.AppendQuote([]byte("Message: "), "Hello"))
}
```

## 4. math - 数学函数

**功能**：提供数学常数和函数

**主要功能**：
- 基本数学运算（三角函数、对数、指数）
- 数学常数
- 数值比较和限制

**示例**：
```go
package main

import (
    "fmt"
    "math"
)

func main() {
    // 数学常数
    fmt.Printf("Pi: %.15f\n", math.Pi)
    fmt.Printf("E: %.15f\n", math.E)
    fmt.Printf("Phi: %.15f\n", math.Phi)
    fmt.Printf("Sqrt2: %.15f\n", math.Sqrt2)

    // 基本运算
    fmt.Printf("Abs(-4.2): %.1f\n", math.Abs(-4.2))
    fmt.Printf("Ceil(3.14): %.1f\n", math.Ceil(3.14))
    fmt.Printf("Floor(3.14): %.1f\n", math.Floor(3.14))
    fmt.Printf("Round(3.14): %.1f\n", math.Round(3.14))

    // 指数和对数
    fmt.Printf("Pow(2, 3): %.1f\n", math.Pow(2, 3))
    fmt.Printf("Exp(2): %.1f\n", math.Exp(2))
    fmt.Printf("Log(10): %.1f\n", math.Log(10))
    fmt.Printf("Log10(100): %.1f\n", math.Log10(100))
    fmt.Printf("Log2(8): %.1f\n", math.Log2(8))

    // 三角函数
    angle := math.Pi / 4
    fmt.Printf("Sin(π/4): %.4f\n", math.Sin(angle))
    fmt.Printf("Cos(π/4): %.4f\n", math.Cos(angle))
    fmt.Printf("Tan(π/4): %.4f\n", math.Tan(angle))

    // 反三角函数
    asin := math.Asin(0.5)
    fmt.Printf("Asin(0.5): %.4f radians\n", asin)

    // 双曲函数
    fmt.Printf("Sinh(1): %.4f\n", math.Sinh(1))
    fmt.Printf("Cosh(1): %.4f\n", math.Cosh(1))
    fmt.Printf("Tanh(1): %.4f\n", math.Tanh(1))

    // 数值限制和比较
    fmt.Printf("Max(3, 5): %.1f\n", math.Max(3, 5))
    fmt.Printf("Min(3, 5): %.1f\n", math.Min(3, 5))
    fmt.Printf("Dim(5, 3): %.1f\n", math.Dim(5, 3)) // 5-3=2

    // 取模和余数
    fmt.Printf("Mod(10, 3): %.1f\n", math.Mod(10, 3))
    fmt.Printf("Remainder(10, 3): %.1f\n", math.Remainder(10, 3))

    // 特殊函数
    fmt.Printf("Sqrt(16): %.1f\n", math.Sqrt(16))
    fmt.Printf("Cbrt(27): %.1f\n", math.Cbrt(27))
    fmt.Printf("Hypot(3, 4): %.1f\n", math.Hypot(3, 4))

    // 特殊值
    fmt.Printf("Inf(1): %v\n", math.Inf(1))
    fmt.Printf("NaN(): %v\n", math.NaN())
    fmt.Printf("IsNaN(NaN()): %t\n", math.IsNaN(math.NaN()))
    fmt.Printf("IsInf(Inf(1), 1): %t\n", math.IsInf(math.Inf(1), 1))
}
```

## 5. time - 时间和日期

**功能**：时间和日期操作

**主要功能**：
- 时间获取和格式化
- 时间计算和比较
- 时区处理
- 定时器和休眠

**示例**：
```go
package main

import (
    "fmt"
    "time"
)

func main() {
    // 当前时间
    now := time.Now()
    fmt.Println("当前时间:", now)

    // 时间格式化
    fmt.Println("RFC3339:", now.Format(time.RFC3339))
    fmt.Println("自定义格式:", now.Format("2006-01-02 15:04:05"))

    // 时间解析
    t, err := time.Parse("2006-01-02", "2024-01-01")
    if err == nil {
        fmt.Println("解析时间:", t)
    }

    // 时间组件
    fmt.Printf("年: %d, 月: %d, 日: %d\n", now.Year(), now.Month(), now.Day())
    fmt.Printf("时: %d, 分: %d, 秒: %d\n", now.Hour(), now.Minute(), now.Second())
    fmt.Printf("星期: %d, 年中日: %d\n", now.Weekday(), now.YearDay())

    // 时间计算
    future := now.Add(24 * time.Hour)     // 24小时后
    past := now.Add(-7 * 24 * time.Hour) // 7天前

    fmt.Println("24小时后:", future)
    fmt.Println("7天前:", past)

    // 时间差
    duration := future.Sub(now)
    fmt.Printf("时间差: %v\n", duration)
    fmt.Printf("小时数: %.1f\n", duration.Hours())

    // 时间比较
    fmt.Println("now > past:", now.After(past))
    fmt.Println("now < future:", now.Before(future))
    fmt.Println("now == now:", now.Equal(now))

    // 时区
    loc, _ := time.LoadLocation("America/New_York")
    nyTime := now.In(loc)
    fmt.Println("纽约时间:", nyTime)

    // Unix时间戳
    fmt.Printf("Unix时间戳: %d\n", now.Unix())
    fmt.Printf("纳秒时间戳: %d\n", now.UnixNano())

    // 定时器
    timer := time.NewTimer(2 * time.Second)
    <-timer.C
    fmt.Println("2秒定时器触发")

    // 周期性定时器
    ticker := time.NewTicker(1 * time.Second)
    go func() {
        for i := 0; i < 3; i++ {
            <-ticker.C
            fmt.Println("Ticker:", i+1)
        }
        ticker.Stop()
    }()

    // 等待ticker完成
    time.Sleep(4 * time.Second)

    // 时间间隔
    fmt.Printf("1毫秒: %v\n", time.Millisecond)
    fmt.Printf("1秒: %v\n", time.Second)
    fmt.Printf("1分钟: %v\n", time.Minute)
    fmt.Printf("1小时: %v\n", time.Hour)
}
```

## 6. os - 操作系统功能

**功能**：操作系统相关的功能

**主要功能**：
- 文件和目录操作
- 环境变量
- 进程管理
- 系统信号

**示例**：
```go
package main

import (
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
)

func main() {
    // 获取当前工作目录
    wd, _ := os.Getwd()
    fmt.Println("工作目录:", wd)

    // 环境变量
    fmt.Println("PATH:", os.Getenv("PATH"))
    os.Setenv("MY_VAR", "test_value")
    fmt.Println("MY_VAR:", os.Getenv("MY_VAR"))

    // 列出环境变量
    for _, env := range os.Environ() {
        fmt.Println(env)
        break // 只显示第一个
    }

    // 文件信息
    fileInfo, err := os.Stat("main.go")
    if err == nil {
        fmt.Printf("文件大小: %d 字节\n", fileInfo.Size())
        fmt.Printf("文件模式: %v\n", fileInfo.Mode())
        fmt.Printf("修改时间: %v\n", fileInfo.ModTime())
    }

    // 创建目录
    err = os.Mkdir("test_dir", 0755)
    if err != nil {
        fmt.Println("创建目录失败:", err)
    } else {
        fmt.Println("创建目录成功")
    }

    // 创建文件
    file, err := os.Create("test.txt")
    if err == nil {
        defer file.Close()
        file.WriteString("Hello, World!\n")
        fmt.Println("创建文件成功")
    }

    // 文件重命名
    err = os.Rename("test.txt", "renamed.txt")
    if err == nil {
        fmt.Println("文件重命名成功")
    }

    // 删除文件
    err = os.Remove("renamed.txt")
    if err == nil {
        fmt.Println("文件删除成功")
    }

    // 删除目录
    err = os.Remove("test_dir")
    if err == nil {
        fmt.Println("目录删除成功")
    }

    // 进程ID
    fmt.Println("进程ID:", os.Getpid())
    fmt.Println("父进程ID:", os.Getppid())

    // 用户信息
    fmt.Println("用户ID:", os.Getuid())
    fmt.Println("组ID:", os.Getgid())

    // 执行外部命令
    cmd := exec.Command("ls", "-l")
    output, err := cmd.Output()
    if err == nil {
        fmt.Println("命令输出:")
        fmt.Println(string(output))
    }

    // 系统信息
    hostname, _ := os.Hostname()
    fmt.Println("主机名:", hostname)

    // 退出程序
    // os.Exit(0) // 注释掉以避免程序提前退出

    // 标准文件描述符
    fmt.Fprintln(os.Stdout, "标准输出")
    fmt.Fprintln(os.Stderr, "标准错误")
}
```

## 7. io - 基本I/O接口

**功能**：基本的输入输出接口

**主要功能**：
- Reader和Writer接口
- 复制和限制读取
- 缓冲操作

**示例**：
```go
package main

import (
    "bytes"
    "fmt"
    "io"
    "os"
    "strings"
)

func main() {
    // Reader接口
    reader := strings.NewReader("Hello, World!")

    // 读取到缓冲区
    buf := make([]byte, 5)
    n, err := reader.Read(buf)
    if err == nil {
        fmt.Printf("读取 %d 字节: %s\n", n, buf[:n])
    }

    // Writer接口
    var builder strings.Builder
    writer := io.Writer(&builder)

    n, err = writer.Write([]byte("Hello, Go!"))
    if err == nil {
        fmt.Printf("写入 %d 字节, 结果: %s\n", n, builder.String())
    }

    // Copy操作
    src := strings.NewReader("This is a test string")
    var dst bytes.Buffer

    copied, err := io.Copy(&dst, src)
    if err == nil {
        fmt.Printf("复制 %d 字节: %s\n", copied, dst.String())
    }

    // LimitReader
    limited := io.LimitReader(strings.NewReader("1234567890"), 5)
    buf2 := make([]byte, 10)
    n, _ = limited.Read(buf2)
    fmt.Printf("限制读取 %d 字节: %s\n", n, buf2[:n])

    // MultiReader
    r1 := strings.NewReader("Hello, ")
    r2 := strings.NewReader("World!")
    multi := io.MultiReader(r1, r2)

    buf3 := make([]byte, 50)
    n, _ = multi.Read(buf3)
    fmt.Printf("多重读取 %d 字节: %s\n", n, buf3[:n])

    // TeeReader
    var teeBuf bytes.Buffer
    tee := io.TeeReader(strings.NewReader("Tee test"), &teeBuf)

    buf4 := make([]byte, 20)
    n, _ = tee.Read(buf4)
    fmt.Printf("Tee读取 %d 字节: %s\n", n, buf4[:n])
    fmt.Printf("Tee缓冲区: %s\n", teeBuf.String())

    // SectionReader
    section := io.NewSectionReader(strings.NewReader("0123456789"), 2, 4)
    buf5 := make([]byte, 10)
    n, _ = section.Read(buf5)
    fmt.Printf("区间读取 %d 字节: %s\n", n, buf5[:n])

    // Pipe
    pr, pw := io.Pipe()

    go func() {
        defer pw.Close()
        pw.Write([]byte("Pipe test"))
    }()

    buf6 := make([]byte, 20)
    n, err = pr.Read(buf6)
    if err == nil {
        fmt.Printf("管道读取 %d 字节: %s\n", n, buf6[:n])
    }
}
```

## 8. bufio - 缓冲I/O

**功能**：带缓冲的I/O操作

**主要功能**：
- 缓冲读取和写入
- 按行读取
- 扫描器

**示例**：
```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "strings"
)

func main() {
    // 缓冲写入器
    writer := bufio.NewWriter(os.Stdout)
    defer writer.Flush()

    writer.WriteString("Hello, ")
    writer.WriteString("Buffered Writer!\n")

    // 缓冲读取器
    reader := bufio.NewReader(strings.NewReader("Line 1\nLine 2\nLine 3\n"))

    for {
        line, err := reader.ReadString('\n')
        if err != nil {
            break
        }
        fmt.Printf("读取行: %s", line)
    }

    // 按行读取
    reader2 := bufio.NewReader(strings.NewReader("First line\nSecond line\nThird line\n"))

    line, err := reader2.ReadString('\n')
    if err == nil {
        fmt.Println("第一行:", strings.TrimSpace(line))
    }

    // 扫描器
    scanner := bufio.NewScanner(strings.NewReader("word1 word2 word3"))
    scanner.Split(bufio.ScanWords)

    for scanner.Scan() {
        fmt.Println("单词:", scanner.Text())
    }

    if err := scanner.Err(); err != nil {
        fmt.Println("扫描错误:", err)
    }

    // 自定义分割函数
    customScanner := bufio.NewScanner(strings.NewReader("a,b,c,d,e"))
    customScanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
        for i := 0; i < len(data); i++ {
            if data[i] == ',' {
                return i + 1, data[:i], nil
            }
        }
        return 0, data, nil
    })

    for customScanner.Scan() {
        fmt.Println("自定义分割:", customScanner.Text())
    }

    // 读取全部
    reader3 := bufio.NewReader(strings.NewReader("Full content to read"))
    content, err := reader3.ReadString('\x00') // 读取到结束
    if err != io.EOF {
        fmt.Println("读取内容:", strings.TrimSpace(content))
    }

    // 缓冲大小
    largeReader := bufio.NewReaderSize(strings.NewReader("Large content"), 1024)
    fmt.Printf("缓冲区大小: %d\n", largeReader.Size())

    // 统计行数
    lineCount := 0
    lineScanner := bufio.NewScanner(strings.NewReader("Line1\nLine2\nLine3\n"))
    for lineScanner.Scan() {
        lineCount++
    }
    fmt.Printf("总行数: %d\n", lineCount)
}
```

## 9. net - 网络编程

**功能**：网络编程的基础包

**主要功能**：
- TCP/UDP网络连接
- 地址解析
- 网络类型判断

**示例**：
```go
package main

import (
    "fmt"
    "net"
    "time"
)

func main() {
    // TCP服务器
    listener, err := net.Listen("tcp", ":8080")
    if err != nil {
        fmt.Println("监听失败:", err)
        return
    }
    defer listener.Close()

    fmt.Println("TCP服务器启动，监听端口 8080")

    // 在另一个goroutine中处理连接
    go func() {
        for {
            conn, err := listener.Accept()
            if err != nil {
                fmt.Println("接受连接失败:", err)
                continue
            }

            go handleConnection(conn)
        }
    }()

    // TCP客户端
    time.Sleep(1 * time.Second) // 等待服务器启动

    conn, err := net.Dial("tcp", "localhost:8080")
    if err != nil {
        fmt.Println("连接失败:", err)
        return
    }
    defer conn.Close()

    // 发送数据
    _, err = conn.Write([]byte("Hello, Server!"))
    if err != nil {
        fmt.Println("发送失败:", err)
        return
    }

    // 接收数据
    buf := make([]byte, 1024)
    n, err := conn.Read(buf)
    if err != nil {
        fmt.Println("接收失败:", err)
        return
    }

    fmt.Printf("服务器响应: %s\n", buf[:n])

    // UDP服务器
    udpAddr, err := net.ResolveUDPAddr("udp", ":8081")
    if err != nil {
        fmt.Println("解析UDP地址失败:", err)
        return
    }

    udpConn, err := net.ListenUDP("udp", udpAddr)
    if err != nil {
        fmt.Println("UDP监听失败:", err)
        return
    }
    defer udpConn.Close()

    fmt.Println("UDP服务器启动，监听端口 8081")

    go func() {
        buf := make([]byte, 1024)
        for {
            n, addr, err := udpConn.ReadFromUDP(buf)
            if err != nil {
                fmt.Println("UDP读取失败:", err)
                continue
            }

            fmt.Printf("UDP收到来自 %s 的数据: %s\n", addr, buf[:n])

            // 回复
            udpConn.WriteToUDP([]byte("UDP响应"), addr)
        }
    }()

    // UDP客户端
    time.Sleep(1 * time.Second)

    udpClient, err := net.Dial("udp", "localhost:8081")
    if err != nil {
        fmt.Println("UDP客户端连接失败:", err)
        return
    }
    defer udpClient.Close()

    udpClient.Write([]byte("Hello, UDP Server!"))

    // 网络地址解析
    host, err := net.LookupHost("google.com")
    if err == nil {
        fmt.Println("Google IP地址:", host)
    }

    // 网络类型判断
    fmt.Println("判断网络类型:")
    fmt.Println("tcp是否为已知网络:", net.ParseIP("192.168.1.1") != nil)
    fmt.Println("127.0.0.1是否为回环地址:", net.ParseIP("127.0.0.1").IsLoopback())
    fmt.Println("192.168.1.1是否为私有地址:", net.ParseIP("192.168.1.1").IsPrivate())

    // 等待程序结束
    time.Sleep(2 * time.Second)
}

func handleConnection(conn net.Conn) {
    defer conn.Close()

    buf := make([]byte, 1024)
    n, err := conn.Read(buf)
    if err != nil {
        fmt.Println("读取数据失败:", err)
        return
    }

    fmt.Printf("收到数据: %s\n", buf[:n])

    // 回复客户端
    conn.Write([]byte("Hello, Client!"))
}
```

## 10. encoding/json - JSON处理

**功能**：JSON编码和解码

**主要功能**：
- 结构体与JSON转换
- 流式JSON处理
- 自定义编解码

**示例**：
```go
package main

import (
    "encoding/json"
    "fmt"
    "os"
)

type Person struct {
    Name    string   `json:"name"`
    Age     int      `json:"age"`
    Email   string   `json:"email,omitempty"`
    Hobbies []string `json:"hobbies"`
}

func main() {
    // 基本编码
    person := Person{
        Name:    "Alice",
        Age:     25,
        Hobbies: []string{"reading", "gaming"},
    }

    jsonData, err := json.Marshal(person)
    if err != nil {
        fmt.Println("编码失败:", err)
        return
    }

    fmt.Println("JSON编码结果:", string(jsonData))

    // 格式化输出
    prettyJson, err := json.MarshalIndent(person, "", "  ")
    if err == nil {
        fmt.Println("格式化JSON:")
        fmt.Println(string(prettyJson))
    }

    // 解码
    var decodedPerson Person
    err = json.Unmarshal(jsonData, &decodedPerson)
    if err == nil {
        fmt.Printf("解码结果: %+v\n", decodedPerson)
    }

    // 动态JSON处理
    jsonStr := `{"name": "Bob", "age": 30, "city": "New York"}`
    var dynamic map[string]interface{}

    err = json.Unmarshal([]byte(jsonStr), &dynamic)
    if err == nil {
        fmt.Println("动态JSON:")
        for k, v := range dynamic {
            fmt.Printf("  %s: %v (%T)\n", k, v, v)
        }
    }

    // JSON数组处理
    jsonArray := `[
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35}
    ]`

    var people []Person
    err = json.Unmarshal([]byte(jsonArray), &people)
    if err == nil {
        fmt.Println("JSON数组:")
        for i, p := range people {
            fmt.Printf("  [%d] %s (%d)\n", i, p.Name, p.Age)
        }
    }

    // 流式编码器
    file, err := os.Create("output.json")
    if err == nil {
        defer file.Close()

        encoder := json.NewEncoder(file)
        err = encoder.Encode(person)
        if err == nil {
            fmt.Println("流式编码成功")
        }
    }

    // 流式解码器
    file2, err := os.Open("output.json")
    if err == nil {
        defer file2.Close()

        var streamPerson Person
        decoder := json.NewDecoder(file2)
        err = decoder.Decode(&streamPerson)
        if err == nil {
            fmt.Printf("流式解码结果: %+v\n", streamPerson)
        }
    }

    // 自定义编解码
    type CustomDate struct {
        time.Time
    }

    // 自定义MarshalJSON
    func (cd CustomDate) MarshalJSON() ([]byte, error) {
        return json.Marshal(cd.Time.Format("2006-01-02"))
    }

    // 自定义UnmarshalJSON
    func (cd *CustomDate) UnmarshalJSON(data []byte) error {
        var s string
        if err := json.Unmarshal(data, &s); err != nil {
            return err
        }
        t, err := time.Parse("2006-01-02", s)
        if err != nil {
            return err
        }
        cd.Time = t
        return nil
    }

    // 使用自定义类型
    type Event struct {
        Name string      `json:"name"`
        Date CustomDate  `json:"date"`
    }

    event := Event{
        Name: "Conference",
        Date: CustomDate{time.Now()},
    }

    eventJson, _ := json.Marshal(event)
    fmt.Println("自定义日期JSON:", string(eventJson))
}
```

## 11. database/sql - 数据库操作

**功能**：数据库访问接口

**主要功能**：
- 数据库连接池
- 事务处理
- 预编译语句

**示例**：
```go
package main

import (
    "database/sql"
    "fmt"
    "log"
    "time"

    _ "github.com/lib/pq" // PostgreSQL驱动
)

type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

func main() {
    // 连接数据库
    db, err := sql.Open("postgres", "host=localhost port=5432 user=postgres password=password dbname=testdb sslmode=disable")
    if err != nil {
        log.Fatal("连接数据库失败:", err)
    }
    defer db.Close()

    // 测试连接
    err = db.Ping()
    if err != nil {
        log.Fatal("数据库连接测试失败:", err)
    }

    fmt.Println("数据库连接成功")

    // 创建表
    createTable := `
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`

    _, err = db.Exec(createTable)
    if err != nil {
        log.Fatal("创建表失败:", err)
    }

    // 插入数据
    insertSQL := "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id"
    var id int
    err = db.QueryRow(insertSQL, "Alice", "alice@example.com").Scan(&id)
    if err != nil {
        log.Fatal("插入数据失败:", err)
    }
    fmt.Printf("插入成功，ID: %d\n", id)

    // 查询单条记录
    querySQL := "SELECT id, name, email, created_at FROM users WHERE id = $1"
    var user User
    err = db.QueryRow(querySQL, id).Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)
    if err != nil {
        log.Fatal("查询失败:", err)
    }
    fmt.Printf("查询结果: %+v\n", user)

    // 查询多条记录
    rows, err := db.Query("SELECT id, name, email, created_at FROM users")
    if err != nil {
        log.Fatal("查询失败:", err)
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        err := rows.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt)
        if err != nil {
            log.Fatal("扫描行失败:", err)
        }
        users = append(users, u)
    }

    fmt.Printf("所有用户: %+v\n", users)

    // 预编译语句
    stmt, err := db.Prepare("UPDATE users SET name = $1 WHERE id = $2")
    if err != nil {
        log.Fatal("准备语句失败:", err)
    }
    defer stmt.Close()

    result, err := stmt.Exec("Alice Smith", id)
    if err != nil {
        log.Fatal("执行更新失败:", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        log.Fatal("获取影响行数失败:", err)
    }
    fmt.Printf("更新了 %d 行\n", rowsAffected)

    // 事务处理
    tx, err := db.Begin()
    if err != nil {
        log.Fatal("开始事务失败:", err)
    }

    // 在事务中执行多个操作
    _, err = tx.Exec("INSERT INTO users (name, email) VALUES ($1, $2)", "Bob", "bob@example.com")
    if err != nil {
        tx.Rollback()
        log.Fatal("事务插入失败:", err)
    }

    _, err = tx.Exec("INSERT INTO users (name, email) VALUES ($1, $2)", "Charlie", "charlie@example.com")
    if err != nil {
        tx.Rollback()
        log.Fatal("事务插入失败:", err)
    }

    err = tx.Commit()
    if err != nil {
        log.Fatal("提交事务失败:", err)
    }

    fmt.Println("事务提交成功")

    // 批量操作
    batchStmt, err := db.Prepare("INSERT INTO users (name, email) VALUES ($1, $2)")
    if err != nil {
        log.Fatal("准备批量语句失败:", err)
    }
    defer batchStmt.Close()

    names := []string{"David", "Eve", "Frank"}
    emails := []string{"david@example.com", "eve@example.com", "frank@example.com"}

    for i := 0; i < len(names); i++ {
        _, err = batchStmt.Exec(names[i], emails[i])
        if err != nil {
            log.Printf("批量插入失败: %v\n", err)
        }
    }

    fmt.Println("批量插入完成")

    // 连接池配置
    db.SetMaxOpenConns(25)        // 最大打开连接数
    db.SetMaxIdleConns(25)        // 最大空闲连接数
    db.SetConnMaxLifetime(5 * time.Minute) // 连接最大生命周期

    fmt.Printf("连接池状态: Open=%d, Idle=%d\n", db.Stats().OpenConnections, db.Stats().Idle)
}
```

## 12. context - 上下文管理

**功能**：上下文管理和控制

**主要功能**：
- 超时控制
- 取消信号传递
- 值传递

**示例**：
```go
package main

import (
    "context"
    "fmt"
    "time"
)

func main() {
    // 基本上下文
    ctx := context.Background()
    fmt.Println("基本上下文:", ctx)

    // 带取消的上下文
    ctxWithCancel, cancel := context.WithCancel(ctx)

    go func() {
        time.Sleep(2 * time.Second)
        cancel() // 2秒后取消
    }()

    select {
    case <-ctxWithCancel.Done():
        fmt.Println("上下文被取消:", ctxWithCancel.Err())
    case <-time.After(3 * time.Second):
        fmt.Println("超时")
    }

    // 带超时的上下文
    ctxWithTimeout, cancel := context.WithTimeout(ctx, 3*time.Second)
    defer cancel()

    select {
    case <-ctxWithTimeout.Done():
        fmt.Println("超时上下文:", ctxWithTimeout.Err())
    }

    // 带截止时间的上下文
    deadline := time.Now().Add(5 * time.Second)
    ctxWithDeadline, cancel := context.WithDeadline(ctx, deadline)
    defer cancel()

    select {
    case <-ctxWithDeadline.Done():
        fmt.Println("截止时间上下文:", ctxWithDeadline.Err())
    }

    // 带值的上下文
    ctxWithValue := context.WithValue(ctx, "key", "value")
    value := ctxWithValue.Value("key")
    fmt.Println("上下文值:", value)

    // 多层上下文
    ctx1 := context.WithValue(ctx, "user", "alice")
    ctx2 := context.WithValue(ctx1, "request-id", "12345")

    fmt.Println("用户:", ctx2.Value("user"))
    fmt.Println("请求ID:", ctx2.Value("request-id"))

    // 实际使用示例
    workerExample()
}

func workerExample() {
    fmt.Println("\n=== 工作协程示例 ===")

    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // 启动多个工作协程
    for i := 0; i < 3; i++ {
        go worker(ctx, i)
    }

    // 模拟一段时间后取消所有工作
    time.Sleep(2 * time.Second)
    cancel()

    // 等待协程完成
    time.Sleep(1 * time.Second)
}

func worker(ctx context.Context, id int) {
    for {
        select {
        case <-ctx.Done():
            fmt.Printf("工作协程 %d 收到取消信号\n", id)
            return
        default:
            fmt.Printf("工作协程 %d 正在工作...\n", id)
            time.Sleep(500 * time.Millisecond)
        }
    }
}
```

## 13. sync - 同步原语

**功能**：并发同步工具

**主要功能**：
- 互斥锁
- 等待组
- 条件变量
- 原子操作

**示例**：
```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
    "time"
)

func main() {
    // 互斥锁示例
    mutexExample()

    // 读写锁示例
    rwMutexExample()

    // 等待组示例
    waitGroupExample()

    // 原子操作示例
    atomicExample()

    // 条件变量示例
    condExample()

    // 单次执行示例
    onceExample()

    // 池示例
    poolExample()
}

func mutexExample() {
    fmt.Println("\n=== 互斥锁示例 ===")

    var counter int
    var mutex sync.Mutex

    var wg sync.WaitGroup
    wg.Add(100)

    for i := 0; i < 100; i++ {
        go func() {
            defer wg.Done()

            mutex.Lock()
            counter++
            mutex.Unlock()
        }()
    }

    wg.Wait()
    fmt.Printf("最终计数器值: %d\n", counter)
}

func rwMutexExample() {
    fmt.Println("\n=== 读写锁示例 ===")

    var data map[string]string = make(map[string]string)
    var rwMutex sync.RWMutex

    var wg sync.WaitGroup

    // 写入者
    wg.Add(1)
    go func() {
        defer wg.Done()

        for i := 0; i < 5; i++ {
            rwMutex.Lock()
            data[fmt.Sprintf("key%d", i)] = fmt.Sprintf("value%d", i)
            rwMutex.Unlock()
            time.Sleep(100 * time.Millisecond)
        }
    }()

    // 读取者
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            rwMutex.RLock()
            fmt.Printf("读取者 %d 读取数据: %v\n", id, data)
            rwMutex.RUnlock()
        }(i)
    }

    wg.Wait()
}

func waitGroupExample() {
    fmt.Println("\n=== 等待组示例 ===")

    var wg sync.WaitGroup

    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            fmt.Printf("协程 %d 开始工作\n", id)
            time.Sleep(time.Duration(id) * 100 * time.Millisecond)
            fmt.Printf("协程 %d 完成工作\n", id)
        }(i)
    }

    fmt.Println("等待所有协程完成...")
    wg.Wait()
    fmt.Println("所有协程已完成")
}

func atomicExample() {
    fmt.Println("\n=== 原子操作示例 ===")

    var counter int64

    var wg sync.WaitGroup
    wg.Add(1000)

    for i := 0; i < 1000; i++ {
        go func() {
            defer wg.Done()
            atomic.AddInt64(&counter, 1)
        }()
    }

    wg.Wait()
    fmt.Printf("原子计数器值: %d\n", counter)

    // 比较并交换
    var value int64 = 100
    swapped := atomic.CompareAndSwapInt64(&value, 100, 200)
    fmt.Printf("交换成功: %t, 新值: %d\n", swapped, value)

    // 加载和存储
    atomic.StoreInt64(&value, 300)
    loaded := atomic.LoadInt64(&value)
    fmt.Printf("存储和加载值: %d\n", loaded)
}

func condExample() {
    fmt.Println("\n=== 条件变量示例 ===")

    var mutex sync.Mutex
    cond := sync.NewCond(&mutex)

    var ready bool

    // 等待者
    go func() {
        mutex.Lock()
        for !ready {
            cond.Wait()
        }
        fmt.Println("条件满足，继续执行")
        mutex.Unlock()
    }()

    // 通知者
    time.Sleep(1 * time.Second)
    mutex.Lock()
    ready = true
    cond.Signal()
    mutex.Unlock()

    time.Sleep(100 * time.Millisecond)
}

func onceExample() {
    fmt.Println("\n=== 单次执行示例 ===")

    var once sync.Once
    var counter int

    increment := func() {
        counter++
        fmt.Printf("函数执行，计数器: %d\n", counter)
    }

    for i := 0; i < 5; i++ {
        go once.Do(increment)
    }

    time.Sleep(100 * time.Millisecond)
    fmt.Printf("最终计数器: %d\n", counter)
}

func poolExample() {
    fmt.Println("\n=== 池示例 ===")

    var pool = sync.Pool{
        New: func() interface{} {
            return make([]byte, 1024)
        },
    }

    // 获取对象
    buf := pool.Get().([]byte)
    fmt.Printf("获取缓冲区，容量: %d\n", cap(buf))

    // 使用对象
    buf = append(buf, []byte("Hello, Pool!")...)

    // 放回对象
    pool.Put(buf)

    // 再次获取
    buf2 := pool.Get().([]byte)
    fmt.Printf("再次获取缓冲区，内容: %s\n", string(buf2))

    // 清理并放回
    buf2 = buf2[:0]
    pool.Put(buf2)
}
```

## 14. log - 日志记录

**功能**：简单的日志记录功能

**主要功能**：
- 基本日志输出
- 日志级别控制
- 自定义日志格式

**示例**：
```go
package main

import (
    "log"
    "os"
)

func main() {
    // 基本日志
    log.Println("这是一条普通日志")
    log.Printf("格式化日志: %s, %d\n", "Hello", 42)

    // 不同级别的日志
    log.Fatal("致命错误，程序将退出") // 这会调用os.Exit(1)
    // log.Panic("恐慌错误，程序会panic")

    // 自定义日志格式
    log.SetFlags(log.LstdFlags | log.Lshortfile)
    log.Println("带文件名的日志")

    // 自定义前缀
    log.SetPrefix("[MYAPP] ")
    log.Println("带前缀的日志")

    // 输出到文件
    file, err := os.OpenFile("app.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
    if err != nil {
        log.Fatal("打开日志文件失败:", err)
    }
    defer file.Close()

    log.SetOutput(file)
    log.Println("这条日志会写入文件")

    // 创建不同的日志器
    infoLog := log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)
    errorLog := log.New(os.Stderr, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)

    infoLog.Println("这是一条信息日志")
    errorLog.Println("这是一条错误日志")
}
```

## 15. flag - 命令行参数解析

**功能**：命令行参数解析

**主要功能**：
- 参数定义和解析
- 帮助信息生成
- 子命令支持

**示例**：
```go
package main

import (
    "flag"
    "fmt"
    "os"
)

func main() {
    // 基本参数
    name := flag.String("name", "World", "姓名")
    age := flag.Int("age", 0, "年龄")
    verbose := flag.Bool("verbose", false, "详细输出")

    // 自定义类型
    var interval DurationFlag
    flag.Var(&interval, "interval", "时间间隔")

    flag.Parse()

    // 使用参数
    fmt.Printf("姓名: %s\n", *name)
    fmt.Printf("年龄: %d\n", *age)
    fmt.Printf("详细输出: %t\n", *verbose)
    fmt.Printf("时间间隔: %v\n", time.Duration(interval))

    // 非标志参数
    args := flag.Args()
    fmt.Printf("其他参数: %v\n", args)

    // 子命令示例
    if len(args) > 0 {
        switch args[0] {
        case "hello":
            fmt.Printf("Hello, %s!\n", *name)
        case "goodbye":
            fmt.Printf("Goodbye, %s!\n", *name)
        }
    }
}

// 自定义标志类型
type DurationFlag time.Duration

func (d *DurationFlag) String() string {
    return time.Duration(*d).String()
}

func (d *DurationFlag) Set(value string) error {
    duration, err := time.ParseDuration(value)
    if err != nil {
        return err
    }
    *d = DurationFlag(duration)
    return nil
}
```

## 16. reflect - 反射

**功能**：运行时反射

**主要功能**：
- 类型检查
- 值操作
- 方法调用

**示例**：
```go
package main

import (
    "fmt"
    "reflect"
)

type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}

func (p Person) Greet() string {
    return fmt.Sprintf("Hello, %s!", p.Name)
}

func main() {
    // 类型反射
    var x float64 = 3.14
    fmt.Println("类型:", reflect.TypeOf(x))
    fmt.Println("值:", reflect.ValueOf(x))

    // 结构体反射
    p := Person{Name: "Alice", Age: 25}
    v := reflect.ValueOf(p)
    t := reflect.TypeOf(p)

    fmt.Println("结构体类型:", t)
    fmt.Println("结构体值:", v)

    // 字段遍历
    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        value := v.Field(i)
        fmt.Printf("字段 %d: %s (%s) = %v\n", i, field.Name, field.Type, value)

        // 获取标签
        tag := field.Tag.Get("json")
        fmt.Printf("  JSON标签: %s\n", tag)
    }

    // 方法调用
    method := v.MethodByName("Greet")
    if method.IsValid() {
        result := method.Call(nil)
        fmt.Println("方法调用结果:", result[0])
    }

    // 创建新值
    newPerson := reflect.New(t).Elem()
    newPerson.FieldByName("Name").SetString("Bob")
    newPerson.FieldByName("Age").SetInt(30)

    fmt.Println("新创建的Person:", newPerson.Interface())

    // 接口类型检查
    var iface interface{} = p
    if ifaceValue := reflect.ValueOf(iface); ifaceValue.IsValid() {
        fmt.Println("接口值:", ifaceValue)
        fmt.Println("接口类型:", ifaceValue.Type())
    }

    // 切片反射
    slice := []int{1, 2, 3}
    sliceValue := reflect.ValueOf(slice)
    fmt.Println("切片长度:", sliceValue.Len())

    for i := 0; i < sliceValue.Len(); i++ {
        fmt.Printf("切片[%d] = %v\n", i, sliceValue.Index(i).Interface())
    }

    // 映射反射
    m := map[string]int{"a": 1, "b": 2}
    mapValue := reflect.ValueOf(m)

    for _, key := range mapValue.MapKeys() {
        value := mapValue.MapIndex(key)
        fmt.Printf("映射[%v] = %v\n", key.Interface(), value.Interface())
    }
}
```

## 17. testing - 测试框架

**功能**：Go语言内置的测试框架

**主要功能**：
- 单元测试
- 基准测试
- 示例测试

**示例**：
```go
package math

import "testing"

// 待测试的函数
func Add(a, b int) int {
    return a + b
}

func Multiply(a, b int) int {
    return a * b
}

// 单元测试
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"正数相加", 2, 3, 5},
        {"负数相加", -1, -1, -2},
        {"零相加", 0, 0, 0},
        {"正负相加", 5, -3, 2},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; 期望 %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}

// 基准测试
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(i, i+1)
    }
}

func BenchmarkMultiply(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Multiply(i, i+1)
    }
}

// 示例测试
func ExampleAdd() {
    result := Add(2, 3)
    fmt.Println(result)
    // Output: 5
}

// 并发测试
func TestConcurrentAdd(t *testing.T) {
    const goroutines = 100
    done := make(chan bool, goroutines)

    for i := 0; i < goroutines; i++ {
        go func() {
            defer func() { done <- true }()

            result := Add(i, i+1)
            expected := 2*i + 1
            if result != expected {
                t.Errorf("Add(%d, %d) = %d; 期望 %d", i, i+1, result, expected)
            }
        }()
    }

    for i := 0; i < goroutines; i++ {
        <-done
    }
}
```

## 18. sort - 排序算法

**功能**：排序相关功能

**主要功能**：
- 基本类型排序
- 自定义排序
- 搜索算法

**示例**：
```go
package main

import (
    "fmt"
    "sort"
)

type Person struct {
    Name string
    Age  int
}

type ByAge []Person
type ByName []Person

func (a ByAge) Len() int           { return len(a) }
func (a ByAge) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByAge) Less(i, j int) bool { return a[i].Age < a[j].Age }

func (a ByName) Len() int           { return len(a) }
func (a ByName) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByName) Less(i, j int) bool { return a[i].Name < a[j].Name }

func main() {
    // 基本类型排序
    numbers := []int{5, 2, 8, 1, 9, 3}
    sort.Ints(numbers)
    fmt.Println("排序后的整数:", numbers)

    strings := []string{"banana", "apple", "orange", "grape"}
    sort.Strings(strings)
    fmt.Println("排序后的字符串:", strings)

    // 逆序排序
    sort.Sort(sort.Reverse(sort.IntSlice(numbers)))
    fmt.Println("逆序排序:", numbers)

    // 重新正序排序
    sort.Ints(numbers)

    // 搜索
    index := sort.SearchInts(numbers, 8)
    fmt.Println("搜索8的位置:", index)

    // 检查是否已排序
    isSorted := sort.IntsAreSorted(numbers)
    fmt.Println("是否已排序:", isSorted)

    // 自定义类型排序
    people := []Person{
        {"Alice", 25},
        {"Bob", 30},
        {"Charlie", 20},
    }

    // 按年龄排序
    sort.Sort(ByAge(people))
    fmt.Println("按年龄排序:", people)

    // 按姓名排序
    sort.Sort(ByName(people))
    fmt.Println("按姓名排序:", people)

    // 使用sort.Slice
    sort.Slice(people, func(i, j int) bool {
        return people[i].Age < people[j].Age
    })
    fmt.Println("使用sort.Slice按年龄排序:", people)

    // 稳定排序
    data := []struct {
        Name string
        Rank int
    }{
        {"Alice", 2},
        {"Bob", 1},
        {"Charlie", 2},
        {"David", 1},
    }

    // 先按rank排序
    sort.Slice(data, func(i, j int) bool {
        return data[i].Rank < data[j].Rank
    })
    fmt.Println("按rank排序:", data)

    // 稳定排序保持相同rank的原始顺序
    sort.SliceStable(data, func(i, j int) bool {
        return data[i].Rank < data[j].Rank
    })
    fmt.Println("稳定排序:", data)
}
```

## 标准库使用最佳实践

### 1. 错误处理
```go
// 使用errors包进行错误处理
import "errors"

func process(data string) error {
    if data == "" {
        return errors.New("empty data")
    }

    // 处理逻辑
    return nil
}

// 自定义错误类型
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}
```

### 2. 并发安全
```go
// 使用sync包确保并发安全
type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}
```

### 3. 资源管理
```go
// 使用defer确保资源释放
func readFile(filename string) ([]byte, error) {
    file, err := os.Open(filename)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    return io.ReadAll(file)
}
```

### 4. 性能优化
```go
// 使用bytes.Buffer进行字符串拼接
func buildString(parts []string) string {
    var buffer bytes.Buffer
    for _, part := range parts {
        buffer.WriteString(part)
    }
    return buffer.String()
}

// 使用sync.Pool减少内存分配
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func processData(data []byte) {
    buf := bufferPool.Get().(*bytes.Buffer)
    buf.Reset()
    defer bufferPool.Put(buf)

    buf.Write(data)
    // 处理逻辑
}
```

## 标准库总结

Go标准库提供了丰富的功能，涵盖了：

1. **基础数据结构**：strings, strconv, math, sort
2. **I/O操作**：io, bufio, os, fmt
3. **网络编程**：net, net/http, net/url
4. **数据库**：database/sql
5. **并发控制**：sync, context
6. **时间处理**：time
7. **编码解码**：encoding/json, encoding/xml
8. **测试**：testing
9. **反射**：reflect
10. **日志**：log

掌握这些标准库的使用是Go开发的基础，能够帮助你高效地完成各种编程任务。