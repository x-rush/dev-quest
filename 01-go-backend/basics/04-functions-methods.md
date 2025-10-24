# Go 面向对象编程 - 从PHP视角理解

## 📚 概述

Go语言虽然没有传统的类(class)概念，但通过结构体(struct)、接口(interface)和方法(method)实现了面向对象编程。作为PHP开发者，理解Go的OOP实现方式对于掌握Go编程至关重要。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐⭐ |
| **标签** | `#面向对象` `#结构体` `#方法` `#接口` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

### 🎯 学习目标
- 掌握Go的结构体和方法定义
- 理解Go的接口和多态性
- 学会Go的组合和嵌入模式
- 熟悉Go的OOP与PHP的差异

## 🔄 Go vs PHP 面向对象对比

### 类定义对比

#### PHP 类定义
```php
<?php
class User {
    private $id;
    protected $name;
    public $email;

    public function __construct($id, $name, $email) {
        $this->id = $id;
        $this->name = $name;
        $this->email = $email;
    }

    public function getId() {
        return $this->id;
    }

    protected function getName() {
        return $this->name;
    }

    public function setEmail($email) {
        $this->email = $email;
    }

    public function getInfo() {
        return "ID: {$this->id}, Name: {$this->name}, Email: {$this->email}";
    }
}

// 继承
class Admin extends User {
    private $role;

    public function __construct($id, $name, $email, $role) {
        parent::__construct($id, $name, $email);
        $this->role = $role;
    }

    public function getRole() {
        return $this->role;
    }
}
```

#### Go 结构体实现
```go
// User结构体
type User struct {
    id    int
    name  string
    email string
}

// 构造函数
func NewUser(id int, name, email string) *User {
    return &User{
        id:    id,
        name:  name,
        email: email,
    }
}

// 方法定义
func (u *User) GetId() int {
    return u.id
}

func (u *User) GetName() string {
    return u.name
}

func (u *User) SetEmail(email string) {
    u.email = email
}

func (u *User) GetInfo() string {
    return fmt.Sprintf("ID: %d, Name: %s, Email: %s", u.id, u.name, u.email)
}

// 组合 (替代继承)
type Admin struct {
    User
    role string
}

func NewAdmin(id int, name, email, role string) *Admin {
    return &Admin{
        User: User{
            id:    id,
            name:  name,
            email: email,
        },
        role: role,
    }
}

func (a *Admin) GetRole() string {
    return a.role
}
```

### 接口对比

#### PHP 接口
```php
<?php
interface Logger {
    public function log($message);
    public function error($message);
}

interface Database {
    public function connect();
    public function query($sql);
    public function close();
}

class FileLogger implements Logger {
    public function log($message) {
        file_put_contents('app.log', $message . PHP_EOL, FILE_APPEND);
    }

    public function error($message) {
        file_put_contents('error.log', $message . PHP_EOL, FILE_APPEND);
    }
}
```

#### Go 接口
```go
// Logger接口
type Logger interface {
    Log(message string)
    Error(message string)
}

// Database接口
type Database interface {
    Connect() error
    Query(sql string) (interface{}, error)
    Close() error
}

// FileLogger实现
type FileLogger struct {
    filename string
}

func (fl *FileLogger) Log(message string) {
    f, err := os.OpenFile(fl.filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        return
    }
    defer f.Close()
    f.WriteString(message + "\n")
}

func (fl *FileLogger) Error(message string) {
    f, err := os.OpenFile("error.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        return
    }
    defer f.Close()
    f.WriteString(message + "\n")
}
```

## 📝 Go 面向对象编程详解

### 1. 结构体和方法

#### 结构体定义
```go
// 基本结构体
type Person struct {
    ID      int
    Name    string
    Age     int
    Address string
}

// 匿名结构体
var anonymous struct {
    Name string
    Age  int
} = struct{
    Name string
    Age  int
}{
    Name: "临时用户",
    Age:  30,
}

// 嵌套结构体
type Address struct {
    Street  string
    City    string
    Country string
}

type Employee struct {
    Person      // 匿名嵌入
    Position    string
    Salary      float64
    HireDate    time.Time
    HomeAddress Address
}

// 结构体实例化
func createPerson() {
    // 方式1: 使用字段名
    person1 := Person{
        ID:      1,
        Name:    "张三",
        Age:     25,
        Address: "北京市朝阳区",
    }

    // 方式2: 按顺序初始化
    person2 := Person{2, "李四", 30, "上海市浦东新区"}

    // 方式3: 使用new函数 (返回指针)
    person3 := new(Person)
    person3.ID = 3
    person3.Name = "王五"
    person3.Age = 28
}
```

#### 方法定义
```go
// 值接收器方法
func (p Person) GetInfo() string {
    return fmt.Sprintf("ID: %d, Name: %s, Age: %d", p.ID, p.Name, p.Age)
}

// 指针接收器方法
func (p *Person) SetName(name string) {
    p.Name = name
}

func (p *Person) IncrementAge() {
    p.Age++
}

// 方法链式调用
func (p *Person) SetAddress(address string) *Person {
    p.Address = address
    return p
}

// 方法重载 (Go不支持重载，使用不同方法名)
func (p *Person) GetNameWithPrefix(prefix string) string {
    return prefix + p.Name
}

func (p *Person) GetNameWithSuffix(suffix string) string {
    return p.Name + suffix
}
```

### 2. 构造函数和工厂模式

#### 构造函数模式
```go
// 构造函数
func NewPerson(id int, name, address string) *Person {
    return &Person{
        ID:      id,
        Name:    name,
        Age:     0,
        Address: address,
    }
}

// 工厂模式
type PersonFactory struct{}

func (pf *PersonFactory) CreateEmployee(id int, name, address, position string, salary float64) *Employee {
    return &Employee{
        Person: Person{
            ID:      id,
            Name:    name,
            Age:     0,
            Address: address,
        },
        Position: position,
        Salary:   salary,
        HireDate: time.Now(),
    }
}

func (pf *PersonFactory) CreateCustomer(id int, name, address, phone string) *Customer {
    return &Customer{
        Person: Person{
            ID:      id,
            Name:    name,
            Age:     0,
            Address: address,
        },
        Phone: phone,
    }
}
```

### 3. 组合和嵌入

#### 组合模式
```go
// 组件接口
type Component interface {
    Render() string
}

// 基础组件
type BaseComponent struct {
    name string
}

func (bc *BaseComponent) Render() string {
    return fmt.Sprintf("<div>%s</div>", bc.name)
}

// 容器组件
type Container struct {
    BaseComponent
    children []Component
}

func (c *Container) AddChild(child Component) {
    c.children = append(c.children, child)
}

func (c *Container) Render() string {
    result := fmt.Sprintf("<div class='container'>\n")
    for _, child := range c.children {
        result += "  " + child.Render() + "\n"
    }
    result += "</div>"
    return result
}

// 按钮组件
type Button struct {
    BaseComponent
    text string
}

func (b *Button) Render() string {
    return fmt.Sprintf("<button>%s</button>", b.text)
}
```

#### 嵌入模式
```go
// 基础形状
type Shape struct {
    name string
}

func (s *Shape) Name() string {
    return s.name
}

func (s *Shape) Area() float64 {
    return 0
}

// 圆形
type Circle struct {
    Shape
    radius float64
}

func (c *Circle) Area() float64 {
    return math.Pi * c.radius * c.radius
}

func NewCircle(radius float64) *Circle {
    return &Circle{
        Shape:  Shape{name: "圆形"},
        radius: radius,
    }
}

// 矩形
type Rectangle struct {
    Shape
    width, height float64
}

func (r *Rectangle) Area() float64 {
    return r.width * r.height
}

func NewRectangle(width, height float64) *Rectangle {
    return &Rectangle{
        Shape:  Shape{name: "矩形"},
        width:  width,
        height: height,
    }
}
```

### 4. 接口和多态

#### 接口定义
```go
// Shape接口
type Shape interface {
    Area() float64
    Perimeter() float64
    Name() string
}

// Drawable接口
type Drawable interface {
    Draw() string
}

// Resizeable接口
type Resizeable interface {
    Scale(factor float64)
}

// 实现多个接口
type Circle struct {
    radius float64
}

func (c *Circle) Area() float64 {
    return math.Pi * c.radius * c.radius
}

func (c *Circle) Perimeter() float64 {
    return 2 * math.Pi * c.radius
}

func (c *Circle) Name() string {
    return "圆形"
}

func (c *Circle) Draw() string {
    return fmt.Sprintf("绘制一个半径为%.2f的圆形", c.radius)
}

func (c *Circle) Scale(factor float64) {
    c.radius *= factor
}
```

#### 多态性
```go
// 处理不同形状
func ProcessShape(shape Shape) {
    fmt.Printf("形状: %s\n", shape.Name())
    fmt.Printf("面积: %.2f\n", shape.Area())
    fmt.Printf("周长: %.2f\n", shape.Perimeter())
}

// 绘制所有可绘制对象
func DrawAll(drawables []Drawable) {
    for _, d := range drawables {
        fmt.Println(d.Draw())
    }
}

// 调整所有可调整大小的对象
func ScaleAll(resizeables []Resizeable, factor float64) {
    for _, r := range resizeables {
        r.Scale(factor)
    }
}

// 使用示例
func main() {
    shapes := []Shape{
        &Circle{radius: 5},
        &Rectangle{width: 4, height: 6},
    }

    for _, shape := range shapes {
        ProcessShape(shape)
    }
}
```

### 5. 封装和可见性

#### 可见性规则
```go
// 包名: person
package person

// 公开的类型和函数 (大写字母开头)
type Person struct {
    ID     int     // 公开字段
    name   string  // 私有字段
    age    int     // 私有字段
    salary float64 // 私有字段
}

// 公开的构造函数
func NewPerson(id int, name string) *Person {
    return &Person{
        ID:   id,
        name: name,
        age:  0,
    }
}

// 公开的方法
func (p *Person) GetName() string {
    return p.name
}

func (p *Person) SetName(name string) {
    p.name = name
}

func (p *Person) GetAge() int {
    return p.age
}

// 私有的方法 (小写字母开头)
func (p *Person) calculateTax() float64 {
    return p.salary * 0.1
}

// 公开的业务方法
func (p *Person) GetSalaryInfo() string {
    tax := p.calculateTax()
    return fmt.Sprintf("薪资: %.2f, 税费: %.2f", p.salary, tax)
}
```

### 6. 错误处理和异常

#### 自定义错误类型
```go
// 业务错误类型
type BusinessError struct {
    Code    string
    Message string
    Details interface{}
}

func (e *BusinessError) Error() string {
    return fmt.Sprintf("业务错误 [%s]: %s", e.Code, e.Message)
}

// 用户相关错误
type UserError struct {
    UserID  int
    Action  string
    Err     error
}

func (e *UserError) Error() string {
    return fmt.Sprintf("用户错误 [ID:%d, Action:%s]: %v", e.UserID, e.Action, e.Err)
}

func (e *UserError) Unwrap() error {
    return e.Err
}
```

## 🧪 实践练习

### 练习1: 结构体和方法
```go
package main

import "fmt"

// 定义银行账户结构体
type BankAccount struct {
    accountNumber string
    owner         string
    balance       float64
}

// 构造函数
func NewBankAccount(accountNumber, owner string, initialBalance float64) *BankAccount {
    return &BankAccount{
        accountNumber: accountNumber,
        owner:         owner,
        balance:       initialBalance,
    }
}

// 方法
func (ba *BankAccount) GetBalance() float64 {
    return ba.balance
}

func (ba *BankAccount) Deposit(amount float64) error {
    if amount <= 0 {
        return fmt.Errorf("存款金额必须大于0")
    }
    ba.balance += amount
    return nil
}

func (ba *BankAccount) Withdraw(amount float64) error {
    if amount <= 0 {
        return fmt.Errorf("取款金额必须大于0")
    }
    if amount > ba.balance {
        return fmt.Errorf("余额不足")
    }
    ba.balance -= amount
    return nil
}

func (ba *BankAccount) GetInfo() string {
    return fmt.Sprintf("账户: %s, 户主: %s, 余额: %.2f", ba.accountNumber, ba.owner, ba.balance)
}

func main() {
    // 创建账户
    account := NewBankAccount("123456", "张三", 1000.0)

    fmt.Println(account.GetInfo())

    // 存款
    err := account.Deposit(500.0)
    if err != nil {
        fmt.Printf("存款失败: %v\n", err)
    } else {
        fmt.Printf("存款后余额: %.2f\n", account.GetBalance())
    }

    // 取款
    err = account.Withdraw(200.0)
    if err != nil {
        fmt.Printf("取款失败: %v\n", err)
    } else {
        fmt.Printf("取款后余额: %.2f\n", account.GetBalance())
    }
}
```

### 练习2: 接口和多态
```go
package main

import (
    "fmt"
    "math"
)

// 定义形状接口
type Shape interface {
    Area() float64
    Perimeter() float64
    String() string
}

// 圆形
type Circle struct {
    radius float64
}

func (c *Circle) Area() float64 {
    return math.Pi * c.radius * c.radius
}

func (c *Circle) Perimeter() float64 {
    return 2 * math.Pi * c.radius
}

func (c *Circle) String() string {
    return fmt.Sprintf("圆形(半径: %.2f)", c.radius)
}

// 矩形
type Rectangle struct {
    width, height float64
}

func (r *Rectangle) Area() float64 {
    return r.width * r.height
}

func (r *Rectangle) Perimeter() float64 {
    return 2 * (r.width + r.height)
}

func (r *Rectangle) String() string {
    return fmt.Sprintf("矩形(宽: %.2f, 高: %.2f)", r.width, r.height)
}

// 计算所有形状的总面积
func TotalArea(shapes []Shape) float64 {
    total := 0.0
    for _, shape := range shapes {
        total += shape.Area()
    }
    return total
}

// 打印所有形状信息
func PrintShapes(shapes []Shape) {
    for _, shape := range shapes {
        fmt.Printf("%s - 面积: %.2f, 周长: %.2f\n",
            shape.String(), shape.Area(), shape.Perimeter())
    }
}

func main() {
    // 创建形状
    shapes := []Shape{
        &Circle{radius: 5},
        &Rectangle{width: 4, height: 6},
        &Circle{radius: 3},
        &Rectangle{width: 5, height: 5},
    }

    // 打印形状信息
    PrintShapes(shapes)

    // 计算总面积
    total := TotalArea(shapes)
    fmt.Printf("总面积: %.2f\n", total)
}
```

### 练习3: 组合和嵌入
```go
package main

import "fmt"

// 基础组件
type Component struct {
    name string
}

func (c *Component) GetName() string {
    return c.name
}

// 按钮
type Button struct {
    Component
    text string
    onClick func()
}

func NewButton(name, text string, onClick func()) *Button {
    return &Button{
        Component: Component{name: name},
        text:      text,
        onClick:   onClick,
    }
}

func (b *Button) Click() {
    if b.onClick != nil {
        b.onClick()
    }
}

func (b *Button) String() string {
    return fmt.Sprintf("Button[%s: %s]", b.name, b.text)
}

// 输入框
type Input struct {
    Component
    placeholder string
    value      string
}

func NewInput(name, placeholder string) *Input {
    return &Input{
        Component: Component{name: name},
        placeholder: placeholder,
    }
}

func (i *Input) SetValue(value string) {
    i.value = value
}

func (i *Input) GetValue() string {
    return i.value
}

func (i *Input) String() string {
    return fmt.Sprintf("Input[%s: %s]", i.name, i.placeholder)
}

// 表单
type Form struct {
    Component
    components []interface{}
}

func NewForm(name string) *Form {
    return &Form{
        Component: Component{name: name},
        components: make([]interface{}, 0),
    }
}

func (f *Form) AddComponent(component interface{}) {
    f.components = append(f.components, component)
}

func (f *Form) String() string {
    result := fmt.Sprintf("Form[%s]:\n", f.name)
    for _, component := range f.components {
        result += fmt.Sprintf("  - %v\n", component)
    }
    return result
}

func main() {
    // 创建表单
    form := NewForm("用户注册")

    // 添加按钮
    submitButton := NewButton("submit", "提交", func() {
        fmt.Println("表单已提交!")
    })

    // 添加输入框
    nameInput := NewInput("username", "请输入用户名")
    emailInput := NewInput("email", "请输入邮箱")

    // 添加组件到表单
    form.AddComponent(nameInput)
    form.AddComponent(emailInput)
    form.AddComponent(submitButton)

    // 显示表单
    fmt.Println(form)

    // 测试按钮点击
    submitButton.Click()
}
```

## 📋 检查清单

- [ ] 掌握Go的结构体定义和使用
- [ ] 理解Go的方法定义和接收器
- [ ] 学会Go的接口和多态性
- [ ] 掌握Go的组合和嵌入模式
- [ ] 理解Go的封装和可见性规则
- [ ] 学会构造函数和工厂模式
- [ ] 掌握Go的错误处理机制
- [ ] 理解Go的OOP与PHP的差异

## 🚀 下一步

掌握Go的面向对象编程后，你可以继续学习：
- **标准库**: 常用包的使用方法
- **Web开发**: Gin框架和REST API
- **并发编程**: Goroutine和Channel
- **测试工程**: 单元测试和性能测试

---

**学习提示**: Go的OOP虽然与传统PHP的OOP有所不同，但提供了更灵活和强大的组合能力。通过接口和组合，你可以实现更清晰的代码结构。多练习这些模式，你会发现Go的OOP实际上更符合现代软件工程的最佳实践。

*最后更新: 2025年9月*