# Go 标准库：encoding/json 包 - 从PHP视角理解

## 📚 概述

JSON是现代Web应用中最常用的数据交换格式。Go的`encoding/json`包提供了强大的JSON编码和解码功能，与PHP的JSON处理相比，Go采用了更类型安全和高效的方式。

### 🎯 学习目标
- 掌握Go的JSON编码和解码
- 理解结构体标签的使用
- 学会处理复杂的JSON数据
- 熟悉Go JSON处理与PHP的差异

## 🔄 Go vs PHP JSON处理对比

### PHP JSON处理
```php
<?php
// PHP数组转JSON
$data = [
    'name' => 'John Doe',
    'age' => 30,
    'email' => 'john@example.com',
    'hobbies' => ['reading', 'swimming', 'coding']
];

$jsonString = json_encode($data, JSON_PRETTY_PRINT);
echo $jsonString;

// JSON转PHP数组
$jsonString = '{"name":"John Doe","age":30,"email":"john@example.com"}';
$data = json_decode($jsonString, true); // true表示转换为关联数组

// 处理JSON错误
if (json_last_error() !== JSON_ERROR_NONE) {
    echo "JSON错误: " . json_last_error_msg();
}

// 对象处理
class User {
    public $name;
    public $age;
    public $email;

    public function __construct($name, $age, $email) {
        $this->name = $name;
        $this->age = $age;
        $this->email = $email;
    }
}

$user = new User('Jane Doe', 25, 'jane@example.com');
$jsonUser = json_encode($user);
```

### Go JSON处理
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
)

// 定义结构体
type User struct {
    Name    string   `json:"name"`
    Age     int      `json:"age"`
    Email   string   `json:"email"`
    Hobbies []string `json:"hobbies,omitempty"`
}

func main() {
    // 结构体转JSON
    user := User{
        Name:    "John Doe",
        Age:     30,
        Email:   "john@example.com",
        Hobbies: []string{"reading", "swimming", "coding"},
    }

    jsonData, err := json.MarshalIndent(user, "", "  ")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(string(jsonData))

    // JSON转结构体
    jsonString := `{"name":"Jane Doe","age":25,"email":"jane@example.com"}`
    var user2 User
    if err := json.Unmarshal([]byte(jsonString), &user2); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("%+v\n", user2)
}
```

## 📝 JSON 编码 (Marshaling)

### 1. 基础结构体编码
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
)

type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
    City string `json:"city"`
}

func basicMarshaling() {
    person := Person{
        Name: "张三",
        Age:  25,
        City: "北京",
    }

    // 基础编码
    jsonData, err := json.Marshal(person)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("基础编码: %s\n", jsonData)

    // 格式化编码
    jsonData, err = json.MarshalIndent(person, "", "  ")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("格式化编码:\n%s\n", jsonData)
}
```

### 2. 结构体标签详解
```go
type Product struct {
    ID          int     `json:"id"`                    // 标准字段名
    Name        string  `json:"product_name"`         // 自定义字段名
    Price       float64 `json:"price,omitempty"`      // omitempty: 值为空时省略
    Description string  `json:"description,omitempty"`
    InStock     bool    `json:"in_stock"`              // 布尔值
    CreatedAt   string  `json:"created_at"`            // 时间戳
    UpdatedAt   string  `json:"updated_at,omitempty"`

    // 忽略字段
    InternalCode string `json:"-"`                     // - 表示忽略该字段

    // 字符串选项
    DisplayName string `json:"display_name,string"`     // 字符串化

    // 空值处理
    Category *string `json:"category,omitempty"`        // 指针类型可以更好处理空值
}

func tagExamples() {
    category := "electronics"
    product := Product{
        ID:          1,
        Name:        "智能手机",
        Price:       2999.99,
        InStock:     true,
        CreatedAt:   "2025-01-01T00:00:00Z",
        InternalCode: "P001",
        Category:    &category,
    }

    jsonData, _ := json.MarshalIndent(product, "", "  ")
    fmt.Printf("产品JSON:\n%s\n", jsonData)

    // 空值测试
    emptyProduct := Product{
        ID:        2,
        Name:      "缺货产品",
        InStock:   false,
        CreatedAt: "2025-01-02T00:00:00Z",
    }

    jsonData, _ = json.MarshalIndent(emptyProduct, "", "  ")
    fmt.Printf("缺货产品JSON:\n%s\n", jsonData)
}
```

### 3. 复杂类型编码
```go
type Address struct {
    Street  string `json:"street"`
    City    string `json:"city"`
    Country string `json:"country"`
}

type Employee struct {
    ID      int      `json:"id"`
    Name    string   `json:"name"`
    Email   string   `json:"email"`
    Skills  []string `json:"skills"`
    Address Address  `json:"address"`
    Manager *Employee `json:"manager,omitempty"` // 嵌套结构
    Meta    map[string]interface{} `json:"meta"`   // 动态字段
}

func complexMarshaling() {
    manager := &Employee{
        ID:    1,
        Name:  "李经理",
        Email: "manager@company.com",
    }

    employee := Employee{
        ID:    2,
        Name:  "王员工",
        Email: "employee@company.com",
        Skills: []string{"Go", "Python", "Docker"},
        Address: Address{
            Street:  "科技路123号",
            City:    "北京",
            Country: "中国",
        },
        Manager: manager,
        Meta: map[string]interface{}{
            "department": "研发部",
            "level":      "高级",
            "salary":     15000.0,
            "join_date":  "2023-01-15",
        },
    }

    jsonData, err := json.MarshalIndent(employee, "", "  ")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("复杂结构JSON:\n%s\n", jsonData)
}
```

### 4. 自定义编码逻辑
```go
type DateTime struct {
    time.Time
}

// 实现json.Marshaler接口
func (dt DateTime) MarshalJSON() ([]byte, error) {
    return json.Marshal(dt.Time.Format("2006-01-02 15:04:05"))
}

type User struct {
    ID       int      `json:"id"`
    Name     string   `json:"name"`
    Email    string   `json:"email"`
    Tags     []string `json:"tags"`
    JoinDate DateTime `json:"join_date"`
}

func customMarshaling() {
    user := User{
        ID:    1,
        Name:  "张三",
        Email: "zhangsan@example.com",
        Tags:  []string{"developer", "golang"},
        JoinDate: DateTime{
            Time: time.Date(2023, 1, 15, 0, 0, 0, 0, time.UTC),
        },
    }

    jsonData, err := json.MarshalIndent(user, "", "  ")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("自定义编码JSON:\n%s\n", jsonData)
}
```

## 📝 JSON 解码 (Unmarshaling)

### 1. 基础解码
```go
func basicUnmarshaling() {
    jsonString := `{
        "id": 1,
        "name": "李四",
        "age": 30,
        "city": "上海"
    }`

    var person Person
    if err := json.Unmarshal([]byte(jsonString), &person); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("解码结果: %+v\n", person)

    // 使用指针接收
    var person2 *Person
    if err := json.Unmarshal([]byte(jsonString), &person2); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("指针解码结果: %+v\n", person2)
}
```

### 2. 动态解码
```go
func dynamicUnmarshaling() {
    // 解码到interface{}
    jsonString := `{
        "name": "产品",
        "price": 99.99,
        "in_stock": true,
        "tags": ["electronics", "gadget"],
        "specs": {
            "cpu": "Intel i7",
            "ram": "16GB"
        }
    }`

    var data interface{}
    if err := json.Unmarshal([]byte(jsonString), &data); err != nil {
        log.Fatal(err)
    }

    // 类型断言处理
    if obj, ok := data.(map[string]interface{}); ok {
        fmt.Printf("产品名称: %v\n", obj["name"])
        fmt.Printf("产品价格: %v\n", obj["price"])
        fmt.Printf("是否库存: %v\n", obj["in_stock"])

        if tags, ok := obj["tags"].([]interface{}); ok {
            fmt.Printf("标签: %v\n", tags)
        }

        if specs, ok := obj["specs"].(map[string]interface{}); ok {
            fmt.Printf("CPU: %v\n", specs["cpu"])
            fmt.Printf("RAM: %v\n", specs["ram"])
        }
    }
}
```

### 3. 流式解码
```go
func streamingDecode() {
    jsonString := `[
        {"id": 1, "name": "产品1", "price": 10.99},
        {"id": 2, "name": "产品2", "price": 20.99},
        {"id": 3, "name": "产品3", "price": 30.99}
    ]`

    // 创建解码器
    decoder := json.NewDecoder(strings.NewReader(jsonString))

    // 读取开始数组
    token, err := decoder.Token()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("开始标记: %v\n", token) // [

    // 逐个解码对象
    for decoder.More() {
        var product struct {
            ID    int     `json:"id"`
            Name  string  `json:"name"`
            Price float64 `json:"price"`
        }

        if err := decoder.Decode(&product); err != nil {
            log.Fatal(err)
        }
        fmt.Printf("产品: %+v\n", product)
    }

    // 读取结束数组
    token, err = decoder.Token()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("结束标记: %v\n", token) // ]
}
```

### 4. 错误处理
```go
func errorHandling() {
    // 不完整JSON
    invalidJSON := `{"name": "张三", "age": 25` // 缺少闭合括号

    var person Person
    if err := json.Unmarshal([]byte(invalidJSON), &person); err != nil {
        var syntaxErr *json.SyntaxError
        var unmarshalErr *json.UnmarshalTypeError

        switch {
        case errors.As(err, &syntaxErr):
            fmt.Printf("语法错误: 偏移量 %d\n", syntaxErr.Offset)
        case errors.As(err, &unmarshalErr):
            fmt.Printf("类型错误: 字段 %s 期望类型 %s\n",
                unmarshalErr.Field, unmarshalErr.Type)
        default:
            fmt.Printf("其他JSON错误: %v\n", err)
        }
    }

    // 类型不匹配
    typeMismatchJSON := `{"name": "李四", "age": "不是数字"}`

    var person2 Person
    if err := json.Unmarshal([]byte(typeMismatchJSON), &person2); err != nil {
        fmt.Printf("类型不匹配错误: %v\n", err)
    }
}
```

## 📝 高级JSON处理

### 1. JSON流处理
```go
func streamProcessing() {
    // 处理大型JSON文件
    largeJSON := `{
        "users": [
            {"id": 1, "name": "用户1", "email": "user1@example.com"},
            {"id": 2, "name": "用户2", "email": "user2@example.com"},
            {"id": 3, "name": "用户3", "email": "user3@example.com"}
        ],
        "total": 3
    }`

    decoder := json.NewDecoder(strings.NewReader(largeJSON))

    // 查找users数组
    for {
        token, err := decoder.Token()
        if err != nil {
            break
        }

        if token == "users" {
            // 下一个token应该是 [
            token, err = decoder.Token()
            if err != nil {
                break
            }

            // 处理用户数组
            for decoder.More() {
                var user struct {
                    ID    int    `json:"id"`
                    Name  string `json:"name"`
                    Email string `json:"email"`
                }

                if err := decoder.Decode(&user); err != nil {
                    break
                }

                fmt.Printf("处理用户: %s (%s)\n", user.Name, user.Email)
            }
        }
    }
}
```

### 2. JSON Patch操作
```go
func jsonPatchExample() {
    // 原始数据
    original := `{
        "name": "张三",
        "age": 25,
        "city": "北京",
        "hobbies": ["reading", "swimming"]
    }`

    // 应用补丁操作
    patches := []map[string]interface{}{
        {
            "op":    "replace",
            "path":  "/age",
            "value": 26,
        },
        {
            "op":    "add",
            "path":  "/hobbies/1",
            "value": "coding",
        },
        {
            "op":    "remove",
            "path":  "/city",
        },
    }

    var data map[string]interface{}
    json.Unmarshal([]byte(original), &data)

    for _, patch := range patches {
        op := patch["op"].(string)
        path := patch["path"].(string)

        switch op {
        case "replace":
            // 简化实现
            if path == "/age" {
                data["age"] = patch["value"]
            }
        case "add":
            if path == "/hobbies/1" {
                hobbies := data["hobbies"].([]interface{})
                hobbies = append(hobbies, patch["value"])
                data["hobbies"] = hobbies
            }
        case "remove":
            if path == "/city" {
                delete(data, "city")
            }
        }
    }

    result, _ := json.MarshalIndent(data, "", "  ")
    fmt.Printf("补丁后结果:\n%s\n", result)
}
```

### 3. JSON Schema验证
```go
func jsonSchemaValidation() {
    // 简化的Schema验证
    schema := map[string]interface{}{
        "type": "object",
        "properties": map[string]interface{}{
            "name": map[string]interface{}{
                "type": "string",
                "minLength": 1,
            },
            "age": map[string]interface{}{
                "type": "integer",
                "minimum": 0,
                "maximum": 150,
            },
            "email": map[string]interface{}{
                "type": "string",
                "format": "email",
            },
        },
        "required": []string{"name", "age"},
    }

    validateData := func(data map[string]interface{}) bool {
        // 检查必需字段
        required := schema["required"].([]interface{})
        for _, field := range required {
            if _, exists := data[field.(string)]; !exists {
                fmt.Printf("缺少必需字段: %s\n", field)
                return false
            }
        }

        // 检查字段类型
        properties := schema["properties"].(map[string]interface{})
        for field, value := range data {
            if prop, exists := properties[field]; exists {
                propMap := prop.(map[string]interface{})
                expectedType := propMap["type"].(string)

                switch expectedType {
                case "string":
                    if _, ok := value.(string); !ok {
                        fmt.Printf("字段 %s 应该是字符串类型\n", field)
                        return false
                    }
                case "integer":
                    if _, ok := value.(float64); !ok {
                        fmt.Printf("字段 %s 应该是整数类型\n", field)
                        return false
                    }
                }
            }
        }

        return true
    }

    // 测试数据
    testData := map[string]interface{}{
        "name":  "张三",
        "age":   25,
        "email": "zhangsan@example.com",
    }

    if validateData(testData) {
        fmt.Println("数据验证通过")
    } else {
        fmt.Println("数据验证失败")
    }
}
```

## 📝 实际应用场景

### 1. API响应处理
```go
type APIResponse struct {
    Status  string      `json:"status"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
    Error   string      `json:"error,omitempty"`
}

func handleAPIResponse(jsonString string) {
    var response APIResponse
    if err := json.Unmarshal([]byte(jsonString), &response); err != nil {
        log.Fatal(err)
    }

    fmt.Printf("API响应状态: %s\n", response.Status)
    fmt.Printf("API响应消息: %s\n", response.Message)

    if response.Error != "" {
        fmt.Printf("API错误: %s\n", response.Error)
        return
    }

    if response.Data != nil {
        switch data := response.Data.(type) {
        case map[string]interface{}:
            fmt.Printf("数据详情: %+v\n", data)
        case []interface{}:
            fmt.Printf("数据列表，共 %d 项\n", len(data))
        }
    }
}
```

### 2. 配置文件处理
```go
type Config struct {
    Server   ServerConfig   `json:"server"`
    Database DatabaseConfig `json:"database"`
    Logging  LoggingConfig  `json:"logging"`
}

type ServerConfig struct {
    Host string `json:"host"`
    Port int    `json:"port"`
}

type DatabaseConfig struct {
    Host     string `json:"host"`
    Port     int    `json:"port"`
    Username string `json:"username"`
    Password string `json:"password"`
    Database string `json:"database"`
}

type LoggingConfig struct {
    Level  string `json:"level"`
    Format string `json:"format"`
    File   string `json:"file,omitempty"`
}

func loadConfig(configPath string) (*Config, error) {
    data, err := os.ReadFile(configPath)
    if err != nil {
        return nil, err
    }

    var config Config
    if err := json.Unmarshal(data, &config); err != nil {
        return nil, err
    }

    return &config, nil
}
```

### 3. 数据导入导出
```go
type ExportData struct {
    Users      []User          `json:"users"`
    Products   []Product       `json:"products"`
    Orders     []Order         `json:"orders"`
    ExportTime string          `json:"export_time"`
    Metadata   map[string]interface{} `json:"metadata"`
}

func exportData(filename string, data *ExportData) error {
    // 添加导出时间
    data.ExportTime = time.Now().Format(time.RFC3339)

    // 添加元数据
    data.Metadata = map[string]interface{}{
        "version":     "1.0",
        "total_users": len(data.Users),
        "total_products": len(data.Products),
        "total_orders": len(data.Orders),
    }

    jsonData, err := json.MarshalIndent(data, "", "  ")
    if err != nil {
        return err
    }

    return os.WriteFile(filename, jsonData, 0644)
}

func importData(filename string) (*ExportData, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        return nil, err
    }

    var exportData ExportData
    if err := json.Unmarshal(data, &exportData); err != nil {
        return nil, err
    }

    return &exportData, nil
}
```

## 🧪 实践练习

### 练习1: JSON编解码基础
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "time"
)

type Book struct {
    ID          string    `json:"id"`
    Title       string    `json:"title"`
    Author      string    `json:"author"`
    ISBN        string    `json:"isbn"`
    PublishedAt time.Time `json:"published_at"`
    Price       float64   `json:"price"`
    Tags        []string  `json:"tags,omitempty"`
    Description string    `json:"description,omitempty"`
}

func main() {
    // 创建书籍数据
    book := Book{
        ID:          "001",
        Title:       "Go程序设计语言",
        Author:      "Alan A. A. Donovan",
        ISBN:        "978-7-115-44728-3",
        PublishedAt: time.Date(2015, 10, 26, 0, 0, 0, 0, time.UTC),
        Price:       99.00,
        Tags:        []string{"编程", "Go语言", "计算机"},
        Description: "Go语言权威指南",
    }

    // 编码为JSON
    jsonData, err := json.MarshalIndent(book, "", "  ")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("书籍JSON:\n%s\n", jsonData)

    // 解码JSON
    jsonString := `{
        "id": "002",
        "title": "Go并发编程实战",
        "author": "作者名",
        "isbn": "978-7-xxx-xxxx-x",
        "published_at": "2023-01-15T00:00:00Z",
        "price": 79.00,
        "tags": ["编程", "并发", "Go语言"]
    }`

    var book2 Book
    if err := json.Unmarshal([]byte(jsonString), &book2); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("解码书籍: %+v\n", book2)

    // 处理日期
    fmt.Printf("发布日期: %s\n", book2.PublishedAt.Format("2006年01月02日"))
}
```

### 练习2: 动态JSON处理
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "strings"
)

func main() {
    // 复杂JSON数据
    complexJSON := `{
        "system": {
            "name": "订单管理系统",
            "version": "1.0.0",
            "modules": ["用户管理", "订单管理", "库存管理"]
        },
        "users": [
            {
                "id": 1,
                "name": "张三",
                "profile": {
                    "age": 25,
                    "city": "北京"
                }
            },
            {
                "id": 2,
                "name": "李四",
                "profile": {
                    "age": 30,
                    "city": "上海"
                }
            }
        ],
        "statistics": {
            "total_users": 2,
            "active_users": 2,
            "system_uptime": "72h"
        }
    }`

    // 解码到interface{}
    var data interface{}
    if err := json.Unmarshal([]byte(complexJSON), &data); err != nil {
        log.Fatal(err)
    }

    // 处理数据
    if obj, ok := data.(map[string]interface{}); ok {
        // 系统信息
        if system, ok := obj["system"].(map[string]interface{}); ok {
            fmt.Printf("系统名称: %s\n", system["name"])
            fmt.Printf("系统版本: %s\n", system["version"])

            if modules, ok := system["modules"].([]interface{}); ok {
                fmt.Printf("系统模块: %v\n", modules)
            }
        }

        // 用户信息
        if users, ok := obj["users"].([]interface{}); ok {
            fmt.Printf("\n用户列表:\n")
            for _, user := range users {
                if userMap, ok := user.(map[string]interface{}); ok {
                    fmt.Printf("  - %s (ID: %v)\n", userMap["name"], userMap["id"])

                    if profile, ok := userMap["profile"].(map[string]interface{}); ok {
                        fmt.Printf("    年龄: %v, 城市: %v\n",
                            profile["age"], profile["city"])
                    }
                }
            }
        }

        // 统计信息
        if stats, ok := obj["statistics"].(map[string]interface{}); ok {
            fmt.Printf("\n统计信息:\n")
            fmt.Printf("  总用户数: %v\n", stats["total_users"])
            fmt.Printf("  活跃用户: %v\n", stats["active_users"])
            fmt.Printf("  系统运行时间: %v\n", stats["system_uptime"])
        }
    }

    // 生成报告
    fmt.Println("\n=== 系统报告 ===")
    generateReport(data)
}

func generateReport(data interface{}) {
    if obj, ok := data.(map[string]interface{}); ok {
        // 系统概览
        if system, ok := obj["system"].(map[string]interface{}); ok {
            fmt.Printf("系统: %s v%s\n", system["name"], system["version"])
        }

        // 用户统计
        if users, ok := obj["users"].([]interface{}); ok {
            fmt.Printf("用户总数: %d\n", len(users))
        }

        if stats, ok := obj["statistics"].(map[string]interface{}); ok {
            if activeUsers, ok := stats["active_users"].(float64); ok {
                fmt.Printf("活跃用户: %d\n", int(activeUsers))
            }
        }
    }
}
```

## 📋 最佳实践

### 1. 结构体设计最佳实践
- 使用有意义的结构体标签
- 合理使用`omitempty`选项
- 考虑使用指针类型处理可选字段
- 为复杂的JSON结构定义嵌套结构体

### 2. 性能优化建议
- 对于大型JSON数据使用流式处理
- 重用`json.Encoder`和`json.Decoder`对象
- 避免频繁的内存分配
- 使用缓冲区提高I/O性能

### 3. 错误处理最佳实践
- 始终检查JSON编解码的错误
- 提供有意义的错误信息
- 使用类型断言处理动态数据
- 验证输入数据的完整性

### 4. 安全考虑
- 避免解码来自不可信源的JSON
- 验证解码后的数据类型
- 限制解析的数据大小
- 防止JSON注入攻击

## 📋 检查清单

- [ ] 掌握JSON编码和解码基础
- [ ] 理解结构体标签的使用
- [ ] 学会处理复杂JSON结构
- [ ] 掌握流式JSON处理
- [ ] 理解自定义编码逻辑
- [ ] 学会JSON错误处理
- [ ] 掌握动态JSON处理
- [ ] 理解JSON Schema验证
- [ ] 能够处理API响应
- [ ] 学会配置文件处理

## 🚀 下一步

掌握encoding/json包后，你可以继续学习：
- **database/sql包**: 数据库操作
- **Gin框架**: Web框架中的JSON处理
- **API设计**: RESTful API最佳实践
- **性能优化**: JSON处理性能优化

---

**学习提示**: Go的encoding/json包提供了类型安全和高效的JSON处理能力。相比PHP的动态JSON处理，Go的静态类型系统在编译时就能发现许多错误，提高了代码的可靠性。掌握JSON处理是现代Go开发的核心技能。

*最后更新: 2025年9月*