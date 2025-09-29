# Gin测试策略详解

本文档详细介绍Gin框架的测试策略，包括Handler测试、中间件测试、性能测试、集成测试等完整的测试体系。

## 1. 测试环境搭建

### 1.1 测试框架配置

#### 1.1.1 测试依赖管理
```go
// go.mod
module your-project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/stretchr/testify v1.8.4
    github.com/golang/mock v1.6.0
    github.com/andreyvit/diff v0.0.0-20210706072047-35b8766d3293
    golang.org/x/net v0.17.0
    github.com/stretchr/testify/assert v1.8.4
    github.com/stretchr/testify/require v1.8.4
    github.com/ory/dockertest v3.8.2+incompatible
    github.com/stretchr/testify/suite v1.8.4
)

require (
    // ... 其他依赖
)
```

#### 1.1.2 测试工具类
```go
package testutils

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

// 测试HTTP请求构建器
type TestRequestBuilder struct {
    method  string
    path    string
    headers map[string]string
    body    interface{}
    params  map[string]string
    queries map[string]string
}

func NewTestRequestBuilder(method, path string) *TestRequestBuilder {
    return &TestRequestBuilder{
        method:  method,
        path:    path,
        headers: make(map[string]string),
        params:  make(map[string]string),
        queries: make(map[string]string),
    }
}

func (b *TestRequestBuilder) SetHeader(key, value string) *TestRequestBuilder {
    b.headers[key] = value
    return b
}

func (b *TestRequestBuilder) SetBody(body interface{}) *TestRequestBuilder {
    b.body = body
    return b
}

func (b *TestRequestBuilder) SetParam(key, value string) *TestRequestBuilder {
    b.params[key] = value
    return b
}

func (b *TestRequestBuilder) SetQuery(key, value string) *TestRequestBuilder {
    b.queries[key] = value
    return b
}

func (b *TestRequestBuilder) Build() (*http.Request, error) {
    // 构建查询参数
    if len(b.queries) > 0 {
        var queryParts []string
        for key, value := range b.queries {
            queryParts = append(queryParts, fmt.Sprintf("%s=%s", key, value))
        }
        b.path += "?" + strings.Join(queryParts, "&")
    }

    // 构建请求体
    var body io.Reader
    if b.body != nil {
        bodyBytes, err := json.Marshal(b.body)
        if err != nil {
            return nil, err
        }
        body = bytes.NewReader(bodyBytes)
    }

    req, err := http.NewRequest(b.method, b.path, body)
    if err != nil {
        return nil, err
    }

    // 设置请求头
    for key, value := range b.headers {
        req.Header.Set(key, value)
    }

    // 设置路由参数
    if len(b.params) > 0 {
        gin.Params = make([]gin.Param, 0, len(b.params))
        for key, value := range b.params {
            gin.Params = append(gin.Params, gin.Param{Key: key, Value: value})
        }
    }

    return req, nil
}

// 测试响应断言器
type TestResponseAsserter struct {
    t       *testing.T
    recorder *httptest.ResponseRecorder
}

func NewTestResponseAsserter(t *testing.T, recorder *httptest.ResponseRecorder) *TestResponseAsserter {
    return &TestResponseAsserter{
        t:       t,
        recorder: recorder,
    }
}

func (a *TestResponseAsserter) Status(status int) *TestResponseAsserter {
    assert.Equal(a.t, status, a.recorder.Code)
    return a
}

func (a *TestResponseAsserter) Header(key, value string) *TestResponseAsserter {
    assert.Equal(a.t, value, a.recorder.Header().Get(key))
    return a
}

func (a *TestResponseAsserter) Contains(substring string) *TestResponseAsserter {
    assert.Contains(a.t, a.recorder.Body.String(), substring)
    return a
}

func (a *TestResponseAsserter) NotContains(substring string) *TestResponseAsserter {
    assert.NotContains(a.t, a.recorder.Body.String(), substring)
    return a
}

func (a *TestResponseAsserter) JSONBody(target interface{}) *TestResponseAsserter {
    var result interface{}
    err := json.Unmarshal(a.recorder.Body.Bytes(), &result)
    assert.NoError(a.t, err)
    assert.Equal(a.t, target, result)
    return a
}

func (a *TestResponseAsserter) JSONPath(path string, target interface{}) *TestResponseAsserter {
    var result map[string]interface{}
    err := json.Unmarshal(a.recorder.Body.Bytes(), &result)
    assert.NoError(a.t, err)

    // 简单的JSON路径解析
    parts := strings.Split(path, ".")
    current := result

    for _, part := range parts {
        if currentMap, ok := current.(map[string]interface{}); ok {
            current = currentMap[part]
        } else {
            a.t.Fatalf("JSON path not found: %s", path)
        }
    }

    assert.Equal(a.t, target, current)
    return a
}

// 测试辅助函数
func NewTestGinEngine() *gin.Engine {
    gin.SetMode(gin.TestMode)
    return gin.New()
}

func ExecuteTestRequest(router *gin.Engine, req *http.Request) *httptest.ResponseRecorder {
    recorder := httptest.NewRecorder()
    router.ServeHTTP(recorder, req)
    return recorder
}

// 构建测试请求的便捷函数
func BuildTestRequest(method, path string, body interface{}) *http.Request {
    builder := NewTestRequestBuilder(method, path)
    if body != nil {
        builder.SetBody(body)
    }
    req, _ := builder.Build()
    return req
}
```

### 1.2 测试数据库配置

#### 1.2.1 测试数据库管理
```go
package testutils

import (
    "database/sql"
    "fmt"
    "log"
    "os"
    "sync"
    "time"

    "github.com/ory/dockertest"
    "github.com/ory/dockertest/docker"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

// 测试数据库管理器
type TestDatabaseManager struct {
    pool      *dockertest.Pool
    resource  *dockertest.Resource
    db        *gorm.DB
    sqlDB     *sql.DB
    mu        sync.Mutex
    initialized bool
}

// 新建测试数据库管理器
func NewTestDatabaseManager() *TestDatabaseManager {
    return &TestDatabaseManager{}
}

// 初始化测试数据库
func (tdm *TestDatabaseManager) SetupDatabase() (*gorm.DB, error) {
    tdm.mu.Lock()
    defer tdm.mu.Unlock()

    if tdm.initialized {
        return tdm.db, nil
    }

    // 使用Docker启动PostgreSQL测试容器
    pool, err := dockertest.NewPool("")
    if err != nil {
        return nil, fmt.Errorf("could not connect to Docker: %v", err)
    }

    // 拉取PostgreSQL镜像
    resource, err := pool.RunWithOptions(&dockertest.RunOptions{
        Repository: "postgres",
        Tag:        "15",
        Env: []string{
            "POSTGRES_PASSWORD=testpass",
            "POSTGRES_USER=testuser",
            "POSTGRES_DB=testdb",
        },
    })
    if err != nil {
        return nil, fmt.Errorf("could not start resource: %v", err)
    }

    // 等待数据库启动
    var db *gorm.DB
    if err := pool.Retry(func() error {
        dbHost := resource.GetHostPort("5432/tcp")
        dsn := fmt.Sprintf("host=localhost port=%s user=testuser password=testpass dbname=testdb sslmode=disable", dbHost)

        var sqlDB *sql.DB
        sqlDB, err = sql.Open("postgres", dsn)
        if err != nil {
            return err
        }

        if err = sqlDB.Ping(); err != nil {
            return err
        }

        db, err = gorm.Open(postgres.New(postgres.Config{
            Conn: sqlDB,
        }), &gorm.Config{
            Logger: logger.Default.LogMode(logger.Silent),
        })
        if err != nil {
            return err
        }

        tdm.sqlDB = sqlDB
        return nil
    }); err != nil {
        return nil, fmt.Errorf("could not connect to database: %v", err)
    }

    tdm.pool = pool
    tdm.resource = resource
    tdm.db = db
    tdm.initialized = true

    // 运行数据库迁移
    if err := tdm.runMigrations(); err != nil {
        return nil, fmt.Errorf("failed to run migrations: %v", err)
    }

    return tdm.db, nil
}

// 运行数据库迁移
func (tdm *TestDatabaseManager) runMigrations() error {
    // 这里可以添加数据库迁移逻辑
    // 例如：自动创建表结构
    return tdm.db.AutoMigrate(
        &User{},
        &Product{},
        &Order{},
        // ... 其他模型
    )
}

// 清理测试数据
func (tdm *TestDatabaseManager) Cleanup() error {
    tdm.mu.Lock()
    defer tdm.mu.Unlock()

    if tdm.db == nil {
        return nil
    }

    // 清理所有表数据
    tables := []string{"users", "products", "orders"}
    for _, table := range tables {
        if err := tdm.db.Exec(fmt.Sprintf("TRUNCATE TABLE %s CASCADE", table)).Error; err != nil {
            return err
        }
    }

    return nil
}

// 关闭数据库连接
func (tdm *TestDatabaseManager) Close() error {
    tdm.mu.Lock()
    defer tdm.mu.Unlock()

    if tdm.sqlDB != nil {
        tdm.sqlDB.Close()
    }

    if tdm.pool != nil && tdm.resource != nil {
        if err := tdm.pool.Purge(tdm.resource); err != nil {
            return err
        }
    }

    tdm.initialized = false
    return nil
}

// 获取数据库连接
func (tdm *TestDatabaseManager) GetDB() *gorm.DB {
    return tdm.db
}

// 测试模型定义
type User struct {
    ID        uint      `gorm:"primarykey" json:"id"`
    Username  string    `gorm:"unique;not null" json:"username"`
    Email     string    `gorm:"unique;not null" json:"email"`
    Password  string    `gorm:"not null" json:"-"`
    CreatedAt time.Time `gorm:"autoCreateTime" json:"created_at"`
    UpdatedAt time.Time `gorm:"autoUpdateTime" json:"updated_at"`
}

type Product struct {
    ID          uint      `gorm:"primarykey" json:"id"`
    Name        string    `gorm:"not null" json:"name"`
    Description string    `json:"description"`
    Price       float64   `gorm:"not null" json:"price"`
    Stock       int       `gorm:"default:0" json:"stock"`
    CreatedAt   time.Time `gorm:"autoCreateTime" json:"created_at"`
    UpdatedAt   time.Time `gorm:"autoUpdateTime" json:"updated_at"`
}

type Order struct {
    ID        uint      `gorm:"primarykey" json:"id"`
    UserID    uint      `gorm:"not null" json:"user_id"`
    ProductID uint      `gorm:"not null" json:"product_id"`
    Quantity  int       `gorm:"not null" json:"quantity"`
    Status    string    `gorm:"default:pending" json:"status"`
    CreatedAt time.Time `gorm:"autoCreateTime" json:"created_at"`
    UpdatedAt time.Time `gorm:"autoUpdateTime" json:"updated_at"`
}

// 全局测试数据库管理器实例
var GlobalTestDB *TestDatabaseManager

// 初始化全局测试数据库
func SetupTestDatabase() (*gorm.DB, error) {
    if GlobalTestDB == nil {
        GlobalTestDB = NewTestDatabaseManager()
    }
    return GlobalTestDB.SetupDatabase()
}

// 清理测试数据
func CleanupTestDatabase() error {
    if GlobalTestDB != nil {
        return GlobalTestDB.Cleanup()
    }
    return nil
}

// 关闭测试数据库
func CloseTestDatabase() error {
    if GlobalTestDB != nil {
        return GlobalTestDB.Close()
    }
    return nil
}
```

#### 1.2.2 Mock服务配置
```go
package testutils

import (
    "encoding/json"
    "fmt"
    "net/http"
    "net/http/httptest"
    "sync"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/mock"
)

// Mock服务配置
type MockServerConfig struct {
    Port     int
    Routes   []MockRoute
    Response map[string]interface{}
}

type MockRoute struct {
    Path    string
    Method  string
    Handler http.HandlerFunc
}

// Mock服务
type MockServer struct {
    server   *httptest.Server
    config   *MockServerConfig
    mu       sync.Mutex
}

func NewMockServer(config *MockServerConfig) *MockServer {
    router := gin.New()

    // 注册Mock路由
    for _, route := range config.Routes {
        switch route.Method {
        case http.MethodGet:
            router.GET(route.Path, gin.WrapH(route.Handler))
        case http.MethodPost:
            router.POST(route.Path, gin.WrapH(route.Handler))
        case http.MethodPut:
            router.PUT(route.Path, gin.WrapH(route.Handler))
        case http.MethodDelete:
            router.DELETE(route.Path, gin.WrapH(route.Handler))
        case http.MethodPatch:
            router.PATCH(route.Path, gin.WrapH(route.Handler))
        }
    }

    server := httptest.NewServer(router)

    return &MockServer{
        server: server,
        config: config,
    }
}

// 获取服务器URL
func (ms *MockServer) GetURL() string {
    return ms.server.URL
}

// 关闭服务器
func (ms *MockServer) Close() {
    ms.server.Close()
}

// Mock HTTP客户端
type MockHTTPClient struct {
    mock       *mock.Mock
    responses  map[string]*http.Response
    errors     map[string]error
    mu         sync.Mutex
}

func NewMockHTTPClient() *MockHTTPClient {
    return &MockHTTPClient{
        mock:      &mock.Mock{},
        responses: make(map[string]*http.Response),
        errors:    make(map[string]error),
    }
}

// Mock Do方法
func (m *MockHTTPClient) Do(req *http.Request) (*http.Response, error) {
    m.mu.Lock()
    defer m.mu.Unlock()

    key := req.Method + ":" + req.URL.String()

    if err, exists := m.errors[key]; exists {
        return nil, err
    }

    if resp, exists := m.responses[key]; exists {
        return resp, nil
    }

    // 调用mock方法
    args := m.mock.Called(req)
    if len(args) > 0 {
        if resp, ok := args.Get(0).(*http.Response); ok {
            return resp, nil
        }
    }

    return nil, fmt.Errorf("no mock response for request: %s", key)
}

// 设置Mock响应
func (m *MockHTTPClient) SetMockResponse(method, url string, response *http.Response) {
    m.mu.Lock()
    defer m.mu.Unlock()

    key := method + ":" + url
    m.responses[key] = response
}

// 设置Mock错误
func (m *MockHTTPClient) SetMockError(method, url string, err error) {
    m.mu.Lock()
    defer m.mu.Unlock()

    key := method + ":" + url
    m.errors[key] = err
}

// 创建Mock HTTP响应
func CreateMockResponse(statusCode int, body interface{}) *http.Response {
    bodyBytes, _ := json.Marshal(body)

    return &http.Response{
        StatusCode: statusCode,
        Body:       &MockResponseBody{data: bodyBytes},
        Header:     make(http.Header),
    }
}

// Mock响应体
type MockResponseBody struct {
    data []byte
    pos  int
}

func (m *MockResponseBody) Read(p []byte) (n int, err error) {
    if m.pos >= len(m.data) {
        return 0, io.EOF
    }
    n = copy(p, m.data[m.pos:])
    m.pos += n
    return n, nil
}

func (m *MockResponseBody) Close() error {
    return nil
}

// Mock认证服务
type MockAuthService struct {
    mock *mock.Mock
}

func NewMockAuthService() *MockAuthService {
    return &MockAuthService{
        mock: &mock.Mock{},
    }
}

func (m *MockAuthService) Authenticate(token string) (bool, *UserInfo, error) {
    args := m.mock.Called(token)
    return args.Bool(0), args.Get(1).(*UserInfo), args.Error(2)
}

func (m *MockAuthService) GenerateToken(userID string) (string, error) {
    args := m.mock.Called(userID)
    return args.String(0), args.Error(1)
}

type UserInfo struct {
    ID       string   `json:"id"`
    Username string   `json:"username"`
    Roles    []string `json:"roles"`
}

// Mock缓存服务
type MockCacheService struct {
    mock *mock.Mock
}

func NewMockCacheService() *MockCacheService {
    return &MockCacheService{
        mock: &mock.Mock{},
    }
}

func (m *MockCacheService) Get(key string) (interface{}, bool) {
    args := m.mock.Called(key)
    return args.Get(0), args.Bool(1)
}

func (m *MockCacheService) Set(key string, value interface{}, ttl int) {
    m.mock.Called(key, value, ttl)
}

func (m *MockCacheService) Delete(key string) {
    m.mock.Called(key)
}

// Mock消息队列服务
type MockMessageQueue struct {
    mock *mock.Mock
}

func NewMockMessageQueue() *MockMessageQueue {
    return &MockMessageQueue{
        mock: &mock.Mock{},
    }
}

func (m *MockMessageQueue) Publish(queue string, message interface{}) error {
    args := m.mock.Called(queue, message)
    return args.Error(0)
}

func (m *MockMessageQueue) Consume(queue string, handler func(interface{}) error) error {
    args := m.mock.Called(queue, handler)
    return args.Error(0)
}
```

## 2. Handler测试

### 2.1 基本 Handler 测试

#### 2.1.1 简单 Handler 测试
```go
package handlers

import (
    "net/http"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/your-project/testutils"
)

// UserHandler 用户处理器
type UserHandler struct {
    userService *UserService
}

func NewUserHandler(userService *UserService) *UserHandler {
    return &UserHandler{
        userService: userService,
    }
}

// GetUser 获取用户信息
func (h *UserHandler) GetUser(c *gin.Context) {
    userID := c.Param("id")

    user, err := h.userService.GetUserByID(userID)
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    c.JSON(http.StatusOK, user)
}

// CreateUser 创建用户
func (h *UserHandler) CreateUser(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    user, err := h.userService.CreateUser(&req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    c.JSON(http.StatusCreated, user)
}

type CreateUserRequest struct {
    Username string `json:"username" binding:"required,min=3,max=50"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,min=8"`
}

// 用户服务接口
type UserService interface {
    GetUserByID(id string) (*User, error)
    CreateUser(req *CreateUserRequest) (*User, error)
}

// 测试 GetUser Handler
func TestGetUser(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    // 创建 Mock 用户服务
    mockUserService := &MockUserService{}

    // 创建 Handler
    userHandler := NewUserHandler(mockUserService)

    // 创建路由
    router := testutils.NewTestGinEngine()
    router.GET("/users/:id", userHandler.GetUser)

    t.Run("用户存在", func(t *testing.T) {
        // 准备 Mock 数据
        expectedUser := &User{
            ID:       1,
            Username: "testuser",
            Email:    "test@example.com",
        }

        mockUserService.On("GetUserByID", "1").Return(expectedUser, nil)

        // 创建测试请求
        req := testutils.BuildTestRequest("GET", "/users/1", nil)
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONBody(gin.H{
                "id":       uint(1),
                "username": "testuser",
                "email":    "test@example.com",
            })
    })

    t.Run("用户不存在", func(t *testing.T) {
        // 准备 Mock 数据
        mockUserService.On("GetUserByID", "999").Return(nil, fmt.Errorf("user not found"))

        // 创建测试请求
        req := testutils.BuildTestRequest("GET", "/users/999", nil)
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusNotFound).
            JSONBody(gin.H{"error": "User not found"})
    })
}

// 测试 CreateUser Handler
func TestCreateUser(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    // 创建 Mock 用户服务
    mockUserService := &MockUserService{}

    // 创建 Handler
    userHandler := NewUserHandler(mockUserService)

    // 创建路由
    router := testutils.NewTestGinEngine()
    router.POST("/users", userHandler.CreateUser)

    t.Run("创建用户成功", func(t *testing.T) {
        // 准备请求数据
        reqBody := CreateUserRequest{
            Username: "newuser",
            Email:    "newuser@example.com",
            Password: "password123",
        }

        // 准备 Mock 响应
        expectedUser := &User{
            ID:       2,
            Username: "newuser",
            Email:    "newuser@example.com",
        }

        mockUserService.On("CreateUser", &reqBody).Return(expectedUser, nil)

        // 创建测试请求
        req := testutils.BuildTestRequest("POST", "/users", reqBody)
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusCreated).
            JSONBody(gin.H{
                "id":       uint(2),
                "username": "newuser",
                "email":    "newuser@example.com",
            })
    })

    t.Run("请求数据无效", func(t *testing.T) {
        // 准备无效请求数据
        reqBody := map[string]interface{}{
            "username": "ab", // 用户名太短
            "email":    "invalid-email",
            "password": "123", // 密码太短
        }

        // 创建测试请求
        req := testutils.BuildTestRequest("POST", "/users", reqBody)
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusBadRequest).
            Contains("Key: 'CreateUserRequest.Username' Error:Field validation")
    })
}

// Mock 用户服务
type MockUserService struct {
    mock.Mock
}

func (m *MockUserService) GetUserByID(id string) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserService) CreateUser(req *CreateUserRequest) (*User, error) {
    args := m.Called(req)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}
```

#### 2.1.2 复杂 Handler 测试
```go
package handlers

import (
    "fmt"
    "net/http"
    "strconv"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/your-project/models"
    "github.com/your-project/services"
    "github.com/your-project/testutils"
)

// ProductHandler 产品处理器
type ProductHandler struct {
    productService  services.ProductService
    cacheService    services.CacheService
    analyticsService services.AnalyticsService
}

func NewProductHandler(
    productService services.ProductService,
    cacheService services.CacheService,
    analyticsService services.AnalyticsService,
) *ProductHandler {
    return &ProductHandler{
        productService:  productService,
        cacheService:    cacheService,
        analyticsService: analyticsService,
    }
}

// SearchProducts 搜索产品
func (h *ProductHandler) SearchProducts(c *gin.Context) {
    // 解析查询参数
    query := c.Query("q")
    category := c.Query("category")
    minPrice, _ := strconv.ParseFloat(c.Query("min_price"), 64)
    maxPrice, _ := strconv.ParseFloat(c.Query("max_price"), 64)
    page, _ := strconv.Atoi(c.Query("page"))
    if page == 0 {
        page = 1
    }
    pageSize, _ := strconv.Atoi(c.Query("page_size"))
    if pageSize == 0 {
        pageSize = 10
    }

    // 构建搜索请求
    searchReq := &services.ProductSearchRequest{
        Query:    query,
        Category: category,
        MinPrice: minPrice,
        MaxPrice: maxPrice,
        Page:     page,
        PageSize: pageSize,
    }

    // 生成缓存键
    cacheKey := fmt.Sprintf("products:search:%v", searchReq)

    // 尝试从缓存获取
    if cached, found := h.cacheService.Get(cacheKey); found {
        h.analyticsService.TrackSearch(c, searchReq)
        c.JSON(http.StatusOK, cached)
        return
    }

    // 从数据库搜索
    result, err := h.productService.SearchProducts(searchReq)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    // 缓存结果
    h.cacheService.Set(cacheKey, result, 300) // 5分钟缓存

    // 记录分析数据
    h.analyticsService.TrackSearch(c, searchReq)

    c.JSON(http.StatusOK, result)
}

// GetProduct 获取产品详情
func (h *ProductHandler) GetProduct(c *gin.Context) {
    productID := c.Param("id")

    // 尝试从缓存获取
    cacheKey := fmt.Sprintf("products:%s", productID)
    if cached, found := h.cacheService.Get(cacheKey); found {
        h.analyticsService.TrackProductView(c, productID)
        c.JSON(http.StatusOK, cached)
        return
    }

    // 从数据库获取
    product, err := h.productService.GetProductByID(productID)
    if err != nil {
        if err == services.ErrProductNotFound {
            c.JSON(http.StatusNotFound, gin.H{"error": "Product not found"})
            return
        }
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    // 缓存产品信息
    h.cacheService.Set(cacheKey, product, 600) // 10分钟缓存

    // 记录分析数据
    h.analyticsService.TrackProductView(c, productID)

    c.JSON(http.StatusOK, product)
}

// 测试 SearchProducts Handler
func TestSearchProducts(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    // 创建 Mock 服务
    mockProductService := &MockProductService{}
    mockCacheService := &MockCacheService{}
    mockAnalyticsService := &MockAnalyticsService{}

    // 创建 Handler
    productHandler := NewProductHandler(mockProductService, mockCacheService, mockAnalyticsService)

    // 创建路由
    router := testutils.NewTestGinEngine()
    router.GET("/products/search", productHandler.SearchProducts)

    t.Run("基本搜索", func(t *testing.T) {
        // 准备 Mock 数据
        searchReq := &services.ProductSearchRequest{
            Query:    "laptop",
            Category: "",
            MinPrice: 0,
            MaxPrice: 0,
            Page:     1,
            PageSize: 10,
        }

        expectedResult := &services.ProductSearchResult{
            Products: []*models.Product{
                {
                    ID:          1,
                    Name:        "Laptop A",
                    Description: "High performance laptop",
                    Price:       999.99,
                    Stock:       10,
                },
                {
                    ID:          2,
                    Name:        "Laptop B",
                    Description: "Business laptop",
                    Price:       1299.99,
                    Stock:       5,
                },
            },
            Total:     2,
            Page:      1,
            PageSize:  10,
            TotalPages: 1,
        }

        mockCacheService.On("Get", mock.Anything).Return(nil, false)
        mockProductService.On("SearchProducts", searchReq).Return(expectedResult, nil)
        mockCacheService.On("Set", mock.Anything, expectedResult, 300).Return()
        mockAnalyticsService.On("TrackSearch", mock.Anything, searchReq).Return()

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/products/search").
            SetQuery("q", "laptop").
            SetQuery("page", "1").
            SetQuery("page_size", "10").
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONPath("total", 2).
            JSONPath("products.0.name", "Laptop A").
            JSONPath("products.1.name", "Laptop B")
    })

    t.Run("从缓存获取", func(t *testing.T) {
        // 准备缓存数据
        cachedResult := &services.ProductSearchResult{
            Products: []*models.Product{
                {
                    ID:          1,
                    Name:        "Cached Product",
                    Description: "Product from cache",
                    Price:       99.99,
                    Stock:       50,
                },
            },
            Total:     1,
            Page:      1,
            PageSize:  10,
            TotalPages: 1,
        }

        mockCacheService.On("Get", mock.Anything).Return(cachedResult, true)
        mockAnalyticsService.On("TrackSearch", mock.Anything, mock.Anything).Return()

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/products/search").
            SetQuery("q", "cached").
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONPath("products.0.name", "Cached Product")

        // 验证没有调用产品服务
        mockProductService.AssertNotCalled(t, "SearchProducts")
    })

    t.Run("价格范围搜索", func(t *testing.T) {
        searchReq := &services.ProductSearchRequest{
            Query:    "phone",
            Category: "electronics",
            MinPrice: 100,
            MaxPrice: 1000,
            Page:     1,
            PageSize: 10,
        }

        expectedResult := &services.ProductSearchResult{
            Products: []*models.Product{
                {
                    ID:          3,
                    Name:        "Smartphone",
                    Description: "Android smartphone",
                    Price:       599.99,
                    Stock:       20,
                },
            },
            Total:     1,
            Page:      1,
            PageSize:  10,
            TotalPages: 1,
        }

        mockCacheService.On("Get", mock.Anything).Return(nil, false)
        mockProductService.On("SearchProducts", searchReq).Return(expectedResult, nil)
        mockCacheService.On("Set", mock.Anything, expectedResult, 300).Return()
        mockAnalyticsService.On("TrackSearch", mock.Anything, searchReq).Return()

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/products/search").
            SetQuery("q", "phone").
            SetQuery("category", "electronics").
            SetQuery("min_price", "100").
            SetQuery("max_price", "1000").
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONPath("products.0.price", 599.99)
    })

    t.Run("服务错误", func(t *testing.T) {
        mockCacheService.On("Get", mock.Anything).Return(nil, false)
        mockProductService.On("SearchProducts", mock.Anything).Return(nil, fmt.Errorf("database error"))

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/products/search").
            SetQuery("q", "error").
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusInternalServerError).
            Contains("database error")
    })
}

// Mock 产品服务
type MockProductService struct {
    mock.Mock
}

func (m *MockProductService) SearchProducts(req *services.ProductSearchRequest) (*services.ProductSearchResult, error) {
    args := m.Called(req)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*services.ProductSearchResult), args.Error(1)
}

func (m *MockProductService) GetProductByID(id string) (*models.Product, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*models.Product), args.Error(1)
}

// Mock 缓存服务
type MockCacheService struct {
    mock.Mock
}

func (m *MockCacheService) Get(key string) (interface{}, bool) {
    args := m.Called(key)
    return args.Get(0), args.Bool(1)
}

func (m *MockCacheService) Set(key string, value interface{}, ttl int) {
    m.Called(key, value, ttl)
}

// Mock 分析服务
type MockAnalyticsService struct {
    mock.Mock
}

func (m *MockAnalyticsService) TrackSearch(c *gin.Context, req *services.ProductSearchRequest) {
    m.Called(c, req)
}

func (m *MockAnalyticsService) TrackProductView(c *gin.Context, productID string) {
    m.Called(c, productID)
}
```

### 2.2 表单和文件上传测试

#### 2.2.1 表单数据处理测试
```go
package handlers

import (
    "bytes"
    "mime/multipart"
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/your-project/testutils"
)

// UploadHandler 文件上传处理器
type UploadHandler struct {
    uploadService UploadService
}

func NewUploadHandler(uploadService UploadService) *UploadHandler {
    return &UploadHandler{
        uploadService: uploadService,
    }
}

// UploadFile 上传文件
func (h *UploadHandler) UploadFile(c *gin.Context) {
    // 获取上传的文件
    file, err := c.FormFile("file")
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
        return
    }

    // 验证文件类型
    if !h.isValidFileType(file.Header.Get("Content-Type")) {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
        return
    }

    // 验证文件大小
    if file.Size > 10*1024*1024 { // 10MB
        c.JSON(http.StatusBadRequest, gin.H{"error": "File too large"})
        return
    }

    // 保存文件
    filename := h.generateFilename(file.Filename)
    if err := h.uploadService.SaveFile(file, filename); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "filename": filename,
        "size":     file.Size,
        "type":     file.Header.Get("Content-Type"),
    })
}

// 验证文件类型
func (h *UploadHandler) isValidFileType(contentType string) bool {
    validTypes := []string{
        "image/jpeg",
        "image/png",
        "image/gif",
        "application/pdf",
        "text/plain",
    }

    for _, validType := range validTypes {
        if contentType == validType {
            return true
        }
    }
    return false
}

// 生成文件名
func (h *UploadHandler) generateFilename(originalName string) string {
    // 简化的文件名生成逻辑
    return "upload_" + originalName
}

// UploadService 上传服务接口
type UploadService interface {
    SaveFile(file *multipart.FileHeader, filename string) error
}

// 测试文件上传 Handler
func TestUploadFile(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    // 创建 Mock 上传服务
    mockUploadService := &MockUploadService{}

    // 创建 Handler
    uploadHandler := NewUploadHandler(mockUploadService)

    // 创建路由
    router := testutils.NewTestGinEngine()
    router.POST("/upload", uploadHandler.UploadFile)

    t.Run("成功上传文件", func(t *testing.T) {
        // 创建测试文件内容
        fileContent := "test file content"
        body := &bytes.Buffer{}
        writer := multipart.NewWriter(body)

        // 创建表单文件字段
        part, err := writer.CreateFormFile("file", "test.txt")
        assert.NoError(t, err)

        // 写入文件内容
        _, err = part.Write([]byte(fileContent))
        assert.NoError(t, err)

        // 关闭写入器
        err = writer.Close()
        assert.NoError(t, err)

        // 准备 Mock 数据
        expectedFilename := "upload_test.txt"
        mockUploadService.On("SaveFile", mock.Anything, expectedFilename).Return(nil)

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("POST", "/upload").
            SetHeader("Content-Type", writer.FormDataContentType()).
            SetBody(body.Bytes()).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONPath("filename", expectedFilename).
            JSONPath("size", int64(len(fileContent)))
    })

    t.Run("没有上传文件", func(t *testing.T) {
        // 创建空请求体
        body := &bytes.Buffer{}
        writer := multipart.NewWriter(body)
        writer.Close()

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("POST", "/upload").
            SetHeader("Content-Type", writer.FormDataContentType()).
            SetBody(body.Bytes()).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusBadRequest).
            JSONBody(gin.H{"error": "No file uploaded"})
    })

    t.Run("文件类型无效", func(t *testing.T) {
        // 创建无效类型的文件
        fileContent := "malicious content"
        body := &bytes.Buffer{}
        writer := multipart.NewWriter(body)

        part, err := writer.CreateFormFile("file", "malicious.exe")
        assert.NoError(t, err)

        _, err = part.Write([]byte(fileContent))
        assert.NoError(t, err)

        writer.Close()

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("POST", "/upload").
            SetHeader("Content-Type", writer.FormDataContentType()).
            SetBody(body.Bytes()).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusBadRequest).
            JSONBody(gin.H{"error": "Invalid file type"})
    })

    t.Run("文件过大", func(t *testing.T) {
        // 创建大文件 (超过10MB)
        body := &bytes.Buffer{}
        writer := multipart.NewWriter(body)

        part, err := writer.CreateFormFile("file", "large.jpg")
        assert.NoError(t, err)

        // 写入大文件内容
        largeContent := strings.Repeat("x", 11*1024*1024) // 11MB
        _, err = part.Write([]byte(largeContent))
        assert.NoError(t, err)

        writer.Close()

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("POST", "/upload").
            SetHeader("Content-Type", writer.FormDataContentType()).
            SetBody(body.Bytes()).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusBadRequest).
            JSONBody(gin.H{"error": "File too large"})
    })

    t.Run("保存文件失败", func(t *testing.T) {
        // 创建测试文件
        fileContent := "test file content"
        body := &bytes.Buffer{}
        writer := multipart.NewWriter(body)

        part, err := writer.CreateFormFile("file", "test.txt")
        assert.NoError(t, err)

        _, err = part.Write([]byte(fileContent))
        assert.NoError(t, err)

        writer.Close()

        // 准备 Mock 返回错误
        expectedFilename := "upload_test.txt"
        mockUploadService.On("SaveFile", mock.Anything, expectedFilename).Return(fmt.Errorf("save failed"))

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("POST", "/upload").
            SetHeader("Content-Type", writer.FormDataContentType()).
            SetBody(body.Bytes()).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusInternalServerError).
            JSONBody(gin.H{"error": "Failed to save file"})
    })
}

// 表单数据处理测试
func TestFormSubmission(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    // 创建 Mock 表单服务
    mockFormService := &MockFormService{}

    // 创建 Handler
    formHandler := NewFormHandler(mockFormService)

    // 创建路由
    router := testutils.NewTestGinEngine()
    router.POST("/submit", formHandler.SubmitForm)

    t.Run("表单提交成功", func(t *testing.T) {
        // 准备表单数据
        formData := url.Values{
            "name":    []string{"John Doe"},
            "email":   []string{"john@example.com"},
            "message": []string{"Hello World"},
        }

        // 准备 Mock 响应
        expectedResponse := &FormResponse{
            ID:      "form123",
            Name:    "John Doe",
            Email:   "john@example.com",
            Message: "Hello World",
        }

        mockFormService.On("ProcessForm", mock.Anything).Return(expectedResponse, nil)

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("POST", "/submit").
            SetHeader("Content-Type", "application/x-www-form-urlencoded").
            SetBody(strings.NewReader(formData.Encode())).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONPath("id", "form123").
            JSONPath("name", "John Doe")
    })

    t.Run("表单验证失败", func(t *testing.T) {
        // 准备无效表单数据
        formData := url.Values{
            "name":    []string{""}, // 必填字段为空
            "email":   []string{"invalid-email"},
            "message": []string{"Hello"},
        }

        mockFormService.On("ProcessForm", mock.Anything).Return(nil, fmt.Errorf("validation failed"))

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("POST", "/submit").
            SetHeader("Content-Type", "application/x-www-form-urlencoded").
            SetBody(strings.NewReader(formData.Encode())).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusBadRequest).
            Contains("validation failed")
    })
}

// Mock 上传服务
type MockUploadService struct {
    mock.Mock
}

func (m *MockUploadService) SaveFile(file *multipart.FileHeader, filename string) error {
    args := m.Called(file, filename)
    return args.Error(0)
}

// Mock 表单服务
type MockFormService struct {
    mock.Mock
}

func (m *MockFormService) ProcessForm(data *FormData) (*FormResponse, error) {
    args := m.Called(data)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*FormResponse), args.Error(1)
}
```

## 3. 中间件测试

### 3.1 认证中间件测试

#### 3.1.1 JWT 认证中间件测试
```go
package middleware

import (
    "net/http"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/your-project/auth"
    "github.com/your-project/testutils"
)

// JWTAuthMiddleware JWT认证中间件
func JWTAuthMiddleware(authService auth.AuthService) gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Missing token"})
            return
        }

        // 移除Bearer前缀
        if len(token) > 7 && token[:7] == "Bearer " {
            token = token[7:]
        }

        // 验证token
        claims, err := authService.VerifyToken(token)
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
            return
        }

        // 设置用户信息到Context
        c.Set("user_id", claims.UserID)
        c.Set("username", claims.Username)
        c.Set("user_roles", claims.Roles)

        c.Next()
    }
}

// 测试 JWT 认证中间件
func TestJWTAuthMiddleware(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    // 创建 Mock 认证服务
    mockAuthService := &MockAuthService{}

    // 创建测试路由
    router := testutils.NewTestGinEngine()

    // 应用中间件
    router.Use(JWTAuthMiddleware(mockAuthService))

    // 测试路由
    router.GET("/protected", func(c *gin.Context) {
        userID := c.GetString("user_id")
        username := c.GetString("username")
        roles := c.GetStringSlice("user_roles")

        c.JSON(http.StatusOK, gin.H{
            "user_id":  userID,
            "username": username,
            "roles":    roles,
        })
    })

    t.Run("认证成功", func(t *testing.T) {
        // 准备 Mock 数据
        token := "valid_token_123"
        claims := &auth.Claims{
            UserID:   "user123",
            Username: "testuser",
            Roles:    []string{"user", "admin"},
        }

        mockAuthService.On("VerifyToken", token).Return(claims, nil)

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/protected").
            SetHeader("Authorization", "Bearer "+token).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONPath("user_id", "user123").
            JSONPath("username", "testuser").
            JSONPath("roles", []string{"user", "admin"})
    })

    t.Run("缺少Token", func(t *testing.T) {
        // 创建测试请求（不带Authorization头）
        req := testutils.NewTestRequestBuilder("GET", "/protected").Build()
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusUnauthorized).
            JSONBody(gin.H{"error": "Missing token"})
    })

    t.Run("Token格式错误", func(t *testing.T) {
        // 创建测试请求（只有Bearer没有token）
        req := testutils.NewTestRequestBuilder("GET", "/protected").
            SetHeader("Authorization", "Bearer").
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusUnauthorized).
            JSONBody(gin.H{"error": "Invalid token"})
    })

    t.Run("Token验证失败", func(t *testing.T) {
        // 准备 Mock 数据（验证失败）
        token := "invalid_token_123"
        mockAuthService.On("VerifyToken", token).Return(nil, fmt.Errorf("token expired"))

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/protected").
            SetHeader("Authorization", "Bearer "+token).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusUnauthorized).
            JSONBody(gin.H{"error": "Invalid token"})
    })

    t.Run("没有Bearer前缀", func(t *testing.T) {
        // 准备 Mock 数据
        token := "valid_token_123"
        claims := &auth.Claims{
            UserID:   "user123",
            Username: "testuser",
            Roles:    []string{"user"},
        }

        mockAuthService.On("VerifyToken", token).Return(claims, nil)

        // 创建测试请求（不带Bearer前缀）
        req := testutils.NewTestRequestBuilder("GET", "/protected").
            SetHeader("Authorization", token).
            Build()

        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONPath("user_id", "user123")
    })
}
```

#### 3.1.2 角色权限中间件测试
```go
package middleware

import (
    "net/http"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/your-project/testutils"
)

// RoleMiddleware 角色权限中间件
func RoleMiddleware(allowedRoles ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRoles, exists := c.GetStringSlice("user_roles")
        if !exists {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
            return
        }

        // 检查用户是否拥有所需角色
        for _, allowedRole := range allowedRoles {
            for _, userRole := range userRoles {
                if userRole == allowedRole {
                    c.Next()
                    return
                }
            }
        }

        c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions"})
    }
}

// 测试角色权限中间件
func TestRoleMiddleware(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    t.Run("拥有所需角色", func(t *testing.T) {
        // 创建测试路由
        router := testutils.NewTestGinEngine()

        // 应用中间件
        router.Use(func(c *gin.Context) {
            c.Set("user_roles", []string{"user", "admin"})
        })
        router.Use(RoleMiddleware("admin"))

        router.GET("/admin", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"message": "Welcome admin"})
        })

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/admin").Build()
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONBody(gin.H{"message": "Welcome admin"})
    })

    t.Run("缺少所需角色", func(t *testing.T) {
        // 创建测试路由
        router := testutils.NewTestGinEngine()

        // 应用中间件
        router.Use(func(c *gin.Context) {
            c.Set("user_roles", []string{"user"})
        })
        router.Use(RoleMiddleware("admin"))

        router.GET("/admin", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"message": "Welcome admin"})
        })

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/admin").Build()
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusForbidden).
            JSONBody(gin.H{"error": "Insufficient permissions"})
    })

    t.Run("多角色验证", func(t *testing.T) {
        // 创建测试路由
        router := testutils.NewTestGinEngine()

        // 应用中间件
        router.Use(func(c *gin.Context) {
            c.Set("user_roles", []string{"editor"})
        })
        router.Use(RoleMiddleware("admin", "editor")) // 管理员或编辑器都可以访问

        router.GET("/content", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"message": "Content access granted"})
        })

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/content").Build()
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK).
            JSONBody(gin.H{"message": "Content access granted"})
    })

    t.Run("未认证用户", func(t *testing.T) {
        // 创建测试路由
        router := testutils.NewTestGinEngine()

        // 应用中间件（不设置用户角色）
        router.Use(RoleMiddleware("admin"))

        router.GET("/admin", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"message": "Welcome admin"})
        })

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/admin").Build()
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusUnauthorized).
            JSONBody(gin.H{"error": "User not authenticated"})
    })
}
```

### 3.2 日志和监控中间件测试

#### 3.2.1 日志中间件测试
```go
package middleware

import (
    "bytes"
    "net/http"
    "net/http/httptest"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/your-project/testutils"
)

// LoggerMiddleware 日志中间件
func LoggerMiddleware(logger Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        raw := c.Request.URL.RawQuery

        // 处理请求
        c.Next()

        // 记录请求日志
        end := time.Now()
        latency := end.Sub(start)

        clientIP := c.ClientIP()
        method := c.Request.Method
        statusCode := c.Writer.Status()
        bodySize := c.Writer.Size()

        if raw != "" {
            path = path + "?" + raw
        }

        logger.LogRequest(LogEntry{
            Timestamp:   end,
            ClientIP:    clientIP,
            Method:      method,
            Path:        path,
            Status:      statusCode,
            Latency:     latency,
            BodySize:    bodySize,
            UserAgent:   c.Request.UserAgent(),
            Error:       c.Errors.String(),
        })
    }
}

type Logger interface {
    LogRequest(entry LogEntry)
}

type LogEntry struct {
    Timestamp time.Time
    ClientIP  string
    Method    string
    Path      string
    Status    int
    Latency   time.Duration
    BodySize  int
    UserAgent string
    Error     string
}

// 测试日志中间件
func TestLoggerMiddleware(t *testing.T) {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    t.Run("记录成功请求日志", func(t *testing.T) {
        // 创建 Mock 日志器
        mockLogger := &MockLogger{}
        var capturedEntry LogEntry
        mockLogger.On("LogRequest", mock.Anything).Run(func(args mock.Arguments) {
            capturedEntry = args.Get(0).(LogEntry)
        }).Return()

        // 创建测试路由
        router := testutils.NewTestGinEngine()
        router.Use(LoggerMiddleware(mockLogger))
        router.GET("/test", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"message": "test"})
        })

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/test").Build()
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusOK)

        // 断言日志记录
        mockLogger.AssertCalled(t, "LogRequest", mock.Anything)
        assert.Equal(t, "/test", capturedEntry.Path)
        assert.Equal(t, "GET", capturedEntry.Method)
        assert.Equal(t, http.StatusOK, capturedEntry.Status)
        assert.True(t, capturedEntry.Latency > 0)
    })

    t.Run("记录错误请求日志", func(t *testing.T) {
        // 创建 Mock 日志器
        mockLogger := &MockLogger{}
        var capturedEntry LogEntry
        mockLogger.On("LogRequest", mock.Anything).Run(func(args mock.Arguments) {
            capturedEntry = args.Get(0).(LogEntry)
        }).Return()

        // 创建测试路由
        router := testutils.NewTestGinEngine()
        router.Use(LoggerMiddleware(mockLogger))
        router.GET("/error", func(c *gin.Context) {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "test error"})
        })

        // 创建测试请求
        req := testutils.NewTestRequestBuilder("GET", "/error").Build()
        recorder := testutils.ExecuteTestRequest(router, req)

        // 断言响应
        testutils.NewTestResponseAsserter(t, recorder).
            Status(http.StatusInternalServerError)

        // 断言日志记录
        mockLogger.AssertCalled(t, "LogRequest", mock.Anything)
        assert.Equal(t, "/error", capturedEntry.Path)
        assert.Equal(t, http.StatusInternalServerError, capturedEntry.Status)
    })
}
```

## 4. 性能测试

### 4.1 基准测试

#### 4.1.1 路由性能测试
```go
package benchmarks

import (
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/your-project/handlers"
)

// BenchmarkSimpleRoute 测试简单路由性能
func BenchmarkSimpleRoute(b *testing.B) {
    // 设置测试模式
    gin.SetMode(gin.ReleaseMode)

    // 创建路由
    router := gin.New()
    router.GET("/simple", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "simple response"})
    })

    // 创建测试请求
    req, _ := http.NewRequest("GET", "/simple", nil)

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            recorder := httptest.NewRecorder()
            router.ServeHTTP(recorder, req)
        }
    })
}

// BenchmarkParameterizedRoute 测试参数化路由性能
func BenchmarkParameterizedRoute(b *testing.B) {
    // 设置测试模式
    gin.SetMode(gin.ReleaseMode)

    // 创建路由
    router := gin.New()
    router.GET("/users/:id", func(c *gin.Context) {
        userID := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"user_id": userID})
    })

    // 创建测试请求
    req, _ := http.NewRequest("GET", "/users/12345", nil)

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            recorder := httptest.NewRecorder()
            router.ServeHTTP(recorder, req)
        }
    })
}

// BenchmarkMiddlewareRoute 测试带中间件的路由性能
func BenchmarkMiddlewareRoute(b *testing.B) {
    // 设置测试模式
    gin.SetMode(gin.ReleaseMode)

    // 创建 Mock 认证服务
    mockAuthService := &MockAuthService{}

    // 创建路由
    router := gin.New()
    router.Use(middleware.LoggerMiddleware(mockAuthService))
    router.Use(middleware.JWTAuthMiddleware(mockAuthService))
    router.GET("/protected", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "protected response"})
    })

    // 创建测试请求
    req, _ := http.NewRequest("GET", "/protected", nil)
    req.Header.Set("Authorization", "Bearer valid_token")

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            recorder := httptest.NewRecorder()
            router.ServeHTTP(recorder, req)
        }
    })
}

// BenchmarkDatabaseRoute 测试数据库查询路由性能
func BenchmarkDatabaseRoute(b *testing.B) {
    // 设置测试模式
    gin.SetMode(gin.ReleaseMode)

    // 设置测试数据库
    db, err := testutils.SetupTestDatabase()
    if err != nil {
        b.Fatalf("Failed to setup test database: %v", err)
    }
    defer testutils.CloseTestDatabase()

    // 创建处理器
    userHandler := handlers.NewUserHandler(services.NewUserService(db))

    // 创建路由
    router := gin.New()
    router.GET("/users/:id", userHandler.GetUser)

    // 创建测试请求
    req, _ := http.NewRequest("GET", "/users/1", nil)

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            recorder := httptest.NewRecorder()
            router.ServeHTTP(recorder, req)
        }
    })
}
```

#### 4.1.2 内存使用测试
```go
package benchmarks

import (
    "net/http"
    "net/http/httptest"
    "runtime"
    "testing"

    "github.com/gin-gonic/gin"
)

// BenchmarkMemoryUsage 测试内存使用情况
func BenchmarkMemoryUsage(b *testing.B) {
    // 设置测试模式
    gin.SetMode(gin.ReleaseMode)

    // 创建路由
    router := gin.New()
    router.GET("/memory", func(c *gin.Context) {
        // 分配一些内存
        data := make([]byte, 1024) // 1KB
        for i := range data {
            data[i] = byte(i % 256)
        }
        c.JSON(http.StatusOK, gin.H{"size": len(data)})
    })

    // 创建测试请求
    req, _ := http.NewRequest("GET", "/memory", nil)

    // 运行基准测试
    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            recorder := httptest.NewRecorder()
            router.ServeHTTP(recorder, req)
        }
    })

    // 打印内存统计信息
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    b.Logf("Memory Stats:")
    b.Logf("  Alloc: %v bytes", m.Alloc)
    b.Logf("  TotalAlloc: %v bytes", m.TotalAlloc)
    b.Logf("  Sys: %v bytes", m.Sys)
    b.Logf("  NumGC: %d", m.NumGC)
}

// BenchmarkGoroutineLeaks 测试Goroutine泄漏
func BenchmarkGoroutineLeaks(b *testing.B) {
    // 设置测试模式
    gin.SetMode(gin.ReleaseMode)

    // 创建路由
    router := gin.New()
    router.GET("/goroutine", func(c *gin.Context) {
        // 创建Goroutine但不泄漏
        done := make(chan bool)
        go func() {
            // 模拟一些工作
            time.Sleep(10 * time.Millisecond)
            done <- true
        }()
        <-done // 等待Goroutine完成
        c.JSON(http.StatusOK, gin.H{"message": "goroutine test"})
    })

    // 创建测试请求
    req, _ := http.NewRequest("GET", "/goroutine", nil)

    // 记录初始Goroutine数量
    initialGoroutines := runtime.NumGoroutine()

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            recorder := httptest.NewRecorder()
            router.ServeHTTP(recorder, req)
        }
    })

    // 检查Goroutine数量
    finalGoroutines := runtime.NumGoroutine()
    b.Logf("Goroutine count - Initial: %d, Final: %d", initialGoroutines, finalGoroutines)

    // 允许少量的Goroutine增长（由于测试框架）
    if finalGoroutines-initialGoroutines > 10 {
        b.Errorf("Potential goroutine leak: %d goroutines created", finalGoroutines-initialGoroutines)
    }
}
```

## 5. 测试套件和集成测试

### 5.1 测试套件

#### 5.1.1 API 测试套件
```go
package integration

import (
    "net/http"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
    "github.com/your-project/config"
    "github.com/your-project/handlers"
    "github.com/your-project/middleware"
    "github.com/your-project/services"
)

// APITestSuite API测试套件
type APITestSuite struct {
    suite.Suite
    router      *gin.Engine
    db          *gorm.DB
    userService services.UserService
    authService services.AuthService
}

// SetupSuite 设置测试套件
func (suite *APITestSuite) SetupSuite() {
    // 设置测试模式
    gin.SetMode(gin.TestMode)

    // 设置测试数据库
    var err error
    suite.db, err = testutils.SetupTestDatabase()
    suite.Require().NoError(err)

    // 创建服务
    suite.userService = services.NewUserService(suite.db)
    suite.authService = services.NewAuthService(suite.db)

    // 创建处理器
    userHandler := handlers.NewUserHandler(suite.userService)

    // 创建路由
    suite.router = gin.New()

    // 应用中间件
    suite.router.Use(middleware.LoggerMiddleware(suite.authService))
    suite.router.Use(middleware.ErrorHandlerMiddleware())

    // 注册路由
    api := suite.router.Group("/api/v1")
    {
        users := api.Group("/users")
        {
            users.POST("", userHandler.CreateUser)
            users.GET("/:id", userHandler.GetUser)
            users.PUT("/:id", userHandler.UpdateUser)
            users.DELETE("/:id", userHandler.DeleteUser)
        }
    }
}

// TearDownSuite 清理测试套件
func (suite *APITestSuite) TearDownSuite() {
    if suite.db != nil {
        testutils.CloseTestDatabase()
    }
}

// SetupTest 每个测试前的设置
func (suite *APITestSuite) SetupTest() {
    // 清理测试数据
    testutils.CleanupTestDatabase()
}

// TearDownTest 每个测试后的清理
func (suite *APITestSuite) TearDownTest() {
    // 清理测试数据
    testutils.CleanupTestDatabase()
}

// TestUserCreation 测试用户创建
func (suite *APITestSuite) TestUserCreation() {
    // 准备测试数据
    userReq := map[string]interface{}{
        "username": "testuser",
        "email":    "test@example.com",
        "password": "password123",
    }

    // 发送请求
    req := testutils.BuildTestRequest("POST", "/api/v1/users", userReq)
    recorder := testutils.ExecuteTestRequest(suite.router, req)

    // 断言响应
    testutils.NewTestResponseAsserter(suite.T(), recorder).
        Status(http.StatusCreated).
        JSONPath("username", "testuser").
        JSONPath("email", "test@example.com")

    // 验证用户是否创建成功
    user, err := suite.userService.GetUserByEmail("test@example.com")
    suite.Require().NoError(err)
    suite.Equal("testuser", user.Username)
}

// TestGetUser 测试获取用户
func (suite *APITestSuite) TestGetUser() {
    // 创建测试用户
    user := &models.User{
        Username: "gettest",
        Email:    "gettest@example.com",
        Password: "password123",
    }
    err := suite.userService.CreateUser(user)
    suite.Require().NoError(err)

    // 发送请求
    req := testutils.BuildTestRequest("GET", "/api/v1/users/"+user.ID, nil)
    recorder := testutils.ExecuteTestRequest(suite.router, req)

    // 断言响应
    testutils.NewTestResponseAsserter(suite.T(), recorder).
        Status(http.StatusOK).
        JSONPath("username", "gettest").
        JSONPath("email", "gettest@example.com")
}

// TestUserNotFound 测试用户不存在的情况
func (suite *APITestSuite) TestUserNotFound() {
    // 发送请求
    req := testutils.BuildTestRequest("GET", "/api/v1/users/999999", nil)
    recorder := testutils.ExecuteTestRequest(suite.router, req)

    // 断言响应
    testutils.NewTestResponseAsserter(suite.T(), recorder).
        Status(http.StatusNotFound).
        Contains("User not found")
}

// TestInvalidUserData 测试无效的用户数据
func (suite *APITestSuite) TestInvalidUserData() {
    // 准备无效数据
    userReq := map[string]interface{}{
        "username": "", // 必填字段为空
        "email":    "invalid-email",
        "password": "123", // 密码太短
    }

    // 发送请求
    req := testutils.BuildTestRequest("POST", "/api/v1/users", userReq)
    recorder := testutils.ExecuteTestRequest(suite.router, req)

    // 断言响应
    testutils.NewTestResponseAsserter(suite.T(), recorder).
        Status(http.StatusBadRequest).
        Contains("validation failed")
}

// TestDuplicateUser 测试重复用户
func (suite *APITestSuite) TestDuplicateUser() {
    // 创建第一个用户
    userReq := map[string]interface{}{
        "username": "duplicate",
        "email":    "duplicate@example.com",
        "password": "password123",
    }

    req := testutils.BuildTestRequest("POST", "/api/v1/users", userReq)
    recorder := testutils.ExecuteTestRequest(suite.router, req)

    // 第一个用户应该创建成功
    testutils.NewTestResponseAsserter(suite.T(), recorder).
        Status(http.StatusCreated)

    // 尝试创建重复用户
    req = testutils.BuildTestRequest("POST", "/api/v1/users", userReq)
    recorder = testutils.ExecuteTestRequest(suite.router, req)

    // 应该返回冲突错误
    testutils.NewTestResponseAsserter(suite.T(), recorder).
        Status(http.StatusConflict).
        Contains("already exists")
}

// 运行测试套件
func TestAPITestSuite(t *testing.T) {
    suite.Run(t, new(APITestSuite))
}
```

#### 5.1.2 性能测试套件
```go
package integration

import (
    "fmt"
    "net/http"
    "runtime"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
)

// PerformanceTestSuite 性能测试套件
type PerformanceTestSuite struct {
    suite.Suite
    router *gin.Engine
    baseURL string
}

// SetupSuite 设置性能测试套件
func (suite *PerformanceTestSuite) SetupSuite() {
    // 设置测试模式
    gin.SetMode(gin.ReleaseMode)

    // 创建测试服务器
    suite.router = gin.New()

    // 配置路由
    suite.setupRoutes()

    // 启动测试服务器
    server := &http.Server{
        Addr:    ":8080",
        Handler: suite.router,
    }

    go server.ListenAndServe()

    // 等待服务器启动
    time.Sleep(100 * time.Millisecond)

    suite.baseURL = "http://localhost:8080"
}

// TearDownSuite 清理性能测试套件
func (suite *PerformanceTestSuite) TearDownSuite() {
    // 停止测试服务器
    // 注意：这里简化处理，实际应该优雅关闭服务器
}

// setupRoutes 设置测试路由
func (suite *PerformanceTestSuite) setupRoutes() {
    // 简单路由
    suite.router.GET("/simple", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "simple response"})
    })

    // 数据库查询路由
    suite.router.GET("/db", func(c *gin.Context) {
        // 模拟数据库查询
        time.Sleep(10 * time.Millisecond)
        c.JSON(http.StatusOK, gin.H{"message": "database response"})
    })

    // CPU密集型路由
    suite.router.GET("/cpu", func(c *gin.Context) {
        // 模拟CPU密集型操作
        result := 0
        for i := 0; i < 1000000; i++ {
            result += i
        }
        c.JSON(http.StatusOK, gin.H{"result": result})
    })

    // 内存密集型路由
    suite.router.GET("/memory", func(c *gin.Context) {
        // 分配内存
        data := make([]byte, 1024*1024) // 1MB
        for i := range data {
            data[i] = byte(i % 256)
        }
        c.JSON(http.StatusOK, gin.H{"size": len(data)})
    })
}

// TestConcurrentRequests 测试并发请求处理
func (suite *PerformanceTestSuite) TestConcurrentRequests() {
    concurrency := 100
    requestsPerClient := 50

    var wg sync.WaitGroup
    results := make(chan time.Duration, concurrency*requestsPerClient)
    errors := make(chan error, concurrency*requestsPerClient)

    start := time.Now()

    for i := 0; i < concurrency; i++ {
        wg.Add(1)
        go func(clientID int) {
            defer wg.Done()

            for j := 0; j < requestsPerClient; j++ {
                reqStart := time.Now()

                resp, err := http.Get(suite.baseURL + "/simple")
                if err != nil {
                    errors <- err
                    continue
                }
                defer resp.Body.Close()

                if resp.StatusCode != http.StatusOK {
                    errors <- fmt.Errorf("unexpected status code: %d", resp.StatusCode)
                    continue
                }

                results <- time.Since(reqStart)
            }
        }(i)
    }

    wg.Wait()
    close(results)
    close(errors)

    totalDuration := time.Since(start)
    totalRequests := concurrency * requestsPerClient

    // 统计结果
    var totalLatency time.Duration
    requestCount := 0
    for latency := range results {
        totalLatency += latency
        requestCount++
    }

    // 统计错误
    errorCount := 0
    for err := range errors {
        suite.T().Logf("Request error: %v", err)
        errorCount++
    }

    // 计算性能指标
    avgLatency := totalLatency / time.Duration(requestCount)
    rps := float64(requestCount) / totalDuration.Seconds()

    suite.T().Logf("Performance Results:")
    suite.T().Logf("  Total Requests: %d", totalRequests)
    suite.T().Logf("  Successful Requests: %d", requestCount)
    suite.T().Logf("  Failed Requests: %d", errorCount)
    suite.T().Logf("  Total Duration: %v", totalDuration)
    suite.T().Logf("  Average Latency: %v", avgLatency)
    suite.T().Logf("  Requests Per Second: %.2f", rps)

    // 断言性能指标
    suite.Greater(rps, 1000.0, "RPS should be greater than 1000")
    suite.Less(avgLatency, 100*time.Millisecond, "Average latency should be less than 100ms")
    suite.Equal(0, errorCount, "There should be no errors")
}

// TestMemoryUsage 测试内存使用情况
func (suite *PerformanceTestSuite) TestMemoryUsage() {
    // 记录初始内存
    var initialMem runtime.MemStats
    runtime.ReadMemStats(&initialMem)

    // 发送大量请求
    for i := 0; i < 1000; i++ {
        resp, err := http.Get(suite.baseURL + "/memory")
        if err != nil {
            suite.T().Fatalf("Request failed: %v", err)
        }
        resp.Body.Close()
    }

    // 强制垃圾回收
    runtime.GC()

    // 记录最终内存
    var finalMem runtime.MemStats
    runtime.ReadMemStats(&finalMem)

    // 计算内存增长
    memGrowth := finalMem.Alloc - initialMem.Alloc

    suite.T().Logf("Memory Usage:")
    suite.T().Logf("  Initial Memory: %v bytes", initialMem.Alloc)
    suite.T().Logf("  Final Memory: %v bytes", finalMem.Alloc)
    suite.T().Logf("  Memory Growth: %v bytes", memGrowth)
    suite.T().Logf("  GC Cycles: %d", finalMem.NumGC-initialMem.NumGC)

    // 断言内存增长在合理范围内
    suite.Less(memGrowth, int64(10*1024*1024), "Memory growth should be less than 10MB")
}

// TestDatabasePerformance 测试数据库性能
func (suite *PerformanceTestSuite) TestDatabasePerformance() {
    iterations := 100
    var totalTime time.Duration

    for i := 0; i < iterations; i++ {
        start := time.Now()

        resp, err := http.Get(suite.baseURL + "/db")
        if err != nil {
            suite.T().Fatalf("Request failed: %v", err)
        }
        resp.Body.Close()

        totalTime += time.Since(start)
    }

    avgTime := totalTime / time.Duration(iterations)

    suite.T().Logf("Database Performance:")
    suite.T().Logf("  Total Requests: %d", iterations)
    suite.T().Logf("  Total Time: %v", totalTime)
    suite.T().Logf("  Average Time: %v", avgTime)

    // 断言数据库查询时间在合理范围内
    suite.Less(avgTime, 50*time.Millisecond, "Average database query time should be less than 50ms")
}

// 运行性能测试套件
func TestPerformanceTestSuite(t *testing.T) {
    suite.Run(t, new(PerformanceTestSuite))
}
```

## 6. 测试覆盖率

### 6.1 测试覆盖率配置

#### 6.1.1 覆盖率配置文件
```yaml
# .cover.yml
service: coveralls
repo_token: YOUR_COVERALLS_TOKEN

coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 1%
    patch:
      default:
        target: 80%
        threshold: 1%

comment:
  layout: "reach,diff,flags,tree"
  behavior: default
  require_changes: false
```

#### 6.1.2 Makefile 配置
```makefile
# Makefile
.PHONY: test test-unit test-integration test-bench coverage coverage-html coverage-upload clean

# 运行所有测试
test: test-unit test-integration

# 运行单元测试
test-unit:
	@echo "Running unit tests..."
	go test -v -short ./...

# 运行集成测试
test-integration:
	@echo "Running integration tests..."
	go test -v -tags=integration ./...

# 运行基准测试
test-bench:
	@echo "Running benchmark tests..."
	go test -bench=. -benchmem ./...

# 生成覆盖率报告
coverage:
	@echo "Generating coverage report..."
	go test -v -coverprofile=coverage.out ./...

# 生成HTML覆盖率报告
coverage-html:
	@echo "Generating HTML coverage report..."
	go test -v -coverprofile=coverage.out -covermode=count ./...
	go tool cover -html=coverage.out -o coverage.html

# 上传覆盖率到Coveralls
coverage-upload:
	@echo "Uploading coverage to Coveralls..."
	goveralls -coverprofile=coverage.out -service=github

# 运行测试并生成覆盖率
test-with-coverage:
	@echo "Running tests with coverage..."
	go test -v -coverprofile=coverage.out -covermode=count ./...

# 清理测试文件
clean:
	@echo "Cleaning up..."
	rm -f coverage.out coverage.html
```

#### 6.1.3 GitHub Actions 配置
```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_USER: testuser
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: 1.21

    - name: Download dependencies
      run: go mod download

    - name: Run unit tests
      run: make test-unit

    - name: Run integration tests
      run: make test-integration
      env:
        DB_HOST: localhost
        DB_PORT: 5432
        DB_USER: testuser
        DB_PASSWORD: testpass
        DB_NAME: testdb

    - name: Run benchmark tests
      run: make test-bench

    - name: Generate coverage report
      run: make coverage

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.out
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
```

## 7. Mock 和 Stub

### 7.1 高级 Mock 模式

#### 7.1.1 Mock 链式调用
```go
package mocks

import (
    "github.com/stretchr/testify/mock"
)

// MockUserService 链式调用Mock
type MockUserService struct {
    mock.Mock
}

func (m *MockUserService) GetUserByID(id string) (*User, error) {
    args := m.Called(id)
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserService) GetUserByEmail(email string) (*User, error) {
    args := m.Called(email)
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserService) CreateUser(user *CreateUserRequest) (*User, error) {
    args := m.Called(user)
    return args.Get(0).(*User), args.Error(1)
}

// 链式调用设置
func TestChainedMockCalls(t *testing.T) {
    mockUserService := &MockUserService{}

    // 设置链式调用期望
    mockUserService.On("GetUserByEmail", "test@example.com").
        Return(&User{ID: 1, Username: "test", Email: "test@example.com"}, nil)

    mockUserService.On("CreateUser", &CreateUserRequest{
        Username: "newuser",
        Email:    "newuser@example.com",
        Password: "password123",
    }).Return(&User{ID: 2, Username: "newuser", Email: "newuser@example.com"}, nil)

    // 测试链式调用
    user, err := mockUserService.GetUserByEmail("test@example.com")
    assert.NoError(t, err)
    assert.NotNil(t, user)

    newUser, err := mockUserService.CreateUser(&CreateUserRequest{
        Username: "newuser",
        Email:    "newuser@example.com",
        Password: "password123",
    })
    assert.NoError(t, err)
    assert.NotNil(t, newUser)

    // 验证所有期望都被调用
    mockUserService.AssertExpectations(t)
}
```

#### 7.1.2 条件 Mock
```go
package mocks

import (
    "github.com/stretchr/testify/mock"
)

// 条件Mock匹配器
type ConditionMock struct {
    mock.Mock
}

// 匹配特定条件的参数
func TestConditionalMock(t *testing.T) {
    mockService := &ConditionMock{}

    // 使用MatchedBy匹配满足条件的参数
    mockService.On("ProcessUser", mock.MatchedBy(func(user *User) bool {
        return user.Username == "admin" && len(user.Roles) > 0
    })).Return(nil)

    // 测试不同条件
    adminUser := &User{Username: "admin", Roles: []string{"admin"}}
    regularUser := &User{Username: "user", Roles: []string{}}

    // 应该匹配
    err := mockService.ProcessUser(adminUser)
    assert.NoError(t, err)

    // 不应该匹配（不会调用Mock）
    err = mockService.ProcessUser(regularUser)
    assert.Error(t, err)
}
```

---

这个Gin测试策略文档提供了完整的测试体系，包括：

1. **测试环境搭建**：测试框架配置、数据库管理、Mock服务
2. **Handler测试**：基本测试、复杂测试、表单处理、文件上传
3. **中间件测试**：认证中间件、权限中间件、日志中间件
4. **性能测试**：基准测试、内存测试、并发测试
5. **测试套件**：API测试套件、性能测试套件
6. **测试覆盖率**：覆盖率配置、CI/CD集成
7. **Mock和Stub**：高级Mock模式、条件Mock

每个部分都提供了完整的代码示例和最佳实践，帮助开发者构建高质量的Gin应用测试体系。