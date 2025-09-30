# Go 标准库：fmt 和 io 包 - 从PHP视角理解

## 📚 概述

Go的标准库是其核心优势之一，`fmt`和`io`包是Go开发中最常用的基础包。作为PHP开发者，理解这些包的使用模式对于掌握Go的输入输出操作至关重要。

### 🎯 学习目标
- 掌握`fmt`包的格式化输入输出
- 理解`io`包的接口和操作
- 学会文件和缓冲区操作
- 熟悉Go的I/O与PHP的差异

## 🔄 Go vs PHP I/O 对比

### PHP 输出操作
```php
<?php
// 基本输出
echo "Hello, World!";
print "Hello, World!";
printf("Hello, %s!", $name);

// 格式化输出
$formatted = sprintf("用户: %s, 年龄: %d", $name, $age);
var_dump($variable);
print_r($array);

// 文件操作
$content = file_get_contents('file.txt');
file_put_contents('file.txt', $content);
$lines = file('file.txt');

// 文件句柄操作
$handle = fopen('file.txt', 'r');
fwrite($handle, "Hello World");
$content = fread($handle, 1024);
fclose($handle);
```

### Go I/O 操作
```go
// 基本输出
fmt.Println("Hello, World!")
fmt.Printf("Hello, %s!\n", name)

// 格式化输出
formatted := fmt.Sprintf("用户: %s, 年龄: %d", name, age)
fmt.Printf("%+v\n", variable) // 详细输出
fmt.Printf("%#v\n", variable) // Go语法格式

// 文件操作
content, err := os.ReadFile("file.txt")
if err != nil {
    log.Fatal(err)
}
err = os.WriteFile("file.txt", content, 0644)

// 文件句柄操作
file, err := os.Open("file.txt")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

writer := bufio.NewWriter(file)
writer.WriteString("Hello World")
writer.Flush()
```

## 📝 fmt 包详解

### 1. 基础输出函数

#### Print 系列函数
```go
package main

import "fmt"

func basicOutput() {
    // Print - 不换行输出
    fmt.Print("Hello, ")
    fmt.Print("World!")
    // 输出: Hello, World!

    // Println - 自动换行输出
    fmt.Println("Hello, World!")
    // 输出: Hello, World!

    // Printf - 格式化输出
    name := "Alice"
    age := 25
    fmt.Printf("姓名: %s, 年龄: %d\n", name, age)
    // 输出: 姓名: Alice, 年龄: 25
}
```

#### 格式化动词
```go
func formattingVerbs() {
    // 通用格式
    v := 42
    fmt.Printf("%v\n", v)    // 默认格式: 42
    fmt.Printf("%+v\n", v)   // 显示字段名: 42
    fmt.Printf("%#v\n", v)   // Go语法格式: 42
    fmt.Printf("%T\n", v)    // 类型: int

    // 整数格式
    fmt.Printf("%d\n", 42)        // 十进制: 42
    fmt.Printf("%b\n", 42)        // 二进制: 101010
    fmt.Printf("%o\n", 42)        // 八进制: 52
    fmt.Printf("%x\n", 42)        // 十六进制: 2a
    fmt.Printf("%X\n", 42)        // 大写十六进制: 2A

    // 浮点数格式
    fmt.Printf("%f\n", 3.14159)   // 默认浮点数: 3.141590
    fmt.Printf("%.2f\n", 3.14159) // 2位小数: 3.14
    fmt.Printf("%e\n", 3.14159)   // 科学计数法: 3.141590e+00
    fmt.Printf("%E\n", 3.14159)   // 大写科学计数法: 3.141590E+00

    // 字符串格式
    fmt.Printf("%s\n", "hello")    // 字符串: hello
    fmt.Printf("%q\n", "hello")   // 引用字符串: "hello"
    fmt.Printf("%x\n", "hello")   // 十六进制: 68656c6c6f

    // 布尔值
    fmt.Printf("%t\n", true)      // 布尔值: true

    // 指针
    ptr := &v
    fmt.Printf("%p\n", ptr)       // 指针地址: 0x...
}
```

#### Sprintf 和 Fprintf
```go
func stringAndFileFormatting() {
    // Sprintf - 格式化到字符串
    name := "Bob"
    age := 30
    message := fmt.Sprintf("用户信息 - 姓名: %s, 年龄: %d", name, age)
    fmt.Println(message)

    // Fprintf - 格式化到文件
    file, err := os.Create("output.txt")
    if err != nil {
        log.Fatal(err)
    }
    defer file.Close()

    fmt.Fprintf(file, "日志时间: %s\n", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Fprintf(file, "操作内容: %s\n", "用户登录")
}
```

### 2. 输入函数

#### Scan 系列函数
```go
func inputOperations() {
    // Scan - 从标准输入读取
    var name string
    var age int

    fmt.Print("请输入姓名: ")
    fmt.Scan(&name)

    fmt.Print("请输入年龄: ")
    fmt.Scan(&age)

    fmt.Printf("姓名: %s, 年龄: %d\n", name, age)

    // Scanln - 读取到换行符
    var city string
    fmt.Print("请输入城市: ")
    fmt.Scanln(&city)

    // Scanf - 格式化读取
    var country string
    var population int
    fmt.Print("请输入国家名和人口(格式: 国家 人口): ")
    fmt.Scanf("%s %d", &country, &population)
}
```

### 3. 错误格式化

#### Errorf 函数
```go
func errorFormatting() {
    // 基础错误格式化
    err := fmt.Errorf("文件未找到: %s", "config.json")
    fmt.Println(err)

    // 带上下文的错误
    id := 123
    err = fmt.Errorf("用户ID %d 不存在", id)
    fmt.Println(err)

    // 错误包装
    originalErr := os.ErrNotExist
    wrappedErr := fmt.Errorf("配置文件错误: %w", originalErr)
    fmt.Println(wrappedErr)
}
```

## 📝 io 包详解

### 1. 基础接口

#### Reader 接口
```go
// Reader 接口定义
type Reader interface {
    Read(p []byte) (n int, err error)
}

// 实现 Reader 接口
type StringReader struct {
    data string
    pos  int
}

func (sr *StringReader) Read(p []byte) (n int, err error) {
    if sr.pos >= len(sr.data) {
        return 0, io.EOF
    }

    n = copy(p, sr.data[sr.pos:])
    sr.pos += n
    return n, nil
}

func usingReader() {
    reader := &StringReader{data: "Hello, World!"}

    buffer := make([]byte, 32)
    n, err := reader.Read(buffer)
    if err != nil && err != io.EOF {
        log.Fatal(err)
    }

    fmt.Printf("读取了 %d 个字节: %s\n", n, buffer[:n])
}
```

#### Writer 接口
```go
// Writer 接口定义
type Writer interface {
    Write(p []byte) (n int, err error)
}

// 实现 Writer 接口
type ConsoleWriter struct{}

func (cw *ConsoleWriter) Write(p []byte) (n int, err error) {
    fmt.Print(string(p))
    return len(p), nil
}

func usingWriter() {
    writer := &ConsoleWriter{}

    data := []byte("Hello, Writer!")
    n, err := writer.Write(data)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("写入了 %d 个字节\n", n)
}
```

### 2. 常用 I/O 操作

#### Copy 操作
```go
func copyOperations() {
    // 从文件复制到标准输出
    src, err := os.Open("input.txt")
    if err != nil {
        log.Fatal(err)
    }
    defer src.Close()

    _, err = io.Copy(os.Stdout, src)
    if err != nil {
        log.Fatal(err)
    }

    // 带缓冲的复制
    dst, err := os.Create("output.txt")
    if err != nil {
        log.Fatal(err)
    }
    defer dst.Close()

    buffer := make([]byte, 32*1024) // 32KB 缓冲区
    _, err = io.CopyBuffer(dst, src, buffer)
    if err != nil {
        log.Fatal(err)
    }
}
```

#### LimitReader 操作
```go
func limitReaderExample() {
    // 限制读取的字节数
    data := strings.NewReader("这是一段测试文本，用来演示LimitReader的功能")

    // 只读取前10个字节
    limitedReader := io.LimitReader(data, 10)

    buffer := make([]byte, 100)
    n, err := limitedReader.Read(buffer)
    if err != nil && err != io.EOF {
        log.Fatal(err)
    }

    fmt.Printf("限制读取了 %d 个字节: %s\n", n, buffer[:n])
}
```

### 3. 多重读写器

#### MultiReader 和 MultiWriter
```go
func multiReaderWriterExample() {
    // MultiReader - 合并多个Reader
    r1 := strings.NewReader("Hello, ")
    r2 := strings.NewReader("World!")

    multiReader := io.MultiReader(r1, r2)

    data, err := io.ReadAll(multiReader)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("合并读取: %s\n", string(data))

    // MultiWriter - 同时写入多个Writer
    var buf1, buf2 bytes.Buffer

    multiWriter := io.MultiWriter(&buf1, &buf2)

    _, err = multiWriter.Write([]byte("同时写入多个Writer"))
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("缓冲区1: %s\n", buf1.String())
    fmt.Printf("缓冲区2: %s\n", buf2.String())
}
```

### 4. TeeReader 操作
```go
func teeReaderExample() {
    // TeeReader - 复制读取的数据到Writer
    src := strings.NewReader("TeeReader示例文本")

    var buf bytes.Buffer

    teeReader := io.TeeReader(src, &buf)

    // 读取数据，同时会复制到buf
    data, err := io.ReadAll(teeReader)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("读取的数据: %s\n", string(data))
    fmt.Printf("复制到缓冲区: %s\n", buf.String())
}
```

## 📝 实际应用场景

### 1. 文件处理工具
```go
package main

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "strings"
)

// 文件内容搜索工具
type FileSearcher struct {
    keyword string
    matches []string
}

func NewFileSearcher(keyword string) *FileSearcher {
    return &FileSearcher{
        keyword: keyword,
        matches: make([]string, 0),
    }
}

func (fs *FileSearcher) SearchFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    lineNum := 0

    for scanner.Scan() {
        lineNum++
        line := scanner.Text()

        if strings.Contains(line, fs.keyword) {
            match := fmt.Sprintf("%s:%d: %s", filename, lineNum, line)
            fs.matches = append(fs.matches, match)
        }
    }

    return scanner.Err()
}

func (fs *FileSearcher) SearchDirectory(dir string) error {
    return filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }

        if !info.IsDir() && strings.HasSuffix(path, ".go") {
            if err := fs.SearchFile(path); err != nil {
                fmt.Printf("搜索文件 %s 时出错: %v\n", path, err)
            }
        }

        return nil
    })
}

func (fs *FileSearcher) PrintResults() {
    fmt.Printf("搜索 '%s' 的结果:\n", fs.keyword)
    for _, match := range fs.matches {
        fmt.Println(match)
    }
    fmt.Printf("共找到 %d 个匹配项\n", len(fs.matches))
}

func main() {
    if len(os.Args) < 3 {
        fmt.Println("用法: ./searcher <关键词> <目录>")
        os.Exit(1)
    }

    keyword := os.Args[1]
    directory := os.Args[2]

    searcher := NewFileSearcher(keyword)
    if err := searcher.SearchDirectory(directory); err != nil {
        fmt.Printf("搜索出错: %v\n", err)
        os.Exit(1)
    }

    searcher.PrintResults()
}
```

### 2. 日志处理器
```go
package main

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "time"
)

type Logger struct {
    file   *os.File
    writer io.Writer
}

func NewLogger(filename string) (*Logger, error) {
    file, err := os.OpenFile(filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        return nil, err
    }

    // 同时输出到文件和控制台
    writer := io.MultiWriter(file, os.Stdout)

    return &Logger{
        file:   file,
        writer: writer,
    }, nil
}

func (l *Logger) Log(level, message string) {
    timestamp := time.Now().Format("2006-01-02 15:04:05")
    logEntry := fmt.Sprintf("[%s] [%s] %s\n", timestamp, level, message)

    fmt.Fprint(l.writer, logEntry)
}

func (l *Logger) Info(message string) {
    l.Log("INFO", message)
}

func (l *Logger) Error(message string) {
    l.Log("ERROR", message)
}

func (l *Logger) Close() error {
    return l.file.Close()
}

func main() {
    logger, err := NewLogger("app.log")
    if err != nil {
        fmt.Printf("创建日志器失败: %v\n", err)
        os.Exit(1)
    }
    defer logger.Close()

    logger.Info("应用程序启动")
    logger.Error("这是一个错误消息")
    logger.Info("应用程序关闭")
}
```

### 3. 进度条显示
```go
package main

import (
    "fmt"
    "io"
    "os"
    "strings"
)

type ProgressBar struct {
    total     int64
    current   int64
    width     int
    writer    io.Writer
}

func NewProgressBar(total int64, width int) *ProgressBar {
    return &ProgressBar{
        total:  total,
        width:  width,
        writer: os.Stdout,
    }
}

func (pb *ProgressBar) Write(p []byte) (int, error) {
    n := len(p)
    pb.current += int64(n)
    pb.render()
    return n, nil
}

func (pb *ProgressBar) render() {
    percentage := float64(pb.current) / float64(pb.total) * 100
    completed := int(percentage * float64(pb.width) / 100)

    bar := strings.Repeat("=", completed) + strings.Repeat(" ", pb.width-completed)

    fmt.Fprintf(pb.writer, "\r[%s] %.2f%% (%d/%d bytes)",
        bar, percentage, pb.current, pb.total)

    if pb.current >= pb.total {
        fmt.Fprintln(pb.writer)
    }
}

func main() {
    // 模拟文件复制进度
    src, err := os.Open("large_file.txt")
    if err != nil {
        fmt.Printf("打开文件失败: %v\n", err)
        return
    }
    defer src.Close()

    dst, err := os.Create("copy_large_file.txt")
    if err != nil {
        fmt.Printf("创建文件失败: %v\n", err)
        return
    }
    defer dst.Close()

    // 获取文件大小
    fileInfo, err := src.Stat()
    if err != nil {
        fmt.Printf("获取文件信息失败: %v\n", err)
        return
    }

    // 创建进度条
    progressBar := NewProgressBar(fileInfo.Size(), 50)

    // 复制文件并显示进度
    _, err = io.Copy(dst, io.TeeReader(src, progressBar))
    if err != nil {
        fmt.Printf("复制文件失败: %v\n", err)
        return
    }

    fmt.Println("文件复制完成!")
}
```

## 🧪 实践练习

### 练习1: 格式化输出工具
```go
package main

import (
    "fmt"
    "os"
    "reflect"
)

type Person struct {
    Name string
    Age  int
    City string
}

func (p Person) String() string {
    return fmt.Sprintf("Person{Name: %s, Age: %d, City: %s}", p.Name, p.Age, p.City)
}

func main() {
    person := Person{
        Name: "张三",
        Age:  25,
        City: "北京",
    }

    // 练习不同的格式化方式
    fmt.Printf("默认格式: %v\n", person)
    fmt.Printf("详细格式: %+v\n", person)
    fmt.Printf("Go语法格式: %#v\n", person)
    fmt.Printf("类型: %T\n", person)
    fmt.Printf("String方法: %s\n", person)

    // 练习类型检查
    checkType(42)
    checkType(3.14)
    checkType("hello")
    checkType(true)
    checkType(person)
}

func checkType(v interface{}) {
    t := reflect.TypeOf(v)
    switch t.Kind() {
    case reflect.Int:
        fmt.Printf("%d 是整型\n", v)
    case reflect.Float64:
        fmt.Printf("%f 是浮点型\n", v)
    case reflect.String:
        fmt.Printf("%s 是字符串型\n", v)
    case reflect.Bool:
        fmt.Printf("%t 是布尔型\n", v)
    case reflect.Struct:
        fmt.Printf("%v 是结构体型\n", v)
    default:
        fmt.Printf("%v 是其他类型\n", v)
    }
}
```

### 练习2: I/O 操作组合
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
    // 创建测试数据
    testData := "这是第一行。\n这是第二行。\n这是第三行。\n"

    // 练习1: 使用bytes.Buffer
    var buf bytes.Buffer
    buf.WriteString("缓冲区内容开始\n")
    buf.WriteString(testData)
    buf.WriteString("缓冲区内容结束\n")

    fmt.Println("Buffer内容:")
    fmt.Println(buf.String())

    // 练习2: 使用strings.Reader
    reader := strings.NewReader(testData)

    fmt.Println("\n读取的内容:")
    readBuf := make([]byte, 10)
    for {
        n, err := reader.Read(readBuf)
        if err != nil && err != io.EOF {
            fmt.Printf("读取错误: %v\n", err)
            break
        }
        if n == 0 {
            break
        }
        fmt.Printf("读取了 %d 字节: %q\n", n, readBuf[:n])
    }

    // 练习3: I/O 组合
    fmt.Println("\nI/O 组合示例:")

    // 创建多个Reader
    r1 := strings.NewReader("Hello, ")
    r2 := strings.NewReader("World!")
    r3 := strings.NewReader(" Go!")

    // 合并Reader
    multiReader := io.MultiReader(r1, r2, r3)

    // 读取合并后的内容
    combined, err := io.ReadAll(multiReader)
    if err != nil {
        fmt.Printf("读取失败: %v\n", err)
        return
    }

    fmt.Printf("合并后的内容: %s\n", string(combined))

    // 练习4: TeeReader
    fmt.Println("\nTeeReader示例:")

    source := strings.NewReader("这是TeeReader的测试数据")
    var teeBuffer bytes.Buffer

    teeReader := io.TeeReader(source, &teeBuffer)

    // 从TeeReader读取
    result, err := io.ReadAll(teeReader)
    if err != nil {
        fmt.Printf("读取失败: %v\n", err)
        return
    }

    fmt.Printf("从TeeReader读取: %s\n", string(result))
    fmt.Printf("TeeWriter缓冲区: %s\n", teeBuffer.String())
}
```

## 📋 最佳实践

### 1. 格式化输出最佳实践
- 使用`fmt.Sprintf`创建格式化字符串，避免字符串拼接
- 在错误消息中使用`fmt.Errorf`提供详细的错误信息
- 对于调试，使用`%+v`和`%#v`获取详细的结构信息
- 使用`%T`进行类型检查和调试

### 2. I/O 操作最佳实践
- 使用`defer`确保文件句柄正确关闭
- 使用`bufio.Reader`和`bufio.Writer`提高I/O性能
- 处理大文件时使用缓冲区避免内存问题
- 使用`io.Copy`进行高效的文件复制

### 3. 错误处理最佳实践
- 始终检查I/O操作的错误返回值
- 使用`io.EOF`判断读取结束
- 使用`errors.Is`和`errors.As`进行错误类型判断
- 提供有意义的错误上下文信息

### 4. 性能优化建议
- 对于频繁的字符串操作，使用`strings.Builder`代替字符串拼接
- 使用`io.LimitReader`限制读取的字节数，防止内存溢出
- 使用`io.Pipe`进行流式处理，避免大内存分配
- 使用`sync.Pool`重用缓冲区对象

## 📋 检查清单

- [ ] 掌握fmt包的基础输出函数
- [ ] 理解格式化动词的使用
- [ ] 学会输入函数的使用
- [ ] 掌握io包的核心接口
- [ ] 理解Reader和Writer的实现
- [ ] 学会使用常用的I/O组合操作
- [ ] 掌握文件处理技巧
- [ ] 理解错误处理机制
- [ ] 能够创建实用的I/O工具
- [ ] 了解Go I/O与PHP的差异

## 🚀 下一步

掌握fmt和io包后，你可以继续学习：
- **net/http包**: Web应用开发
- **encoding/json包**: JSON数据处理
- **database/sql包**: 数据库操作
- **Gin框架**: 高性能Web框架

---

**学习提示**: Go的fmt和io包提供了强大而灵活的I/O操作能力。相比于PHP的简单输出函数，Go的I/O系统更加类型安全和高效。通过接口设计，Go的I/O操作具有极强的可组合性和扩展性。掌握这些基础包是成为Go开发者的关键一步。

*最后更新: 2025年9月*