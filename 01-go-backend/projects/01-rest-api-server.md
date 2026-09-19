# REST API 服务器实战项目

> **阅读准备**：先通过下方 CLI → HTTP 桥接，再学习 Gin 路由；进入正文数据库阶段前补齐 GORM 基础。

## 从标准库首项目走到 Gin

完成[标准库 TODO CLI](./00-stdlib-todo-cli.md)后，先保留其 `Store` 的输入和错误语义，在独立练习目录中完成一层 HTTP 入口。本段是桥接练习规格，需自行实现并在目标环境执行验收；不把后文的完整服务器结构视为此阶段已经交付的代码。

1. **前置**：CLI 的 `go test ./...` 通过，能解释空标题为何失败、`List` 为什么返回副本。阅读[并发基础](../basics/07-concurrency-basics.md)与 [net/http](../reference/library-guides/03-net-http.md)，明确 HTTP 请求可能并发访问同一个 Store。
2. **产物**：增加 HTTP handler 与 `httptest` 测试，先只实现 `POST /todos` 和 `GET /todos`；Store 由服务共享并保护读写，不能在每次请求内重新创建，也不能无锁复用 CLI 的切片存储。POST 的 JSON 标题沿用原校验，成功返回 201 与 ID，空标题或损坏 JSON 返回 400。
3. **验收**：在同一服务实例创建后，列表包含刚返回的 ID；失败请求前后列表不变；保存 `go test ./...` 的结果，并在支持 race detector 的本地工具链执行 `go test -race ./...` 检查并发读写。此阶段重启清空数据是预期。
4. **失败回查**：创建后列表为空，查 Store 生命周期；非法输入仍写入，查解码与 `Store.Add` 的先后顺序；并发检查失败，回到锁的覆盖范围和 `List` 副本。HTTP 状态不符则回到 handler 的错误映射，不要修改已经通过的业务规则来迁就响应。
5. **下一步**：阅读 [Gin 基础](../frameworks/01-gin-framework-basics.md)，把上述两个 handler 换成 Gin 路由并重跑相同契约测试；再阅读 [GORM](../frameworks/03-gorm-orm-complete.md)，进入本文正文的数据库阶段。正文的用户、商品、认证属于后续扩展，逐项新增验收，不要求一次替换 CLI 全部能力。

## 分阶段练习与验收

**最小阶段**：只完成一类资源的创建与查询，再补修改和删除。

**验收结果**：合法请求能创建并取回同一 ID；无效输入返回明确错误，不写入记录。

**扩展顺序**：先用内存版验证 HTTP 契约，再接数据库；鉴权与部署分阶段进行。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

## 📚 概述

本项目将指导你构建一个完整的REST API服务器，使用Go和Gin框架。通过实际项目开发，你将掌握Go Web开发的核心技能。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `projects/practical-projects` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#rest-api` `#实战项目` `#gin框架` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

### 🎯 项目目标
- 构建高性能REST API服务器
- 掌握Gin框架的使用
- 实现数据库集成和ORM
- 学会中间件和认证
- 理解API设计和最佳实践

### 🛠️ 技术栈
- **框架**: Gin Framework
- **数据库**: PostgreSQL
- **ORM**: GORM
- **认证**: JWT
- **配置**: Viper
- **日志**: Zap
- **测试**: Go Test

## 🏗️ 项目结构

```
rest-api-server/
├── cmd/
│   └── server/
│       └── main.go              # 应用入口
├── internal/
│   ├── config/
│   │   └── config.go            # 配置管理
│   ├── handlers/
│   │   ├── user_handler.go     # 用户处理器
│   │   ├── product_handler.go  # 产品处理器
│   │   └── auth_handler.go     # 认证处理器
│   ├── models/
│   │   ├── user.go              # 用户模型
│   │   ├── product.go           # 产品模型
│   │   └── database.go          # 数据库连接
│   ├── middleware/
│   │   ├── auth_middleware.go   # 认证中间件
│   │   ├── cors_middleware.go   # CORS中间件
│   │   └── logging_middleware.go # 日志中间件
│   ├── services/
│   │   ├── user_service.go      # 用户服务
│   │   ├── product_service.go   # 产品服务
│   │   └── auth_service.go      # 认证服务
│   └── utils/
│       ├── response.go          # 响应工具
│       └── validator.go         # 验证工具
├── pkg/
│   ├── logger/
│   │   └── logger.go            # 日志包
│   └── database/
│       └── database.go          # 数据库包
├── api/
│   └── docs/
│       └── swagger.json         # API文档
├── migrations/
│   └── 001_initial_schema.sql   # 数据库迁移
├── tests/
│   ├── integration/
│   └── unit/
├── configs/
│   ├── config.yaml              # 配置文件
│   └── config.example.yaml     # 配置示例
├── go.mod
├── go.sum
├── Makefile
├── Dockerfile
└── README.md
```

## 🚀 实现步骤

### 步骤1: 项目初始化

#### 创建项目结构
```bash
# 创建项目目录
mkdir rest-api-server
cd rest-api-server

# 初始化Go模块
go mod init github.com/your-username/rest-api-server

# 创建目录结构
mkdir -p cmd/server internal/{config,handlers,models,middleware,services,utils} pkg/{logger,database} api/docs migrations tests/{integration,unit} configs
```

#### 安装依赖
```bash
# 安装Gin框架
go get -u github.com/gin-gonic/gin

# 安装GORM和PostgreSQL驱动
go get -u gorm.io/gorm
go get -u gorm.io/driver/postgres

# 安装JWT库
go get -u github.com/golang-jwt/jwt/v5

# 安装配置库
go get -u github.com/spf13/viper

# 安装日志库
go get -u go.uber.org/zap

# 安装验证库
go get -u github.com/go-playground/validator/v10
```

### 步骤2: 配置管理

#### 创建配置结构
```go
// internal/config/config.go
package config

import (
    "strings"

    "github.com/spf13/viper"
)

type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    JWT      JWTConfig      `mapstructure:"jwt"`
    Logger   LoggerConfig   `mapstructure:"logger"`
}

type ServerConfig struct {
    Host         string `mapstructure:"host"`
    Port         int    `mapstructure:"port"`
    Mode         string `mapstructure:"mode"`
    ReadTimeout  int    `mapstructure:"read_timeout"`
    WriteTimeout int    `mapstructure:"write_timeout"`
}

type DatabaseConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    User     string `mapstructure:"user"`
    Password string `mapstructure:"password"`
    DBName   string `mapstructure:"dbname"`
    SSLMode  string `mapstructure:"sslmode"`
}

type JWTConfig struct {
    SecretKey string `mapstructure:"secret_key"`
    ExpiresIn int   `mapstructure:"expires_in"`
}

type LoggerConfig struct {
    Level  string `mapstructure:"level"`
    Format string `mapstructure:"format"`
}

func LoadConfig(configPath string) (*Config, error) {
    viper.SetConfigFile(configPath)
    viper.AutomaticEnv()
    // 关键：让 DB_HOST、SERVER_PORT 等环境变量能覆盖
    // database.host、server.port 等配置项（点号映射为下划线）
    viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

    if err := viper.ReadInConfig(); err != nil {
        return nil, err
    }

    var config Config
    if err := viper.Unmarshal(&config); err != nil {
        return nil, err
    }

    return &config, nil
}
```

#### 创建配置文件
```yaml
# configs/config.yaml
server:
  host: "0.0.0.0"
  port: 8080
  mode: "debug"  # "release" 时 gin.SetMode(gin.ReleaseMode)
  read_timeout: 30
  write_timeout: 30

database:
  host: "localhost"
  port: 5432
  user: "postgres"
  password: "password"
  dbname: "restapi"
  sslmode: "disable"

jwt:
  secret_key: "your-secret-key-here"
  expires_in: 3600

logger:
  level: "info"
  format: "json"
```

### 步骤3: 数据库模型

#### 用户模型
```go
// internal/models/user.go
package models

import (
    "time"
    "golang.org/x/crypto/bcrypt"
    "gorm.io/gorm"
)

type User struct {
    ID        uint           `gorm:"primaryKey" json:"id"`
    Username  string         `gorm:"uniqueIndex;not null" json:"username"`
    Email     string         `gorm:"uniqueIndex;not null" json:"email"`
    Password  string         `gorm:"not null" json:"-"`
    FirstName string         `gorm:"size:100" json:"first_name"`
    LastName  string         `gorm:"size:100" json:"last_name"`
    IsActive  bool           `gorm:"default:true" json:"is_active"`
    CreatedAt time.Time      `json:"created_at"`
    UpdatedAt time.Time      `json:"updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

type UserResponse struct {
    ID        uint      `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    FirstName string    `json:"first_name"`
    LastName  string    `json:"last_name"`
    IsActive  bool      `json:"is_active"`
    CreatedAt time.Time `json:"created_at"`
}

type CreateUserRequest struct {
    Username  string `json:"username" binding:"required,min=3,max=50"`
    Email     string `json:"email" binding:"required,email"`
    Password  string `json:"password" binding:"required,min=6"`
    FirstName string `json:"first_name" binding:"required,min=1,max=100"`
    LastName  string `json:"last_name" binding:"required,min=1,max=100"`
}

type UpdateUserRequest struct {
    FirstName string `json:"first_name" binding:"required,min=1,max=100"`
    LastName  string `json:"last_name" binding:"required,min=1,max=100"`
}

type LoginRequest struct {
    Username string `json:"username" binding:"required"`
    Password string `json:"password" binding:"required"`
}

// HashPassword hashes the password
func (u *User) HashPassword() error {
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(u.Password), bcrypt.DefaultCost)
    if err != nil {
        return err
    }
    u.Password = string(hashedPassword)
    return nil
}

// CheckPassword checks if the provided password is correct
func (u *User) CheckPassword(password string) error {
    return bcrypt.CompareHashAndPassword([]byte(u.Password), []byte(password))
}

// ToResponse converts User to UserResponse
func (u *User) ToResponse() UserResponse {
    return UserResponse{
        ID:        u.ID,
        Username:  u.Username,
        Email:     u.Email,
        FirstName: u.FirstName,
        LastName:  u.LastName,
        IsActive:  u.IsActive,
        CreatedAt: u.CreatedAt,
    }
}
```

#### 产品模型
```go
// internal/models/product.go
package models

import (
    "time"
    "gorm.io/gorm"
)

type Product struct {
    ID          uint           `gorm:"primaryKey" json:"id"`
    Name        string         `gorm:"not null;size:200" json:"name"`
    Description string         `gorm:"type:text" json:"description"`
    Price       float64        `gorm:"not null;type:decimal(10,2)" json:"price"`
    SKU         string         `gorm:"uniqueIndex;not null;size:100" json:"sku"`
    Stock       int            `gorm:"default:0" json:"stock"`
    CategoryID  uint           `gorm:"not null" json:"category_id"`
    Category    Category       `gorm:"foreignKey:CategoryID" json:"category,omitempty"`
    IsActive    bool           `gorm:"default:true" json:"is_active"`
    CreatedAt   time.Time      `json:"created_at"`
    UpdatedAt   time.Time      `json:"updated_at"`
    DeletedAt   gorm.DeletedAt `gorm:"index" json:"-"`
}

type Category struct {
    ID          uint           `gorm:"primaryKey" json:"id"`
    Name        string         `gorm:"not null;size:100" json:"name"`
    Description string         `gorm:"type:text" json:"description"`
    IsActive    bool           `gorm:"default:true" json:"is_active"`
    CreatedAt   time.Time      `json:"created_at"`
    UpdatedAt   time.Time      `json:"updated_at"`
    DeletedAt   gorm.DeletedAt `gorm:"index" json:"-"`
}

type ProductResponse struct {
    ID          uint      `json:"id"`
    Name        string    `json:"name"`
    Description string    `json:"description"`
    Price       float64   `json:"price"`
    SKU         string    `json:"sku"`
    Stock       int       `json:"stock"`
    CategoryID  uint      `json:"category_id"`
    Category    *Category `json:"category,omitempty"`
    IsActive    bool      `json:"is_active"`
    CreatedAt   time.Time `json:"created_at"`
}

type CreateProductRequest struct {
    Name        string  `json:"name" binding:"required,min=1,max=200"`
    Description string  `json:"description"`
    Price       float64 `json:"price" binding:"required,min=0"`
    SKU         string  `json:"sku" binding:"required,min=1,max=100"`
    Stock       int     `json:"stock" binding:"required,min=0"`
    CategoryID  uint    `json:"category_id" binding:"required"`
}

type UpdateProductRequest struct {
    Name        string  `json:"name" binding:"required,min=1,max=200"`
    Description string  `json:"description"`
    Price       float64 `json:"price" binding:"required,min=0"`
    SKU         string  `json:"sku" binding:"required,min=1,max=100"`
    Stock       int     `json:"stock" binding:"required,min=0"`
    CategoryID  uint    `json:"category_id" binding:"required"`
}

// ToResponse converts Product to ProductResponse
func (p *Product) ToResponse() ProductResponse {
    return ProductResponse{
        ID:          p.ID,
        Name:        p.Name,
        Description: p.Description,
        Price:       p.Price,
        SKU:         p.SKU,
        Stock:       p.Stock,
        CategoryID:  p.CategoryID,
        Category:    &p.Category,
        IsActive:    p.IsActive,
        CreatedAt:   p.CreatedAt,
    }
}
```

#### 数据库连接
```go
// internal/models/database.go
package models

import (
    "log"
    "strconv"
    "your-project/internal/config"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

var DB *gorm.DB

func InitDatabase(cfg *config.Config) error {
    dsn := getDatabaseConnectionString(cfg.Database)

    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Info),
    })

    if err != nil {
        return err
    }

    DB = db

    // Auto migrate the schema
    err = autoMigrate(db)
    if err != nil {
        return err
    }

    log.Println("Database connected successfully")
    return nil
}

func getDatabaseConnectionString(dbConfig config.DatabaseConfig) string {
    return "host=" + dbConfig.Host +
        " user=" + dbConfig.User +
        " password=" + dbConfig.Password +
        " dbname=" + dbConfig.DBName +
        " port=" + strconv.Itoa(dbConfig.Port) +
        " sslmode=" + dbConfig.SSLMode +
        " TimeZone=Asia/Shanghai"
}

func autoMigrate(db *gorm.DB) error {
    return db.AutoMigrate(
        &User{},
        &Category{},
        &Product{},
    )
}

func GetDB() *gorm.DB {
    return DB
}
```

### 步骤4: 认证服务

#### JWT服务
```go
// internal/services/auth_service.go
package services

import (
    "errors"
    "time"
    "github.com/golang-jwt/jwt/v5"
    "your-project/internal/config"
    "your-project/internal/models"
)

type AuthService struct {
    config *config.Config
}

func NewAuthService(cfg *config.Config) *AuthService {
    return &AuthService{config: cfg}
}

type Claims struct {
    UserID   uint   `json:"user_id"`
    Username string `json:"username"`
    Email    string `json:"email"`
    jwt.RegisteredClaims
}

func (s *AuthService) GenerateToken(user *models.User) (string, error) {
    expirationTime := time.Now().Add(time.Duration(s.config.JWT.ExpiresIn) * time.Second)

    claims := &Claims{
        UserID:   user.ID,
        Username: user.Username,
        Email:    user.Email,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(expirationTime),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "rest-api-server",
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    tokenString, err := token.SignedString([]byte(s.config.JWT.SecretKey))
    if err != nil {
        return "", err
    }

    return tokenString, nil
}

func (s *AuthService) ValidateToken(tokenString string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        return []byte(s.config.JWT.SecretKey), nil
    })

    if err != nil {
        return nil, err
    }

    if claims, ok := token.Claims.(*Claims); ok && token.Valid {
        return claims, nil
    }

    return nil, errors.New("invalid token")
}
```

#### 用户服务
```go
// internal/services/user_service.go
package services

import (
    "context"
    "errors"
    "your-project/internal/models"
    "gorm.io/gorm"
)

type UserService struct {
    db *gorm.DB
}

func NewUserService(db *gorm.DB) *UserService {
    return &UserService{db: db}
}

// service 方法统一接收 context.Context，并透传给 GORM 的 WithContext，
// 使取消/超时/链路追踪信息能传导到数据库层（对比 db.Create 裸调用）。
func (s *UserService) CreateUser(ctx context.Context, req *models.CreateUserRequest) (*models.User, error) {
    user := &models.User{
        Username:  req.Username,
        Email:     req.Email,
        FirstName: req.FirstName,
        LastName:  req.LastName,
        IsActive:  true,
    }

    if err := user.HashPassword(); err != nil {
        return nil, err
    }

    if err := s.db.WithContext(ctx).Create(user).Error; err != nil {
        return nil, err
    }

    return user, nil
}

func (s *UserService) GetUserByID(ctx context.Context, id uint) (*models.User, error) {
    var user models.User
    if err := s.db.WithContext(ctx).First(&user, id).Error; err != nil {
        return nil, err
    }
    return &user, nil
}

func (s *UserService) GetUserByUsername(ctx context.Context, username string) (*models.User, error) {
    var user models.User
    if err := s.db.WithContext(ctx).Where("username = ?", username).First(&user).Error; err != nil {
        return nil, err
    }
    return &user, nil
}

func (s *UserService) GetUserByEmail(ctx context.Context, email string) (*models.User, error) {
    var user models.User
    if err := s.db.WithContext(ctx).Where("email = ?", email).First(&user).Error; err != nil {
        return nil, err
    }
    return &user, nil
}

func (s *UserService) UpdateUser(ctx context.Context, id uint, req *models.UpdateUserRequest) (*models.User, error) {
    var user models.User
    if err := s.db.WithContext(ctx).First(&user, id).Error; err != nil {
        return nil, err
    }

    user.FirstName = req.FirstName
    user.LastName = req.LastName

    if err := s.db.WithContext(ctx).Save(&user).Error; err != nil {
        return nil, err
    }

    return &user, nil
}

func (s *UserService) DeleteUser(ctx context.Context, id uint) error {
    if err := s.db.WithContext(ctx).Delete(&models.User{}, id).Error; err != nil {
        return err
    }
    return nil
}

func (s *UserService) ListUsers(ctx context.Context, page, limit int) ([]models.User, int64, error) {
    var users []models.User
    var total int64

    offset := (page - 1) * limit

    if err := s.db.WithContext(ctx).Model(&models.User{}).Count(&total).Error; err != nil {
        return nil, 0, err
    }

    if err := s.db.WithContext(ctx).Offset(offset).Limit(limit).Find(&users).Error; err != nil {
        return nil, 0, err
    }

    return users, total, nil
}

func (s *UserService) Login(ctx context.Context, req *models.LoginRequest) (*models.User, error) {
    user, err := s.GetUserByUsername(ctx, req.Username)
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errors.New("user not found")
        }
        return nil, err
    }

    if !user.IsActive {
        return nil, errors.New("user is inactive")
    }

    if err := user.CheckPassword(req.Password); err != nil {
        return nil, errors.New("invalid password")
    }

    return user, nil
}
```

### 步骤5: 中间件

#### 认证中间件
```go
// internal/middleware/auth_middleware.go
package middleware

import (
    "net/http"
    "strings"
    "your-project/internal/services"
    "github.com/gin-gonic/gin"
)

func AuthMiddleware(authService *services.AuthService) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "authorization header required"})
            c.Abort()
            return
        }

        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        if tokenString == authHeader {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "bearer token required"})
            c.Abort()
            return
        }

        claims, err := authService.ValidateToken(tokenString)
        if err != nil {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
            c.Abort()
            return
        }

        c.Set("user_id", claims.UserID)
        c.Set("username", claims.Username)
        c.Set("email", claims.Email)

        c.Next()
    }
}

func GetCurrentUser(c *gin.Context) (uint, string, string) {
    userID, _ := c.Get("user_id")
    username, _ := c.Get("username")
    email, _ := c.Get("email")

    return userID.(uint), username.(string), email.(string)
}
```

#### CORS中间件
```go
// internal/middleware/cors_middleware.go
package middleware

import (
    "github.com/gin-gonic/gin"
)

func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        origin := c.GetHeader("Origin")

        // Access-Control-Allow-Origin: * 与 Allow-Credentials: true 是非法组合，
        // 浏览器会直接拒绝响应。携带凭据时必须回显具体 Origin；
        // 若无需凭据，则改回 "*" 并删除 Credentials 头。
        if origin != "" {
            c.Header("Access-Control-Allow-Origin", origin)
            c.Header("Vary", "Origin") // 防止 CDN/代理缓存了错误的 CORS 头
        }
        c.Header("Access-Control-Allow-Credentials", "true")
        c.Header("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
        c.Header("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }

        c.Next()
    }
}
```

#### 日志中间件
```go
// internal/middleware/logging_middleware.go
package middleware

import (
    "fmt"
    "time"
    "github.com/gin-gonic/gin"
    "go.uber.org/zap"
)

func LoggingMiddleware(logger *zap.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        raw := c.Request.URL.RawQuery

        c.Next()

        latency := time.Since(start)
        clientIP := c.ClientIP()
        method := c.Request.Method
        statusCode := c.Writer.Status()

        if raw != "" {
            path = path + "?" + raw
        }

        logger.Info("HTTP request",
            zap.String("method", method),
            zap.String("path", path),
            zap.String("client_ip", clientIP),
            zap.Int("status_code", statusCode),
            zap.Duration("latency", latency),
        )

        fmt.Printf("[%s] %s %s %d %v\n",
            method,
            path,
            clientIP,
            statusCode,
            latency,
        )
    }
}
```

### 步骤6: 处理器

#### 用户处理器
```go
// internal/handlers/user_handler.go
package handlers

import (
    "net/http"
    "strconv"
    "your-project/internal/models"
    "your-project/internal/services"
    "your-project/internal/utils"
    "github.com/gin-gonic/gin"
)

type UserHandler struct {
    userService *services.UserService
}

func NewUserHandler(userService *services.UserService) *UserHandler {
    return &UserHandler{userService: userService}
}

// @Summary Create a new user
// @Description Create a new user with the provided information
// @Tags users
// @Accept json
// @Produce json
// @Param user body models.CreateUserRequest true "User information"
// @Success 201 {object} models.UserResponse
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users [post]
func (h *UserHandler) CreateUser(c *gin.Context) {
    var req models.CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, utils.ErrorResponse{
            Error:   "Invalid request body",
            Details: err.Error(),
        })
        return
    }

    user, err := h.userService.CreateUser(c.Request.Context(), &req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, utils.ErrorResponse{
            Error:   "Failed to create user",
            Details: err.Error(),
        })
        return
    }

    c.JSON(http.StatusCreated, utils.SuccessResponse{
        Message: "User created successfully",
        Data:    user.ToResponse(),
    })
}

// @Summary Get user by ID
// @Description Get user information by ID
// @Tags users
// @Accept json
// @Produce json
// @Param id path int true "User ID"
// @Success 200 {object} models.UserResponse
// @Failure 404 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users/{id} [get]
func (h *UserHandler) GetUser(c *gin.Context) {
    idStr := c.Param("id")
    id, err := strconv.ParseUint(idStr, 10, 32)
    if err != nil {
        c.JSON(http.StatusBadRequest, utils.ErrorResponse{
            Error:   "Invalid user ID",
            Details: err.Error(),
        })
        return
    }

    user, err := h.userService.GetUserByID(c.Request.Context(), uint(id))
    if err != nil {
        c.JSON(http.StatusNotFound, utils.ErrorResponse{
            Error:   "User not found",
            Details: err.Error(),
        })
        return
    }

    c.JSON(http.StatusOK, utils.SuccessResponse{
        Message: "User retrieved successfully",
        Data:    user.ToResponse(),
    })
}

// @Summary Update user
// @Description Update user information
// @Tags users
// @Accept json
// @Produce json
// @Param id path int true "User ID"
// @Param user body models.UpdateUserRequest true "User information"
// @Success 200 {object} models.UserResponse
// @Failure 400 {object} utils.ErrorResponse
// @Failure 404 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users/{id} [put]
func (h *UserHandler) UpdateUser(c *gin.Context) {
    idStr := c.Param("id")
    id, err := strconv.ParseUint(idStr, 10, 32)
    if err != nil {
        c.JSON(http.StatusBadRequest, utils.ErrorResponse{
            Error:   "Invalid user ID",
            Details: err.Error(),
        })
        return
    }

    var req models.UpdateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, utils.ErrorResponse{
            Error:   "Invalid request body",
            Details: err.Error(),
        })
        return
    }

    user, err := h.userService.UpdateUser(c.Request.Context(), uint(id), &req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, utils.ErrorResponse{
            Error:   "Failed to update user",
            Details: err.Error(),
        })
        return
    }

    c.JSON(http.StatusOK, utils.SuccessResponse{
        Message: "User updated successfully",
        Data:    user.ToResponse(),
    })
}

// @Summary Delete user
// @Description Delete a user by ID
// @Tags users
// @Accept json
// @Produce json
// @Param id path int true "User ID"
// @Success 200 {object} utils.SuccessResponse
// @Failure 400 {object} utils.ErrorResponse
// @Failure 404 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users/{id} [delete]
func (h *UserHandler) DeleteUser(c *gin.Context) {
    idStr := c.Param("id")
    id, err := strconv.ParseUint(idStr, 10, 32)
    if err != nil {
        c.JSON(http.StatusBadRequest, utils.ErrorResponse{
            Error:   "Invalid user ID",
            Details: err.Error(),
        })
        return
    }

    if err := h.userService.DeleteUser(c.Request.Context(), uint(id)); err != nil {
        c.JSON(http.StatusInternalServerError, utils.ErrorResponse{
            Error:   "Failed to delete user",
            Details: err.Error(),
        })
        return
    }

    c.JSON(http.StatusOK, utils.SuccessResponse{
        Message: "User deleted successfully",
    })
}

// @Summary List users
// @Description Get a paginated list of users
// @Tags users
// @Accept json
// @Produce json
// @Param page query int false "Page number" default(1)
// @Param limit query int false "Items per page" default(10)
// @Success 200 {object} utils.PaginatedResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users [get]
func (h *UserHandler) ListUsers(c *gin.Context) {
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))

    if page < 1 {
        page = 1
    }
    if limit < 1 || limit > 100 {
        limit = 10
    }

    users, total, err := h.userService.ListUsers(c.Request.Context(), page, limit)
    if err != nil {
        c.JSON(http.StatusInternalServerError, utils.ErrorResponse{
            Error:   "Failed to list users",
            Details: err.Error(),
        })
        return
    }

    var userResponses []models.UserResponse
    for _, user := range users {
        userResponses = append(userResponses, user.ToResponse())
    }

    c.JSON(http.StatusOK, utils.PaginatedResponse{
        Message: "Users retrieved successfully",
        Data:    userResponses,
        Meta: utils.Meta{
            Total:    total,
            Page:     page,
            PageSize: limit,
        },
    })
}
```

#### 认证处理器
```go
// internal/handlers/auth_handler.go
package handlers

import (
    "net/http"
    "your-project/internal/middleware"
    "your-project/internal/models"
    "your-project/internal/services"
    "your-project/internal/utils"
    "github.com/gin-gonic/gin"
)

type AuthHandler struct {
    authService  *services.AuthService
    userService  *services.UserService
}

func NewAuthHandler(authService *services.AuthService, userService *services.UserService) *AuthHandler {
    return &AuthHandler{
        authService: authService,
        userService: userService,
    }
}

// @Summary User login
// @Description Authenticate user and return JWT token
// @Tags auth
// @Accept json
// @Produce json
// @Param credentials body models.LoginRequest true "Login credentials"
// @Success 200 {object} map[string]interface{}
// @Failure 400 {object} utils.ErrorResponse
// @Failure 401 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /auth/login [post]
func (h *AuthHandler) Login(c *gin.Context) {
    var req models.LoginRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, utils.ErrorResponse{
            Error:   "Invalid request body",
            Details: err.Error(),
        })
        return
    }

    user, err := h.userService.Login(c.Request.Context(), &req)
    if err != nil {
        c.JSON(http.StatusUnauthorized, utils.ErrorResponse{
            Error:   "Authentication failed",
            Details: err.Error(),
        })
        return
    }

    token, err := h.authService.GenerateToken(user)
    if err != nil {
        c.JSON(http.StatusInternalServerError, utils.ErrorResponse{
            Error:   "Failed to generate token",
            Details: err.Error(),
        })
        return
    }

    c.JSON(http.StatusOK, utils.SuccessResponse{
        Message: "Login successful",
        Data: map[string]interface{}{
            "token": token,
            "user":  user.ToResponse(),
        },
    })
}

// @Summary Get current user
// @Description Get current authenticated user information
// @Tags auth
// @Accept json
// @Produce json
// @Security ApiKeyAuth
// @Success 200 {object} models.UserResponse
// @Failure 401 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /auth/me [get]
func (h *AuthHandler) GetMe(c *gin.Context) {
    userID, _, _ := middleware.GetCurrentUser(c)

    user, err := h.userService.GetUserByID(c.Request.Context(), userID)
    if err != nil {
        c.JSON(http.StatusInternalServerError, utils.ErrorResponse{
            Error:   "Failed to get user",
            Details: err.Error(),
        })
        return
    }

    c.JSON(http.StatusOK, utils.SuccessResponse{
        Message: "User retrieved successfully",
        Data:    user.ToResponse(),
    })
}
```

### 步骤7: 主应用

#### 主应用入口
```go
// cmd/server/main.go
package main

import (
    "context"
    "errors"
    "log"
    "net/http"
    "os/signal"
    "strconv"
    "syscall"
    "time"
    "your-project/internal/config"
    "your-project/internal/handlers"
    "your-project/internal/middleware"
    "your-project/internal/models"
    "your-project/internal/services"
    "github.com/gin-gonic/gin"
    "go.uber.org/zap"
)

func main() {
    // Load configuration
    cfg, err := config.LoadConfig("configs/config.yaml")
    if err != nil {
        log.Fatalf("Failed to load config: %v", err)
    }

    // Initialize database
    if err := models.InitDatabase(cfg); err != nil {
        log.Fatalf("Failed to initialize database: %v", err)
    }

    // Initialize logger
    logger, err := zap.NewProduction()
    if err != nil {
        log.Fatalf("Failed to initialize logger: %v", err)
    }
    defer logger.Sync()

    // Initialize services
    authService := services.NewAuthService(cfg)
    userService := services.NewUserService(models.GetDB())

    // Initialize handlers
    authHandler := handlers.NewAuthHandler(authService, userService)
    userHandler := handlers.NewUserHandler(userService)

    // Setup Gin router
    if cfg.Server.Mode == "production" {
        gin.SetMode(gin.ReleaseMode)
    }

    router := gin.New()

    // Middleware
    router.Use(middleware.CORSMiddleware())
    router.Use(middleware.LoggingMiddleware(logger))
    router.Use(gin.Recovery())

    // Public routes
    public := router.Group("/api/v1")
    {
        auth := public.Group("/auth")
        {
            auth.POST("/login", authHandler.Login)
        }
    }

    // Protected routes
    protected := router.Group("/api/v1")
    protected.Use(middleware.AuthMiddleware(authService))
    {
        auth := protected.Group("/auth")
        {
            auth.GET("/me", authHandler.GetMe)
        }

        users := protected.Group("/users")
        {
            users.POST("", userHandler.CreateUser)
            users.GET("", userHandler.ListUsers)
            users.GET("/:id", userHandler.GetUser)
            users.PUT("/:id", userHandler.UpdateUser)
            users.DELETE("/:id", userHandler.DeleteUser)
        }
    }

    // Health check
    router.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "healthy"})
    })

    // Start server：用 http.Server + signal.NotifyContext + Shutdown 实现优雅关停，
    // 收到 SIGINT/SIGTERM 后先停止接收新请求，等待在途请求完成（最长 10 秒）再退出。
    addr := cfg.Server.Host + ":" + strconv.Itoa(cfg.Server.Port)
    srv := &http.Server{
        Addr:         addr,
        Handler:      router,
        ReadTimeout:  time.Duration(cfg.Server.ReadTimeout) * time.Second,
        WriteTimeout: time.Duration(cfg.Server.WriteTimeout) * time.Second,
    }

    ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    go func() {
        log.Printf("Server starting on %s", addr)
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            log.Fatalf("Failed to start server: %v", err)
        }
    }()

    <-ctx.Done() // 等待 Ctrl+C / SIGTERM
    log.Println("Shutting down server...")

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    if err := srv.Shutdown(shutdownCtx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }
    log.Println("Server exited gracefully")
}
```

### 步骤8: 工具函数

#### 响应工具
```go
// internal/utils/response.go
package utils

import "github.com/gin-gonic/gin"

type SuccessResponse struct {
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

type ErrorResponse struct {
    Error   string `json:"error"`
    Details string `json:"details,omitempty"`
}

type PaginatedResponse struct {
    Message string      `json:"message"`
    Data    interface{} `json:"data"`
    Meta    Meta        `json:"meta"`
}

type Meta struct {
    Total    int64 `json:"total"`
    Page     int   `json:"page"`
    PageSize int   `json:"page_size"`
}

func Success(c *gin.Context, message string, data interface{}) {
    c.JSON(200, SuccessResponse{
        Message: message,
        Data:    data,
    })
}

func Error(c *gin.Context, statusCode int, message string, details string) {
    c.JSON(statusCode, ErrorResponse{
        Error:   message,
        Details: details,
    })
}

func Paginated(c *gin.Context, message string, data interface{}, meta Meta) {
    c.JSON(200, PaginatedResponse{
        Message: message,
        Data:    data,
        Meta:    meta,
    })
}
```

### 步骤9: 测试

#### 集成测试
```go
// tests/integration/auth_test.go
package integration

import (
    "bytes"
    "context"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"
    "your-project/internal/config"
    "your-project/internal/models"
    "your-project/internal/services"
    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

func TestLogin(t *testing.T) {
    // Setup
    cfg, _ := config.LoadConfig("../../../configs/config.yaml")
    if err := models.InitDatabase(cfg); err != nil {
        t.Fatalf("Failed to initialize database: %v", err)
    }

    // Create test user（services.NewUserService 与 CreateUser 均需 context）
    userService := services.NewUserService(models.GetDB())
    if _, err := userService.CreateUser(context.Background(), &models.CreateUserRequest{
        Username:  "testuser",
        Email:     "test@example.com",
        Password:  "password123",
        FirstName: "Test",
        LastName:  "User",
    }); err != nil {
        t.Fatalf("Failed to create test user: %v", err)
    }

    router := setupRouter(cfg)

    // Test login
    loginReq := models.LoginRequest{
        Username: "testuser",
        Password: "password123",
    }

    jsonValue, _ := json.Marshal(loginReq)
    req, _ := http.NewRequest("POST", "/api/v1/auth/login", bytes.NewBuffer(jsonValue))
    req.Header.Set("Content-Type", "application/json")

    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)

    var response map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &response)

    assert.Equal(t, "Login successful", response["message"])
    assert.NotNil(t, response["data"])
}
```

## 📋 部署配置

#### Dockerfile
```dockerfile
# Build stage
FROM golang:1.25-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main cmd/server/main.go

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary from the builder stage
COPY --from=builder /app/main .

# Copy config files
COPY --from=builder /app/configs ./configs

EXPOSE 8080

CMD ["./main"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=restapi
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=restapi
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 📊 API文档

使用Swagger生成API文档：

1. 安装swag工具：
```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

2. 在main.go中添加Swagger注释：
```go
import (
    _ "your-project/docs"
    "github.com/swaggo/files"
    "github.com/swaggo/gin-swagger"
)

// @title REST API Server
// @version 1.0
// @description This is a sample REST API server.
// @termsOfService http://swagger.io/terms/

// @contact.name API Support
// @contact.url http://www.swagger.io/support
// @contact.email support@swagger.io

// @license.name Apache 2.0
// @license.url http://www.apache.org/licenses/LICENSE-2.0.html

// @host localhost:8080
// @BasePath /api/v1
// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name Authorization
```

3. 生成文档：
```bash
swag init -g cmd/server/main.go -o api/docs
```

4. 添加Swagger路由：
```go
router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
```

## 🚀 运行项目

#### 本地开发
```bash
# 安装依赖
go mod tidy

# 创建配置文件
cp configs/config.example.yaml configs/config.yaml

# 运行数据库
docker-compose up -d postgres redis

# 运行应用
go run cmd/server/main.go

# 运行测试
go test ./tests/...
```

#### Docker部署
```bash
# 构建和运行
docker-compose up --build

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

## 📚 学习要点

通过这个项目，你将学到：

1. **Go Web开发基础**
   - Gin框架的使用
   - REST API设计原则
   - 中间件和路由

2. **数据库操作**
   - GORM ORM框架
   - PostgreSQL数据库
   - 数据迁移

3. **认证和授权**
   - JWT token认证
   - 中间件实现
   - 用户权限管理

4. **项目架构**
   - 分层架构设计
   - 依赖注入
   - 服务层模式

5. **测试和部署**
   - 单元测试
   - 集成测试
   - Docker容器化
   - API文档

---

**项目价值**: 这个REST API服务器项目涵盖了现代Go Web开发的核心知识点，是学习Go后端开发的绝佳实践。通过完整的项目开发，你将掌握Go在企业级应用开发中的实际应用。

*最后更新: 2025年9月*

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
