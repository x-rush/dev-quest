# Gin集成测试

## 目录
- [集成测试概述](#集成测试概述)
- [测试环境搭建](#测试环境搭建)
- [数据库集成测试](#数据库集成测试)
- [API集成测试](#api集成测试)
- [外部服务集成测试](#外部服务集成测试)
- [端到端测试](#端到端测试)
- [测试策略和最佳实践](#测试策略和最佳实践)
- [持续集成](#持续集成)

## 集成测试概述

### 什么是集成测试
集成测试是测试多个组件或模块之间的交互，确保它们能够正确地协同工作。对于Gin应用来说，集成测试通常包括：

- 数据库交互测试
- API端点测试
- 外部服务集成测试
- 中间件测试
- 完整业务流程测试

### 集成测试的重要性
- **验证组件协作**：确保不同组件能够正确协作
- **发现集成问题**：提前发现模块间的集成问题
- **提高代码质量**：通过测试驱动开发提高代码质量
- **增强信心**：为部署到生产环境提供信心

### 测试金字塔
```
                 ^                    |
                 | 单元测试 (70%)      | 快速
                 | 集成测试 (20%)      | 中等
                 | 端到端测试 (10%)   | 慢
                 +--------------------+
```

## 测试环境搭建

### 测试环境配置
```go
package testenv

import (
    "database/sql"
    "fmt"
    "os"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/ory/dockertest/v3"
    "github.com/ory/dockertest/v3/docker"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

// 测试环境配置
type TestEnvironment struct {
    DB        *gorm.DB
    Redis     *redis.Client
    Router    *gin.Engine
    Container *dockertest.Pool
}

// 创建测试环境
func CreateTestEnvironment(t *testing.T) *TestEnvironment {
    // 设置Gin为测试模式
    gin.SetMode(gin.TestMode)

    // 创建Docker资源池
    pool, err := dockertest.NewPool("")
    if err != nil {
        t.Fatalf("Could not connect to Docker: %s", err)
    }

    // 启动PostgreSQL容器
    postgresResource, err := pool.RunWithOptions(&dockertest.RunOptions{
        Repository: "postgres",
        Tag:        "13",
        Env: []string{
            "POSTGRES_PASSWORD=test",
            "POSTGRES_USER=test",
            "POSTGRES_DB=testdb",
        },
    })
    if err != nil {
        t.Fatalf("Could not start PostgreSQL: %s", err)
    }

    // 启动Redis容器
    redisResource, err := pool.RunWithOptions(&dockertest.RunOptions{
        Repository: "redis",
        Tag:        "6-alpine",
    })
    if err != nil {
        t.Fatalf("Could not start Redis: %s", err)
    }

    // 等待数据库就绪
    var db *gorm.DB
    pool.Retry(func() error {
        var err error
        dsn := fmt.Sprintf("host=localhost port=%s user=test password=test dbname=testdb sslmode=disable",
            postgresResource.GetPort("5432/tcp"))
        db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
        if err != nil {
            return err
        }
        return db.Exec("SELECT 1").Error
    })

    // 连接Redis
    redisClient := redis.NewClient(&redis.Options{
        Addr: fmt.Sprintf("localhost:%s", redisResource.GetPort("6379/tcp")),
    })

    // 等待Redis就绪
    pool.Retry(func() error {
        return redisClient.Ping(context.Background()).Err()
    })

    // 运行数据库迁移
    if err := runMigrations(db); err != nil {
        t.Fatalf("Failed to run migrations: %s", err)
    }

    // 创建测试路由
    router := setupTestRouter(db, redisClient)

    return &TestEnvironment{
        DB:        db,
        Redis:     redisClient,
        Router:    router,
        Container: pool,
    }
}

// 清理测试环境
func (env *TestEnvironment) Cleanup() {
    if env.DB != nil {
        sqlDB, _ := env.DB.DB()
        sqlDB.Close()
    }
    if env.Redis != nil {
        env.Redis.Close()
    }
    if env.Container != nil {
        env.Container.Purge(context.Background())
    }
}

// 运行数据库迁移
func runMigrations(db *gorm.DB) error {
    // 运行数据库迁移
    return db.AutoMigrate(
        &models.User{},
        &models.Product{},
        &models.Order{},
    )
}

// 设置测试路由
func setupTestRouter(db *gorm.DB, redisClient *redis.Client) *gin.Engine {
    r := gin.New()

    // 创建服务
    userService := services.NewUserService(db)
    productService := services.NewProductService(db, redisClient)
    orderService := services.NewOrderService(db, redisClient)

    // 创建控制器
    userController := controllers.NewUserController(userService)
    productController := controllers.NewProductController(productService)
    orderController := controllers.NewOrderController(orderService)

    // 设置路由
    api := r.Group("/api")
    {
        // 用户路由
        users := api.Group("/users")
        {
            users.GET("", userController.ListUsers)
            users.POST("", userController.CreateUser)
            users.GET("/:id", userController.GetUser)
            users.PUT("/:id", userController.UpdateUser)
            users.DELETE("/:id", userController.DeleteUser)
        }

        // 商品路由
        products := api.Group("/products")
        {
            products.GET("", productController.ListProducts)
            products.POST("", productController.CreateProduct)
            products.GET("/:id", productController.GetProduct)
            products.PUT("/:id", productController.UpdateProduct)
        }

        // 订单路由
        orders := api.Group("/orders")
        {
            orders.GET("", orderController.ListOrders)
            orders.POST("", orderController.CreateOrder)
            orders.GET("/:id", orderController.GetOrder)
        }
    }

    return r
}
```

### 测试工具函数
```go
package testutils

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

// 测试请求构建器
type TestRequestBuilder struct {
    method  string
    path    string
    headers map[string]string
    body    interface{}
    query   map[string]string
}

func NewTestRequestBuilder() *TestRequestBuilder {
    return &TestRequestBuilder{
        headers: make(map[string]string),
        query:   make(map[string]string),
    }
}

func (b *TestRequestBuilder) Method(method string) *TestRequestBuilder {
    b.method = method
    return b
}

func (b *TestRequestBuilder) Path(path string) *TestRequestBuilder {
    b.path = path
    return b
}

func (b *TestRequestBuilder) Header(key, value string) *TestRequestBuilder {
    b.headers[key] = value
    return b
}

func (b *TestRequestBuilder) Body(body interface{}) *TestRequestBuilder {
    b.body = body
    return b
}

func (b *TestRequestBuilder) Query(key, value string) *TestRequestBuilder {
    b.query[key] = value
    return b
}

func (b *TestRequestBuilder) Build() (*http.Request, error) {
    // 构建查询字符串
    queryString := ""
    for key, value := range b.query {
        if queryString == "" {
            queryString = "?"
        } else {
            queryString += "&"
        }
        queryString += key + "=" + value
    }

    // 创建请求
    var body *bytes.Buffer
    if b.body != nil {
        jsonData, err := json.Marshal(b.body)
        if err != nil {
            return nil, err
        }
        body = bytes.NewBuffer(jsonData)
    } else {
        body = bytes.NewBuffer(nil)
    }

    req, err := http.NewRequest(b.method, b.path+queryString, body)
    if err != nil {
        return nil, err
    }

    // 设置请求头
    for key, value := range b.headers {
        req.Header.Set(key, value)
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

func (a *TestResponseAsserter) Header(key, expected string) *TestResponseAsserter {
    assert.Equal(a.t, expected, a.recorder.Header().Get(key))
    return a
}

func (a *TestResponseAsserter) ContainsJSON(key string, expected interface{}) *TestResponseAsserter {
    var response map[string]interface{}
    err := json.Unmarshal(a.recorder.Body.Bytes(), &response)
    assert.NoError(a.t, err)
    assert.Contains(a.t, response, key)
    assert.Equal(a.t, expected, response[key])
    return a
}

func (a *TestResponseAsserter) JSONBody(expected interface{}) *TestResponseAsserter {
    var actual interface{}
    err := json.Unmarshal(a.recorder.Body.Bytes(), &actual)
    assert.NoError(a.t, err)
    assert.Equal(a.t, expected, actual)
    return a
}

// 执行测试请求
func ExecuteTestRequest(router *gin.Engine, req *http.Request) *httptest.ResponseRecorder {
    recorder := httptest.NewRecorder()
    router.ServeHTTP(recorder, req)
    return recorder
}

// 创建测试用户
func CreateTestUser(t *testing.T, db *gorm.DB) *models.User {
    user := &models.User{
        Username: "testuser",
        Email:    "test@example.com",
        Password: "password123",
    }

    if err := db.Create(user).Error; err != nil {
        t.Fatalf("Failed to create test user: %s", err)
    }

    return user
}

// 创建测试商品
func CreateTestProduct(t *testing.T, db *gorm.DB) *models.Product {
    product := &models.Product{
        Name:  "Test Product",
        Price: 99.99,
        Stock: 100,
    }

    if err := db.Create(product).Error; err != nil {
        t.Fatalf("Failed to create test product: %s", err)
    }

    return product
}
```

## 数据库集成测试

### 数据库测试基础
```go
package database

import (
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
    "gorm.io/gorm"
)

// 数据库测试套件
type DatabaseTestSuite struct {
    suite.Suite
    DB     *gorm.DB
    Env    *TestEnvironment
}

func (s *DatabaseTestSuite) SetupSuite() {
    s.Env = CreateTestEnvironment(s.T())
    s.DB = s.Env.DB
}

func (s *DatabaseTestSuite) TearDownSuite() {
    s.Env.Cleanup()
}

func (s *DatabaseTestSuite) SetupTest() {
    // 每个测试前清理数据
    s.DB.Exec("DELETE FROM users")
    s.DB.Exec("DELETE FROM products")
    s.DB.Exec("DELETE FROM orders")
}

func (s *DatabaseTestSuite) TearDownTest() {
    // 每个测试后清理数据
    s.DB.Exec("DELETE FROM users")
    s.DB.Exec("DELETE FROM products")
    s.DB.Exec("DELETE FROM orders")
}

func TestDatabaseTestSuite(t *testing.T) {
    suite.Run(t, new(DatabaseTestSuite))
}

// 用户模型测试
func (s *DatabaseTestSuite) TestCreateUser() {
    user := &models.User{
        Username: "testuser",
        Email:    "test@example.com",
        Password: "password123",
    }

    err := s.DB.Create(user).Error
    s.NoError(err)
    s.NotZero(user.ID)
    s.Equal("testuser", user.Username)
    s.Equal("test@example.com", user.Email)
}

func (s *DatabaseTestSuite) TestGetUser() {
    // 创建测试用户
    user := CreateTestUser(s.T(), s.DB)

    // 获取用户
    var foundUser models.User
    err := s.DB.First(&foundUser, user.ID).Error
    s.NoError(err)
    s.Equal(user.ID, foundUser.ID)
    s.Equal(user.Username, foundUser.Username)
}

func (s *DatabaseTestSuite) TestUpdateUser() {
    user := CreateTestUser(s.T(), s.DB)

    // 更新用户
    updatedUser := map[string]interface{}{
        "username": "updateduser",
        "email":    "updated@example.com",
    }

    err := s.DB.Model(&user).Updates(updatedUser).Error
    s.NoError(err)

    // 验证更新
    var foundUser models.User
    err = s.DB.First(&foundUser, user.ID).Error
    s.NoError(err)
    s.Equal("updateduser", foundUser.Username)
    s.Equal("updated@example.com", foundUser.Email)
}

func (s *DatabaseTestSuite) TestDeleteUser() {
    user := CreateTestUser(s.T(), s.DB)

    // 删除用户
    err := s.DB.Delete(&user).Error
    s.NoError(err)

    // 验证删除
    var foundUser models.User
    err = s.DB.First(&foundUser, user.ID).Error
    s.Error(err)
    s.Equal(gorm.ErrRecordNotFound, err)
}

// 商品模型测试
func (s *DatabaseTestSuite) TestCreateProduct() {
    product := &models.Product{
        Name:  "Test Product",
        Price: 99.99,
        Stock: 100,
    }

    err := s.DB.Create(product).Error
    s.NoError(err)
    s.NotZero(product.ID)
    s.Equal("Test Product", product.Name)
    s.Equal(99.99, product.Price)
    s.Equal(100, product.Stock)
}

// 订单模型测试
func (s *DatabaseTestSuite) TestCreateOrder() {
    user := CreateTestUser(s.T(), s.DB)
    product := CreateTestProduct(s.T(), s.DB)

    order := &models.Order{
        UserID:  user.ID,
        ProductID: product.ID,
        Quantity: 2,
        Total:   199.98,
        Status:  "pending",
    }

    err := s.DB.Create(order).Error
    s.NoError(err)
    s.NotZero(order.ID)
    s.Equal(user.ID, order.UserID)
    s.Equal(product.ID, order.ProductID)
    s.Equal(2, order.Quantity)
    s.Equal(199.98, order.Total)
    s.Equal("pending", order.Status)
}

// 关联查询测试
func (s *DatabaseTestSuite) TestUserOrdersAssociation() {
    user := CreateTestUser(s.T(), s.DB)
    product := CreateTestProduct(s.T(), s.DB)

    // 创建多个订单
    orders := []*models.Order{
        {
            UserID:    user.ID,
            ProductID: product.ID,
            Quantity:  1,
            Total:     99.99,
            Status:    "pending",
        },
        {
            UserID:    user.ID,
            ProductID: product.ID,
            Quantity:  3,
            Total:     299.97,
            Status:    "completed",
        },
    }

    for _, order := range orders {
        err := s.DB.Create(order).Error
        s.NoError(err)
    }

    // 预加载用户订单
    var foundUser models.User
    err := s.DB.Preload("Orders").First(&foundUser, user.ID).Error
    s.NoError(err)
    s.Len(foundUser.Orders, 2)
}

// 事务测试
func (s *DatabaseTestSuite) TestTransaction() {
    user := CreateTestUser(s.T(), s.DB)
    product := CreateTestProduct(s.T(), s.DB)

    // 开始事务
    tx := s.DB.Begin()
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
        }
    }()

    // 创建订单
    order := &models.Order{
        UserID:    user.ID,
        ProductID: product.ID,
        Quantity:  2,
        Total:     199.98,
        Status:    "pending",
    }

    err := tx.Create(order).Error
    s.NoError(err)

    // 更新库存
    err = tx.Model(&product).Update("stock", product.Stock-2).Error
    s.NoError(err)

    // 提交事务
    err = tx.Commit().Error
    s.NoError(err)

    // 验证结果
    var foundOrder models.Order
    err = s.DB.First(&foundOrder, order.ID).Error
    s.NoError(err)

    var foundProduct models.Product
    err = s.DB.First(&foundProduct, product.ID).Error
    s.NoError(err)
    s.Equal(product.Stock-2, foundProduct.Stock)
}
```

### 复杂查询测试
```go
package database

import (
    "testing"

    "github.com/stretchr/testify/assert"
)

// 复杂查询测试
func (s *DatabaseTestSuite) TestComplexQueries() {
    // 创建测试数据
    user := CreateTestUser(s.T(), s.DB)

    products := []*models.Product{
        {Name: "Product A", Price: 10.00, Stock: 100},
        {Name: "Product B", Price: 20.00, Stock: 50},
        {Name: "Product C", Price: 30.00, Stock: 200},
    }

    for _, product := range products {
        err := s.DB.Create(product).Error
        s.NoError(err)
    }

    // 创建订单
    orders := []*models.Order{
        {UserID: user.ID, ProductID: products[0].ID, Quantity: 2, Total: 20.00, Status: "completed"},
        {UserID: user.ID, ProductID: products[1].ID, Quantity: 1, Total: 20.00, Status: "pending"},
        {UserID: user.ID, ProductID: products[2].ID, Quantity: 3, Total: 90.00, Status: "completed"},
    }

    for _, order := range orders {
        err := s.DB.Create(order).Error
        s.NoError(err)
    }

    // 测试聚合查询
    var totalRevenue float64
    err := s.DB.Model(&models.Order{}).
        Where("user_id = ? AND status = ?", user.ID, "completed").
        Select("COALESCE(SUM(total), 0)").
        Scan(&totalRevenue).Error
    s.NoError(err)
    s.Equal(110.00, totalRevenue)

    // 测试分组查询
    var results []struct {
        Status  string
        Count   int
        Total   float64
    }

    err = s.DB.Model(&models.Order{}).
        Where("user_id = ?", user.ID).
        Select("status, COUNT(*) as count, COALESCE(SUM(total), 0) as total").
        Group("status").
        Scan(&results).Error
    s.NoError(err)
    s.Len(results, 2)

    // 验证分组结果
    statusCounts := make(map[string]float64)
    for _, result := range results {
        statusCounts[result.Status] = result.Total
    }
    s.Equal(110.00, statusCounts["completed"])
    s.Equal(20.00, statusCounts["pending"])

    // 测试JOIN查询
    var orderDetails []struct {
        OrderID   uint
        ProductID uint
        ProductName string
        Quantity  int
        Total     float64
    }

    err = s.DB.Table("orders").
        Select("orders.id as order_id, orders.product_id, products.name as product_name, orders.quantity, orders.total").
        Joins("LEFT JOIN products ON products.id = orders.product_id").
        Where("orders.user_id = ?", user.ID).
        Scan(&orderDetails).Error
    s.NoError(err)
    s.Len(orderDetails, 3)

    // 验证JOIN结果
    for _, detail := range orderDetails {
        s.NotZero(detail.OrderID)
        s.NotZero(detail.ProductID)
        s.NotEmpty(detail.ProductName)
        s.Greater(detail.Quantity, 0)
        s.Greater(detail.Total, 0.0)
    }
}

// 性能测试
func (s *DatabaseTestSuite) TestDatabasePerformance() {
    // 创建大量测试数据
    user := CreateTestUser(s.T(), s.DB)

    products := make([]*models.Product, 100)
    for i := 0; i < 100; i++ {
        products[i] = &models.Product{
            Name:  fmt.Sprintf("Product %d", i),
            Price: float64(i) + 1.00,
            Stock: 100,
        }
    }

    for _, product := range products {
        err := s.DB.Create(product).Error
        s.NoError(err)
    }

    orders := make([]*models.Order, 1000)
    for i := 0; i < 1000; i++ {
        orders[i] = &models.Order{
            UserID:    user.ID,
            ProductID: products[i%100].ID,
            Quantity:  i%10 + 1,
            Total:     float64(i%10+1) * float64(i%100+1),
            Status:    []string{"pending", "completed"}[i%2],
        }
    }

    for _, order := range orders {
        err := s.DB.Create(order).Error
        s.NoError(err)
    }

    // 测试批量查询性能
    s.T().Run("BatchSelect", func(t *testing.T) {
        start := time.Now()

        var selectedOrders []models.Order
        err := s.DB.Where("user_id = ?", user.ID).Limit(100).Find(&selectedOrders).Error
        assert.NoError(t, err)

        duration := time.Since(start)
        t.Logf("Batch select took: %v", duration)
        assert.Less(t, duration, 100*time.Millisecond)
    })

    // 测试复杂查询性能
    s.T().Run("ComplexQuery", func(t *testing.T) {
        start := time.Now()

        var results []struct {
            ProductID uint
            TotalQuantity int
            TotalRevenue float64
        }

        err := s.DB.Table("orders").
            Select("product_id, SUM(quantity) as total_quantity, SUM(total) as total_revenue").
            Where("user_id = ? AND status = ?", user.ID, "completed").
            Group("product_id").
            Scan(&results).Error
        assert.NoError(t, err)

        duration := time.Since(start)
        t.Logf("Complex query took: %v", duration)
        assert.Less(t, duration, 200*time.Millisecond)
    })
}
```

## API集成测试

### API测试基础
```go
package api

import (
    "bytes"
    "encoding/json"
    "net/http"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
)

// API测试套件
type APITestSuite struct {
    suite.Suite
    Env    *TestEnvironment
    Router *gin.Engine
}

func (s *APITestSuite) SetupSuite() {
    s.Env = CreateTestEnvironment(s.T())
    s.Router = s.Env.Router
}

func (s *APITestSuite) TearDownSuite() {
    s.Env.Cleanup()
}

func (s *APITestSuite) SetupTest() {
    // 每个测试前清理数据
    s.Env.DB.Exec("DELETE FROM users")
    s.Env.DB.Exec("DELETE FROM products")
    s.Env.DB.Exec("DELETE FROM orders")
}

func (s *APITestSuite) TearDownTest() {
    // 每个测试后清理数据
    s.Env.DB.Exec("DELETE FROM users")
    s.Env.DB.Exec("DELETE FROM products")
    s.Env.DB.Exec("DELETE FROM orders")
}

func TestAPITestSuite(t *testing.T) {
    suite.Run(t, new(APITestSuite))
}

// 用户API测试
func (s *APITestSuite) TestCreateUser() {
    userRequest := map[string]interface{}{
        "username": "testuser",
        "email":    "test@example.com",
        "password": "password123",
    }

    req, err := NewTestRequestBuilder().
        Method("POST").
        Path("/api/users").
        Body(userRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusCreated).
        Header("Content-Type", "application/json; charset=utf-8").
        ContainsJSON("message", "User created successfully").
        ContainsJSON("user.username", "testuser").
        ContainsJSON("user.email", "test@example.com")
}

func (s *APITestSuite) TestCreateUser_InvalidData() {
    userRequest := map[string]interface{}{
        "username": "", // 无效用户名
        "email":    "invalid-email", // 无效邮箱
        "password": "123", // 密码太短
    }

    req, err := NewTestRequestBuilder().
        Method("POST").
        Path("/api/users").
        Body(userRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusBadRequest).
        ContainsJSON("error", "Validation failed")
}

func (s *APITestSuite) TestGetUser() {
    // 创建测试用户
    user := CreateTestUser(s.T(), s.Env.DB)

    req, err := NewTestRequestBuilder().
        Method("GET").
        Path("/api/users/" + strconv.FormatUint(uint64(user.ID), 10)).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("user.id", float64(user.ID)).
        ContainsJSON("user.username", user.Username).
        ContainsJSON("user.email", user.Email)
}

func (s *APITestSuite) TestGetUser_NotFound() {
    req, err := NewTestRequestBuilder().
        Method("GET").
        Path("/api/users/99999").
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusNotFound).
        ContainsJSON("error", "User not found")
}

func (s *APITestSuite) TestUpdateUser() {
    user := CreateTestUser(s.T(), s.Env.DB)

    updateRequest := map[string]interface{}{
        "username": "updateduser",
        "email":    "updated@example.com",
    }

    req, err := NewTestRequestBuilder().
        Method("PUT").
        Path("/api/users/" + strconv.FormatUint(uint64(user.ID), 10)).
        Body(updateRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("message", "User updated successfully").
        ContainsJSON("user.username", "updateduser").
        ContainsJSON("user.email", "updated@example.com")
}

func (s *APITestSuite) TestDeleteUser() {
    user := CreateTestUser(s.T(), s.Env.DB)

    req, err := NewTestRequestBuilder().
        Method("DELETE").
        Path("/api/users/" + strconv.FormatUint(uint64(user.ID), 10)).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("message", "User deleted successfully")

    // 验证用户已删除
    var deletedUser models.User
    err = s.Env.DB.First(&deletedUser, user.ID).Error
    s.Error(err)
    s.Equal(gorm.ErrRecordNotFound, err)
}

func (s *APITestSuite) TestListUsers() {
    // 创建多个用户
    users := []*models.User{
        {Username: "user1", Email: "user1@example.com", Password: "password123"},
        {Username: "user2", Email: "user2@example.com", Password: "password123"},
        {Username: "user3", Email: "user3@example.com", Password: "password123"},
    }

    for _, user := range users {
        err := s.Env.DB.Create(user).Error
        s.NoError(err)
    }

    req, err := NewTestRequestBuilder().
        Method("GET").
        Path("/api/users").
        Query("page", "1").
        Query("page_size", "10").
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("page", 1.0).
        ContainsJSON("page_size", 10.0).
        ContainsJSON("total", 3.0)

    var response map[string]interface{}
    err = json.Unmarshal(recorder.Body.Bytes(), &response)
    s.NoError(err)

    usersList, ok := response["users"].([]interface{})
    s.True(ok)
    s.Len(usersList, 3)
}
```

### 商品API测试
```go
package api

import (
    "strconv"
    "testing"

    "github.com/stretchr/testify/assert"
)

// 商品API测试
func (s *APITestSuite) TestCreateProduct() {
    productRequest := map[string]interface{}{
        "name":  "Test Product",
        "price": 99.99,
        "stock": 100,
    }

    req, err := NewTestRequestBuilder().
        Method("POST").
        Path("/api/products").
        Body(productRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusCreated).
        ContainsJSON("message", "Product created successfully").
        ContainsJSON("product.name", "Test Product").
        ContainsJSON("product.price", 99.99).
        ContainsJSON("product.stock", 100)
}

func (s *APITestSuite) TestCreateProduct_InvalidPrice() {
    productRequest := map[string]interface{}{
        "name":  "Test Product",
        "price": -10.00, // 无效价格
        "stock": 100,
    }

    req, err := NewTestRequestBuilder().
        Method("POST").
        Path("/api/products").
        Body(productRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusBadRequest).
        ContainsJSON("error", "Validation failed")
}

func (s *APITestSuite) TestGetProduct() {
    product := CreateTestProduct(s.T(), s.Env.DB)

    req, err := NewTestRequestBuilder().
        Method("GET").
        Path("/api/products/" + strconv.FormatUint(uint64(product.ID), 10)).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("product.id", float64(product.ID)).
        ContainsJSON("product.name", product.Name).
        ContainsJSON("product.price", product.Price).
        ContainsJSON("product.stock", product.Stock)
}

func (s *APITestSuite) TestUpdateProductStock() {
    product := CreateTestProduct(s.T(), s.Env.DB)

    updateRequest := map[string]interface{}{
        "stock": 50,
    }

    req, err := NewTestRequestBuilder().
        Method("PUT").
        Path("/api/products/" + strconv.FormatUint(uint64(product.ID), 10)).
        Body(updateRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("message", "Product updated successfully").
        ContainsJSON("product.stock", 50)

    // 验证库存更新
    var updatedProduct models.Product
    err = s.Env.DB.First(&updatedProduct, product.ID).Error
    s.NoError(err)
    s.Equal(50, updatedProduct.Stock)
}

func (s *APITestSuite) TestListProducts_WithFilter() {
    // 创建测试商品
    products := []*models.Product{
        {Name: "Product A", Price: 10.00, Stock: 100},
        {Name: "Product B", Price: 20.00, Stock: 50},
        {Name: "Product C", Price: 30.00, Stock: 200},
    }

    for _, product := range products {
        err := s.Env.DB.Create(product).Error
        s.NoError(err)
    }

    // 测试价格过滤
    req, err := NewTestRequestBuilder().
        Method("GET").
        Path("/api/products").
        Query("min_price", "15.00").
        Query("max_price", "25.00").
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK)

    var response map[string]interface{}
    err = json.Unmarshal(recorder.Body.Bytes(), &response)
    s.NoError(err)

    productsList, ok := response["products"].([]interface{})
    s.True(ok)
    s.Len(productsList, 1) // 只有Product B符合条件
}
```

### 订单API测试
```go
package api

import (
    "strconv"
    "testing"

    "github.com/stretchr/testify/assert"
)

// 订单API测试
func (s *APITestSuite) TestCreateOrder() {
    user := CreateTestUser(s.T(), s.Env.DB)
    product := CreateTestProduct(s.T(), s.Env.DB)

    orderRequest := map[string]interface{}{
        "user_id":    user.ID,
        "product_id": product.ID,
        "quantity":  2,
    }

    req, err := NewTestRequestBuilder().
        Method("POST").
        Path("/api/orders").
        Body(orderRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusCreated).
        ContainsJSON("message", "Order created successfully").
        ContainsJSON("order.user_id", float64(user.ID)).
        ContainsJSON("order.product_id", float64(product.ID)).
        ContainsJSON("order.quantity", 2).
        ContainsJSON("order.total", product.Price*2)

    // 验证库存减少
    var updatedProduct models.Product
    err = s.Env.DB.First(&updatedProduct, product.ID).Error
    s.NoError(err)
    s.Equal(product.Stock-2, updatedProduct.Stock)
}

func (s *APITestSuite) TestCreateOrder_InsufficientStock() {
    user := CreateTestUser(s.T(), s.Env.DB)
    product := CreateTestProduct(s.T(), s.Env.DB)

    orderRequest := map[string]interface{}{
        "user_id":    user.ID,
        "product_id": product.ID,
        "quantity":  product.Stock + 1, // 超出库存
    }

    req, err := NewTestRequestBuilder().
        Method("POST").
        Path("/api/orders").
        Body(orderRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusBadRequest).
        ContainsJSON("error", "Insufficient stock")
}

func (s *APITestSuite) TestGetOrder() {
    user := CreateTestUser(s.T(), s.Env.DB)
    product := CreateTestProduct(s.T(), s.Env.DB)

    order := &models.Order{
        UserID:    user.ID,
        ProductID: product.ID,
        Quantity:  2,
        Total:     product.Price * 2,
        Status:    "pending",
    }

    err := s.Env.DB.Create(order).Error
    s.NoError(err)

    req, err := NewTestRequestBuilder().
        Method("GET").
        Path("/api/orders/" + strconv.FormatUint(uint64(order.ID), 10)).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("order.id", float64(order.ID)).
        ContainsJSON("order.user_id", float64(user.ID)).
        ContainsJSON("order.product_id", float64(product.ID)).
        ContainsJSON("order.quantity", 2).
        ContainsJSON("order.total", product.Price*2)
}

func (s *APITestSuite) TestListOrders_WithPagination() {
    user := CreateTestUser(s.T(), s.Env.DB)
    product := CreateTestProduct(s.T(), s.Env.DB)

    // 创建多个订单
    orders := []*models.Order{
        {UserID: user.ID, ProductID: product.ID, Quantity: 1, Total: product.Price, Status: "pending"},
        {UserID: user.ID, ProductID: product.ID, Quantity: 2, Total: product.Price * 2, Status: "completed"},
        {UserID: user.ID, ProductID: product.ID, Quantity: 3, Total: product.Price * 3, Status: "pending"},
    }

    for _, order := range orders {
        err := s.Env.DB.Create(order).Error
        s.NoError(err)
    }

    req, err := NewTestRequestBuilder().
        Method("GET").
        Path("/api/orders").
        Query("page", "1").
        Query("page_size", "2").
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)

    NewTestResponseAsserter(s.T(), recorder).
        Status(http.StatusOK).
        ContainsJSON("page", 1.0).
        ContainsJSON("page_size", 2.0).
        ContainsJSON("total", 3.0)

    var response map[string]interface{}
    err = json.Unmarshal(recorder.Body.Bytes(), &response)
    s.NoError(err)

    ordersList, ok := response["orders"].([]interface{})
    s.True(ok)
    s.Len(ordersList, 2)
}

func (s *APITestSuite) TestOrderWorkflow() {
    // 测试完整的订单工作流
    user := CreateTestUser(s.T(), s.Env.DB)
    product := CreateTestProduct(s.T(), s.Env.DB)
    originalStock := product.Stock

    // 1. 创建订单
    orderRequest := map[string]interface{}{
        "user_id":    user.ID,
        "product_id": product.ID,
        "quantity":  2,
    }

    req, err := NewTestRequestBuilder().
        Method("POST").
        Path("/api/orders").
        Body(orderRequest).
        Build()
    s.NoError(err)

    recorder := ExecuteTestRequest(s.Router, req)
    s.Equal(http.StatusCreated, recorder.Code)

    // 解析订单ID
    var response map[string]interface{}
    err = json.Unmarshal(recorder.Body.Bytes(), &response)
    s.NoError(err)

    orderData := response["order"].(map[string]interface{})
    orderID := uint(orderData["id"].(float64))

    // 2. 验证库存减少
    var updatedProduct models.Product
    err = s.Env.DB.First(&updatedProduct, product.ID).Error
    s.NoError(err)
    s.Equal(originalStock-2, updatedProduct.Stock)

    // 3. 更新订单状态
    updateRequest := map[string]interface{}{
        "status": "completed",
    }

    req, err = NewTestRequestBuilder().
        Method("PUT").
        Path("/api/orders/"+strconv.FormatUint(uint64(orderID), 10)).
        Body(updateRequest).
        Build()
    s.NoError(err)

    recorder = ExecuteTestRequest(s.Router, req)
    s.Equal(http.StatusOK, recorder.Code)

    // 4. 验证订单状态
    var updatedOrder models.Order
    err = s.Env.DB.First(&updatedOrder, orderID).Error
    s.NoError(err)
    s.Equal("completed", updatedOrder.Status)
}
```

## 外部服务集成测试

### 外部服务测试基础
```go
package external

import (
    "context"
    "net/http"
    "testing"
    "time"

    "github.com/ory/dockertest/v3"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
)

// 外部服务测试套件
type ExternalServiceTestSuite struct {
    suite.Suite
    RedisContainer *dockertest.Resource
    RedisClient    *redis.Client
    HTTPMockServer *httptest.Server
}

func (s *ExternalServiceTestSuite) SetupSuite() {
    // 启动Redis容器
    pool, err := dockertest.NewPool("")
    s.NoError(err)

    redisResource, err := pool.RunWithOptions(&dockertest.RunOptions{
        Repository: "redis",
        Tag:        "6-alpine",
    })
    s.NoError(err)

    s.RedisContainer = redisResource

    // 等待Redis就绪
    redisClient := redis.NewClient(&redis.Options{
        Addr: fmt.Sprintf("localhost:%s", redisResource.GetPort("6379/tcp")),
    })

    err = pool.Retry(func() error {
        return redisClient.Ping(context.Background()).Err()
    })
    s.NoError(err)

    s.RedisClient = redisClient

    // 启动HTTP Mock服务器
    s.HTTPMockServer = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        switch r.URL.Path {
        case "/api/users/1":
            if r.Method == "GET" {
                json.NewEncoder(w).Encode(map[string]interface{}{
                    "id":    1,
                    "name":  "External User",
                    "email": "external@example.com",
                })
            }
        case "/api/products/1":
            if r.Method == "GET" {
                json.NewEncoder(w).Encode(map[string]interface{}{
                    "id":    1,
                    "name":  "External Product",
                    "price": 99.99,
                })
            }
        default:
            w.WriteHeader(http.StatusNotFound)
        }
    }))
}

func (s *ExternalServiceTestSuite) TearDownSuite() {
    if s.RedisClient != nil {
        s.RedisClient.Close()
    }
    if s.RedisContainer != nil {
        s.RedisContainer.Close()
    }
    if s.HTTPMockServer != nil {
        s.HTTPMockServer.Close()
    }
}

func TestExternalServiceTestSuite(t *testing.T) {
    suite.Run(t, new(ExternalServiceTestSuite))
}

// Redis集成测试
func (s *ExternalServiceTestSuite) TestRedisCacheIntegration() {
    // 创建缓存服务
    cache := services.NewRedisCache(s.RedisClient)

    // 测试缓存设置和获取
    ctx := context.Background()
    key := "test_key"
    value := "test_value"

    err := cache.Set(ctx, key, value, time.Hour)
    s.NoError(err)

    retrievedValue, err := cache.Get(ctx, key)
    s.NoError(err)
    s.Equal(value, retrievedValue)

    // 测试缓存删除
    err = cache.Delete(ctx, key)
    s.NoError(err)

    _, err = cache.Get(ctx, key)
    s.Error(err)
    s.Equal(redis.Nil, err)
}

func (s *ExternalServiceTestSuite) TestRedisRateLimiting() {
    // 创建限流器
    limiter := services.NewRedisRateLimiter(s.RedisClient, 10, time.Minute)

    ctx := context.Background()
    userID := "user123"

    // 测试限流
    for i := 0; i < 10; i++ {
        allowed, err := limiter.Allow(ctx, userID)
        s.NoError(err)
        s.True(allowed)
    }

    // 第11次请求应该被拒绝
    allowed, err := limiter.Allow(ctx, userID)
    s.NoError(err)
    s.False(allowed)
}

// HTTP客户端测试
func (s *ExternalServiceTestSuite) TestHTTPClientIntegration() {
    // 创建HTTP客户端
    client := services.NewHTTPClient()

    // 配置客户端使用Mock服务器
    client.SetBaseURL(s.HTTPMockServer.URL)

    // 测试用户获取
    user, err := client.GetUser(1)
    s.NoError(err)
    s.Equal(uint(1), user.ID)
    s.Equal("External User", user.Name)
    s.Equal("external@example.com", user.Email)

    // 测试产品获取
    product, err := client.GetProduct(1)
    s.NoError(err)
    s.Equal(uint(1), product.ID)
    s.Equal("External Product", product.Name)
    s.Equal(99.99, product.Price)
}

func (s *ExternalServiceTestSuite) TestHTTPClientErrorHandling() {
    client := services.NewHTTPClient()
    client.SetBaseURL(s.HTTPMockServer.URL)

    // 测试404错误
    user, err := client.GetUser(999)
    s.Error(err)
    s.Nil(user)
    s.Equal("user not found", err.Error())

    // 测试网络错误
    client.SetBaseURL("http://invalid-server")
    _, err = client.GetUser(1)
    s.Error(err)
    s.Contains(err.Error(), "connection refused")
}
```

### 消息队列测试
```go
package messaging

import (
    "context"
    "testing"
    "time"

    "github.com/ory/dockertest/v3"
    "github.com/streadway/amqp"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
)

// 消息队列测试套件
type MessagingTestSuite struct {
    suite.Suite
    RabbitMQContainer *dockertest.Resource
    Connection        *amqp.Connection
    Channel           *amqp.Channel
}

func (s *MessagingTestSuite) SetupSuite() {
    // 启动RabbitMQ容器
    pool, err := dockertest.NewPool("")
    s.NoError(err)

    rabbitResource, err := pool.RunWithOptions(&dockertest.RunOptions{
        Repository: "rabbitmq",
        Tag:        "3-management",
        Env: []string{
            "RABBITMQ_DEFAULT_USER=guest",
            "RABBITMQ_DEFAULT_PASS=guest",
        },
    })
    s.NoError(err)

    s.RabbitMQContainer = rabbitResource

    // 等待RabbitMQ就绪
    var connection *amqp.Connection
    err = pool.Retry(func() error {
        var err error
        connection, err = amqp.Dial(fmt.Sprintf("amqp://guest:guest@localhost:%s/",
            rabbitResource.GetPort("5672/tcp")))
        return err
    })
    s.NoError(err)

    s.Connection = connection

    // 创建通道
    channel, err := connection.Channel()
    s.NoError(err)
    s.Channel = channel
}

func (s *MessagingTestSuite) TearDownSuite() {
    if s.Channel != nil {
        s.Channel.Close()
    }
    if s.Connection != nil {
        s.Connection.Close()
    }
    if s.RabbitMQContainer != nil {
        s.RabbitMQContainer.Close()
    }
}

func TestMessagingTestSuite(t *testing.T) {
    suite.Run(t, new(MessagingTestSuite))
}

// 消息发布订阅测试
func (s *MessagingTestSuite) TestMessagePublishSubscribe() {
    // 声明交换机和队列
    err := s.Channel.ExchangeDeclare("test_exchange", "direct", true, false, false, false, nil)
    s.NoError(err)

    queue, err := s.Channel.QueueDeclare("test_queue", true, false, false, false, nil)
    s.NoError(err)

    err = s.Channel.QueueBind(queue.Name, "test_routing_key", "test_exchange", false, nil)
    s.NoError(err)

    // 创建消费者
    messages := make(chan []byte, 1)
    errors := make(chan error, 1)

    deliveries, err := s.Channel.Consume(queue.Name, "", false, false, false, false, nil)
    s.NoError(err)

    go func() {
        for delivery := range deliveries {
            messages <- delivery.Body
            delivery.Ack(false)
        }
    }()

    // 发布消息
    message := []byte("test message")
    err = s.Channel.Publish("test_exchange", "test_routing_key", false, false, amqp.Publishing{
        ContentType: "text/plain",
        Body:        message,
    })
    s.NoError(err)

    // 等待消息接收
    select {
    case received := <-messages:
        s.Equal(message, received)
    case err := <-errors:
        s.NoError(err)
    case <-time.After(5 * time.Second):
        s.Fail("Timeout waiting for message")
    }
}

// 消息队列工作流测试
func (s *MessagingTestSuite) TestMessageQueueWorkflow() {
    // 声明工作队列
    queue, err := s.Channel.QueueDeclare("work_queue", true, false, false, false, nil)
    s.NoError(err)

    // 创建多个工作器
    numWorkers := 3
    results := make(chan string, numWorkers)

    for i := 0; i < numWorkers; i++ {
        go func(workerID int) {
            deliveries, err := s.Channel.Consume(queue.Name, "", false, false, false, false, nil)
            s.NoError(err)

            for delivery := range deliveries {
                message := string(delivery.Body)
                result := fmt.Sprintf("Worker %d processed: %s", workerID, message)
                results <- result
                delivery.Ack(false)
            }
        }(i)
    }

    // 发布多个任务
    numTasks := 10
    for i := 0; i < numTasks; i++ {
        task := fmt.Sprintf("Task %d", i)
        err = s.Channel.Publish("", queue.Name, false, false, amqp.Publishing{
            ContentType: "text/plain",
            Body:        []byte(task),
        })
        s.NoError(err)
    }

    // 收集结果
    receivedResults := make(map[string]bool)
    for i := 0; i < numTasks; i++ {
        select {
        case result := <-results:
            receivedResults[result] = true
        case <-time.After(10 * time.Second):
            s.Fail("Timeout waiting for task completion")
        }
    }

    s.Len(receivedResults, numTasks)
}
```

## 端到端测试

### E2E测试基础
```go
package e2e

import (
    "context"
    "database/sql"
    "fmt"
    "net/http"
    "testing"
    "time"

    "github.com/ory/dockertest/v3"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
)

// 端到端测试套件
type EndToEndTestSuite struct {
    suite.Suite
    TestEnvironment *TestEnvironment
    AppContainer    *dockertest.Resource
    AppURL         string
}

func (s *EndToEndTestSuite) SetupSuite() {
    // 创建完整的测试环境
    s.TestEnvironment = CreateTestEnvironment(s.T())

    // 构建并启动应用容器
    pool, err := dockertest.NewPool("")
    s.NoError(err)

    // 构建应用镜像
    err = pool.Client.BuildImage(docker.BuildImageOptions{
        Dockerfile: "../Dockerfile",
        Name:       "gin-app-test",
        ContextDir: "../",
    })
    s.NoError(err)

    // 启动应用容器
    appResource, err := pool.RunWithOptions(&dockertest.RunOptions{
        Repository: "gin-app-test",
        Tag:        "latest",
        Env: []string{
            "DB_HOST=postgres",
            "DB_PORT=5432",
            "DB_USER=test",
            "DB_PASSWORD=test",
            "DB_NAME=testdb",
            "REDIS_HOST=redis",
            "REDIS_PORT=6379",
            "GIN_MODE=release",
        },
        PortBindings: map[docker.Port][]docker.PortBinding{
            "8080/tcp": {{HostIP: "", HostPort: "8080"}},
        },
    })
    s.NoError(err)

    s.AppContainer = appResource
    s.AppURL = fmt.Sprintf("http://localhost:%s", appResource.GetPort("8080/tcp"))

    // 等待应用启动
    err = pool.Retry(func() error {
        resp, err := http.Get(s.AppURL + "/health")
        if err != nil {
            return err
        }
        defer resp.Body.Close()
        if resp.StatusCode != http.StatusOK {
            return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
        }
        return nil
    })
    s.NoError(err)
}

func (s *EndToEndTestSuite) TearDownSuite() {
    if s.AppContainer != nil {
        s.AppContainer.Close()
    }
    if s.TestEnvironment != nil {
        s.TestEnvironment.Cleanup()
    }
}

func TestEndToEndTestSuite(t *testing.T) {
    suite.Run(t, new(EndToEndTestSuite))
}

// 完整用户注册流程测试
func (s *EndToEndTestSuite) TestUserRegistrationFlow() {
    // 1. 用户注册
    registerData := map[string]interface{}{
        "username": "e2euser",
        "email":    "e2e@example.com",
        "password": "password123",
    }

    resp, err := http.Post(s.AppURL+"/api/users", "application/json", jsonBody(registerData))
    s.NoError(err)
    s.Equal(http.StatusCreated, resp.StatusCode)

    var registerResponse map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&registerResponse)
    s.NoError(err)

    userID := uint(registerResponse["user"].(map[string]interface{})["id"].(float64))

    // 2. 用户登录
    loginData := map[string]interface{}{
        "username": "e2euser",
        "password": "password123",
    }

    resp, err = http.Post(s.AppURL+"/api/auth/login", "application/json", jsonBody(loginData))
    s.NoError(err)
    s.Equal(http.StatusOK, resp.StatusCode)

    var loginResponse map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&loginResponse)
    s.NoError(err)

    token := loginResponse["token"].(string)

    // 3. 获取用户信息
    req, err := http.NewRequest("GET", s.AppURL+"/api/auth/profile", nil)
    s.NoError(err)
    req.Header.Set("Authorization", "Bearer "+token)

    client := &http.Client{}
    resp, err = client.Do(req)
    s.NoError(err)
    s.Equal(http.StatusOK, resp.StatusCode)

    var profileResponse map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&profileResponse)
    s.NoError(err)

    s.Equal(float64(userID), profileResponse["user"].(map[string]interface{})["id"])
    s.Equal("e2euser", profileResponse["user"].(map[string]interface{})["username"])
    s.Equal("e2e@example.com", profileResponse["user"].(map[string]interface{})["email"])
}

// 完整电商流程测试
func (s *EndToEndTestSuite) TestECommerceWorkflow() {
    // 1. 用户注册和登录
    token := s.registerAndLogin("ecomuser", "ecom@example.com")

    // 2. 创建商品
    productID := s.createTestProduct()

    // 3. 创建订单
    orderID := s.createOrder(token, productID)

    // 4. 支付订单
    s.processPayment(token, orderID)

    // 5. 验证订单状态
    s.verifyOrderStatus(orderID, "completed")

    // 6. 验证库存更新
    s.verifyInventoryUpdate(productID)
}

func (s *EndToEndTestSuite) registerAndLogin(username, email string) string {
    // 注册用户
    registerData := map[string]interface{}{
        "username": username,
        "email":    email,
        "password": "password123",
    }

    resp, err := http.Post(s.AppURL+"/api/users", "application/json", jsonBody(registerData))
    s.NoError(err)
    s.Equal(http.StatusCreated, resp.StatusCode)

    // 登录
    loginData := map[string]interface{}{
        "username": username,
        "password": "password123",
    }

    resp, err = http.Post(s.AppURL+"/api/auth/login", "application/json", jsonBody(loginData))
    s.NoError(err)
    s.Equal(http.StatusOK, resp.StatusCode)

    var response map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&response)
    s.NoError(err)

    return response["token"].(string)
}

func (s *EndToEndTestSuite) createTestProduct() uint {
    productData := map[string]interface{}{
        "name":  "E2E Test Product",
        "price": 99.99,
        "stock": 100,
    }

    resp, err := http.Post(s.AppURL+"/api/products", "application/json", jsonBody(productData))
    s.NoError(err)
    s.Equal(http.StatusCreated, resp.StatusCode)

    var response map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&response)
    s.NoError(err)

    return uint(response["product"].(map[string]interface{})["id"].(float64))
}

func (s *EndToEndTestSuite) createOrder(token string, productID uint) uint {
    orderData := map[string]interface{}{
        "product_id": productID,
        "quantity":  2,
    }

    req, err := http.NewRequest("POST", s.AppURL+"/api/orders", jsonBody(orderData))
    s.NoError(err)
    req.Header.Set("Authorization", "Bearer "+token)

    client := &http.Client{}
    resp, err := client.Do(req)
    s.NoError(err)
    s.Equal(http.StatusCreated, resp.StatusCode)

    var response map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&response)
    s.NoError(err)

    return uint(response["order"].(map[string]interface{})["id"].(float64))
}

func (s *EndToEndTestSuite) processPayment(token string, orderID uint) {
    paymentData := map[string]interface{}{
        "order_id": orderID,
        "method":   "credit_card",
        "amount":   199.98,
    }

    req, err := http.NewRequest("POST", s.AppURL+"/api/payments", jsonBody(paymentData))
    s.NoError(err)
    req.Header.Set("Authorization", "Bearer "+token)

    client := &http.Client{}
    resp, err := client.Do(req)
    s.NoError(err)
    s.Equal(http.StatusOK, resp.StatusCode)
}

func (s *EndToEndTestSuite) verifyOrderStatus(orderID uint, expectedStatus string) {
    req, err := http.NewRequest("GET", fmt.Sprintf("%s/api/orders/%d", s.AppURL, orderID), nil)
    s.NoError(err)

    client := &http.Client{}
    resp, err := client.Do(req)
    s.NoError(err)
    s.Equal(http.StatusOK, resp.StatusCode)

    var response map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&response)
    s.NoError(err)

    status := response["order"].(map[string]interface{})["status"].(string)
    s.Equal(expectedStatus, status)
}

func (s *EndToEndTestSuite) verifyInventoryUpdate(productID uint) {
    req, err := http.NewRequest("GET", fmt.Sprintf("%s/api/products/%d", s.AppURL, productID), nil)
    s.NoError(err)

    client := &http.Client{}
    resp, err := client.Do(req)
    s.NoError(err)
    s.Equal(http.StatusOK, resp.StatusCode)

    var response map[string]interface{}
    err = json.NewDecoder(resp.Body).Decode(&response)
    s.NoError(err)

    stock := int(response["product"].(map[string]interface{})["stock"].(float64))
    s.Equal(98, stock) // 100 - 2
}

// 辅助函数
func jsonBody(data interface{}) *bytes.Buffer {
    body, _ := json.Marshal(data)
    return bytes.NewBuffer(body)
}
```

## 测试策略和最佳实践

### 测试策略
```go
package testing

import (
    "context"
    "fmt"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

// 测试策略示例
func TestTestingStrategies(t *testing.T) {
    // 1. 使用require进行关键断言
    require.NotEmpty(t, "test-data", "Test data should not be empty")

    // 2. 使用assert进行非关键断言
    assert.Contains(t, "hello world", "hello", "Should contain hello")

    // 3. 子测试组织
    t.Run("Group related tests", func(t *testing.T) {
        t.Run("Test case 1", func(t *testing.T) {
            assert.Equal(t, 2+2, 4)
        })
        t.Run("Test case 2", func(t *testing.T) {
            assert.Equal(t, 2*2, 4)
        })
    })

    // 4. 并发测试
    t.Run("Concurrent operations", func(t *testing.T) {
        results := make(chan int, 2)

        go func() {
            results <- 1
        }()

        go func() {
            results <- 2
        }()

        count := 0
        sum := 0
        for i := range results {
            sum += i
            count++
            if count == 2 {
                break
            }
        }

        assert.Equal(t, 3, sum)
    })
}

// 表格驱动测试
func TestTableDrivenTesting(t *testing.T) {
    tests := []struct {
        name     string
        input    int
        expected int
        wantErr  bool
    }{
        {"Positive number", 5, 25, false},
        {"Zero", 0, 0, false},
        {"Negative number", -5, 25, false},
        {"Large number", 1000, 1000000, false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := square(tt.input)
            if tt.wantErr {
                assert.Error(t, err)
                return
            }
            assert.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}

func square(n int) (int, error) {
    return n * n, nil
}

// Mock和Stub示例
type Database interface {
    GetUser(id int) (*User, error)
    SaveUser(user *User) error
}

type MockDatabase struct {
    users map[int]*User
}

func (m *MockDatabase) GetUser(id int) (*User, error) {
    user, exists := m.users[id]
    if !exists {
        return nil, fmt.Errorf("user not found")
    }
    return user, nil
}

func (m *MockDatabase) SaveUser(user *User) error {
    m.users[user.ID] = user
    return nil
}

func TestUserServiceWithMock(t *testing.T) {
    // 创建Mock数据库
    mockDB := &MockDatabase{
        users: make(map[int]*User),
    }

    // 创建用户服务
    userService := NewUserService(mockDB)

    // 测试用户创建
    user := &User{
        ID:       1,
        Username: "testuser",
        Email:    "test@example.com",
    }

    err := userService.CreateUser(user)
    assert.NoError(t, err)

    // 验证用户已保存
    savedUser, err := mockDB.GetUser(1)
    assert.NoError(t, err)
    assert.Equal(t, user.Username, savedUser.Username)
    assert.Equal(t, user.Email, savedUser.Email)
}

// 测试辅助函数
func createTestUser() *User {
    return &User{
        ID:       1,
        Username: "testuser",
        Email:    "test@example.com",
    }
}

func assertUserEqual(t *testing.T, expected, actual *User) {
    assert.Equal(t, expected.ID, actual.ID)
    assert.Equal(t, expected.Username, actual.Username)
    assert.Equal(t, expected.Email, actual.Email)
}

// 基准测试最佳实践
func BenchmarkUserService(b *testing.B) {
    mockDB := &MockDatabase{
        users: make(map[int]*User),
    }
    userService := NewUserService(mockDB)

    user := createTestUser()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        err := userService.CreateUser(user)
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 并发安全测试
func TestConcurrentSafety(t *testing.T) {
    userService := NewUserService(&MockDatabase{users: make(map[int]*User)})

    const numGoroutines = 100
    done := make(chan bool, numGoroutines)

    for i := 0; i < numGoroutines; i++ {
        go func(id int) {
            user := &User{
                ID:       id,
                Username: fmt.Sprintf("user%d", id),
                Email:    fmt.Sprintf("user%d@example.com", id),
            }
            err := userService.CreateUser(user)
            assert.NoError(t, err)
            done <- true
        }(i)
    }

    // 等待所有goroutine完成
    for i := 0; i < numGoroutines; i++ {
        <-done
    }
}

// 超时测试
func TestWithTimeout(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
    defer cancel()

    done := make(chan bool)

    go func() {
        time.Sleep(50 * time.Millisecond)
        done <- true
    }()

    select {
    case <-done:
        // 测试通过
    case <-ctx.Done():
        t.Fatal("Test timed out")
    }
}
```

### 测试配置和环境
```go
package config

import (
    "flag"
    "fmt"
    "os"
    "testing"
)

// 测试配置
type TestConfig struct {
    DatabaseURL string
    RedisURL    string
    AppURL      string
    Debug       bool
    Timeout     time.Duration
}

// 全局测试配置
var GlobalTestConfig *TestConfig

func init() {
    // 解析测试标志
    databaseURL := flag.String("test-db-url", "postgres://test:test@localhost:5432/testdb", "Test database URL")
    redisURL := flag.String("test-redis-url", "redis://localhost:6379", "Test Redis URL")
    appURL := flag.String("test-app-url", "http://localhost:8080", "Test application URL")
    debug := flag.Bool("test-debug", false, "Enable debug mode")
    timeout := flag.Duration("test-timeout", 30*time.Second, "Test timeout")

    flag.Parse()

    // 支持环境变量
    if envDBURL := os.Getenv("TEST_DB_URL"); envDBURL != "" {
        *databaseURL = envDBURL
    }
    if envRedisURL := os.Getenv("TEST_REDIS_URL"); envRedisURL != "" {
        *redisURL = envRedisURL
    }
    if envAppURL := os.Getenv("TEST_APP_URL"); envAppURL != "" {
        *appURL = envAppURL
    }

    GlobalTestConfig = &TestConfig{
        DatabaseURL: *databaseURL,
        RedisURL:    *redisURL,
        AppURL:      *appURL,
        Debug:       *debug,
        Timeout:     *timeout,
    }
}

// 获取测试环境
func GetTestEnvironment(t *testing.T) *TestEnvironment {
    if GlobalTestConfig.Debug {
        t.Logf("Test configuration: %+v", GlobalTestConfig)
    }

    return &TestEnvironment{
        DatabaseURL: GlobalTestConfig.DatabaseURL,
        RedisURL:    GlobalTestConfig.RedisURL,
        AppURL:      GlobalTestConfig.AppURL,
        Timeout:     GlobalTestConfig.Timeout,
    }
}

// 测试环境
type TestEnvironment struct {
    DatabaseURL string
    RedisURL    string
    AppURL      string
    Timeout     time.Duration
}

// 创建测试上下文
func (env *TestEnvironment) CreateContext() (context.Context, context.CancelFunc) {
    return context.WithTimeout(context.Background(), env.Timeout)
}

// 测试辅助函数
func SkipIfIntegration(t *testing.T) {
    if os.Getenv("TEST_INTEGRATION") == "" {
        t.Skip("Skipping integration test")
    }
}

func SkipIfE2E(t *testing.T) {
    if os.Getenv("TEST_E2E") == "" {
        t.Skip("Skipping E2E test")
    }
}

func RequireTestDB(t *testing.T) {
    if os.Getenv("TEST_DB_URL") == "" {
        t.Skip("Skipping test: TEST_DB_URL not set")
    }
}

func RequireTestRedis(t *testing.T) {
    if os.Getenv("TEST_REDIS_URL") == "" {
        t.Skip("Skipping test: TEST_REDIS_URL not set")
    }
}
```

## 持续集成

### CI/CD配置示例
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

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
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_USER: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

      redis:
        image: redis:6-alpine
        ports:
          - 6379:6379
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5

    strategy:
      matrix:
        go-version: [1.19, 1.20, 1.21]

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Go
      uses: actions/setup-go@v4
      with:
        go-version: ${{ matrix.go-version }}

    - name: Cache Go modules
      uses: actions/cache@v3
      with:
        path: ~/go/pkg/mod
        key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
        restore-keys: |
          ${{ runner.os }}-go-

    - name: Install dependencies
      run: |
        go mod download
        go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

    - name: Run linter
      run: golangci-lint run

    - name: Run unit tests
      run: go test -v -race -coverprofile=coverage.out ./...
      env:
        TEST_DB_URL: postgres://test:test@localhost:5432/testdb
        TEST_REDIS_URL: redis://localhost:6379

    - name: Run integration tests
      run: go test -v -tags=integration ./...
      env:
        TEST_INTEGRATION: 1
        TEST_DB_URL: postgres://test:test@localhost:5432/testdb
        TEST_REDIS_URL: redis://localhost:6379

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.out

    - name: Build application
      run: go build -v -o app ./cmd/api

    - name: Build Docker image
      run: |
        docker build -t gin-app:${{ github.sha }} .

    - name: Run E2E tests
      run: go test -v -tags=e2e ./...
      env:
        TEST_E2E: 1
        TEST_APP_URL: http://localhost:8080
        TEST_DB_URL: postgres://test:test@localhost:5432/testdb
        TEST_REDIS_URL: redis://localhost:6379

  security:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: 'security-scan.sarif'

    - name: Run vulnerability scan
      run: |
        go install github.com/sonatype-community/nancy@latest
        nancy sleuth

  deploy:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Deploy to staging
      run: |
        # 部署到测试环境
        echo "Deploying to staging environment..."

    - name: Run smoke tests
      run: |
        # 运行冒烟测试
        echo "Running smoke tests..."

    - name: Deploy to production
      run: |
        # 部署到生产环境
        echo "Deploying to production environment..."
```

这个Gin集成测试文档涵盖了从基础测试环境搭建到完整的端到端测试的各个方面，包括数据库测试、API测试、外部服务测试、E2E测试以及CI/CD配置。通过这些测试策略，可以确保Gin应用的质量和稳定性。