# Go 测试驱动开发(TDD)实战指南

> **文档简介**: 用一个小功能反复执行“先写失败断言 → 最小实现 → 保持行为的重构”。重点不是追求测试数量，而是让每一步都能说明需求、失败原因和下一次改动的边界。

> **目标读者**: Go开发者，希望提升代码质量和开发效率的开发者

> **前置知识**: Go语言基础、单元测试基础、测试框架使用

> **预计时长**: 4-5小时完整学习

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `testing/quality-assurance` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#TDD` `#测试驱动开发` `#重构` `#代码质量` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 本文结束时应能完成的练习

以 `ReverseString` 为例，先写出对普通字符串、空字符串和 Unicode 字符串的行为断言。第一次运行必须因为缺少实现或行为不符而失败；补上最小实现后，测试应转绿；再把实现从只满足一个输入的硬编码改为通用实现，并确认原有测试仍通过。

完成后应能回答：这个测试保护的是哪条外部行为？删掉或改坏哪一行会让它失败？新加一个相邻输入时，测试是否揭露了实现只为第一个样例硬编码？这些问题比“覆盖率是多少”更能判断本轮 TDD 是否有效。

## 📖 TDD基础概念

### 什么是测试驱动开发
测试驱动开发(Test-Driven Development, TDD)是一种软件开发方法论，要求在编写功能代码之前先编写测试代码。

#### TDD核心循环：红-绿-重构
```mermaid
graph LR
    A[红 - 编写失败测试] --> B[绿 - 编写最少代码通过]
    B --> C[重构 - 改进代码质量]
    C --> A
```

#### TDD 何时提供价值

测试先迫使你给调用方可观察的契约命名：输入是什么、输出或错误是什么、状态是否改变。它不能自动产生好 API，也不能证明所有功能都正确；如果断言只检查内部字段、总是传同一个输入，或测试本身从不失败，重构时仍可能缺少保护。把测试视为一段可执行的使用说明：读者应能从测试看出如何调用、什么结果可接受、什么输入被拒绝。

### Go 中的最小工具选择

从标准库 `testing` 开始：`go test` 发现 `*_test.go`、隔离测试进程并报告失败位置。需要更清晰的断言文字时再评估 Testify；需要替身时先定义窄接口，再评估 gomock 或手写 fake。工具不会替你决定测试应覆盖的错误、并发和资源清理边界；测试速度也应以当前包的实际耗时与稳定性为准，而不是预设“足够快”。

## 🛠️ TDD实战流程

### 1. 红色阶段 - 编写失败测试

#### 示例：字符串反转功能
```go
// 先写测试，预期会失败
func TestStringReverse(t *testing.T) {
    result := ReverseString("hello")
    expected := "olleh"
    if result != expected {
        t.Errorf("Expected %q, got %q", expected, result)
    }
}
```

#### 运行测试（会失败）
```bash
$ go test
# command-line-arguments
undefined: ReverseString
```

#### 测试失败是好事！
- **验证测试有效**: 确保测试能检测到功能缺失
- **明确需求**: 测试描述了期望的功能行为
- **设计指导**: 测试暗示了函数的签名和接口

### 2. 绿色阶段 - 编写最少代码通过测试

#### 最简单的实现
```go
// 为当前断言写出最少实现
func ReverseString(s string) string {
    // 硬编码解决当前测试
    if s == "hello" {
        return "olleh"
    }
    return ""
}
```

#### 运行测试（通过）
```bash
$ go test
PASS  # 成功时的预期示例输出；实际耗时随环境变化
ok      example.com/stringutils    0.002s
```

#### 绿色阶段原则
- **最小实现**: 用最简单的方式满足当前断言
- **不要完美**: 避免过度设计
- **专注目标**: 只解决当前测试的需求

### 3. 重构阶段 - 改进代码质量

#### 泛化实现
```go
// 重构为通用实现
func ReverseString(s string) string {
    runes := []rune(s)
    n := len(runes)

    for i := 0; i < n/2; i++ {
        runes[i], runes[n-1-i] = runes[n-1-i], runes[i]
    }

    return string(runes)
}
```

#### 验证重构
```bash
$ go test
PASS  # 成功时的预期示例输出；实际耗时随环境变化
ok      example.com/stringutils    0.002s
```

#### 重构原则
- **保持绿色**: 重构期间测试必须一直通过
- **小步重构**: 每次只改进一个方面
- **测试保护**: 依赖测试确保重构正确性

## 🎯 TDD实战案例

### 案例1：用户注册功能

#### 第一个测试 - 验证邮箱格式
```go
func TestUserValidator_ValidEmail(t *testing.T) {
    validator := NewUserValidator()

    err := validator.ValidateEmail("user@example.com")
    if err != nil {
        t.Errorf("Expected valid email, got error: %v", err)
    }
}
```

#### 实现验证器基础结构
```go
type UserValidator struct{}

func NewUserValidator() *UserValidator {
    return &UserValidator{}
}

func (uv *UserValidator) ValidateEmail(email string) error {
    // 最简单的实现
    if email == "user@example.com" {
        return nil
    }
    return errors.New("invalid email")
}
```

#### 第二个测试 - 无效邮箱
```go
func TestUserValidator_InvalidEmail(t *testing.T) {
    validator := NewUserValidator()

    testCases := []struct {
        email    string
        expected string
    }{
        {"", "empty email"},
        {"invalid", "invalid format"},
        {"@", "missing domain"},
        {"test@", "missing domain after @"},
    }

    for _, tc := range testCases {
        t.Run(tc.email, func(t *testing.T) {
            err := validator.ValidateEmail(tc.email)
            if err == nil {
                t.Errorf("Expected error for %q", tc.email)
            }
        })
    }
}
```

#### 重构为完整的邮箱验证
```go
func (uv *UserValidator) ValidateEmail(email string) error {
    if email == "" {
        return errors.New("empty email")
    }

    // 简单的邮箱格式验证
    if !strings.Contains(email, "@") {
        return errors.New("invalid format")
    }

    parts := strings.Split(email, "@")
    if len(parts) != 2 || parts[0] == "" || parts[1] == "" {
        return errors.New("invalid format")
    }

    return nil
}
```

#### 第三个测试 - 用户注册
```go
func TestUserService_RegisterUser(t *testing.T) {
    validator := NewUserValidator()
    service := NewUserService(validator)

    user := &User{
        Name:  "John Doe",
        Email: "john@example.com",
    }

    err := service.Register(user)
    if err != nil {
        t.Errorf("Expected successful registration, got error: %v", err)
    }

    if user.ID == "" {
        t.Error("Expected user ID to be generated")
    }
}
```

#### 实现用户服务
```go
type User struct {
    ID    string
    Name  string
    Email string
}

type UserService struct {
    validator *UserValidator
    users     map[string]*User
}

func NewUserService(validator *UserValidator) *UserService {
    return &UserService{
        validator: validator,
        users:     make(map[string]*User),
    }
}

func (us *UserService) Register(user *User) error {
    if err := us.validator.ValidateEmail(user.Email); err != nil {
        return fmt.Errorf("invalid email: %w", err)
    }

    user.ID = generateID()
    us.users[user.ID] = user

    return nil
}

func generateID() string {
    return fmt.Sprintf("user-%d", time.Now().UnixNano())
}
```

### 案例2：购物车系统

#### 测试驱动购物车开发
```go
func TestShoppingCart_AddItem(t *testing.T) {
    cart := NewShoppingCart()

    item := &Item{
        ID:    "item-1",
        Name:  "Product A",
        Price: 10.99,
    }

    err := cart.AddItem(item, 1)
    if err != nil {
        t.Errorf("Expected to add item successfully, got error: %v", err)
    }

    if len(cart.Items()) != 1 {
        t.Errorf("Expected 1 item in cart, got %d", len(cart.Items()))
    }
}

func TestShoppingCart_RemoveItem(t *testing.T) {
    cart := NewShoppingCart()

    item := &Item{
        ID:    "item-1",
        Name:  "Product A",
        Price: 10.99,
    }

    cart.AddItem(item, 1)
    err := cart.RemoveItem("item-1")
    if err != nil {
        t.Errorf("Expected to remove item successfully, got error: %v", err)
    }

    if len(cart.Items()) != 0 {
        t.Errorf("Expected 0 items in cart, got %d", len(cart.Items()))
    }
}
```

## 🔧 TDD高级技巧

### 1. 测试驱动API设计

#### 先写测试定义API
```go
// 测试定义了我们期望的API
func TestAPIClient_GetUser(t *testing.T) {
    client := NewAPIClient("http://api.example.com")

    user, err := client.GetUser("user-123")
    if err != nil {
        t.Errorf("Expected successful request, got error: %v", err)
    }

    if user.ID != "user-123" {
        t.Errorf("Expected user ID %q, got %q", "user-123", user.ID)
    }
}

func TestAPIClient_GetUser_NotFound(t *testing.T) {
    client := NewAPIClient("http://api.example.com")

    user, err := client.GetUser("nonexistent")
    if err == nil {
        t.Error("Expected error for nonexistent user")
    }

    if user != nil {
        t.Error("Expected nil user for nonexistent request")
    }
}
```

#### 实现API客户端
```go
type APIClient struct {
    baseURL string
    client  *http.Client
}

func NewAPIClient(baseURL string) *APIClient {
    return &APIClient{
        baseURL: baseURL,
        client:  &http.Client{Timeout: 30 * time.Second},
    }
}

type User struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func (c *APIClient) GetUser(userID string) (*User, error) {
    url := fmt.Sprintf("%s/users/%s", c.baseURL, userID)

    resp, err := c.client.Get(url)
    if err != nil {
        return nil, fmt.Errorf("request failed: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode == http.StatusNotFound {
        return nil, fmt.Errorf("user not found")
    }

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }

    var user User
    if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
        return nil, fmt.Errorf("decode failed: %w", err)
    }

    return &user, nil
}
```

### 2. 表格驱动测试与TDD结合

#### 使用表格驱动多个测试案例
```go
func TestPasswordValidator_Validate(t *testing.T) {
    validator := NewPasswordValidator()

    testCases := []struct {
        name     string
        password string
        wantErr  bool
    }{
        {"valid password", "SecurePass123!", false},
        {"too short", "123", true},
        {"no uppercase", "securepass123!", true},
        {"no lowercase", "SECUREPASS123!", true},
        {"no numbers", "SecurePass!", true},
        {"no special chars", "SecurePass123", true},
    }

    for _, tc := range testCases {
        t.Run(tc.name, func(t *testing.T) {
            err := validator.Validate(tc.password)
            if (err != nil) != tc.wantErr {
                t.Errorf("Validate() error = %v, wantErr %v", err, tc.wantErr)
            }
        })
    }
}
```

#### 实现密码验证器
```go
type PasswordValidator struct{}

func NewPasswordValidator() *PasswordValidator {
    return &PasswordValidator{}
}

func (pv *PasswordValidator) Validate(password string) error {
    if len(password) < 8 {
        return errors.New("password too short")
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

    if !hasUpper {
        return errors.New("password must contain uppercase letter")
    }
    if !hasLower {
        return errors.New("password must contain lowercase letter")
    }
    if !hasDigit {
        return errors.New("password must contain digit")
    }
    if !hasSpecial {
        return errors.New("password must contain special character")
    }

    return nil
}
```

### 3. Mock与TDD结合

#### 使用Mock进行TDD
```go
// 先定义接口
type EmailSender interface {
    Send(to, subject, body string) error
}

// Mock实现
type MockEmailSender struct {
    mock.Mock
}

func (m *MockEmailSender) Send(to, subject, body string) error {
    args := m.Called(to, subject, body)
    return args.Error(0)
}

// 测试用户通知服务
func TestNotificationService_SendWelcomeEmail(t *testing.T) {
    // 创建Mock
    mockSender := new(MockEmailSender)
    service := NewNotificationService(mockSender)

    // 设置Mock期望
    mockSender.
        On("Send", "user@example.com", "Welcome!", "Welcome to our service!").
        Return(nil)

    // 执行测试
    user := &User{Email: "user@example.com", Name: "John"}
    err := service.SendWelcomeEmail(user)

    // 验证结果
    if err != nil {
        t.Errorf("Expected successful email sending, got error: %v", err)
    }

    // 验证Mock调用
    mockSender.AssertExpectations(t)
}
```

## 🚨 TDD常见陷阱和解决方案

### 1. 测试过多细节

#### ❌ 错误：测试实现细节
```go
func TestUserRepository_Store(t *testing.T) {
    repo := NewInMemoryUserRepository()

    user := &User{Name: "John"}
    err := repo.Store(user)

    // 测试内部存储细节 - 错误
    if len(repo.users) != 1 {
        t.Error("Repository should have 1 user")
    }
    if repo.users["user-1"] != user {
        t.Error("User not stored correctly")
    }
}
```

#### ✅ 正确：测试行为和结果
```go
func TestUserRepository_StoreAndRetrieve(t *testing.T) {
    repo := NewInMemoryUserRepository()

    user := &User{Name: "John"}
    err := repo.Store(user)
    if err != nil {
        t.Errorf("Failed to store user: %v", err)
    }

    // 测试可观察的行为
    retrieved, err := repo.FindByID(user.ID)
    if err != nil {
        t.Errorf("Failed to retrieve user: %v", err)
    }

    if retrieved.Name != user.Name {
        t.Errorf("Expected name %q, got %q", user.Name, retrieved.Name)
    }
}
```

### 2. 跳过红色阶段

#### ❌ 错误：先写代码后写测试
```go
// 先写实现 - 违反TDD原则
func Calculator() {
    result := 2 + 2
    fmt.Println(result)
}

// 后写测试 - 不是真正的TDD
func TestCalculator(t *testing.T) {
    // 测试已经知道的实现
    result := calculate()
    expected := 4
    if result != expected {
        t.Errorf("Expected %d, got %d", expected, result)
    }
}
```

#### ✅ 正确：先写测试
```go
// 先写测试描述期望行为
func TestCalculator_Add(t *testing.T) {
    calc := NewCalculator()

    result := calc.Add(2, 2)
    expected := 4
    if result != expected {
        t.Errorf("Expected %d, got %d", expected, result)
    }
}

// 然后实现最小代码通过测试
type Calculator struct{}

func NewCalculator() *Calculator {
    return &Calculator{}
}

func (c *Calculator) Add(a, b int) int {
    return a + b  // 最简单的实现
}
```

### 3. 过度设计

#### ❌ 错误：在绿色阶段过度设计
```go
func Add(a, b int) int {
    // 绿色阶段不应该这样复杂
    logger := NewLogger()
    metrics := NewMetrics()
    cache := NewCache()

    logger.Info("Adding numbers")
    metrics.Increment("add_calls")

    key := fmt.Sprintf("add:%d:%d", a, b)
    if cached, exists := cache.Get(key); exists {
        return cached.(int)
    }

    result := a + b
    cache.Set(key, result, time.Hour)
    return result
}
```

#### ✅ 正确：绿色阶段保持简单
```go
func Add(a, b int) int {
    return a + b  // 简单直接
}

// 后续在重构阶段添加复杂功能
```

## 📊 TDD工作流程优化

### 1. 小步快跑策略

#### 分解复杂功能
```go
// 不一次性实现复杂功能，而是分解为小步骤

// 步骤1：基础加法
func TestCalculator_Add(t *testing.T) {
    calc := NewCalculator()
    result := calc.Add(2, 3)
    expected := 5
    if result != expected {
        t.Errorf("Expected %d, got %d", expected, result)
    }
}

// 步骤2：处理负数
func TestCalculator_AddNegativeNumbers(t *testing.T) {
    calc := NewCalculator()
    result := calc.Add(-2, 3)
    expected := 1
    if result != expected {
        t.Errorf("Expected %d, got %d", expected, result)
    }
}

// 步骤3：处理大数
func TestCalculator_AddLargeNumbers(t *testing.T) {
    calc := NewCalculator()
    result := calc.Add(1000000, 2000000)
    expected := 3000000
    if result != expected {
        t.Errorf("Expected %d, got %d", expected, result)
    }
}
```

### 2. 持续重构

#### 在测试保护下持续改进
```go
// 初始实现
func Add(a, b int) int {
    return a + b
}

// 重构1：添加参数验证
func (c *Calculator) Add(a, b int) (int, error) {
    if a < 0 || b < 0 {
        return 0, errors.New("negative numbers not supported")
    }
    return a + b, nil
}

// 重构2：支持更多数值类型
func (c *Calculator) Add(a, b interface{}) (interface{}, error) {
    switch a := a.(type) {
    case int:
        if b, ok := b.(int); ok {
            return a + b, nil
        }
    case float64:
        if b, ok := b.(float64); ok {
            return a + b, nil
        }
    }
    return nil, errors.New("unsupported types")
}
```

### 3. 测试覆盖率监控

#### 设置覆盖率目标
```bash
# 生成覆盖率报告
go test -coverprofile=coverage.out ./...

# 查看覆盖率
go tool cover -func=coverage.out

# 生成HTML报告
go tool cover -html=coverage.out -o coverage.html

# 设置覆盖率阈值
go test -coverprofile=coverage.out -covermode=count ./...
go tool cover -func=coverage.out | grep "total:" | awk '{print $3}' | sed 's/%//'
```

#### 集成到CI/CD
```yaml
# .github/workflows/test.yml
name: Test and Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-go@v4
      with:
        go-version: '1.25'

    - name: Run tests with coverage
      run: go test -v -race -coverprofile=coverage.out ./...

    - name: Check coverage threshold
      run: |
        COVERAGE=$(go tool cover -func=coverage.out | grep "total:" | awk '{print $3}' | sed 's/%//')
        echo "Coverage: $COVERAGE%"
        if (( $(echo "$COVERAGE < 80" | bc -l) )); then
          echo "Coverage is below 80%"
          exit 1
        fi

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.out
```

## 🔗 文档交叉引用

### 相关文档
- 📄 **[单元测试]**: [testing/01-unit-testing.md](01-unit-testing.md) - Go单元测试基础
- 📄 **[Mock测试]**: [testing/02-mocking-stubbing.md](02-mocking-stubbing.md) - Mock和桩测试技术
- 📄 **[集成测试]**: [testing/03-integration-testing.md](03-integration-testing.md) - 系统集成测试
- 📄 **[基准测试]**: [testing/04-benchmarking.md](04-benchmarking.md) - 性能基准测试

### 参考章节
- 📖 **[重构技巧]**: [advanced-topics/performance/02-performance-tuning.md](../advanced-topics/performance/02-performance-tuning.md) - 代码重构和性能优化
- 📖 **[API设计]**: [advanced-topics/api-advanced/01-restful-patterns.md](../advanced-topics/api-advanced/01-restful-patterns.md) - RESTful API设计模式

## 📝 总结

### 红、绿、重构各自证明什么

1. **红阶段证明需求缺口**：先写一个描述新行为的最小测试，运行 `go test` 并确认它因缺少该行为而失败。编译错误、包路径错误或依赖下载失败不算需求测试的“红”。
2. **绿阶段只补当前规则**：写能让该测试通过的最小实现，再运行整个相关包的测试。此时不为了未来假设加入多余抽象，也不接受只硬编码当前输入而放过相邻边界。
3. **重构保持外部契约**：消除重复、改善命名或拆分函数后，测试集仍应通过；若修改可观察行为，先增加相应测试，再把它当成下一轮红阶段。
4. **小步的大小由反馈决定**：一次循环应短到能从失败输出看懂原因。遇到并发、数据库或 HTTP 边界时，先用纯函数或接口替身锁定业务规则，再用集成测试验证真实接缝。

### 学习成果验收

- [ ] 为一个规则写出第一个失败测试，并在记录中说明失败消息为何准确指向该规则。
- [ ] 用最小实现使测试通过，再增加一个相邻边界用例，确认实现不是只为第一个样例硬编码。
- [ ] 在全部相关测试通过后重命名或抽取一段重复逻辑，运行 `go test ./...`，确认重构没有改变外部行为。
- [ ] 让一个测试只依赖替身来覆盖纯业务规则，再为实际存储或 HTTP 边界补一条集成验证，明确两者分别覆盖什么。

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0

---

> 💡 **实践建议**:
> - 从小功能开始实践TDD，逐步积累经验
> - 不要追求完美的测试，关注核心功能覆盖
> - 定期回顾和重构测试代码，保持测试质量
> - 团队协作时建立TDD规范和代码审查标准

<!-- full-library-explanation -->
## 每一次变绿都只证明已有用例

前置是函数与单元测试。红阶段不仅要看到命令失败，还要确认失败原因正是待实现的行为；依赖下载失败或导入路径错误并不验证业务规则。绿阶段最小实现是推进下一条需求的临时步骤，不能把硬编码通过一个样例当成完成整个功能。重构保持已有行为，新增需求应先补充新测试再修改实现。

字符串反转示例需要先约定“字符”的含义。[]rune 能按 Unicode 码点反转，但组合音标和由多个码点构成的 emoji 仍可能被拆散；若需求是用户可见字符，应按字素簇处理并选择相应实现。测试反过来促使你澄清范围，而不是给“支持 Unicode”贴一个过宽的标签。

练习：依次加入空串、ASCII、多字节中文、组合字符四类用例，明确哪些是本函数承诺支持的语义。每次记录新增测试为何失败、最小改动是什么，再做一次不改变结果的函数整理。注册案例中的邮箱语法检查也不能证明地址存在或归用户所有，后者需要验证邮件流程。覆盖率阈值只能提供提示，应以关键行为、失败路径和边界规则是否被验证作为主要验收标准。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
