# Go 单元测试 - 从PHP视角理解

## 📚 概述

Go内置了强大的测试框架，与PHP的PHPUnit等测试库相比，Go的测试更加简洁和集成度高。掌握Go的测试是编写高质量Go应用的重要技能。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `testing/quality-assurance` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#单元测试` `#testing包` `#测试框架` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

### 🎯 学习目标
- 掌握Go的testing包使用
- 学会表驱动测试模式
- 理解Mock和Stub技术
- 掌握测试覆盖率分析
- 熟悉Go测试与PHP测试的差异

## 🔄 Go vs PHP 测试对比

### 基础测试对比

#### PHP 单元测试 (PHPUnit)
```php
<?php
use PHPUnit\Framework\TestCase;

class UserServiceTest extends TestCase {
    private $userService;
    private $dbMock;

    protected function setUp(): void {
        // 创建Mock对象
        $this->dbMock = $this->createMock(Database::class);
        $this->userService = new UserService($this->dbMock);
    }

    public function testCreateUser(): void {
        // 设置Mock期望
        $this->dbMock->expects($this->once())
                   ->method('insert')
                   ->with($this->equalTo('users'), $this->callback(function($data) {
                       return $data['name'] === '张三' && $data['email'] === 'zhangsan@example.com';
                   }))
                   ->willReturn(1);

        // 执行测试
        $result = $this->userService->createUser('张三', 'zhangsan@example.com');

        // 断言结果
        $this->assertEquals(1, $result['id']);
        $this->assertEquals('张三', $result['name']);
    }

    public function testCreateUserWithInvalidEmail(): void {
        $this->expectException(InvalidArgumentException::class);
        $this->userService->createUser('张三', 'invalid-email');
    }

    protected function tearDown(): void {
        // 清理资源
        unset($this->userService);
        unset($this->dbMock);
    }
}
```

#### Go 单元测试
```go
package services_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "your-project/internal/services"
    "your-project/internal/models"
)

// Mock数据库
type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) Create(table string, data interface{}) (int64, error) {
    args := m.Called(table, data)
    return args.Get(0).(int64), args.Error(1)
}

func TestUserService_CreateUser(t *testing.T) {
    // 创建Mock对象
    mockDB := new(MockDatabase)
    userService := services.NewUserService(mockDB)

    // 设置Mock期望
    mockDB.On("Create", "users", mock.MatchedBy(func(data *models.User) bool {
        return data.Name == "张三" && data.Email == "zhangsan@example.com"
    })).Return(int64(1), nil)

    // 执行测试
    user, err := userService.CreateUser(&models.CreateUserRequest{
        Name:  "张三",
        Email: "zhangsan@example.com",
    })

    // 断言结果
    assert.NoError(t, err)
    assert.Equal(t, "张三", user.Name)
    assert.Equal(t, "zhangsan@example.com", user.Email)

    // 验证Mock调用
    mockDB.AssertExpectations(t)
}

func TestUserService_CreateUser_InvalidEmail(t *testing.T) {
    mockDB := new(MockDatabase)
    userService := services.NewUserService(mockDB)

    // 执行测试
    _, err := userService.CreateUser(&models.CreateUserRequest{
        Name:  "张三",
        Email: "invalid-email",
    })

    // 断言错误
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "invalid email")
}
```

## 📝 Go 单元测试详解

### 1. 基础测试结构

#### 测试文件组织
```go
// 文件命名规则
// 源文件: user_service.go
// 测试文件: user_service_test.go

// 包命名规则
// 源文件包: services
// 测试文件包: services_test 或 services (同一包测试)

package services_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    "your-project/internal/services"
)
```

#### 基本测试函数
```go
// 基本测试函数
func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }
}

// 使用assert库的测试
func TestAddWithAssert(t *testing.T) {
    result := Add(2, 3)
    assert.Equal(t, 5, result)
    assert.NotEqual(t, 6, result)
}

// 使用require库的测试 (遇到错误立即终止)
func TestAddWithRequire(t *testing.T) {
    result := Add(2, 3)
    require.Equal(t, 5, result)
    require.NotZero(t, result)
}
```

### 2. 表驱动测试

#### 基本表驱动测试
```go
// 测试数据结构
type addTest struct {
    a, b int
    want int
}

// 测试用例
var addTests = []addTest{
    {1, 2, 3},
    {2, 3, 5},
    {-1, 1, 0},
    {0, 0, 0},
    {-1, -1, -2},
}

// 表驱动测试函数
func TestAddTableDriven(t *testing.T) {
    for _, tt := range addTests {
        t.Run(fmt.Sprintf("%d+%d", tt.a, tt.b), func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.want {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.want)
            }
        })
    }
}
```

#### 复杂表驱动测试
```go
// 用户服务测试用例
type userCreateTest struct {
    name        string
    input       *models.CreateUserRequest
    wantErr     bool
    errMsg      string
    mockSetup   func(*MockDatabase)
}

var userCreateTests = []userCreateTest{
    {
        name: "Valid user creation",
        input: &models.CreateUserRequest{
            Name:  "张三",
            Email: "zhangsan@example.com",
        },
        wantErr: false,
        mockSetup: func(m *MockDatabase) {
            m.On("Create", "users", mock.AnythingOfType("*models.User")).
               Return(int64(1), nil)
        },
    },
    {
        name: "Invalid email",
        input: &models.CreateUserRequest{
            Name:  "张三",
            Email: "invalid-email",
        },
        wantErr: true,
        errMsg:  "invalid email",
    },
    {
        name: "Database error",
        input: &models.CreateUserRequest{
            Name:  "李四",
            Email: "lisi@example.com",
        },
        wantErr: true,
        errMsg:  "database error",
        mockSetup: func(m *MockDatabase) {
            m.On("Create", "users", mock.AnythingOfType("*models.User")).
               Return(int64(0), errors.New("database error"))
        },
    },
}

func TestUserService_CreateUser_TableDriven(t *testing.T) {
    for _, tt := range userCreateTests {
        t.Run(tt.name, func(t *testing.T) {
            // 创建Mock对象
            mockDB := new(MockDatabase)
            userService := services.NewUserService(mockDB)

            // 设置Mock
            if tt.mockSetup != nil {
                tt.mockSetup(mockDB)
            }

            // 执行测试
            result, err := userService.CreateUser(tt.input)

            // 断言结果
            if tt.wantErr {
                assert.Error(t, err)
                if tt.errMsg != "" {
                    assert.Contains(t, err.Error(), tt.errMsg)
                }
            } else {
                assert.NoError(t, err)
                assert.NotNil(t, result)
                assert.Equal(t, tt.input.Name, result.Name)
                assert.Equal(t, tt.input.Email, result.Email)
            }

            // 验证Mock调用
            mockDB.AssertExpectations(t)
        })
    }
}
```

### 3. Mock和Stub

#### 接口Mock
```go
// 定义接口
type UserRepository interface {
    FindByID(id int) (*User, error)
    Create(user *User) error
    Update(user *User) error
    Delete(id int) error
}

// Mock实现
type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) FindByID(id int) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil { return nil, args.Error(1) }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) Create(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}

func (m *MockUserRepository) Update(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}

func (m *MockUserRepository) Delete(id int) error {
    args := m.Called(id)
    return args.Error(0)
}
```

#### 使用Mock进行测试
```go
func TestUserService_GetUser(t *testing.T) {
    // 创建Mock对象
    mockRepo := new(MockUserRepository)
    userService := services.NewUserService(mockRepo)

    // 预期用户数据
    expectedUser := &User{
        ID:    1,
        Name:  "张三",
        Email: "zhangsan@example.com",
    }

    // 设置Mock期望
    mockRepo.On("FindByID", 1).Return(expectedUser, nil)

    // 执行测试
    result, err := userService.GetUser(1)

    // 断言结果
    assert.NoError(t, err)
    assert.Equal(t, expectedUser, result)

    // 验证Mock调用
    mockRepo.AssertCalled(t, "FindByID", 1)
}
```

#### HTTP服务Mock
```go
// Mock HTTP客户端
type MockHTTPClient struct {
    mock.Mock
}

func (m *MockHTTPClient) Do(req *http.Request) (*http.Response, error) {
    args := m.Called(req)
    if args.Get(0) == nil { return nil, args.Error(1) }
    return args.Get(0).(*http.Response), args.Error(1)
}

func TestExternalService_CallAPI(t *testing.T) {
    // 创建Mock客户端
    mockClient := new(MockHTTPClient)
    service := services.NewExternalService(mockClient)

    // 预期响应
    expectedResponse := &http.Response{
        StatusCode: http.StatusOK,
        Body:       io.NopCloser(strings.NewReader(`{"result": "success"}`)),
    }

    // 设置Mock期望
    mockClient.On("Do", mock.MatchedBy(func(req *http.Request) bool {
        return req.URL.String() == "https://api.example.com/data" &&
               req.Method == "GET"
    })).Return(expectedResponse, nil)

    // 执行测试
    result, err := service.CallAPI()

    // 断言结果
    assert.NoError(t, err)
    assert.Equal(t, "success", result.Result)

    // 验证Mock调用
    mockClient.AssertExpectations(t)
}
```

### 4. 测试辅助函数

#### 测试辅助函数
```go
// 创建测试用户
func createTestUser(name, email string) *models.User {
    return &models.User{
        Name:  name,
        Email: email,
    }
}

// 比较用户 (忽略时间戳)
func assertUsersEqual(t *testing.T, expected, actual *models.User) {
    assert.Equal(t, expected.ID, actual.ID)
    assert.Equal(t, expected.Name, actual.Name)
    assert.Equal(t, expected.Email, actual.Email)
}

// 创建测试HTTP请求
func createTestRequest(method, url string, body interface{}) *http.Request {
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest(method, url, bytes.NewBuffer(jsonBody))
    req.Header.Set("Content-Type", "application/json")
    return req
}

// 解析响应
func parseResponse(t *testing.T, resp *http.Response, target interface{}) {
    defer resp.Body.Close()
    body, err := io.ReadAll(resp.Body)
    require.NoError(t, err)
    require.NoError(t, json.Unmarshal(body, target))
}
```

#### 测试Setup和Teardown
```go
// TestMain函数
func TestMain(m *testing.M) {
    // 测试前初始化
    setupTest()

    // 运行测试
    code := m.Run()

    // 测试后清理
    teardownTest()

    // 退出
    os.Exit(code)
}

func setupTest() {
    // 初始化测试数据库
    testDB = setupTestDatabase()

    // 创建测试用户
    createTestUsers()
}

func teardownTest() {
    // 清理测试数据
    cleanupTestDatabase()

    // 关闭连接
    testDB.Close()
}

// 子测试Setup和Teardown
func TestUserService_SomeTest(t *testing.T) {
    // Setup
    mockDB := new(MockDatabase)
    userService := services.NewUserService(mockDB)

    defer func() {
        // Teardown
        mockDB.AssertExpectations(t)
    }()

    // 测试代码
    // ...
}
```

### 5. 基准测试

#### 基本基准测试
```go
// 基准测试函数
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(2, 3)
    }
}

// 复杂基准测试
func BenchmarkUserService_CreateUser(b *testing.B) {
    // 创建测试数据
    mockDB := new(MockDatabase)
    userService := services.NewUserService(mockDB)

    mockDB.On("Create", "users", mock.Anything).Return(int64(1), nil)

    req := &models.CreateUserRequest{
        Name:  "测试用户",
        Email: "test@example.com",
    }

    b.ResetTimer() // 重置计时器
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            _, err := userService.CreateUser(req)
            if err != nil {
                b.Error(err)
            }
        }
    })
}
```

### 6. 测试覆盖率

#### 运行测试并生成覆盖率报告
```bash
# 运行测试并生成覆盖率报告
go test -coverprofile=coverage.out ./...

# 查看覆盖率报告
go tool cover -func=coverage.out

# 生成HTML覆盖率报告
go tool cover -html=coverage.out -o coverage.html

# 查看特定包的覆盖率
go test -coverprofile=coverage.out ./services
go tool cover -func=coverage.out
```

#### 设置覆盖率阈值
```go
// 在测试文件中添加覆盖率检查
func TestCoverage(t *testing.T) {
    if testing.CoverMode() == "" {
        t.Skip("跳过覆盖率检查")
    }

    // 这里可以添加覆盖率相关的断言
    // 通常在CI/CD中使用工具检查覆盖率
}
```

## 🧪 实践练习

### 练习1: 基础单元测试
```go
package calculator_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

// Calculator 结构体
type Calculator struct{}

func (c *Calculator) Add(a, b int) int {
    return a + b
}

func (c *Calculator) Subtract(a, b int) int {
    return a - b
}

func (c *Calculator) Multiply(a, b int) int {
    return a * b
}

func (c *Calculator) Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// 测试Add方法
func TestCalculator_Add(t *testing.T) {
    calc := &Calculator{}

    result := calc.Add(2, 3)
    assert.Equal(t, 5, result)

    result = calc.Add(-1, 1)
    assert.Equal(t, 0, result)

    result = calc.Add(0, 0)
    assert.Equal(t, 0, result)
}

// 测试Subtract方法
func TestCalculator_Subtract(t *testing.T) {
    calc := &Calculator{}

    result := calc.Subtract(5, 3)
    assert.Equal(t, 2, result)

    result = calc.Subtract(3, 5)
    assert.Equal(t, -2, result)
}

// 测试Multiply方法
func TestCalculator_Multiply(t *testing.T) {
    calc := &Calculator{}

    result := calc.Multiply(3, 4)
    assert.Equal(t, 12, result)

    result = calc.Multiply(-2, 3)
    assert.Equal(t, -6, result)

    result = calc.Multiply(0, 5)
    assert.Equal(t, 0, result)
}

// 测试Divide方法
func TestCalculator_Divide(t *testing.T) {
    calc := &Calculator{}

    // 正常情况
    result, err := calc.Divide(10, 2)
    assert.NoError(t, err)
    assert.Equal(t, 5, result)

    // 除零错误
    result, err = calc.Divide(10, 0)
    assert.Error(t, err)
    assert.Equal(t, "division by zero", err.Error())
    assert.Equal(t, 0, result)
}

// 表驱动测试
func TestCalculator_Divide_TableDriven(t *testing.T) {
    tests := []struct {
        name        string
        a, b        int
        want        int
        wantErr     bool
        errMsg      string
    }{
        {"Positive numbers", 10, 2, 5, false, ""},
        {"Negative numbers", -10, 2, -5, false, ""},
        {"Division by zero", 10, 0, 0, true, "division by zero"},
        {"Zero divided", 0, 5, 0, false, ""},
    }

    calc := &Calculator{}

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := calc.Divide(tt.a, tt.b)

            if tt.wantErr {
                assert.Error(t, err)
                assert.Equal(t, tt.errMsg, err.Error())
            } else {
                assert.NoError(t, err)
                assert.Equal(t, tt.want, result)
            }
        })
    }
}
```

### 练习2: Mock和Stub
```go
package services_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

// 定义接口
type DataStore interface {
    Get(key string) (string, error)
    Set(key, value string) error
    Delete(key string) error
}

// Mock实现
type MockDataStore struct {
    mock.Mock
}

func (m *MockDataStore) Get(key string) (string, error) {
    args := m.Called(key)
    return args.String(0), args.Error(1)
}

func (m *MockDataStore) Set(key, value string) error {
    args := m.Called(key, value)
    return args.Error(0)
}

func (m *MockDataStore) Delete(key string) error {
    args := m.Called(key)
    return args.Error(0)
}

// Cache服务
type CacheService struct {
    store DataStore
}

func NewCacheService(store DataStore) *CacheService {
    return &CacheService{store: store}
}

func (c *CacheService) GetValue(key string) (string, error) {
    return c.store.Get(key)
}

func (c *CacheService) SetValue(key, value string) error {
    return c.store.Set(key, value)
}

func (c *CacheService) DeleteValue(key string) error {
    return c.store.Delete(key)
}

// 测试CacheService
func TestCacheService_GetValue(t *testing.T) {
    // 创建Mock对象
    mockStore := new(MockDataStore)
    cacheService := NewCacheService(mockStore)

    // 设置Mock期望
    mockStore.On("Get", "test_key").Return("test_value", nil)

    // 执行测试
    result, err := cacheService.GetValue("test_key")

    // 断言结果
    assert.NoError(t, err)
    assert.Equal(t, "test_value", result)

    // 验证Mock调用
    mockStore.AssertCalled(t, "Get", "test_key")
}

func TestCacheService_GetValue_NotFound(t *testing.T) {
    mockStore := new(MockDataStore)
    cacheService := NewCacheService(mockStore)

    // 设置Mock期望 - 返回错误
    mockStore.On("Get", "nonexistent_key").Return("", errors.New("key not found"))

    // 执行测试
    result, err := cacheService.GetValue("nonexistent_key")

    // 断言结果
    assert.Error(t, err)
    assert.Equal(t, "key not found", err.Error())
    assert.Equal(t, "", result)

    // 验证Mock调用
    mockStore.AssertCalled(t, "Get", "nonexistent_key")
}

func TestCacheService_SetValue(t *testing.T) {
    mockStore := new(MockDataStore)
    cacheService := NewCacheService(mockStore)

    // 设置Mock期望
    mockStore.On("Set", "new_key", "new_value").Return(nil)

    // 执行测试
    err := cacheService.SetValue("new_key", "new_value")

    // 断言结果
    assert.NoError(t, err)

    // 验证Mock调用
    mockStore.AssertCalled(t, "Set", "new_key", "new_value")
}

func TestCacheService_DeleteValue(t *testing.T) {
    mockStore := new(MockDataStore)
    cacheService := NewCacheService(mockStore)

    // 设置Mock期望
    mockStore.On("Delete", "old_key").Return(nil)

    // 执行测试
    err := cacheService.DeleteValue("old_key")

    // 断言结果
    assert.NoError(t, err)

    // 验证Mock调用
    mockStore.AssertCalled(t, "Delete", "old_key")
}
```

### 练习3: HTTP处理器测试
```go
package handlers_test

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"
    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

// UserHandler
type UserHandler struct {
    users map[string]interface{}
}

func NewUserHandler() *UserHandler {
    return &UserHandler{
        users: make(map[string]interface{}),
    }
}

func (h *UserHandler) GetUser(c *gin.Context) {
    id := c.Param("id")

    user, exists := h.users[id]
    if !exists {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    c.JSON(http.StatusOK, gin.H{"data": user})
}

func (h *UserHandler) CreateUser(c *gin.Context) {
    var user map[string]interface{}

    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
        return
    }

    id := user["id"].(string)
    h.users[id] = user

    c.JSON(http.StatusCreated, gin.H{"data": user})
}

// 设置测试路由
func setupTestRouter(handler *UserHandler) *gin.Engine {
    gin.SetMode(gin.TestMode)
    router := gin.New()

    router.GET("/users/:id", handler.GetUser)
    router.POST("/users", handler.CreateUser)

    return router
}

// 测试GetUser
func TestUserHandler_GetUser(t *testing.T) {
    // 创建测试处理器
    handler := NewUserHandler()

    // 添加测试数据
    testUser := map[string]interface{}{
        "id":   "1",
        "name": "张三",
        "age":  25,
    }
    handler.users["1"] = testUser

    // 创建路由
    router := setupTestRouter(handler)

    // 创建测试请求
    req, _ := http.NewRequest("GET", "/users/1", nil)
    w := httptest.NewRecorder()

    // 执行请求
    router.ServeHTTP(w, req)

    // 断言响应
    assert.Equal(t, http.StatusOK, w.Code)

    var response map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &response)

    assert.Equal(t, testUser, response["data"])
}

func TestUserHandler_GetUser_NotFound(t *testing.T) {
    handler := NewUserHandler()
    router := setupTestRouter(handler)

    req, _ := http.NewRequest("GET", "/users/999", nil)
    w := httptest.NewRecorder()

    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusNotFound, w.Code)

    var response map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &response)

    assert.Equal(t, "User not found", response["error"])
}

// 测试CreateUser
func TestUserHandler_CreateUser(t *testing.T) {
    handler := NewUserHandler()
    router := setupTestRouter(handler)

    // 创建请求数据
    newUser := map[string]interface{}{
        "id":   "2",
        "name": "李四",
        "age":  30,
    }

    jsonValue, _ := json.Marshal(newUser)
    req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(jsonValue))
    req.Header.Set("Content-Type", "application/json")

    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusCreated, w.Code)

    var response map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &response)

    assert.Equal(t, newUser, response["data"])
    assert.Equal(t, newUser, handler.users["2"])
}

func TestUserHandler_CreateUser_InvalidRequest(t *testing.T) {
    handler := NewUserHandler()
    router := setupTestRouter(handler)

    // 创建无效请求
    req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer([]byte("invalid json")))
    req.Header.Set("Content-Type", "application/json")

    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusBadRequest, w.Code)

    var response map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &response)

    assert.Equal(t, "Invalid request", response["error"])
}
```

## 📋 测试最佳实践

### 1. 测试命名规范
```go
// 好的测试函数名
func TestUserService_CreateUser_ValidInput(t *testing.T)
func TestUserService_CreateUser_InvalidEmail(t *testing.T)
func TestUserService_CreateUser_DatabaseError(t *testing.T)

// 好的子测试名
t.Run("with valid input", func(t *testing.T) {})
t.Run("with invalid email", func(t *testing.T) {})
t.Run("with database error", func(t *testing.T) {})
```

### 2. 测试组织结构
```go
// 测试文件组织
package services_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

// 常量定义
const (
    TestUserName  = "测试用户"
    TestUserEmail = "test@example.com"
)

// 辅助函数
func createTestUser() *models.User {
    return &models.User{
        Name:  TestUserName,
        Email: TestUserEmail,
    }
}

// 测试组
func TestUserService(t *testing.T) {
    // 这里可以放置共享的Setup代码
}

// 具体测试函数
func TestUserService_CreateUser(t *testing.T) {
    // 测试逻辑
}
```

### 3. 测试覆盖率检查
```bash
# 在Makefile中添加测试目标
.PHONY: test
test:
	go test -v -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

.PHONY: test-coverage
test-coverage:
	go test -v -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	open coverage.html

.PHONY: test-race
test-race:
	go test -v -race ./...
```

## 📋 检查清单

- [ ] 理解Go的testing包基本用法
- [ ] 掌握表驱动测试模式
- [ ] 学会使用Mock和Stub
- [ ] 理解测试覆盖率分析
- [ ] 掌握基准测试编写
- [ ] 学会HTTP处理器测试
- [ ] 理解Go测试与PHP测试的差异
- [ ] 掌握测试最佳实践

## 🚀 下一步

掌握单元测试后，你可以继续学习：
- **集成测试**: 测试多个组件的交互
- **性能测试**: 基准测试和性能分析
- **测试驱动开发**: TDD实践
- **持续集成**: CI/CD中的自动化测试

---

**学习提示**: Go的测试框架虽然简单，但功能强大。通过良好的测试实践，你可以构建更加可靠的Go应用。相比于PHP的PHPUnit，Go的测试更加内聚和高效。

*最后更新: 2025年9月*

<!-- full-library-explanation -->
## 第一条单元测试应独立说明一条业务规则

前置是函数、error 和接口，不要求先了解 PHP。先挑一个不依赖网络的小规则，例如用户名去除两端空白后长度必须在 3 到 20 之间。为正常值、边界长度、空字符串分别给出输入与预期结果，测试失败信息写出 got 与 want。测试预期应来自规则，不应调用另一遍同一实现来计算。

当规则依赖外部数据时再引入小接口。例如注册服务依赖 EmailExists 和 Save，可用内存实现模拟邮箱重复，验证重复时不发生保存。测试关注服务对外行为；如果断言每个内部辅助函数的调用顺序，重构实现即使没有改变行为也会导致大量无意义失败。

练习：把用户名最小长度从 3 故意改为 4，至少一个边界测试应失败；恢复实现后应通过。再模拟仓储返回错误，服务应返回可识别的失败且不继续保存。共享 map、时钟和随机源都可能让并行测试不稳定，使用每个测试独立的夹具和可控制输入。示例中的 your-project 导入是占位，需要替换为自己的模块路径并补齐被测服务。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
