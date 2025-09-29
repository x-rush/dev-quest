# Gin完整实战项目文档

## 目录
- [项目概述](#项目概述)
- [项目架构](#项目架构)
- [核心功能模块](#核心功能模块)
- [数据库设计](#数据库设计)
- [API设计](#api设计)
- [中间件实现](#中间件实现)
- [测试策略](#测试策略)
- [部署配置](#部署配置)
- [性能优化](#性能优化)
- [监控告警](#监控告警)

## 项目概述

### 项目背景
本项目是一个完整的电商后端系统，使用Gin框架构建，涵盖用户管理、商品管理、订单处理、支付集成等核心功能。项目采用微服务架构，展示了Gin框架在实际生产环境中的应用。

### 技术栈
- **Web框架**: Gin
- **数据库**: MySQL + Redis
- **ORM**: GORM
- **消息队列**: RabbitMQ
- **缓存**: Redis
- **监控**: Prometheus + Grafana
- **日志**: Zap
- **配置管理**: Viper
- **测试**: Testify + GoConvey

### 项目特色
- 完整的DDD分层架构
- 高性能中间件实现
- 全面的测试覆盖
- 自动化部署流程
- 实时监控告警

## 项目架构

### 整体架构
```
├── cmd/                    # 应用入口
│   ├── api/               # API服务
│   ├── worker/            # 后台任务
│   └── migration/         # 数据库迁移
├── internal/              # 内部模块
│   ├── controller/        # 控制器层
│   ├── service/           # 服务层
│   ├── repository/        # 数据访问层
│   ├── domain/            # 领域模型
│   ├── middleware/        # 中间件
│   └── infrastructure/    # 基础设施
├── pkg/                   # 公共包
├── configs/               # 配置文件
├── scripts/               # 脚本文件
├── deployments/           # 部署配置
└── docs/                  # 文档
```

### 分层架构
```go
// 领域层 - 业务逻辑核心
type Order struct {
    ID        string
    UserID    string
    Items     []OrderItem
    Total     decimal.Decimal
    Status    OrderStatus
    CreatedAt time.Time
    UpdatedAt time.Time
}

// 应用层 - 应用服务
type OrderService struct {
    orderRepo   OrderRepository
    productRepo ProductRepository
    paymentRepo PaymentRepository
    eventBus    EventBus
}

// 接口层 - 控制器和中间件
type OrderController struct {
    orderService *OrderService
    validator    *Validator
}

// 基础设施层 - 技术实现
type OrderRepository struct {
    db    *gorm.DB
    cache *Cache
}
```

## 核心功能模块

### 1. 用户模块
```go
// internal/domain/user/user.go
type User struct {
    ID           string    `json:"id" gorm:"primary_key"`
    Username     string    `json:"username" gorm:"unique;not null"`
    Email        string    `json:"email" gorm:"unique;not null"`
    PasswordHash string    `json:"-"`
    Phone        string    `json:"phone"`
    Status       UserStatus `json:"status"`
    Roles        []Role    `json:"roles" gorm:"many2many:user_roles;"`
    CreatedAt    time.Time `json:"created_at"`
    UpdatedAt    time.Time `json:"updated_at"`
}

type UserService struct {
    userRepo    UserRepository
    roleRepo    RoleRepository
    cache       *Cache
    eventBus    EventBus
    passwordHash PasswordHasher
}

func (s *UserService) RegisterUser(ctx context.Context, req RegisterUserRequest) (*User, error) {
    // 验证输入
    if err := s.validateRegistrationRequest(req); err != nil {
        return nil, err
    }

    // 检查用户是否存在
    exists, err := s.userRepo.ExistsByUsername(ctx, req.Username)
    if err != nil {
        return nil, err
    }
    if exists {
        return nil, ErrUserAlreadyExists
    }

    // 创建用户
    passwordHash, err := s.passwordHash.Hash(req.Password)
    if err != nil {
        return nil, err
    }

    user := &User{
        ID:           uuid.New().String(),
        Username:     req.Username,
        Email:        req.Email,
        PasswordHash: passwordHash,
        Phone:        req.Phone,
        Status:       UserStatusActive,
    }

    // 保存用户
    if err := s.userRepo.Create(ctx, user); err != nil {
        return nil, err
    }

    // 发送欢迎事件
    s.eventBus.Publish(ctx, UserRegisteredEvent{
        UserID:    user.ID,
        Username:  user.Username,
        Email:     user.Email,
        Timestamp: time.Now(),
    })

    return user, nil
}
```

### 2. 商品模块
```go
// internal/domain/product/product.go
type Product struct {
    ID          string          `json:"id" gorm:"primary_key"`
    Name        string          `json:"name" gorm:"not null"`
    Description string          `json:"description"`
    Price       decimal.Decimal `json:"price" gorm:"type:decimal(10,2);not null"`
    Stock       int             `json:"stock" gorm:"not null"`
    CategoryID  string          `json:"category_id"`
    Category    *Category       `json:"category,omitempty" gorm:"foreignKey:CategoryID"`
    Images      []ProductImage  `json:"images" gorm:"foreignKey:ProductID"`
    Status      ProductStatus   `json:"status" gorm:"not null"`
    Tags        []Tag           `json:"tags" gorm:"many2many:product_tags;"`
    CreatedAt   time.Time       `json:"created_at"`
    UpdatedAt   time.Time       `json:"updated_at"`
}

type ProductService struct {
    productRepo ProductRepository
    categoryRepo CategoryRepository
    cache      *Cache
    search     SearchEngine
}

func (s *ProductService) CreateProduct(ctx context.Context, req CreateProductRequest) (*Product, error) {
    // 验证商品信息
    if err := s.validateProductRequest(req); err != nil {
        return nil, err
    }

    // 检查分类是否存在
    if req.CategoryID != "" {
        category, err := s.categoryRepo.GetByID(ctx, req.CategoryID)
        if err != nil {
            return nil, err
        }
        if category == nil {
            return nil, ErrCategoryNotFound
        }
    }

    // 创建商品
    product := &Product{
        ID:          uuid.New().String(),
        Name:        req.Name,
        Description: req.Description,
        Price:       req.Price,
        Stock:       req.Stock,
        CategoryID:  req.CategoryID,
        Status:      ProductStatusActive,
    }

    // 保存商品
    if err := s.productRepo.Create(ctx, product); err != nil {
        return nil, err
    }

    // 添加到搜索引擎
    if err := s.search.IndexProduct(ctx, product); err != nil {
        // 记录错误但不影响主要流程
        log.Printf("Failed to index product: %v", err)
    }

    return product, nil
}
```

### 3. 订单模块
```go
// internal/domain/order/order.go
type Order struct {
    ID        string        `json:"id" gorm:"primary_key"`
    UserID    string        `json:"user_id"`
    User      *User         `json:"user,omitempty" gorm:"foreignKey:UserID"`
    Items     []OrderItem   `json:"items" gorm:"foreignKey:OrderID"`
    Total     decimal.Decimal `json:"total" gorm:"type:decimal(10,2);not null"`
    Status    OrderStatus   `json:"status" gorm:"not null"`
    PaymentID *string       `json:"payment_id,omitempty"`
    Payment   *Payment      `json:"payment,omitempty" gorm:"foreignKey:PaymentID"`
    Address   OrderAddress  `json:"address" gorm:"embedded"`
    CreatedAt time.Time     `json:"created_at"`
    UpdatedAt time.Time     `json:"updated_at"`
}

type OrderService struct {
    orderRepo     OrderRepository
    productRepo   ProductRepository
    paymentRepo   PaymentRepository
    inventory     InventoryService
    cache         *Cache
    eventBus      EventBus
    transaction   TransactionManager
}

func (s *OrderService) CreateOrder(ctx context.Context, req CreateOrderRequest) (*Order, error) {
    // 开始事务
    tx := s.transaction.Begin(ctx)
    defer tx.Rollback()

    // 验证商品库存
    var totalPrice decimal.Decimal
    var orderItems []OrderItem

    for _, item := range req.Items {
        product, err := s.productRepo.GetByID(ctx, item.ProductID)
        if err != nil {
            return nil, err
        }
        if product == nil {
            return nil, ErrProductNotFound
        }

        if product.Stock < item.Quantity {
            return nil, ErrInsufficientStock
        }

        itemTotal := product.Price.Mul(decimal.NewFromInt(item.Quantity))
        totalPrice = totalPrice.Add(itemTotal)

        orderItems = append(orderItems, OrderItem{
            ID:         uuid.New().String(),
            ProductID:  product.ID,
            Product:    *product,
            Quantity:   item.Quantity,
            Price:      product.Price,
            Total:      itemTotal,
        })
    }

    // 创建订单
    order := &Order{
        ID:      uuid.New().String(),
        UserID:  req.UserID,
        Items:   orderItems,
        Total:   totalPrice,
        Status:  OrderStatusPending,
        Address: req.Address,
    }

    // 保存订单
    if err := s.orderRepo.Create(ctx, order); err != nil {
        return nil, err
    }

    // 扣减库存
    for _, item := range orderItems {
        if err := s.inventory.DecreaseStock(ctx, item.ProductID, item.Quantity); err != nil {
            return nil, err
        }
    }

    // 提交事务
    if err := tx.Commit(); err != nil {
        return nil, err
    }

    // 发送订单创建事件
    s.eventBus.Publish(ctx, OrderCreatedEvent{
        OrderID:  order.ID,
        UserID:   order.UserID,
        Total:    order.Total,
        Status:   order.Status,
        Items:    order.Items,
        Timestamp: time.Now(),
    })

    return order, nil
}
```

### 4. 支付模块
```go
// internal/domain/payment/payment.go
type Payment struct {
    ID           string           `json:"id" gorm:"primary_key"`
    OrderID      string           `json:"order_id"`
    Order        *Order           `json:"order,omitempty" gorm:"foreignKey:OrderID"`
    Amount       decimal.Decimal  `json:"amount" gorm:"type:decimal(10,2);not null"`
    Method       PaymentMethod    `json:"method" gorm:"not null"`
    Status       PaymentStatus    `json:"status" gorm:"not null"`
    TransactionID string          `json:"transaction_id"`
    Metadata     PaymentMetadata  `json:"metadata" gorm:"type:jsonb"`
    CreatedAt    time.Time        `json:"created_at"`
    UpdatedAt    time.Time        `json:"updated_at"`
}

type PaymentService struct {
    paymentRepo PaymentRepository
    orderRepo   OrderRepository
    gateway     PaymentGateway
    cache       *Cache
    eventBus    EventBus
}

func (s *PaymentService) ProcessPayment(ctx context.Context, req ProcessPaymentRequest) (*Payment, error) {
    // 获取订单
    order, err := s.orderRepo.GetByID(ctx, req.OrderID)
    if err != nil {
        return nil, err
    }
    if order == nil {
        return nil, ErrOrderNotFound
    }

    // 检查订单状态
    if order.Status != OrderStatusPendingPayment {
        return nil, ErrOrderNotPendingPayment
    }

    // 创建支付记录
    payment := &Payment{
        ID:        uuid.New().String(),
        OrderID:   order.ID,
        Order:     order,
        Amount:    order.Total,
        Method:    req.Method,
        Status:    PaymentStatusPending,
        Metadata:  req.Metadata,
    }

    // 保存支付记录
    if err := s.paymentRepo.Create(ctx, payment); err != nil {
        return nil, err
    }

    // 调用支付网关
    gatewayReq := PaymentGatewayRequest{
        Amount:       payment.Amount,
        Method:       payment.Method,
        OrderID:      payment.OrderID,
        CallbackURL:  req.CallbackURL,
        ReturnURL:    req.ReturnURL,
        Metadata:     payment.Metadata,
    }

    gatewayResp, err := s.gateway.ProcessPayment(ctx, gatewayReq)
    if err != nil {
        // 更新支付状态为失败
        payment.Status = PaymentStatusFailed
        s.paymentRepo.Update(ctx, payment)
        return nil, err
    }

    // 更新支付记录
    payment.TransactionID = gatewayResp.TransactionID
    payment.Status = PaymentStatusProcessing

    if err := s.paymentRepo.Update(ctx, payment); err != nil {
        return nil, err
    }

    // 发送支付处理事件
    s.eventBus.Publish(ctx, PaymentProcessedEvent{
        PaymentID:     payment.ID,
        OrderID:       payment.OrderID,
        Amount:        payment.Amount,
        Status:        payment.Status,
        TransactionID: payment.TransactionID,
        Timestamp:     time.Now(),
    })

    return payment, nil
}
```

## 数据库设计

### 核心表结构
```sql
-- 用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    status ENUM('active', 'inactive', 'suspended') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_status (status)
);

-- 角色表
CREATE TABLE roles (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 用户角色关联表
CREATE TABLE user_roles (
    user_id VARCHAR(36) NOT NULL,
    role_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- 商品分类表
CREATE TABLE categories (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id VARCHAR(36),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_parent_id (parent_id),
    INDEX idx_sort_order (sort_order)
);

-- 商品表
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    category_id VARCHAR(36),
    status ENUM('active', 'inactive', 'deleted') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_price (price),
    FULLTEXT idx_fulltext (name, description)
);

-- 商品图片表
CREATE TABLE product_images (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(200),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_sort_order (sort_order)
);

-- 订单表
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'pending_payment', 'paid', 'shipped', 'delivered', 'cancelled') NOT NULL DEFAULT 'pending',
    payment_id VARCHAR(36),
    address JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 订单项表
CREATE TABLE order_items (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);

-- 支付表
CREATE TABLE payments (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    method ENUM('alipay', 'wechat', 'credit_card', 'bank_transfer') NOT NULL,
    status ENUM('pending', 'processing', 'success', 'failed', 'cancelled') NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(100),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT,
    INDEX idx_order_id (order_id),
    INDEX idx_status (status),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_created_at (created_at)
);
```

### 数据库迁移
```go
// cmd/migration/main.go
package main

import (
    "log"
    "path/filepath"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
    "gorm.io/gorm/schema"
    "github.com/yourproject/internal/domain/models"
    "github.com/yourproject/internal/infrastructure/database"
)

func main() {
    // 配置数据库连接
    dsn := "user:password@tcp(localhost:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local"
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
        NamingStrategy: schema.NamingStrategy{
            TablePrefix:   "",
            SingularTable: false,
        },
    })
    if err != nil {
        log.Fatal("Failed to connect to database:", err)
    }

    // 自动迁移
    err = db.AutoMigrate(
        &models.User{},
        &models.Role{},
        &models.UserRole{},
        &models.Category{},
        &models.Product{},
        &models.ProductImage{},
        &models.ProductTag{},
        &models.Tag{},
        &models.Order{},
        &models.OrderItem{},
        &models.Payment{},
    )

    if err != nil {
        log.Fatal("Failed to migrate database:", err)
    }

    log.Println("Database migration completed successfully")
}
```

## API设计

### API结构
```go
// internal/controller/api/v1/routes.go
package v1

import (
    "github.com/gin-gonic/gin"
    "github.com/yourproject/internal/controller/api/v1/admin"
    "github.com/yourproject/internal/controller/api/v1/public"
    "github.com/yourproject/internal/middleware"
)

func SetupRoutes(r *gin.RouterGroup) {
    // 公共路由
    publicGroup := r.Group("/public")
    {
        publicGroup.GET("/products", public.ListProducts)
        publicGroup.GET("/products/:id", public.GetProduct)
        publicGroup.GET("/categories", public.ListCategories)
        publicGroup.POST("/register", public.Register)
        publicGroup.POST("/login", public.Login)
    }

    // 需要认证的路由
    authGroup := r.Group("/auth")
    authGroup.Use(middleware.JWTAuth())
    {
        authGroup.GET("/profile", public.GetProfile)
        authGroup.PUT("/profile", public.UpdateProfile)
        authGroup.POST("/orders", public.CreateOrder)
        authGroup.GET("/orders", public.ListOrders)
        authGroup.GET("/orders/:id", public.GetOrder)
        authGroup.POST("/payments", public.ProcessPayment)
    }

    // 管理员路由
    adminGroup := r.Group("/admin")
    adminGroup.Use(middleware.JWTAuth(), middleware.RequireRole("admin"))
    {
        adminGroup.GET("/users", admin.ListUsers)
        adminGroup.GET("/users/:id", admin.GetUser)
        adminGroup.POST("/users", admin.CreateUser)
        adminGroup.PUT("/users/:id", admin.UpdateUser)
        adminGroup.DELETE("/users/:id", admin.DeleteUser)

        adminGroup.GET("/products", admin.ListProducts)
        adminGroup.POST("/products", admin.CreateProduct)
        adminGroup.PUT("/products/:id", admin.UpdateProduct)
        adminGroup.DELETE("/products/:id", admin.DeleteProduct)

        adminGroup.GET("/orders", admin.ListOrders)
        adminGroup.PUT("/orders/:id", admin.UpdateOrder)
    }
}
```

### API控制器实现
```go
// internal/controller/api/v1/public/product_controller.go
package public

import (
    "net/http"
    "strconv"

    "github.com/gin-gonic/gin"
    "github.com/yourproject/internal/domain/product"
    "github.com/yourproject/internal/dto"
    "github.com/yourproject/internal/service"
)

type ProductController struct {
    productService *service.ProductService
}

func NewProductController(productService *service.ProductService) *ProductController {
    return &ProductController{
        productService: productService,
    }
}

func (c *ProductController) ListProducts(ctx *gin.Context) {
    // 解析查询参数
    page, _ := strconv.Atoi(ctx.DefaultQuery("page", "1"))
    pageSize, _ := strconv.Atoi(ctx.DefaultQuery("page_size", "20"))
    categoryID := ctx.Query("category_id")
    keyword := ctx.Query("keyword")
    sortBy := ctx.DefaultQuery("sort_by", "created_at")
    sortOrder := ctx.DefaultQuery("sort_order", "desc")

    // 构建查询请求
    req := dto.ListProductsRequest{
        Page:      page,
        PageSize:  pageSize,
        CategoryID: categoryID,
        Keyword:   keyword,
        SortBy:    sortBy,
        SortOrder: sortOrder,
    }

    // 调用服务层
    products, total, err := c.productService.ListProducts(ctx, req)
    if err != nil {
        ctx.JSON(http.StatusInternalServerError, gin.H{
            "error": err.Error(),
        })
        return
    }

    // 构建响应
    response := dto.ListProductsResponse{
        Data:       products,
        Total:      total,
        Page:       page,
        PageSize:   pageSize,
        TotalPages: (total + int64(pageSize) - 1) / int64(pageSize),
    }

    ctx.JSON(http.StatusOK, response)
}

func (c *ProductController) GetProduct(ctx *gin.Context) {
    productID := ctx.Param("id")

    // 调用服务层
    product, err := c.productService.GetProductByID(ctx, productID)
    if err != nil {
        if err == product.ErrProductNotFound {
            ctx.JSON(http.StatusNotFound, gin.H{
                "error": "Product not found",
            })
            return
        }
        ctx.JSON(http.StatusInternalServerError, gin.H{
            "error": err.Error(),
        })
        return
    }

    ctx.JSON(http.StatusOK, product)
}
```

### 请求和响应DTO
```go
// internal/dto/product_dto.go
package dto

import "github.com/yourproject/internal/domain/product"

type ListProductsRequest struct {
    Page      int    `form:"page" binding:"min=1"`
    PageSize  int    `form:"page_size" binding:"min=1,max=100"`
    CategoryID string `form:"category_id"`
    Keyword   string `form:"keyword"`
    SortBy    string `form:"sort_by" binding:"oneof=name price created_at sales"`
    SortOrder string `form:"sort_order" binding:"oneof=asc desc"`
}

type ProductResponse struct {
    ID          string                  `json:"id"`
    Name        string                  `json:"name"`
    Description string                  `json:"description"`
    Price       string                  `json:"price"`
    Stock       int                     `json:"stock"`
    CategoryID  string                  `json:"category_id"`
    Category    *CategoryResponse       `json:"category,omitempty"`
    Images      []ProductImageResponse   `json:"images"`
    Status      string                  `json:"status"`
    Tags        []TagResponse           `json:"tags"`
    CreatedAt   string                  `json:"created_at"`
    UpdatedAt   string                  `json:"updated_at"`
}

type ListProductsResponse struct {
    Data       []ProductResponse `json:"data"`
    Total      int64            `json:"total"`
    Page       int              `json:"page"`
    PageSize   int              `json:"page_size"`
    TotalPages int64            `json:"total_pages"`
}

func ToProductResponse(p *product.Product) *ProductResponse {
    response := &ProductResponse{
        ID:          p.ID,
        Name:        p.Name,
        Description: p.Description,
        Price:       p.Price.String(),
        Stock:       p.Stock,
        CategoryID:  p.CategoryID,
        Status:      string(p.Status),
        CreatedAt:   p.CreatedAt.Format("2006-01-02T15:04:05Z"),
        UpdatedAt:   p.UpdatedAt.Format("2006-01-02T15:04:05Z"),
    }

    if p.Category != nil {
        response.Category = ToCategoryResponse(p.Category)
    }

    for _, image := range p.Images {
        response.Images = append(response.Images, ToProductImageResponse(&image))
    }

    for _, tag := range p.Tags {
        response.Tags = append(response.Tags, ToTagResponse(&tag))
    }

    return response
}
```

## 中间件实现

### JWT认证中间件
```go
// internal/middleware/jwt_auth.go
package middleware

import (
    "net/http"
    "strings"

    "github.com/gin-gonic/gin"
    "github.com/yourproject/internal/auth"
    "github.com/yourproject/internal/repository"
)

func JWTAuth() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 获取Authorization头
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(http.StatusUnauthorized, gin.H{
                "error": "Authorization header required",
            })
            c.Abort()
            return
        }

        // 解析Bearer token
        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        if tokenString == authHeader {
            c.JSON(http.StatusUnauthorized, gin.H{
                "error": "Bearer token required",
            })
            c.Abort()
            return
        }

        // 验证token
        claims, err := auth.ValidateToken(tokenString)
        if err != nil {
            c.JSON(http.StatusUnauthorized, gin.H{
                "error": "Invalid or expired token",
            })
            c.Abort()
            return
        }

        // 获取用户信息
        userRepo := repository.NewUserRepository(database.GetDB())
        user, err := userRepo.GetByID(c, claims.UserID)
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{
                "error": "Failed to get user information",
            })
            c.Abort()
            return
        }

        if user == nil {
            c.JSON(http.StatusUnauthorized, gin.H{
                "error": "User not found",
            })
            c.Abort()
            return
        }

        // 将用户信息存储在上下文中
        c.Set("user", user)
        c.Set("user_id", user.ID)
        c.Set("roles", user.Roles)

        c.Next()
    }
}
```

### 角色权限中间件
```go
// internal/middleware/role_auth.go
package middleware

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

func RequireRole(role string) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 从上下文中获取用户角色
        userRoles, exists := c.Get("roles")
        if !exists {
            c.JSON(http.StatusForbidden, gin.H{
                "error": "Access denied",
            })
            c.Abort()
            return
        }

        // 检查用户是否拥有所需角色
        roles, ok := userRoles.([]domain.Role)
        if !ok {
            c.JSON(http.StatusForbidden, gin.H{
                "error": "Access denied",
            })
            c.Abort()
            return
        }

        hasRole := false
        for _, r := range roles {
            if r.Name == role {
                hasRole = true
                break
            }
        }

        if !hasRole {
            c.JSON(http.StatusForbidden, gin.H{
                "error": "Insufficient permissions",
            })
            c.Abort()
            return
        }

        c.Next()
    }
}

func RequirePermission(permission string) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 从上下文中获取用户角色
        userRoles, exists := c.Get("roles")
        if !exists {
            c.JSON(http.StatusForbidden, gin.H{
                "error": "Access denied",
            })
            c.Abort()
            return
        }

        // 检查用户是否拥有所需权限
        roles, ok := userRoles.([]domain.Role)
        if !ok {
            c.JSON(http.StatusForbidden, gin.H{
                "error": "Access denied",
            })
            c.Abort()
            return
        }

        hasPermission := false
        for _, role := range roles {
            if role.Permissions != nil {
                if perms, ok := role.Permissions.([]string); ok {
                    for _, perm := range perms {
                        if perm == permission {
                            hasPermission = true
                            break
                        }
                    }
                }
            }
        }

        if !hasPermission {
            c.JSON(http.StatusForbidden, gin.H{
                "error": "Insufficient permissions",
            })
            c.Abort()
            return
        }

        c.Next()
    }
}
```

### 限流中间件
```go
// internal/middleware/rate_limit.go
package middleware

import (
    "net/http"
    "strconv"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
    "github.com/yourproject/internal/infrastructure/cache"
)

func RateLimit(maxRequests int, window time.Duration) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 获取客户端IP
        clientIP := c.ClientIP()

        // 构建Redis键
        key := "rate_limit:" + clientIP

        // 获取Redis客户端
        redisClient := cache.GetRedisClient()

        // 使用Redis实现滑动窗口限流
        current := time.Now().Unix()
        windowStart := current - int64(window.Seconds())

        // 移除窗口外的请求记录
        redisClient.ZRemRangeByScore(c, key, "0", strconv.FormatInt(windowStart, 10))

        // 获取当前窗口内的请求数
        count, err := redisClient.ZCard(c, key).Result()
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{
                "error": "Rate limit check failed",
            })
            c.Abort()
            return
        }

        // 检查是否超过限制
        if count >= int64(maxRequests) {
            c.JSON(http.StatusTooManyRequests, gin.H{
                "error": "Rate limit exceeded",
                "retry_after": window,
            })
            c.Abort()
            return
        }

        // 记录当前请求
        redisClient.ZAdd(c, key, &redis.Z{
            Score:  float64(current),
            Member: strconv.FormatInt(current, 10),
        })

        // 设置过期时间
        redisClient.Expire(c, key, window)

        c.Next()
    }
}

func RateLimitByUser(maxRequests int, window time.Duration) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 从上下文中获取用户ID
        userID, exists := c.Get("user_id")
        if !exists {
            c.Next()
            return
        }

        // 构建Redis键
        key := "rate_limit:user:" + userID.(string)

        // 获取Redis客户端
        redisClient := cache.GetRedisClient()

        // 使用令牌桶算法实现限流
        pipe := redisClient.Pipeline()

        // 获取当前令牌数
        tokensCmd := pipe.Get(c, key+":tokens")
        lastRefillCmd := pipe.Get(c, key+":last_refill")

        _, err := pipe.Exec(c)
        if err != nil && err != redis.Nil {
            c.JSON(http.StatusInternalServerError, gin.H{
                "error": "Rate limit check failed",
            })
            c.Abort()
            return
        }

        // 初始化令牌桶
        var tokens float64
        var lastRefill int64

        if tokensCmd.Err() == redis.Nil {
            tokens = float64(maxRequests)
            lastRefill = time.Now().Unix()
        } else {
            tokens, _ = strconv.ParseFloat(tokensCmd.Val(), 64)
            lastRefill, _ = strconv.ParseInt(lastRefillCmd.Val(), 10, 64)
        }

        // 计算令牌补充
        now := time.Now().Unix()
        elapsed := now - lastRefill
        tokensToAdd := float64(elapsed) / window.Seconds() * float64(maxRequests)

        tokens = min(tokens+tokensToAdd, float64(maxRequests))

        // 检查是否有足够令牌
        if tokens < 1 {
            c.JSON(http.StatusTooManyRequests, gin.H{
                "error": "Rate limit exceeded",
                "retry_after": time.Duration(float64(window) * (1 - tokens) / float64(maxRequests)),
            })
            c.Abort()
            return
        }

        // 消耗令牌
        tokens -= 1

        // 更新令牌桶
        pipe = redisClient.Pipeline()
        pipe.Set(c, key+":tokens", tokens, window)
        pipe.Set(c, key+":last_refill", now, window)

        if _, err := pipe.Exec(c); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{
                "error": "Rate limit update failed",
            })
            c.Abort()
            return
        }

        c.Next()
    }
}
```

### 请求日志中间件
```go
// internal/middleware/request_logger.go
package middleware

import (
    "bytes"
    "encoding/json"
    "io/ioutil"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/yourproject/internal/infrastructure/logger"
)

func RequestLogger() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        // 读取请求体
        var requestBody []byte
        if c.Request.Body != nil {
            requestBody, _ = ioutil.ReadAll(c.Request.Body)
            c.Request.Body = ioutil.NopCloser(bytes.NewBuffer(requestBody))
        }

        // 创建响应记录器
        writer := &responseBodyRecorder{
            ResponseWriter: c.Writer,
            body:           bytes.NewBufferString(""),
        }
        c.Writer = writer

        // 处理请求
        c.Next()

        // 计算处理时间
        duration := time.Since(start)

        // 构建日志记录
        logEntry := logger.LogEntry{
            Timestamp:    start.Format("2006-01-02T15:04:05Z"),
            Method:       c.Request.Method,
            Path:         c.Request.URL.Path,
            Query:        c.Request.URL.RawQuery,
            IP:           c.ClientIP(),
            UserAgent:    c.Request.UserAgent(),
            StatusCode:   c.Writer.Status(),
            Duration:     duration.String(),
            RequestSize:  c.Request.ContentLength,
            ResponseSize: writer.Size(),
        }

        // 记录请求体（敏感信息脱敏）
        if len(requestBody) > 0 {
            var body map[string]interface{}
            if err := json.Unmarshal(requestBody, &body); err == nil {
                // 脱敏处理
                if password, ok := body["password"]; ok {
                    body["password"] = "***"
                }
                if card, ok := body["card_number"]; ok {
                    body["card_number"] = "****-****-****-****"
                }
                sanitizedBody, _ := json.Marshal(body)
                logEntry.RequestBody = string(sanitizedBody)
            } else {
                logEntry.RequestBody = string(requestBody)
            }
        }

        // 记录响应体
        if writer.body.Len() > 0 {
            logEntry.ResponseBody = writer.body.String()
        }

        // 从上下文中获取用户信息
        if userID, exists := c.Get("user_id"); exists {
            logEntry.UserID = userID.(string)
        }

        // 记录日志
        logger.Info(logEntry)

        // 根据状态码设置不同的日志级别
        if c.Writer.Status() >= 500 {
            logger.Error("Server error", logEntry)
        } else if c.Writer.Status() >= 400 {
            logger.Warn("Client error", logEntry)
        }
    }
}

type responseBodyRecorder struct {
    gin.ResponseWriter
    body *bytes.Buffer
}

func (r *responseBodyRecorder) Write(b []byte) (int, error) {
    r.body.Write(b)
    return r.ResponseWriter.Write(b)
}

func (r *responseBodyRecorder) WriteString(s string) (int, error) {
    r.body.WriteString(s)
    return r.ResponseWriter.WriteString(s)
}
```

## 测试策略

### 单元测试
```go
// internal/service/product_service_test.go
package service

import (
    "context"
    "testing"
    "time"

    "github.com/shopspring/decimal"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"

    "github.com/yourproject/internal/domain/product"
    "github.com/yourproject/internal/mocks"
)

func TestProductService_CreateProduct(t *testing.T) {
    // 准备测试数据
    tests := []struct {
        name        string
        request     CreateProductRequest
        setupMocks  func(*mocks.ProductRepository, *mocks.CategoryRepository, *mocks.Cache, *mocks.SearchEngine)
        expectError bool
        expected    *product.Product
    }{
        {
            name: "success create product",
            request: CreateProductRequest{
                Name:        "Test Product",
                Description: "Test Description",
                Price:       decimal.NewFromInt(100),
                Stock:       10,
                CategoryID:  "category-1",
            },
            setupMocks: func(pr *mocks.ProductRepository, cr *mocks.CategoryRepository, ch *mocks.Cache, se *mocks.SearchEngine) {
                // 模拟分类存在
                cr.On("GetByID", mock.Anything, "category-1").Return(&product.Category{
                    ID:   "category-1",
                    Name: "Test Category",
                }, nil)

                // 模拟创建成功
                pr.On("Create", mock.Anything, mock.MatchedBy(func(p *product.Product) bool {
                    return p.Name == "Test Product" && p.Price.Equal(decimal.NewFromInt(100))
                })).Return(nil)

                // 模拟搜索引擎索引
                se.On("IndexProduct", mock.Anything, mock.Anything).Return(nil)
            },
            expectError: false,
            expected: &product.Product{
                Name:        "Test Product",
                Description: "Test Description",
                Price:       decimal.NewFromInt(100),
                Stock:       10,
                CategoryID:  "category-1",
                Status:      product.ProductStatusActive,
            },
        },
        {
            name: "category not found",
            request: CreateProductRequest{
                Name:        "Test Product",
                Description: "Test Description",
                Price:       decimal.NewFromInt(100),
                Stock:       10,
                CategoryID:  "non-existent-category",
            },
            setupMocks: func(pr *mocks.ProductRepository, cr *mocks.CategoryRepository, ch *mocks.Cache, se *mocks.SearchEngine) {
                // 模拟分类不存在
                cr.On("GetByID", mock.Anything, "non-existent-category").Return(nil, nil)
            },
            expectError: true,
        },
        {
            name: "invalid price",
            request: CreateProductRequest{
                Name:        "Test Product",
                Description: "Test Description",
                Price:       decimal.NewFromInt(-1),
                Stock:       10,
            },
            setupMocks: func(pr *mocks.ProductRepository, cr *mocks.CategoryRepository, ch *mocks.Cache, se *mocks.SearchEngine) {
                // 不需要模拟任何方法，因为验证会失败
            },
            expectError: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // 创建mock对象
            productRepo := &mocks.ProductRepository{}
            categoryRepo := &mocks.CategoryRepository{}
            cache := &mocks.Cache{}
            searchEngine := &mocks.SearchEngine{}

            // 设置mock行为
            tt.setupMocks(productRepo, categoryRepo, cache, searchEngine)

            // 创建服务
            service := NewProductService(productRepo, categoryRepo, cache, searchEngine)

            // 调用测试方法
            result, err := service.CreateProduct(context.Background(), tt.request)

            // 验证结果
            if tt.expectError {
                assert.Error(t, err)
                assert.Nil(t, result)
            } else {
                assert.NoError(t, err)
                assert.NotNil(t, result)
                assert.Equal(t, tt.expected.Name, result.Name)
                assert.Equal(t, tt.expected.Description, result.Description)
                assert.True(t, tt.expected.Price.Equal(result.Price))
                assert.Equal(t, tt.expected.Stock, result.Stock)
                assert.Equal(t, tt.expected.CategoryID, result.CategoryID)
                assert.Equal(t, tt.expected.Status, result.Status)
            }

            // 验证mock调用
            productRepo.AssertExpectations(t)
            categoryRepo.AssertExpectations(t)
            cache.AssertExpectations(t)
            searchEngine.AssertExpectations(t)
        })
    }
}
```

### 集成测试
```go
// tests/integration/api_test.go
package integration

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"

    "github.com/yourproject/internal/controller/api/v1"
    "github.com/yourproject/internal/infrastructure/database"
    "github.com/yourproject/internal/service"
)

type APITestSuite struct {
    suite.Suite
    router       *gin.Engine
    productRepo  *mocks.ProductRepository
    productService *service.ProductService
    productController *v1.ProductController
}

func (suite *APITestSuite) SetupSuite() {
    // 设置Gin为测试模式
    gin.SetMode(gin.TestMode)

    // 初始化数据库连接
    db := database.SetupTestDB()

    // 创建mock对象
    suite.productRepo = &mocks.ProductRepository{}

    // 创建服务
    suite.productService = service.NewProductService(
        suite.productRepo,
        nil, // category repo
        nil, // cache
        nil, // search engine
    )

    // 创建控制器
    suite.productController = v1.NewProductController(suite.productService)

    // 设置路由
    suite.router = gin.Default()
    api := suite.router.Group("/api/v1")
    v1.SetupRoutes(api)
}

func (suite *APITestSuite) TestListProducts() {
    // 准备测试数据
    mockProducts := []*domain.Product{
        {
            ID:          "1",
            Name:        "Product 1",
            Description: "Description 1",
            Price:       decimal.NewFromInt(100),
            Stock:       10,
            Status:      domain.ProductStatusActive,
            CreatedAt:   time.Now(),
            UpdatedAt:   time.Now(),
        },
        {
            ID:          "2",
            Name:        "Product 2",
            Description: "Description 2",
            Price:       decimal.NewFromInt(200),
            Stock:       20,
            Status:      domain.ProductStatusActive,
            CreatedAt:   time.Now(),
            UpdatedAt:   time.Now(),
        },
    }

    // 设置mock行为
    suite.productRepo.On("List", mock.Anything, mock.Anything).Return(mockProducts, int64(2), nil)

    // 创建请求
    req, _ := http.NewRequest("GET", "/api/v1/public/products?page=1&page_size=10", nil)
    w := httptest.NewRecorder()

    // 发送请求
    suite.router.ServeHTTP(w, req)

    // 验证响应
    assert.Equal(suite.T(), http.StatusOK, w.Code)

    var response dto.ListProductsResponse
    err := json.Unmarshal(w.Body.Bytes(), &response)
    assert.NoError(suite.T(), err)

    assert.Equal(suite.T(), int64(2), response.Total)
    assert.Equal(suite.T(), 1, response.Page)
    assert.Equal(suite.T(), 10, response.PageSize)
    assert.Len(suite.T(), response.Data, 2)

    // 验证mock调用
    suite.productRepo.AssertExpectations(suite.T())
}

func (suite *APITestSuite) TestGetProduct() {
    // 准备测试数据
    mockProduct := &domain.Product{
        ID:          "1",
        Name:        "Product 1",
        Description: "Description 1",
        Price:       decimal.NewFromInt(100),
        Stock:       10,
        Status:      domain.ProductStatusActive,
        CreatedAt:   time.Now(),
        UpdatedAt:   time.Now(),
    }

    // 设置mock行为
    suite.productRepo.On("GetByID", mock.Anything, "1").Return(mockProduct, nil)

    // 创建请求
    req, _ := http.NewRequest("GET", "/api/v1/public/products/1", nil)
    w := httptest.NewRecorder()

    // 发送请求
    suite.router.ServeHTTP(w, req)

    // 验证响应
    assert.Equal(suite.T(), http.StatusOK, w.Code)

    var response domain.Product
    err := json.Unmarshal(w.Body.Bytes(), &response)
    assert.NoError(suite.T(), err)

    assert.Equal(suite.T(), mockProduct.ID, response.ID)
    assert.Equal(suite.T(), mockProduct.Name, response.Name)
    assert.Equal(suite.T(), mockProduct.Description, response.Description)

    // 验证mock调用
    suite.productRepo.AssertExpectations(suite.T())
}

func (suite *APITestSuite) TestCreateProduct() {
    // 准备测试数据
    request := map[string]interface{}{
        "name":        "New Product",
        "description": "New Description",
        "price":       150.00,
        "stock":       15,
        "category_id": "1",
    }

    requestBody, _ := json.Marshal(request)

    // 设置mock行为
    suite.productRepo.On("Create", mock.Anything, mock.MatchedBy(func(p *domain.Product) bool {
        return p.Name == "New Product" && p.Price.Equal(decimal.NewFromFloat(150))
    })).Return(nil)

    // 创建请求
    req, _ := http.NewRequest("POST", "/api/v1/admin/products", bytes.NewBuffer(requestBody))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer valid-token")
    w := httptest.NewRecorder()

    // 发送请求
    suite.router.ServeHTTP(w, req)

    // 验证响应
    assert.Equal(suite.T(), http.StatusCreated, w.Code)

    // 验证mock调用
    suite.productRepo.AssertExpectations(suite.T())
}

func TestAPITestSuite(t *testing.T) {
    suite.Run(t, new(APITestSuite))
}
```

### 性能测试
```go
// tests/performance/product_performance_test.go
package performance

import (
    "context"
    "fmt"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"

    "github.com/yourproject/internal/service"
)

func BenchmarkProductService_CreateProduct(b *testing.B) {
    // 准备测试环境
    productService := setupProductService()

    // 准备测试数据
    request := service.CreateProductRequest{
        Name:        "Benchmark Product",
        Description: "Benchmark Description",
        Price:       decimal.NewFromInt(100),
        Stock:       10,
    }

    // 重置计时器
    b.ResetTimer()

    // 执行基准测试
    for i := 0; i < b.N; i++ {
        _, err := productService.CreateProduct(context.Background(), request)
        if err != nil {
            b.Fatalf("CreateProduct failed: %v", err)
        }
    }
}

func BenchmarkProductService_ListProducts(b *testing.B) {
    // 准备测试环境
    productService := setupProductService()

    // 准备测试数据
    request := service.ListProductsRequest{
        Page:     1,
        PageSize: 20,
    }

    // 重置计时器
    b.ResetTimer()

    // 执行基准测试
    for i := 0; i < b.N; i++ {
        _, _, err := productService.ListProducts(context.Background(), request)
        if err != nil {
            b.Fatalf("ListProducts failed: %v", err)
        }
    }
}

func TestProductService_ConcurrentCreateProduct(t *testing.T) {
    // 准备测试环境
    productService := setupProductService()

    // 并发数量
    concurrency := 100

    // 创建结果通道
    results := make(chan error, concurrency)

    // 启动多个goroutine
    start := time.Now()
    for i := 0; i < concurrency; i++ {
        go func(id int) {
            request := service.CreateProductRequest{
                Name:        fmt.Sprintf("Concurrent Product %d", id),
                Description: "Concurrent Description",
                Price:       decimal.NewFromInt(100),
                Stock:       10,
            }

            _, err := productService.CreateProduct(context.Background(), request)
            results <- err
        }(i)
    }

    // 收集结果
    var errors []error
    for i := 0; i < concurrency; i++ {
        if err := <-results; err != nil {
            errors = append(errors, err)
        }
    }

    // 计算耗时
    duration := time.Since(start)

    // 验证结果
    t.Logf("Concurrent test completed in %v", duration)
    t.Logf("Total requests: %d", concurrency)
    t.Logf("Success rate: %.2f%%", float64(concurrency-len(errors))/float64(concurrency)*100)

    if len(errors) > 0 {
        t.Logf("Errors occurred: %d", len(errors))
        for _, err := range errors {
            t.Logf("Error: %v", err)
        }
    }

    assert.Equal(t, 0, len(errors), "Concurrent operations should not fail")
}

func TestProductService_LoadTest(t *testing.T) {
    // 准备测试环境
    productService := setupProductService()

    // 负载测试参数
    duration := 30 * time.Second
    requestRate := 1000 // 每秒请求数

    // 创建统计信息
    stats := struct {
        TotalRequests int
        SuccessCount  int
        ErrorCount    int
        TotalDuration time.Duration
        MinDuration   time.Duration
        MaxDuration   time.Duration
    }{}

    // 创建ticker控制请求速率
    ticker := time.NewTicker(time.Second / time.Duration(requestRate))
    defer ticker.Stop()

    // 创建结果通道
    results := make(chan time.Duration, requestRate*2)

    // 启动测试
    start := time.Now()
    end := start.Add(duration)

    go func() {
        for time.Now().Before(end) {
            <-ticker

            request := service.ListProductsRequest{
                Page:     1,
                PageSize: 20,
            }

            reqStart := time.Now()
            _, _, err := productService.ListProducts(context.Background(), request)
            reqDuration := time.Since(reqStart)

            if err != nil {
                results <- -reqDuration // 错误用负数表示
            } else {
                results <- reqDuration
            }
        }
    }()

    // 收集结果
    go func() {
        for {
            select {
            case duration := <-results:
                stats.TotalRequests++
                if duration < 0 {
                    stats.ErrorCount++
                    duration = -duration
                } else {
                    stats.SuccessCount++
                }

                if stats.MinDuration == 0 || duration < stats.MinDuration {
                    stats.MinDuration = duration
                }
                if duration > stats.MaxDuration {
                    stats.MaxDuration = duration
                }
            case <-time.After(time.Second):
                return
            }
        }
    }()

    // 等待测试完成
    time.Sleep(duration + time.Second)

    // 计算最终统计
    stats.TotalDuration = time.Since(start)
    avgDuration := stats.MinDuration
    if stats.SuccessCount > 0 {
        avgDuration = stats.TotalDuration / time.Duration(stats.SuccessCount)
    }

    // 输出测试结果
    t.Logf("Load Test Results:")
    t.Logf("Total Duration: %v", stats.TotalDuration)
    t.Logf("Target Rate: %d req/s", requestRate)
    t.Logf("Actual Rate: %.2f req/s", float64(stats.TotalRequests)/stats.TotalDuration.Seconds())
    t.Logf("Total Requests: %d", stats.TotalRequests)
    t.Logf("Success Count: %d", stats.SuccessCount)
    t.Logf("Error Count: %d", stats.ErrorCount)
    t.Logf("Success Rate: %.2f%%", float64(stats.SuccessCount)/float64(stats.TotalRequests)*100)
    t.Logf("Average Response Time: %v", avgDuration)
    t.Logf("Min Response Time: %v", stats.MinDuration)
    t.Logf("Max Response Time: %v", stats.MaxDuration)

    // 验证性能指标
    assert.Greater(t, stats.SuccessCount, 0, "Should have successful requests")
    assert.Greater(t, float64(stats.SuccessCount)/float64(stats.TotalRequests), 0.95, "Success rate should be above 95%")
    assert.Less(t, avgDuration, 100*time.Millisecond, "Average response time should be less than 100ms")
}
```

## 部署配置

### Docker配置
```dockerfile
# Dockerfile
FROM golang:1.21-alpine AS builder

# 安装必要的包
RUN apk add --no-cache git

# 设置工作目录
WORKDIR /app

# 复制go mod文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/api

# 最终镜像
FROM alpine:latest

# 安装ca-certificates用于HTTPS请求
RUN apk --no-cache add ca-certificates

# 设置工作目录
WORKDIR /root/

# 从构建器复制二进制文件
COPY --from=builder /app/main .

# 复制配置文件
COPY --from=builder /app/configs ./configs

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["./main"]
```

### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  # API服务
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=root
      - DB_PASSWORD=password
      - DB_NAME=ecommerce
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - RABBITMQ_HOST=rabbitmq
      - RABBITMQ_PORT=5672
    depends_on:
      - mysql
      - redis
      - rabbitmq
    networks:
      - ecommerce-network

  # MySQL数据库
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=ecommerce
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ecommerce-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - ecommerce-network

  # RabbitMQ消息队列
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=password
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - ecommerce-network

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployments/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./deployments/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
    networks:
      - ecommerce-network

  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./deployments/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - ecommerce-network

  # Grafana可视化
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./deployments/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./deployments/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    networks:
      - ecommerce-network

volumes:
  mysql-data:
  redis-data:
  rabbitmq-data:
  prometheus-data:
  grafana-data:

networks:
  ecommerce-network:
    driver: bridge
```

### Kubernetes部署配置
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
  labels:
    app: ecommerce-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    metadata:
      labels:
        app: ecommerce-api
    spec:
      containers:
      - name: api
        image: your-registry/ecommerce-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          value: "mysql-service"
        - name: DB_PORT
          value: "3306"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        - name: DB_NAME
          value: "ecommerce"
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"
        - name: RABBITMQ_HOST
          value: "rabbitmq-service"
        - name: RABBITMQ_PORT
          value: "5672"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-api-service
spec:
  selector:
    app: ecommerce-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-api-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: ecommerce-api-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ecommerce-api-service
            port:
              number: 80
```

### CI/CD配置
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
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: ecommerce_test
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
    - uses: actions/checkout@v3

    - name: Set up Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.21'

    - name: Install dependencies
      run: go mod download

    - name: Run tests
      run: go test -v -race -coverprofile=coverage.out ./...
      env:
        DB_HOST: localhost
        DB_PORT: 3306
        DB_USER: root
        DB_PASSWORD: password
        DB_NAME: ecommerce_test
        REDIS_HOST: localhost
        REDIS_PORT: 6379

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.out

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          your-registry/ecommerce-api:${{ github.sha }}
          your-registry/ecommerce-api:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3

    - name: Set up Kustomize
      uses: imjasonh/setup-kustomize@v1

    - name: Deploy to Kubernetes
      run: |
        kustomize edit set image your-registry/ecommerce-api=your-registry/ecommerce-api:${{ github.sha }}
        kustomize build ./k8s | kubectl apply -f -
```

## 性能优化

### 数据库优化
```go
// internal/infrastructure/database/db_pool.go
package database

import (
    "fmt"
    "time"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

// 创建优化的数据库连接池
func CreateOptimizedDBConnection(dsn string) (*gorm.DB, error) {
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Silent),
    })
    if err != nil {
        return nil, err
    }

    sqlDB, err := db.DB()
    if err != nil {
        return nil, err
    }

    // 设置连接池参数
    sqlDB.SetMaxIdleConns(10)                    // 最大空闲连接数
    sqlDB.SetMaxOpenConns(100)                   // 最大打开连接数
    sqlDB.SetConnMaxLifetime(time.Hour)          // 连接最大生存时间
    sqlDB.SetConnMaxIdleTime(30 * time.Minute)   // 空闲连接最大存活时间

    return db, nil
}

// 创建读写分离的数据库连接
func CreateReadWriteSeparationDB(readDSNs []string, writeDSN string) (*gorm.DB, error) {
    // 主库（写）
    writeDB, err := gorm.Open(mysql.Open(writeDSN), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Silent),
    })
    if err != nil {
        return nil, err
    }

    // 从库（读）
    var readDBs []*gorm.DB
    for _, dsn := range readDSNs {
        readDB, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
            Logger: logger.Default.LogMode(logger.Silent),
        })
        if err != nil {
            return nil, err
        }
        readDBs = append(readDBs, readDB)
    }

    // 创建读写分离的DB实例
    db := &DB{
        write: writeDB,
        reads: readDBs,
    }

    return db, nil
}

type DB struct {
    write *gorm.DB
    reads []*gorm.DB
}

func (db *DB) Write() *gorm.DB {
    return db.write
}

func (db *DB) Read() *gorm.DB {
    if len(db.reads) == 0 {
        return db.write
    }

    // 简单的轮询负载均衡
    index := time.Now().Unix() % int64(len(db.reads))
    return db.reads[index]
}

// 批量插入优化
func BatchInsert(db *gorm.DB, models interface{}, batchSize int) error {
    // 使用事务
    tx := db.Begin()
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
        }
    }()

    // 分批插入
    sliceValue := reflect.ValueOf(models)
    if sliceValue.Kind() != reflect.Slice {
        return fmt.Errorf("models must be a slice")
    }

    for i := 0; i < sliceValue.Len(); i += batchSize {
        end := i + batchSize
        if end > sliceValue.Len() {
            end = sliceValue.Len()
        }

        batch := sliceValue.Slice(i, end).Interface()
        if err := tx.Create(batch).Error; err != nil {
            tx.Rollback()
            return err
        }
    }

    return tx.Commit().Error
}
```

### 缓存优化
```go
// internal/infrastructure/cache/cache_manager.go
package cache

import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
    "github.com/patrickmn/go-cache"
)

// 多级缓存管理器
type CacheManager struct {
    redis    *redis.Client
    local    *cache.Cache
    defaultTTL time.Duration
}

func NewCacheManager(redisClient *redis.Client, defaultTTL time.Duration) *CacheManager {
    return &CacheManager{
        redis:    redisClient,
        local:    cache.New(defaultTTL, 10*defaultTTL),
        defaultTTL: defaultTTL,
    }
}

// 获取缓存数据
func (cm *CacheManager) Get(ctx context.Context, key string, dest interface{}) error {
    // 先从本地缓存获取
    if data, found := cm.local.Get(key); found {
        return json.Unmarshal(data.([]byte), dest)
    }

    // 从Redis获取
    data, err := cm.redis.Get(ctx, key).Bytes()
    if err == redis.Nil {
        return ErrCacheNotFound
    }
    if err != nil {
        return err
    }

    // 设置到本地缓存
    cm.local.Set(key, data, cm.defaultTTL)

    return json.Unmarshal(data, dest)
}

// 设置缓存数据
func (cm *CacheManager) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
    // 序列化数据
    data, err := json.Marshal(value)
    if err != nil {
        return err
    }

    // 设置到本地缓存
    if ttl == 0 {
        ttl = cm.defaultTTL
    }
    cm.local.Set(key, data, ttl)

    // 设置到Redis
    return cm.redis.Set(ctx, key, data, ttl).Err()
}

// 删除缓存数据
func (cm *CacheManager) Delete(ctx context.Context, key string) error {
    // 从本地缓存删除
    cm.local.Delete(key)

    // 从Redis删除
    return cm.redis.Del(ctx, key).Err()
}

// 批量获取缓存数据
func (cm *CacheManager) MGet(ctx context.Context, keys []string) (map[string]interface{}, error) {
    results := make(map[string]interface{})
    var redisKeys []string
    var redisIndexMap []int

    // 先从本地缓存获取
    for i, key := range keys {
        if data, found := cm.local.Get(key); found {
            var value interface{}
            if err := json.Unmarshal(data.([]byte), &value); err == nil {
                results[key] = value
            }
        } else {
            redisKeys = append(redisKeys, key)
            redisIndexMap = append(redisIndexMap, i)
        }
    }

    // 从Redis批量获取
    if len(redisKeys) > 0 {
        redisResults, err := cm.redis.MGet(ctx, redisKeys...).Result()
        if err != nil {
            return nil, err
        }

        for i, result := range redisResults {
            if result != nil {
                key := redisKeys[i]
                data := []byte(result.(string))

                // 设置到本地缓存
                cm.local.Set(key, data, cm.defaultTTL)

                // 解析结果
                var value interface{}
                if err := json.Unmarshal(data, &value); err == nil {
                    results[key] = value
                }
            }
        }
    }

    return results, nil
}

// 缓存预热
func (cm *CacheManager) WarmUp(ctx context.Context, keys []string, dataGetter func(string) (interface{}, error)) error {
    pipe := cm.redis.Pipeline()

    for _, key := range keys {
        // 检查是否已存在
        exists, err := cm.redis.Exists(ctx, key).Result()
        if err != nil {
            continue
        }

        if exists == 0 {
            // 获取数据
            value, err := dataGetter(key)
            if err != nil {
                continue
            }

            // 序列化数据
            data, err := json.Marshal(value)
            if err != nil {
                continue
            }

            // 异步设置缓存
            pipe.Set(ctx, key, data, cm.defaultTTL)
        }
    }

    // 执行批量操作
    _, err := pipe.Exec(ctx)
    return err
}

// 缓存穿透防护
func (cm *CacheManager) GetWithPenetrationProtection(ctx context.Context, key string, dest interface{}, dataGetter func() (interface{}, error)) error {
    // 尝试从缓存获取
    err := cm.Get(ctx, key, dest)
    if err == nil {
        return nil
    }

    if err != ErrCacheNotFound {
        return err
    }

    // 使用分布式锁防止缓存穿透
    lockKey := fmt.Sprintf("lock:%s", key)
    lockValue := fmt.Sprintf("%d", time.Now().Unix())

    // 尝试获取锁
    acquired, err := cm.redis.SetNX(ctx, lockKey, lockValue, 10*time.Second).Result()
    if err != nil {
        return err
    }

    if acquired {
        // 获取到锁，从数据源获取数据
        value, err := dataGetter()
        if err != nil {
            // 释放锁
            cm.redis.Del(ctx, lockKey)
            return err
        }

        // 设置缓存
        if err := cm.Set(ctx, key, value, cm.defaultTTL); err != nil {
            // 释放锁
            cm.redis.Del(ctx, lockKey)
            return err
        }

        // 释放锁
        cm.redis.Del(ctx, lockKey)

        // 返回数据
        return json.NewEncoder(dest).Encode(value)
    } else {
        // 未获取到锁，等待并重试
        time.Sleep(100 * time.Millisecond)
        return cm.Get(ctx, key, dest)
    }
}
```

### HTTP优化
```go
// internal/infrastructure/http/optimized_server.go
package http

import (
    "context"
    "net"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
)

// 创建优化的HTTP服务器
func CreateOptimizedServer(handler http.Handler) *http.Server {
    return &http.Server{
        Addr:         ":8080",
        Handler:      handler,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
        MaxHeaderBytes: 1 << 20, // 1MB
    }
}

// 创建优化的Gin引擎
func CreateOptimizedGinEngine() *gin.Engine {
    gin.SetMode(gin.ReleaseMode)

    r := gin.New()

    // 添加中间件
    r.Use(gin.Recovery())
    r.Use(CORS())
    r.Use(Compression())
    r.Use(RequestTimeout(30 * time.Second))
    r.Use(SecurityHeaders())

    return r
}

// 压缩中间件
func Compression() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Writer.Header().Set("Content-Encoding", "gzip")
        c.Next()
    }
}

// CORS中间件
func CORS() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
        c.Header("Access-Control-Allow-Credentials", "true")

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }

        c.Next()
    }
}

// 请求超时中间件
func RequestTimeout(timeout time.Duration) gin.HandlerFunc {
    return func(c *gin.Context) {
        ctx, cancel := context.WithTimeout(c.Request.Context(), timeout)
        defer cancel()

        c.Request = c.Request.WithContext(ctx)

        done := make(chan bool)
        go func() {
            c.Next()
            done <- true
        }()

        select {
        case <-done:
            return
        case <-ctx.Done():
            c.AbortWithStatusJSON(http.StatusRequestTimeout, gin.H{
                "error": "Request timeout",
            })
            return
        }
    }
}

// 安全头中间件
func SecurityHeaders() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Referrer-Policy", "strict-origin-when-cross-origin")
        c.Header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';")

        c.Next()
    }
}

// 连接数限制
func ConnectionLimit(maxConnections int) gin.HandlerFunc {
    connections := make(chan struct{}, maxConnections)

    return func(c *gin.Context) {
        select {
        case connections <- struct{}{}:
            defer func() { <-connections }()
            c.Next()
        default:
            c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
                "error": "Too many connections",
            })
            return
        }
    }
}

// 静态文件优化
func StaticFileOptimization() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 设置缓存头
        c.Header("Cache-Control", "public, max-age=3600")
        c.Header("ETag", generateETag(c.Request.URL.Path))

        // 检查If-None-Match
        if match := c.GetHeader("If-None-Match"); match != "" && match == generateETag(c.Request.URL.Path) {
            c.AbortWithStatus(http.StatusNotModified)
            return
        }

        c.Next()
    }
}

func generateETag(path string) string {
    return `"` + path + `"`
}
```

## 监控告警

### Prometheus指标
```go
// internal/metrics/metrics.go
package metrics

import (
    "strconv"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // HTTP请求指标
   HTTPRequestDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Help:    "HTTP request duration in seconds",
        Buckets: prometheus.DefBuckets,
    }, []string{"method", "endpoint", "status_code"})

    HTTPRequestsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total number of HTTP requests",
    }, []string{"method", "endpoint", "status_code"})

    // 数据库指标
    DatabaseOperationsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "database_operations_total",
        Help: "Total number of database operations",
    }, []string{"operation", "table"})

    DatabaseOperationDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name:    "database_operation_duration_seconds",
        Help:    "Database operation duration in seconds",
        Buckets: []float64{0.001, 0.01, 0.1, 1, 10},
    }, []string{"operation", "table"})

    // 缓存指标
    CacheOperationsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "cache_operations_total",
        Help: "Total number of cache operations",
    }, []string{"operation", "cache_type", "status"})

    CacheHitRatio = promauto.NewGaugeVec(prometheus.GaugeOpts{
        Name: "cache_hit_ratio",
        Help: "Cache hit ratio",
    }, []string{"cache_type"})

    // 业务指标
    OrdersTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "orders_total",
        Help: "Total number of orders",
    }, []string{"status"})

    OrderAmountTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "order_amount_total",
        Help: "Total order amount",
    }, []string{"currency"})

    PaymentOperationsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "payment_operations_total",
        Help: "Total number of payment operations",
    }, []string{"method", "status"})

    // 系统指标
    Goroutines = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "goroutines",
        Help: "Number of goroutines",
    })

    MemoryUsage = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "memory_usage_bytes",
        Help: "Memory usage in bytes",
    })
)

// 记录HTTP请求指标
func RecordHTTPRequest(method, endpoint string, statusCode int, duration time.Duration) {
    HTTPRequestDuration.WithLabelValues(method, endpoint, strconv.Itoa(statusCode)).Observe(duration.Seconds())
    HTTPRequestsTotal.WithLabelValues(method, endpoint, strconv.Itoa(statusCode)).Inc()
}

// 记录数据库操作指标
func RecordDatabaseOperation(operation, table string, duration time.Duration) {
    DatabaseOperationsTotal.WithLabelValues(operation, table).Inc()
    DatabaseOperationDuration.WithLabelValues(operation, table).Observe(duration.Seconds())
}

// 记录缓存操作指标
func RecordCacheOperation(operation, cacheType, status string) {
    CacheOperationsTotal.WithLabelValues(operation, cacheType, status).Inc()
}

// 记录订单指标
func RecordOrder(status string, amount float64) {
    OrdersTotal.WithLabelValues(status).Inc()
    OrderAmountTotal.WithLabelValues("CNY").Add(amount)
}

// 记录支付指标
func RecordPayment(method, status string) {
    PaymentOperationsTotal.WithLabelValues(method, status).Inc()
}

// 更新系统指标
func UpdateSystemMetrics(goroutines int, memoryUsage uint64) {
    Goroutines.Set(float64(goroutines))
    MemoryUsage.Set(float64(memoryUsage))
}
```

### 监控中间件
```go
// internal/middleware/metrics.go
package middleware

import (
    "runtime"
    "strconv"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/yourproject/internal/metrics"
)

func Metrics() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        // 处理请求
        c.Next()

        // 记录指标
        duration := time.Since(start)
        statusCode := c.Writer.Status()

        metrics.RecordHTTPRequest(
            c.Request.Method,
            c.Request.URL.Path,
            statusCode,
            duration,
        )

        // 更新系统指标
        var m runtime.MemStats
        runtime.ReadMemStats(&m)

        metrics.UpdateSystemMetrics(
            runtime.NumGoroutine(),
            m.Alloc,
        )
    }
}
```

### 告警规则
```yaml
# deployments/prometheus/alerts.yml
groups:
- name: ecommerce-api
  rules:
  # 高错误率告警
  - alert: HighErrorRate
    expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }} for 5 minutes"

  # 响应时间过长告警
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }}s"

  # 数据库连接池告警
  - alert: DatabaseConnectionPoolHigh
    expr: rate(database_operations_total[5m]) > 100
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connection pool usage"
      description: "Database operations rate is {{ $value }} ops/s"

  # 缓存命中率低告警
  - alert: LowCacheHitRatio
    expr: cache_hit_ratio < 0.8
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Low cache hit ratio"
      description: "Cache hit ratio is {{ $value | humanizePercentage }}"

  # 系统资源告警
  - alert: HighMemoryUsage
    expr: memory_usage_bytes / 1024 / 1024 / 1024 > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }}GB"

  - alert: HighGoroutineCount
    expr: goroutines > 1000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High goroutine count"
      description: "Goroutine count is {{ $value }}"
```

### 健康检查
```go
// internal/health/health.go
package health

import (
    "context"
    "database/sql"
    "net/http"
    "sync"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"

    "github.com/yourproject/internal/infrastructure/database"
    "github.com/yourproject/internal/infrastructure/cache"
)

type HealthChecker struct {
    db    *sql.DB
    redis *redis.Client
}

type HealthStatus struct {
    Status   string                    `json:"status"`
    Services map[string]ServiceHealth  `json:"services"`
    Timestamp time.Time                `json:"timestamp"`
}

type ServiceHealth struct {
    Status    string    `json:"status"`
    Message   string    `json:"message,omitempty"`
    Timestamp time.Time `json:"timestamp"`
}

func NewHealthChecker(db *sql.DB, redis *redis.Client) *HealthChecker {
    return &HealthChecker{
        db:    db,
        redis: redis,
    }
}

func (h *HealthChecker) CheckHealth() HealthStatus {
    status := HealthStatus{
        Status:   "healthy",
        Services: make(map[string]ServiceHealth),
        Timestamp: time.Now(),
    }

    var wg sync.WaitGroup
    var mu sync.Mutex

    // 检查数据库
    wg.Add(1)
    go func() {
        defer wg.Done()

        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()

        err := h.db.PingContext(ctx)
        if err != nil {
            mu.Lock()
            status.Status = "unhealthy"
            status.Services["database"] = ServiceHealth{
                Status:    "unhealthy",
                Message:   err.Error(),
                Timestamp: time.Now(),
            }
            mu.Unlock()
        } else {
            mu.Lock()
            status.Services["database"] = ServiceHealth{
                Status:    "healthy",
                Timestamp: time.Now(),
            }
            mu.Unlock()
        }
    }()

    // 检查Redis
    wg.Add(1)
    go func() {
        defer wg.Done()

        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()

        _, err := h.redis.Ping(ctx).Result()
        if err != nil {
            mu.Lock()
            status.Status = "unhealthy"
            status.Services["redis"] = ServiceHealth{
                Status:    "unhealthy",
                Message:   err.Error(),
                Timestamp: time.Now(),
            }
            mu.Unlock()
        } else {
            mu.Lock()
            status.Services["redis"] = ServiceHealth{
                Status:    "healthy",
                Timestamp: time.Now(),
            }
            mu.Unlock()
        }
    }()

    wg.Wait()

    return status
}

func (h *HealthChecker) HealthHandler(c *gin.Context) {
    status := h.CheckHealth()

    if status.Status == "healthy" {
        c.JSON(http.StatusOK, status)
    } else {
        c.JSON(http.StatusServiceUnavailable, status)
    }
}

func (h *HealthChecker) ReadyHandler(c *gin.Context) {
    status := h.CheckHealth()

    // 就绪检查可能包含更严格的条件
    if status.Status == "healthy" {
        c.JSON(http.StatusOK, status)
    } else {
        c.JSON(http.StatusServiceUnavailable, status)
    }
}

func (h *HealthChecker) LiveHandler(c *gin.Context) {
    // 存活检查通常只是简单检查
    c.JSON(http.StatusOK, HealthStatus{
        Status:    "alive",
        Timestamp: time.Now(),
    })
}
```

## 总结

这个完整的Gin实战项目文档涵盖了构建生产级电商后端系统的所有关键方面：

1. **项目架构**：采用DDD分层架构，清晰的模块划分，便于维护和扩展

2. **核心功能**：完整的用户管理、商品管理、订单处理、支付集成等电商核心功能

3. **数据库设计**：合理的表结构设计，支持事务处理，优化查询性能

4. **API设计**：RESTful API设计，清晰的接口定义，完整的参数验证

5. **中间件实现**：JWT认证、权限控制、限流、日志等完整的中间件体系

6. **测试策略**：单元测试、集成测试、性能测试，确保代码质量

7. **部署配置**：Docker、Kubernetes、CI/CD，支持自动化部署

8. **性能优化**：数据库连接池、多级缓存、HTTP服务器优化

9. **监控告警**：Prometheus指标收集、告警规则、健康检查

通过这个项目，您可以学习到如何使用Gin框架构建完整的Web应用，并掌握生产环境中的各种最佳实践。