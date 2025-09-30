# Go 代码组织和架构设计 - 从PHP视角理解

## 📚 概述

Go语言的代码组织哲学与PHP有显著不同。Go强调简洁性、明确性和可维护性，通过标准化的项目结构和包管理来实现高质量的代码组织。

### 🎯 学习目标
- 掌握Go的标准项目结构
- 理解包的设计和依赖管理
- 学会分层架构和DDD模式
- 掌握Go特有的代码组织模式
- 熟悉Go与PHP代码组织的差异

## 🔄 Go vs PHP 代码组织对比

### 传统PHP项目结构
```php
// PHP典型的MVC结构
project/
├── app/
│   ├── Controllers/
│   │   ├── UserController.php
│   │   └── ProductController.php
│   ├── Models/
│   │   ├── User.php
│   │   └── Product.php
│   ├── Views/
│   │   ├── user/
│   │   └── product/
│   └── Helpers/
│       └── Utils.php
├── config/
│   └── app.php
├── public/
│   └── index.php
├── vendor/
└── composer.json
```

### Go项目标准结构
```
// Go标准项目结构
project/
├── cmd/
│   ├── server/
│   │   └── main.go          # 应用入口
│   └── worker/
│       └── main.go          # 工作进程入口
├── internal/
│   ├── config/
│   │   └── config.go        # 配置管理
│   ├── handlers/
│   │   └── user_handler.go  # HTTP处理器
│   ├── models/
│   │   └── user.go          # 数据模型
│   ├── services/
│   │   └── user_service.go  # 业务逻辑
│   └── repositories/
│       └── user_repo.go     # 数据访问
├── pkg/
│   ├── database/
│   │   └── database.go      # 可重用的数据库包
│   └── logger/
│       └── logger.go        # 可重用的日志包
├── api/
│   └── proto/               # API定义
├── configs/
│   └── config.yaml          # 配置文件
├── scripts/
│   └── migrate.sh           # 脚本文件
├── go.mod
└── go.sum
```

## 📝 Go 代码组织详解

### 1. 标准项目结构

#### cmd目录
```go
// cmd/server/main.go
package main

import (
    "log"
    "your-project/internal/config"
    "your-project/internal/handlers"
    "your-project/internal/services"
    "your-project/pkg/database"
    "github.com/gin-gonic/gin"
)

func main() {
    // 加载配置
    cfg, err := config.Load("configs/config.yaml")
    if err != nil {
        log.Fatal("Failed to load config:", err)
    }

    // 初始化数据库
    db, err := database.Init(cfg.Database)
    if err != nil {
        log.Fatal("Failed to initialize database:", err)
    }

    // 初始化服务
    userService := services.NewUserService(db)

    // 初始化处理器
    userHandler := handlers.NewUserHandler(userService)

    // 设置路由
    router := gin.Default()
    router.GET("/users/:id", userHandler.GetUser)
    router.POST("/users", userHandler.CreateUser)

    // 启动服务
    log.Fatal(router.Run(":" + cfg.Server.Port))
}
```

#### internal目录
```go
// internal/config/config.go
package config

import (
    "github.com/spf13/viper"
)

type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
}

type ServerConfig struct {
    Port string `mapstructure:"port"`
    Host string `mapstructure:"host"`
}

type DatabaseConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    User     string `mapstructure:"user"`
    Password string `mapstructure:"password"`
    DBName   string `mapstructure:"dbname"`
}

func Load(path string) (*Config, error) {
    viper.SetConfigFile(path)

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

#### pkg目录
```go
// pkg/database/database.go
package database

import (
    "fmt"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

type DatabaseConfig struct {
    Host     string
    Port     int
    User     string
    Password string
    DBName   string
}

func Init(cfg DatabaseConfig) (*gorm.DB, error) {
    dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=disable",
        cfg.Host, cfg.User, cfg.Password, cfg.DBName, cfg.Port)

    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        return nil, err
    }

    return db, nil
}

// pkg/logger/logger.go
package logger

import (
    "os"
    "go.uber.org/zap"
)

func New() *zap.Logger {
    config := zap.Config{
        Level:       zap.NewAtomicLevelAt(zap.InfoLevel),
        Development: false,
        Encoding:    "json",
        OutputPaths: []string{"stdout"},
        EncoderConfig: zapcore.EncoderConfig{
            TimeKey:        "timestamp",
            LevelKey:       "level",
            NameKey:        "logger",
            CallerKey:      "caller",
            MessageKey:     "message",
            StacktraceKey:  "stacktrace",
            LineEnding:     zapcore.DefaultLineEnding,
            EncodeLevel:    zapcore.LowercaseLevelEncoder,
            EncodeTime:     zapcore.ISO8601TimeEncoder,
            EncodeDuration: zapcore.SecondsDurationEncoder,
            EncodeCaller:   zapcore.ShortCallerEncoder,
        },
    }

    logger, err := config.Build()
    if err != nil {
        panic(err)
    }

    return logger
}
```

### 2. 分层架构

#### 三层架构
```go
// internal/handlers/user_handler.go
package handlers

import (
    "net/http"
    "your-project/internal/services"
    "github.com/gin-gonic/gin"
)

type UserHandler struct {
    userService *services.UserService
}

func NewUserHandler(userService *services.UserService) *UserHandler {
    return &UserHandler{
        userService: userService,
    }
}

func (h *UserHandler) GetUser(c *gin.Context) {
    id := c.Param("id")

    user, err := h.userService.GetUserByID(id)
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    c.JSON(http.StatusOK, gin.H{"data": user})
}

func (h *UserHandler) CreateUser(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
        return
    }

    user, err := h.userService.CreateUser(&req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"data": user})
}
```

```go
// internal/services/user_service.go
package services

import (
    "errors"
    "your-project/internal/models"
    "your-project/internal/repositories"
)

type UserService struct {
    userRepo *repositories.UserRepository
}

func NewUserService(userRepo *repositories.UserRepository) *UserService {
    return &UserService{
        userRepo: userRepo,
    }
}

func (s *UserService) GetUserByID(id string) (*models.User, error) {
    user, err := s.userRepo.FindByID(id)
    if err != nil {
        return nil, err
    }
    if user == nil {
        return nil, errors.New("user not found")
    }
    return user, nil
}

func (s *UserService) CreateUser(req *CreateUserRequest) (*models.User, error) {
    // 验证逻辑
    if err := validateUserRequest(req); err != nil {
        return nil, err
    }

    // 创建用户
    user := &models.User{
        Name:  req.Name,
        Email: req.Email,
        Age:   req.Age,
    }

    if err := s.userRepo.Create(user); err != nil {
        return nil, err
    }

    return user, nil
}

func validateUserRequest(req *CreateUserRequest) error {
    if req.Name == "" {
        return errors.New("name is required")
    }
    if req.Email == "" {
        return errors.New("email is required")
    }
    return nil
}
```

```go
// internal/repositories/user_repository.go
package repositories

import (
    "gorm.io/gorm"
    "your-project/internal/models"
)

type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) FindByID(id string) (*models.User, error) {
    var user models.User
    result := r.db.First(&user, "id = ?", id)
    if result.Error != nil {
        return nil, result.Error
    }
    return &user, nil
}

func (r *UserRepository) Create(user *models.User) error {
    return r.db.Create(user).Error
}

func (r *UserRepository) Update(user *models.User) error {
    return r.db.Save(user).Error
}

func (r *UserRepository) Delete(id string) error {
    return r.db.Delete(&models.User{}, "id = ?", id).Error
}

func (r *UserRepository) FindByEmail(email string) (*models.User, error) {
    var user models.User
    result := r.db.First(&user, "email = ?", email)
    if result.Error != nil {
        return nil, result.Error
    }
    return &user, nil
}
```

### 3. 领域驱动设计(DDD)

#### 领域模型
```go
// internal/domain/user/entity.go
package user

import (
    "errors"
    "time"
)

type User struct {
    id        UserID
    name      string
    email     Email
    age       int
    createdAt time.Time
    updatedAt time.Time
}

type UserID string
type Email string

func NewUser(id UserID, name string, email Email, age int) (*User, error) {
    if id == "" {
        return nil, errors.New("user id is required")
    }
    if name == "" {
        return nil, errors.New("name is required")
    }
    if email == "" {
        return nil, errors.New("email is required")
    }
    if age < 0 {
        return nil, errors.New("age cannot be negative")
    }

    now := time.Now()
    return &User{
        id:        id,
        name:      name,
        email:     email,
        age:       age,
        createdAt: now,
        updatedAt: now,
    }, nil
}

func (u *User) ID() UserID {
    return u.id
}

func (u *User) Name() string {
    return u.name
}

func (u *User) Email() Email {
    return u.email
}

func (u *User) Age() int {
    return u.age
}

func (u *User) UpdateName(name string) error {
    if name == "" {
        return errors.New("name is required")
    }
    u.name = name
    u.updatedAt = time.Now()
    return nil
}

func (u *User) UpdateEmail(email Email) error {
    if email == "" {
        return errors.New("email is required")
    }
    u.email = email
    u.updatedAt = time.Now()
    return nil
}

func (u *User) UpdateAge(age int) error {
    if age < 0 {
        return errors.New("age cannot be negative")
    }
    u.age = age
    u.updatedAt = time.Now()
    return nil
}
```

#### 值对象
```go
// internal/domain/user/value_objects.go
package user

import (
    "errors"
    "regexp"
    "strings"
)

type Email string

func NewEmail(email string) (Email, error) {
    if email == "" {
        return "", errors.New("email is required")
    }

    email = strings.TrimSpace(email)
    if !isValidEmail(email) {
        return "", errors.New("invalid email format")
    }

    return Email(email), nil
}

func (e Email) String() string {
    return string(e)
}

func (e Email) Equals(other Email) bool {
    return strings.ToLower(string(e)) == strings.ToLower(string(other))
}

func isValidEmail(email string) bool {
    emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    return emailRegex.MatchString(email)
}

type Age int

func NewAge(age int) (Age, error) {
    if age < 0 {
        return 0, errors.New("age cannot be negative")
    }
    if age > 150 {
        return 0, errors.New("age cannot be greater than 150")
    }
    return Age(age), nil
}

func (a Age) Int() int {
    return int(a)
}

func (a Age) IsAdult() bool {
    return a >= 18
}
```

#### 仓储接口
```go
// internal/domain/user/repository.go
package user

import "context"

type UserRepository interface {
    FindByID(ctx context.Context, id UserID) (*User, error)
    FindByEmail(ctx context.Context, email Email) (*User, error)
    Save(ctx context.Context, user *User) error
    Delete(ctx context.Context, id UserID) error
}

type UserReadRepository interface {
    FindAll(ctx context.Context) ([]*User, error)
    FindByAgeRange(ctx context.Context, min, max int) ([]*User, error)
}
```

#### 应用服务
```go
// internal/application/user/service.go
package user

import (
    "context"
    "errors"
)

type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{
        repo: repo,
    }
}

func (s *UserService) CreateUser(ctx context.Context, cmd *CreateUserCommand) (*User, error) {
    // 验证
    email, err := NewEmail(cmd.Email)
    if err != nil {
        return nil, err
    }

    age, err := NewAge(cmd.Age)
    if err != nil {
        return nil, err
    }

    // 检查邮箱是否已存在
    existingUser, err := s.repo.FindByEmail(ctx, email)
    if err != nil {
        return nil, err
    }
    if existingUser != nil {
        return nil, errors.New("user with this email already exists")
    }

    // 创建用户
    user, err := NewUser(UserID(cmd.ID), cmd.Name, email, age.Int())
    if err != nil {
        return nil, err
    }

    // 保存用户
    if err := s.repo.Save(ctx, user); err != nil {
        return nil, err
    }

    return user, nil
}

func (s *UserService) UpdateUser(ctx context.Context, cmd *UpdateUserCommand) (*User, error) {
    // 查找用户
    user, err := s.repo.FindByID(ctx, UserID(cmd.ID))
    if err != nil {
        return nil, err
    }
    if user == nil {
        return nil, errors.New("user not found")
    }

    // 更新用户信息
    if cmd.Name != "" {
        if err := user.UpdateName(cmd.Name); err != nil {
            return nil, err
        }
    }

    if cmd.Email != "" {
        email, err := NewEmail(cmd.Email)
        if err != nil {
            return nil, err
        }
        if err := user.UpdateEmail(email); err != nil {
            return nil, err
        }
    }

    if cmd.Age > 0 {
        age, err := NewAge(cmd.Age)
        if err != nil {
            return nil, err
        }
        if err := user.UpdateAge(age.Int()); err != nil {
            return nil, err
        }
    }

    // 保存更新
    if err := s.repo.Save(ctx, user); err != nil {
        return nil, err
    }

    return user, nil
}

type CreateUserCommand struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

type UpdateUserCommand struct {
    ID    string `json:"id"`
    Name  string `json:"name,omitempty"`
    Email string `json:"email,omitempty"`
    Age   int    `json:"age,omitempty"`
}
```

### 4. 依赖注入

#### 依赖注入容器
```go
// internal/container/container.go
package container

import (
    "your-project/internal/config"
    "your-project/internal/domain/user"
    "your-project/internal/infrastructure/database"
    "your-project/internal/infrastructure/logging"
)

type Container struct {
    Config        *config.Config
    Logger        *zap.Logger
    Database      *gorm.DB
    UserRepository user.UserRepository
    UserService    *user.UserService
}

func New() (*Container, error) {
    // 加载配置
    cfg, err := config.Load("configs/config.yaml")
    if err != nil {
        return nil, err
    }

    // 初始化日志
    logger := logging.New(cfg)

    // 初始化数据库
    db, err := database.Init(cfg.Database)
    if err != nil {
        return nil, err
    }

    // 初始化仓储
    userRepo := database.NewUserRepository(db)

    // 初始化服务
    userService := user.NewUserService(userRepo)

    return &Container{
        Config:        cfg,
        Logger:        logger,
        Database:      db,
        UserRepository: userRepo,
        UserService:    userService,
    }, nil
}

func (c *Container) Close() error {
    // 清理资源
    if c.Logger != nil {
        c.Logger.Sync()
    }

    if sqlDB, err := c.Database.DB(); err == nil {
        sqlDB.Close()
    }

    return nil
}
```

### 5. 错误处理策略

#### 错误定义
```go
// internal/errors/errors.go
package errors

import (
    "fmt"
    "net/http"
)

// 基础错误类型
type AppError struct {
    Code       string      `json:"code"`
    Message    string      `json:"message"`
    Details    string      `json:"details,omitempty"`
    StatusCode int         `json:"-"`
    Context    interface{} `json:"context,omitempty"`
}

func (e *AppError) Error() string {
    return e.Message
}

// 预定义错误
var (
    ErrNotFound = &AppError{
        Code:       "NOT_FOUND",
        Message:    "Resource not found",
        StatusCode: http.StatusNotFound,
    }

    ErrValidation = &AppError{
        Code:       "VALIDATION_ERROR",
        Message:    "Validation failed",
        StatusCode: http.StatusBadRequest,
    }

    ErrUnauthorized = &AppError{
        Code:       "UNAUTHORIZED",
        Message:    "Unauthorized",
        StatusCode: http.StatusUnauthorized,
    }

    ErrInternal = &AppError{
        Code:       "INTERNAL_ERROR",
        Message:    "Internal server error",
        StatusCode: http.StatusInternalServerError,
    }
)

// 创建错误
func NewError(code, message string, statusCode int) *AppError {
    return &AppError{
        Code:       code,
        Message:    message,
        StatusCode: statusCode,
    }
}

func NewErrorWithDetails(code, message, details string, statusCode int) *AppError {
    return &AppError{
        Code:       code,
        Message:    message,
        Details:    details,
        StatusCode: statusCode,
    }
}

func WrapError(err error, code, message string, statusCode int) *AppError {
    return &AppError{
        Code:       code,
        Message:    message,
        Details:    err.Error(),
        StatusCode: statusCode,
    }
}

// 领域错误
type DomainError struct {
    Code    string
    Message string
    Field   string
}

func (e *DomainError) Error() string {
    return fmt.Sprintf("%s: %s (field: %s)", e.Code, e.Message, e.Field)
}

func NewDomainError(code, message, field string) *DomainError {
    return &DomainError{
        Code:    code,
        Message: message,
        Field:   field,
    }
}
```

#### 错误处理中间件
```go
// internal/middleware/error_middleware.go
package middleware

import (
    "net/http"
    "your-project/internal/errors"
    "github.com/gin-gonic/gin"
)

func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()

        // 处理错误
        if len(c.Errors) > 0 {
            err := c.Errors.Last().Err

            // 检查是否是AppError
            if appErr, ok := err.(*errors.AppError); ok {
                c.JSON(appErr.StatusCode, gin.H{
                    "error": appErr,
                })
                return
            }

            // 其他错误
            c.JSON(http.StatusInternalServerError, gin.H{
                "error": errors.NewError(
                    "INTERNAL_ERROR",
                    "Internal server error",
                    http.StatusInternalServerError,
                ),
            })
        }
    }
}
```

## 🧪 实践练习

### 练习1: 标准项目结构
```
my-go-app/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── handlers/
│   │   └── user_handler.go
│   ├── services/
│   │   └── user_service.go
│   └── models/
│       └── user.go
├── pkg/
│   ├── database/
│   │   └── database.go
│   └── logger/
│       └── logger.go
├── configs/
│   └── config.yaml
├── go.mod
└── go.sum
```

### 练习2: 分层架构实现
```go
// internal/models/user.go
package models

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

// internal/repositories/user_repository.go
package repositories

import (
    "gorm.io/gorm"
    "your-project/internal/models"
)

type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) FindByID(id int) (*models.User, error) {
    var user models.User
    result := r.db.First(&user, id)
    return &user, result.Error
}

func (r *UserRepository) Create(user *models.User) error {
    return r.db.Create(user).Error
}
```

## 📋 最佳实践总结

### 1. 项目结构
- 使用标准的项目结构
- 明确区分internal和pkg目录
- 合理组织代码层次

### 2. 包设计
- 保持包的单一职责
- 避免循环依赖
- 使用清晰的包名

### 3. 架构模式
- 选择合适的架构模式
- 遵循依赖倒置原则
- 使用依赖注入

### 4. 错误处理
- 定义清晰的错误类型
- 提供有意义的错误信息
- 使用适当的错误处理策略

## 📋 检查清单

- [ ] 理解Go标准项目结构
- [ ] 掌握包的设计原则
- [ ] 学会分层架构实现
- [ ] 理解DDD模式
- [ ] 掌握依赖注入
- [ ] 学会错误处理策略
- [ ] 理解Go与PHP代码组织的差异
- [ ] 掌握代码组织最佳实践

## 🚀 下一步

掌握代码组织后，你可以继续学习：
- **设计模式**: Go中的设计模式实现
- **性能优化**: 代码优化和性能调优
- **安全实践**: 安全编码和防护
- **团队协作**: 代码规范和协作流程

---

**学习提示**: Go的代码组织哲学强调简洁性和明确性。通过标准化的项目结构和清晰的层次分离，你可以构建更加可维护的Go应用。相比于PHP的灵活性，Go的规范性更有利于大型项目的长期维护。

*最后更新: 2025年9月*