# 分层架构设计

## 概述

分层架构是最常用和最基础的软件架构模式之一。它将应用程序划分为多个层，每个层都有明确的职责和边界。本文档将深入探讨分层架构的设计原则、实现方式和最佳实践。

## 目录

- [分层架构基础](#分层架构基础)
- [经典三层架构](#经典三层架构)
- [四层架构模式](#四层架构模式)
- [五层架构模式](#五层架构模式)
- [领域驱动设计分层](#领域驱动设计分层)
- [各层职责定义](#各层职责定义)
- [依赖关系管理](#依赖关系管理)
- [事务管理](#事务管理)
- [异常处理](#异常处理)
- [性能优化](#性能优化)
- [测试策略](#测试策略)
- [最佳实践总结](#最佳实践总结)

## 分层架构基础

### 分层架构特点

```go
// internal/pkg/architecture/layered/fundamentals.go
package layered

// 分层架构特点
/*
1. 关注点分离：每一层只关注特定的功能
2. 依赖倒置：上层依赖下层的抽象，而不是具体实现
3. 单向依赖：依赖关系严格单向，避免循环依赖
4. 可替换性：每层都可以独立替换和测试
5. 可维护性：清晰的层次结构便于维护和理解
*/

// 分层架构类型
type LayerType int

const (
    LayerPresentation LayerType = iota // 表示层
    LayerApplication                   // 应用层
    LayerDomain                        // 领域层
    LayerInfrastructure                // 基础设施层
    LayerPersistence                   // 持久化层
)

// 分层接口
type Layer interface {
    GetName() string
    GetType() LayerType
    GetDependencies() []LayerType
    Validate() error
}

// 分层上下文
type LayerContext struct {
    RequestID    string
    UserID       string
    Timestamp    time.Time
    Metadata     map[string]interface{}
}
```

### 分层架构配置

```go
// internal/pkg/architecture/layered/config.go
package layered

// 分层架构配置
type LayeredArchitectureConfig struct {
    // 层配置
    Layers []LayerConfig `yaml:"layers"`

    // 依赖关系配置
    Dependencies DependencyConfig `yaml:"dependencies"`

    // 事务配置
    Transaction TransactionConfig `yaml:"transaction"`

    // 异常处理配置
    Exception ExceptionConfig `yaml:"exception"`

    // 性能配置
    Performance PerformanceConfig `yaml:"performance"`
}

// 层配置
type LayerConfig struct {
    Name        string        `yaml:"name"`
    Type        LayerType     `yaml:"type"`
    Enabled     bool          `yaml:"enabled"`
    Package     string        `yaml:"package"`
    Timeout     time.Duration `yaml:"timeout"`
    RetryPolicy *RetryPolicy  `yaml:"retry_policy"`
}

// 依赖配置
type DependencyConfig struct {
    // 严格模式：不允许跨层调用
    StrictMode bool `yaml:"strict_mode"`

    // 允许的跨层依赖
    AllowedCrossDependencies []CrossDependency `yaml:"allowed_cross_dependencies"`

    // 依赖注入配置
    DependencyInjection DIConfig `yaml:"dependency_injection"`
}

// 跨层依赖
type CrossDependency struct {
    From LayerType `yaml:"from"`
    To   LayerType `yaml:"to"`
    Reason string   `yaml:"reason"`
}

// 重试策略
type RetryPolicy struct {
    MaxRetries int           `yaml:"max_retries"`
    Delay      time.Duration `yaml:"delay"`
    Backoff    float64       `yaml:"backoff"`
}

// 事务配置
type TransactionConfig struct {
    // 默认事务超时
    DefaultTimeout time.Duration `yaml:"default_timeout"`

    // 事务传播行为
    Propagation TransactionPropagation `yaml:"propagation"`

    // 隔离级别
    IsolationLevel string `yaml:"isolation_level"`

    // 分布式事务
    Distributed bool `yaml:"distributed"`
}

// 事务传播行为
type TransactionPropagation int

const (
    PropagationRequired TransactionPropagation = iota
    PropagationRequiresNew
    PropagationSupports
    PropagationNotSupported
    PropagationNever
    PropagationNested
)

// 异常配置
type ExceptionConfig struct {
    // 全局异常处理器
    GlobalHandler string `yaml:"global_handler"`

    // 异常映射
    ExceptionMappings []ExceptionMapping `yaml:"exception_mappings"`

    // 错误代码配置
    ErrorCodeConfig ErrorCodeConfig `yaml:"error_code_config"`
}

// 异常映射
type ExceptionMapping struct {
    From      string `yaml:"from"`
    To        string `yaml:"to"`
    StatusCode int    `yaml:"status_code"`
}

// 错误代码配置
type ErrorCodeConfig struct {
    Prefix     string            `yaml:"prefix"`
    Categories map[string]string `yaml:"categories"`
}

// 性能配置
type PerformanceConfig struct {
    // 缓存配置
    Cache CacheConfig `yaml:"cache"`

    // 连接池配置
    ConnectionPool ConnectionPoolConfig `yaml:"connection_pool"`

    // 监控配置
    Monitoring MonitoringConfig `yaml:"monitoring"`
}

// 缓存配置
type CacheConfig struct {
    Enabled     bool          `yaml:"enabled"`
    Type        string        `yaml:"type"`
    TTL         time.Duration `yaml:"ttl"`
    Size        int           `yaml:"size"`
    Strategy    string        `yaml:"strategy"`
}

// 连接池配置
type ConnectionPoolConfig struct {
    MaxOpen     int           `yaml:"max_open"`
    MaxIdle     int           `yaml:"max_idle"`
    MaxLifetime time.Duration `yaml:"max_lifetime"`
    MaxIdleTime time.Duration `yaml:"max_idle_time"`
}

// 监控配置
type MonitoringConfig struct {
    Enabled    bool   `yaml:"enabled"`
    Metrics    bool   `yaml:"metrics"`
    Tracing    bool   `yaml:"tracing"`
    Logging    bool   `yaml:"logging"`
    Exporter   string `yaml:"exporter"`
}

// 依赖注入配置
type DIConfig struct {
    Enabled bool `yaml:"enabled"`
    Mode    string `yaml:"mode"` // constructor, property, method
    AutoWire bool `yaml:"auto_wire"`
}
```

## 经典三层架构

### 表示层实现

```go
// internal/app/presentation/handlers/user_handler.go
package handlers

import (
    "context"
    "net/http"
    "strconv"

    "github.com/gin-gonic/gin"
    "github.com/myapp/internal/app/application/services"
    "github.com/myapp/internal/pkg/architecture/layered"
    "github.com/myapp/internal/pkg/logger"
)

// 用户处理器
type UserHandler struct {
    userService *services.UserService
    logger     *logger.Logger
}

// 创建用户处理器
func NewUserHandler(userService *services.UserService, logger *logger.Logger) *UserHandler {
    return &UserHandler{
        userService: userService,
        logger:     logger,
    }
}

// 创建用户请求
type CreateUserRequest struct {
    Username string `json:"username" binding:"required,min=3,max=50"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,min=6"`
}

// 更新用户请求
type UpdateUserRequest struct {
    Username string `json:"username,omitempty"`
    Email    string `json:"email,omitempty"`
}

// 用户响应
type UserResponse struct {
    ID        string    `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

// 创建用户
func (h *UserHandler) CreateUser(c *gin.Context) {
    ctx := layered.NewLayerContext(c.Request.Context())
    ctx.RequestID = c.GetHeader("X-Request-ID")
    ctx.UserID = c.GetHeader("X-User-ID")

    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 调用应用层服务
    user, err := h.userService.CreateUser(ctx, &services.CreateUserCommand{
        Username: req.Username,
        Email:    req.Email,
        Password: req.Password,
    })

    if err != nil {
        h.logger.WithFields(map[string]interface{}{
            "error":      err,
            "request_id": ctx.RequestID,
        }).Error("Failed to create user")

        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
        return
    }

    response := UserResponse{
        ID:        user.ID,
        Username:  user.Username,
        Email:     user.Email,
        CreatedAt: user.CreatedAt,
        UpdatedAt: user.UpdatedAt,
    }

    c.JSON(http.StatusCreated, response)
}

// 获取用户
func (h *UserHandler) GetUser(c *gin.Context) {
    ctx := layered.NewLayerContext(c.Request.Context())
    ctx.RequestID = c.GetHeader("X-Request-ID")

    userID := c.Param("id")
    if userID == "" {
        c.JSON(http.StatusBadRequest, gin.H{"error": "User ID is required"})
        return
    }

    user, err := h.userService.GetUser(ctx, userID)
    if err != nil {
        h.logger.WithFields(map[string]interface{}{
            "error":      err,
            "request_id": ctx.RequestID,
            "user_id":    userID,
        }).Error("Failed to get user")

        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user"})
        return
    }

    if user == nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    response := UserResponse{
        ID:        user.ID,
        Username:  user.Username,
        Email:     user.Email,
        CreatedAt: user.CreatedAt,
        UpdatedAt: user.UpdatedAt,
    }

    c.JSON(http.StatusOK, response)
}

// 获取用户列表
func (h *UserHandler) ListUsers(c *gin.Context) {
    ctx := layered.NewLayerContext(c.Request.Context())
    ctx.RequestID = c.GetHeader("X-Request-ID")

    // 分页参数
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))

    filter := &services.UserFilter{
        Username: c.Query("username"),
        Email:    c.Query("email"),
        Page:     page,
        Limit:    limit,
    }

    users, total, err := h.userService.ListUsers(ctx, filter)
    if err != nil {
        h.logger.WithFields(map[string]interface{}{
            "error":      err,
            "request_id": ctx.RequestID,
        }).Error("Failed to list users")

        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list users"})
        return
    }

    // 转换为响应格式
    var responses []UserResponse
    for _, user := range users {
        responses = append(responses, UserResponse{
            ID:        user.ID,
            Username:  user.Username,
            Email:     user.Email,
            CreatedAt: user.CreatedAt,
            UpdatedAt: user.UpdatedAt,
        })
    }

    c.JSON(http.StatusOK, gin.H{
        "users": responses,
        "pagination": gin.H{
            "page":  page,
            "limit": limit,
            "total": total,
        },
    })
}

// 更新用户
func (h *UserHandler) UpdateUser(c *gin.Context) {
    ctx := layered.NewLayerContext(c.Request.Context())
    ctx.RequestID = c.GetHeader("X-Request-ID")
    ctx.UserID = c.GetHeader("X-User-ID")

    userID := c.Param("id")
    if userID == "" {
        c.JSON(http.StatusBadRequest, gin.H{"error": "User ID is required"})
        return
    }

    var req UpdateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 检查用户是否存在
    existingUser, err := h.userService.GetUser(ctx, userID)
    if err != nil {
        h.logger.WithFields(map[string]interface{}{
            "error":      err,
            "request_id": ctx.RequestID,
            "user_id":    userID,
        }).Error("Failed to get user")

        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user"})
        return
    }

    if existingUser == nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    // 更新用户
    command := &services.UpdateUserCommand{
        ID:       userID,
        Username: req.Username,
        Email:    req.Email,
    }

    if err := h.userService.UpdateUser(ctx, command); err != nil {
        h.logger.WithFields(map[string]interface{}{
            "error":      err,
            "request_id": ctx.RequestID,
            "user_id":    userID,
        }).Error("Failed to update user")

        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update user"})
        return
    }

    c.JSON(http.StatusOK, gin.H{"message": "User updated successfully"})
}

// 删除用户
func (h *UserHandler) DeleteUser(c *gin.Context) {
    ctx := layered.NewLayerContext(c.Request.Context())
    ctx.RequestID = c.GetHeader("X-Request-ID")
    ctx.UserID = c.GetHeader("X-User-ID")

    userID := c.Param("id")
    if userID == "" {
        c.JSON(http.StatusBadRequest, gin.H{"error": "User ID is required"})
        return
    }

    // 检查用户是否存在
    existingUser, err := h.userService.GetUser(ctx, userID)
    if err != nil {
        h.logger.WithFields(map[string]interface{}{
            "error":      err,
            "request_id": ctx.RequestID,
            "user_id":    userID,
        }).Error("Failed to get user")

        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user"})
        return
    }

    if existingUser == nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    // 删除用户
    if err := h.userService.DeleteUser(ctx, userID); err != nil {
        h.logger.WithFields(map[string]interface{}{
            "error":      err,
            "request_id": ctx.RequestID,
            "user_id":    userID,
        }).Error("Failed to delete user")

        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete user"})
        return
    }

    c.JSON(http.StatusOK, gin.H{"message": "User deleted successfully"})
}

// 中间件：添加分层上下文
func (h *UserHandler) LayerContextMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        ctx := layered.NewLayerContext(c.Request.Context())
        ctx.RequestID = c.GetHeader("X-Request-ID")
        ctx.UserID = c.GetHeader("X-User-ID")
        ctx.Timestamp = time.Now()

        c.Set("layer_context", ctx)
        c.Next()
    }
}
```

### 业务逻辑层实现

```go
// internal/app/application/services/user_service.go
package services

import (
    "context"
    "fmt"
    "time"

    "github.com/myapp/internal/app/domain/entities"
    "github.com/myapp/internal/app/domain/repositories"
    "github.com/myapp/internal/pkg/architecture/layered"
    "github.com/myapp/internal/pkg/errors"
    "github.com/myapp/internal/pkg/logger"
)

// 用户服务接口
type UserService interface {
    CreateUser(ctx context.Context, command *CreateUserCommand) (*entities.User, error)
    GetUser(ctx context.Context, id string) (*entities.User, error)
    UpdateUser(ctx context.Context, command *UpdateUserCommand) error
    DeleteUser(ctx context.Context, id string) error
    ListUsers(ctx context.Context, filter *UserFilter) ([]*entities.User, int64, error)
}

// 创建用户命令
type CreateUserCommand struct {
    Username string
    Email    string
    Password string
}

// 更新用户命令
type UpdateUserCommand struct {
    ID       string
    Username string
    Email    string
}

// 用户过滤器
type UserFilter struct {
    Username string
    Email    string
    Page     int
    Limit    int
}

// 用户服务实现
type userService struct {
    userRepo   repositories.UserRepository
    logger     *logger.Logger
    validator  *UserValidator
    encryptor  *PasswordEncryptor
}

// 创建用户服务
func NewUserService(
    userRepo repositories.UserRepository,
    logger *logger.Logger,
) UserService {
    return &userService{
        userRepo:  userRepo,
        logger:    logger,
        validator: NewUserValidator(),
        encryptor: NewPasswordEncryptor(),
    }
}

// 创建用户
func (s *userService) CreateUser(ctx context.Context, command *CreateUserCommand) (*entities.User, error) {
    // 验证命令
    if err := s.validator.ValidateCreateCommand(command); err != nil {
        return nil, errors.Wrap(err, "VALIDATION_ERROR", "Invalid create user command")
    }

    // 检查用户名是否已存在
    exists, err := s.userRepo.ExistsByUsername(ctx, command.Username)
    if err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error":    err,
            "username": command.Username,
        }).Error("Failed to check username existence")
        return nil, errors.Wrap(err, "DATABASE_ERROR", "Failed to check username existence")
    }

    if exists {
        return nil, errors.New("USERNAME_EXISTS", "Username already exists")
    }

    // 检查邮箱是否已存在
    exists, err = s.userRepo.ExistsByEmail(ctx, command.Email)
    if err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error": err,
            "email": command.Email,
        }).Error("Failed to check email existence")
        return nil, errors.Wrap(err, "DATABASE_ERROR", "Failed to check email existence")
    }

    if exists {
        return nil, errors.New("EMAIL_EXISTS", "Email already exists")
    }

    // 创建用户实体
    user := &entities.User{
        ID:        generateUserID(),
        Username:  command.Username,
        Email:     command.Email,
        Password:  s.encryptor.Encrypt(command.Password),
        Status:    entities.UserStatusActive,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }

    // 保存用户
    if err := s.userRepo.Create(ctx, user); err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error":    err,
            "user_id":  user.ID,
            "username": user.Username,
        }).Error("Failed to create user")
        return nil, errors.Wrap(err, "DATABASE_ERROR", "Failed to create user")
    }

    s.logger.WithFields(map[string]interface{}{
        "user_id":  user.ID,
        "username": user.Username,
    }).Info("User created successfully")

    return user, nil
}

// 获取用户
func (s *userService) GetUser(ctx context.Context, id string) (*entities.User, error) {
    // 验证ID
    if id == "" {
        return nil, errors.New("INVALID_INPUT", "User ID is required")
    }

    // 获取用户
    user, err := s.userRepo.GetByID(ctx, id)
    if err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error":   err,
            "user_id": id,
        }).Error("Failed to get user")
        return nil, errors.Wrap(err, "DATABASE_ERROR", "Failed to get user")
    }

    return user, nil
}

// 更新用户
func (s *userService) UpdateUser(ctx context.Context, command *UpdateUserCommand) error {
    // 验证命令
    if err := s.validator.ValidateUpdateCommand(command); err != nil {
        return errors.Wrap(err, "VALIDATION_ERROR", "Invalid update user command")
    }

    // 获取现有用户
    user, err := s.userRepo.GetByID(ctx, command.ID)
    if err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error":   err,
            "user_id": command.ID,
        }).Error("Failed to get user")
        return errors.Wrap(err, "DATABASE_ERROR", "Failed to get user")
    }

    if user == nil {
        return errors.New("USER_NOT_FOUND", "User not found")
    }

    // 检查用户名是否已被其他用户使用
    if command.Username != "" && command.Username != user.Username {
        exists, err := s.userRepo.ExistsByUsername(ctx, command.Username)
        if err != nil {
            s.logger.WithFields(map[string]interface{}{
                "error":    err,
                "username": command.Username,
            }).Error("Failed to check username existence")
            return errors.Wrap(err, "DATABASE_ERROR", "Failed to check username existence")
        }

        if exists {
            return errors.New("USERNAME_EXISTS", "Username already exists")
        }
        user.Username = command.Username
    }

    // 检查邮箱是否已被其他用户使用
    if command.Email != "" && command.Email != user.Email {
        exists, err := s.userRepo.ExistsByEmail(ctx, command.Email)
        if err != nil {
            s.logger.WithFields(map[string]interface{}{
                "error": err,
                "email": command.Email,
            }).Error("Failed to check email existence")
            return errors.Wrap(err, "DATABASE_ERROR", "Failed to check email existence")
        }

        if exists {
            return errors.New("EMAIL_EXISTS", "Email already exists")
        }
        user.Email = command.Email
    }

    // 更新用户
    user.UpdatedAt = time.Now()

    if err := s.userRepo.Update(ctx, user); err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error":   err,
            "user_id": user.ID,
        }).Error("Failed to update user")
        return errors.Wrap(err, "DATABASE_ERROR", "Failed to update user")
    }

    s.logger.WithFields(map[string]interface{}{
        "user_id":  user.ID,
        "username": user.Username,
    }).Info("User updated successfully")

    return nil
}

// 删除用户
func (s *userService) DeleteUser(ctx context.Context, id string) error {
    // 验证ID
    if id == "" {
        return errors.New("INVALID_INPUT", "User ID is required")
    }

    // 检查用户是否存在
    user, err := s.userRepo.GetByID(ctx, id)
    if err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error":   err,
            "user_id": id,
        }).Error("Failed to get user")
        return errors.Wrap(err, "DATABASE_ERROR", "Failed to get user")
    }

    if user == nil {
        return errors.New("USER_NOT_FOUND", "User not found")
    }

    // 删除用户
    if err := s.userRepo.Delete(ctx, id); err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error":   err,
            "user_id": id,
        }).Error("Failed to delete user")
        return errors.Wrap(err, "DATABASE_ERROR", "Failed to delete user")
    }

    s.logger.WithFields(map[string]interface{}{
        "user_id":  user.ID,
        "username": user.Username,
    }).Info("User deleted successfully")

    return nil
}

// 获取用户列表
func (s *userService) ListUsers(ctx context.Context, filter *UserFilter) ([]*entities.User, int64, error) {
    // 验证过滤器
    if err := s.validator.ValidateFilter(filter); err != nil {
        return nil, 0, errors.Wrap(err, "VALIDATION_ERROR", "Invalid user filter")
    }

    // 获取用户列表
    users, err := s.userRepo.List(ctx, filter)
    if err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error": err,
            "filter": filter,
        }).Error("Failed to list users")
        return nil, 0, errors.Wrap(err, "DATABASE_ERROR", "Failed to list users")
    }

    // 获取总数
    total, err := s.userRepo.Count(ctx, filter)
    if err != nil {
        s.logger.WithFields(map[string]interface{}{
            "error": err,
            "filter": filter,
        }).Error("Failed to count users")
        return nil, 0, errors.Wrap(err, "DATABASE_ERROR", "Failed to count users")
    }

    return users, total, nil
}

// 生成用户ID
func generateUserID() string {
    return fmt.Sprintf("user_%d", time.Now().UnixNano())
}
```

### 数据访问层实现

```go
// internal/app/infrastructure/repositories/user_repository.go
package repositories

import (
    "context"
    "database/sql"
    "errors"
    "fmt"

    "github.com/myapp/internal/app/domain/entities"
    "github.com/myapp/internal/pkg/logger"
)

// 用户仓储实现
type userRepository struct {
    db     *sql.DB
    logger *logger.Logger
}

// 创建用户仓储
func NewUserRepository(db *sql.DB, logger *logger.Logger) UserRepository {
    return &userRepository{
        db:     db,
        logger: logger,
    }
}

// 创建用户
func (r *userRepository) Create(ctx context.Context, user *entities.User) error {
    query := `
        INSERT INTO users (id, username, email, password, status, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    `

    _, err := r.db.ExecContext(ctx, query,
        user.ID,
        user.Username,
        user.Email,
        user.Password,
        user.Status,
        user.CreatedAt,
        user.UpdatedAt,
    )

    if err != nil {
        return fmt.Errorf("failed to create user: %w", err)
    }

    return nil
}

// 根据ID获取用户
func (r *userRepository) GetByID(ctx context.Context, id string) (*entities.User, error) {
    query := `
        SELECT id, username, email, password, status, created_at, updated_at
        FROM users
        WHERE id = $1
    `

    user := &entities.User{}
    err := r.db.QueryRowContext(ctx, query, id).Scan(
        &user.ID,
        &user.Username,
        &user.Email,
        &user.Password,
        &user.Status,
        &user.CreatedAt,
        &user.UpdatedAt,
    )

    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, nil
        }
        return nil, fmt.Errorf("failed to get user: %w", err)
    }

    return user, nil
}

// 根据用户名获取用户
func (r *userRepository) GetByUsername(ctx context.Context, username string) (*entities.User, error) {
    query := `
        SELECT id, username, email, password, status, created_at, updated_at
        FROM users
        WHERE username = $1
    `

    user := &entities.User{}
    err := r.db.QueryRowContext(ctx, query, username).Scan(
        &user.ID,
        &user.Username,
        &user.Email,
        &user.Password,
        &user.Status,
        &user.CreatedAt,
        &user.UpdatedAt,
    )

    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, nil
        }
        return nil, fmt.Errorf("failed to get user by username: %w", err)
    }

    return user, nil
}

// 根据邮箱获取用户
func (r *userRepository) GetByEmail(ctx context.Context, email string) (*entities.User, error) {
    query := `
        SELECT id, username, email, password, status, created_at, updated_at
        FROM users
        WHERE email = $1
    `

    user := &entities.User{}
    err := r.db.QueryRowContext(ctx, query, email).Scan(
        &user.ID,
        &user.Username,
        &user.Email,
        &user.Password,
        &user.Status,
        &user.CreatedAt,
        &user.UpdatedAt,
    )

    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, nil
        }
        return nil, fmt.Errorf("failed to get user by email: %w", err)
    }

    return user, nil
}

// 更新用户
func (r *userRepository) Update(ctx context.Context, user *entities.User) error {
    query := `
        UPDATE users
        SET username = $2, email = $3, password = $4, status = $5, updated_at = $6
        WHERE id = $1
    `

    _, err := r.db.ExecContext(ctx, query,
        user.ID,
        user.Username,
        user.Email,
        user.Password,
        user.Status,
        user.UpdatedAt,
    )

    if err != nil {
        return fmt.Errorf("failed to update user: %w", err)
    }

    return nil
}

// 删除用户
func (r *userRepository) Delete(ctx context.Context, id string) error {
    query := `DELETE FROM users WHERE id = $1`

    _, err := r.db.ExecContext(ctx, query, id)
    if err != nil {
        return fmt.Errorf("failed to delete user: %w", err)
    }

    return nil
}

// 检查用户名是否存在
func (r *userRepository) ExistsByUsername(ctx context.Context, username string) (bool, error) {
    query := `SELECT COUNT(*) FROM users WHERE username = $1`

    var count int
    err := r.db.QueryRowContext(ctx, query, username).Scan(&count)
    if err != nil {
        return false, fmt.Errorf("failed to check username existence: %w", err)
    }

    return count > 0, nil
}

// 检查邮箱是否存在
func (r *userRepository) ExistsByEmail(ctx context.Context, email string) (bool, error) {
    query := `SELECT COUNT(*) FROM users WHERE email = $1`

    var count int
    err := r.db.QueryRowContext(ctx, query, email).Scan(&count)
    if err != nil {
        return false, fmt.Errorf("failed to check email existence: %w", err)
    }

    return count > 0, nil
}

// 获取用户列表
func (r *userRepository) List(ctx context.Context, filter *UserFilter) ([]*entities.User, error) {
    query := `
        SELECT id, username, email, password, status, created_at, updated_at
        FROM users
        WHERE 1=1
    `
    args := []interface{}{}
    argPos := 1

    // 构建查询条件
    if filter.Username != "" {
        query += fmt.Sprintf(" AND username LIKE $%d", argPos)
        args = append(args, "%"+filter.Username+"%")
        argPos++
    }

    if filter.Email != "" {
        query += fmt.Sprintf(" AND email LIKE $%d", argPos)
        args = append(args, "%"+filter.Email+"%")
        argPos++
    }

    // 排序
    query += " ORDER BY created_at DESC"

    // 分页
    if filter.Limit > 0 {
        query += fmt.Sprintf(" LIMIT $%d", argPos)
        args = append(args, filter.Limit)
        argPos++

        if filter.Page > 1 {
            offset := (filter.Page - 1) * filter.Limit
            query += fmt.Sprintf(" OFFSET $%d", argPos)
            args = append(args, offset)
        }
    }

    rows, err := r.db.QueryContext(ctx, query, args...)
    if err != nil {
        return nil, fmt.Errorf("failed to list users: %w", err)
    }
    defer rows.Close()

    var users []*entities.User
    for rows.Next() {
        user := &entities.User{}
        err := rows.Scan(
            &user.ID,
            &user.Username,
            &user.Email,
            &user.Password,
            &user.Status,
            &user.CreatedAt,
            &user.UpdatedAt,
        )
        if err != nil {
            return nil, fmt.Errorf("failed to scan user: %w", err)
        }
        users = append(users, user)
    }

    return users, nil
}

// 统计用户数量
func (r *userRepository) Count(ctx context.Context, filter *UserFilter) (int64, error) {
    query := `SELECT COUNT(*) FROM users WHERE 1=1`
    args := []interface{}{}
    argPos := 1

    // 构建查询条件
    if filter.Username != "" {
        query += fmt.Sprintf(" AND username LIKE $%d", argPos)
        args = append(args, "%"+filter.Username+"%")
        argPos++
    }

    if filter.Email != "" {
        query += fmt.Sprintf(" AND email LIKE $%d", argPos)
        args = append(args, "%"+filter.Email+"%")
        argPos++
    }

    var count int64
    err := r.db.QueryRowContext(ctx, query, args...).Scan(&count)
    if err != nil {
        return 0, fmt.Errorf("failed to count users: %w", err)
    }

    return count, nil
}

// 用户过滤器
type UserFilter struct {
    Username string
    Email    string
    Page     int
    Limit    int
}
```

## 四层架构模式

### 领域层实现

```go
// internal/app/domain/entities/user.go
package entities

import (
    "time"
)

// 用户状态
type UserStatus string

const (
    UserStatusActive   UserStatus = "active"
    UserStatusInactive UserStatus = "inactive"
    UserStatusDeleted  UserStatus = "deleted"
)

// 用户实体
type User struct {
    ID        string     `json:"id"`
    Username  string     `json:"username"`
    Email     string     `json:"email"`
    Password  string     `json:"-"` // 不在JSON中显示密码
    Status    UserStatus `json:"status"`
    CreatedAt time.Time  `json:"created_at"`
    UpdatedAt time.Time  `json:"updated_at"`
}

// 用户验证器
type UserValidator struct{}

// 创建用户验证器
func NewUserValidator() *UserValidator {
    return &UserValidator{}
}

// 验证用户实体
func (v *UserValidator) Validate(user *User) error {
    if user.ID == "" {
        return errors.New("user ID is required")
    }

    if user.Username == "" {
        return errors.New("username is required")
    }

    if len(user.Username) < 3 || len(user.Username) > 50 {
        return errors.New("username must be between 3 and 50 characters")
    }

    if user.Email == "" {
        return errors.New("email is required")
    }

    if !isValidEmail(user.Email) {
        return errors.New("invalid email format")
    }

    if user.Password == "" {
        return errors.New("password is required")
    }

    if len(user.Password) < 6 {
        return errors.New("password must be at least 6 characters")
    }

    if !isValidStatus(user.Status) {
        return errors.New("invalid user status")
    }

    return nil
}

// 验证邮箱格式
func isValidEmail(email string) bool {
    emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    return emailRegex.MatchString(email)
}

// 验证用户状态
func isValidStatus(status UserStatus) bool {
    switch status {
    case UserStatusActive, UserStatusInactive, UserStatusDeleted:
        return true
    default:
        return false
    }
}

// 密码加密器
type PasswordEncryptor struct{}

// 创建密码加密器
func NewPasswordEncryptor() *PasswordEncryptor {
    return &PasswordEncryptor{}
}

// 加密密码
func (e *PasswordEncryptor) Encrypt(password string) string {
    hash, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    return string(hash)
}

// 验证密码
func (e *PasswordEncryptor) Verify(hashedPassword, password string) bool {
    err := bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
    return err == nil
}
```

### 领域服务

```go
// internal/app/domain/services/user_domain_service.go
package services

import (
    "context"
    "errors"
    "fmt"

    "github.com/myapp/internal/app/domain/entities"
    "github.com/myapp/internal/app/domain/repositories"
    "github.com/myapp/internal/pkg/logger"
)

// 用户领域服务
type UserDomainService struct {
    userRepo repositories.UserRepository
    logger   *logger.Logger
}

// 创建用户领域服务
func NewUserDomainService(userRepo repositories.UserRepository, logger *logger.Logger) *UserDomainService {
    return &UserDomainService{
        userRepo: userRepo,
        logger:   logger,
    }
}

// 检查用户名可用性
func (s *UserDomainService) IsUsernameAvailable(ctx context.Context, username string) (bool, error) {
    exists, err := s.userRepo.ExistsByUsername(ctx, username)
    if err != nil {
        return false, fmt.Errorf("failed to check username availability: %w", err)
    }
    return !exists, nil
}

// 检查邮箱可用性
func (s *UserDomainService) IsEmailAvailable(ctx context.Context, email string) (bool, error) {
    exists, err := s.userRepo.ExistsByEmail(ctx, email)
    if err != nil {
        return false, fmt.Errorf("failed to check email availability: %w", err)
    }
    return !exists, nil
}

// 激活用户
func (s *UserDomainService) ActivateUser(ctx context.Context, userID string) error {
    user, err := s.userRepo.GetByID(ctx, userID)
    if err != nil {
        return fmt.Errorf("failed to get user: %w", err)
    }

    if user == nil {
        return errors.New("user not found")
    }

    if user.Status == entities.UserStatusActive {
        return errors.New("user is already active")
    }

    user.Status = entities.UserStatusActive
    user.UpdatedAt = time.Now()

    return s.userRepo.Update(ctx, user)
}

// 停用用户
func (s *UserDomainService) DeactivateUser(ctx context.Context, userID string) error {
    user, err := s.userRepo.GetByID(ctx, userID)
    if err != nil {
        return fmt.Errorf("failed to get user: %w", err)
    }

    if user == nil {
        return errors.New("user not found")
    }

    if user.Status == entities.UserStatusInactive {
        return errors.New("user is already inactive")
    }

    user.Status = entities.UserStatusInactive
    user.UpdatedAt = time.Now()

    return s.userRepo.Update(ctx, user)
}

// 检查用户权限
func (s *UserDomainService) CanUserPerformAction(ctx context.Context, userID string, action string) (bool, error) {
    user, err := s.userRepo.GetByID(ctx, userID)
    if err != nil {
        return false, fmt.Errorf("failed to get user: %w", err)
    }

    if user == nil {
        return false, errors.New("user not found")
    }

    if user.Status != entities.UserStatusActive {
        return false, errors.New("user is not active")
    }

    // 这里可以添加更复杂的权限检查逻辑
    return true, nil
}
```

## 事务管理

### 事务管理器

```go
// internal/pkg/transaction/transaction_manager.go
package transaction

import (
    "context"
    "database/sql"
    "fmt"

    "github.com/myapp/internal/pkg/logger"
)

// 事务管理器
type TransactionManager struct {
    db     *sql.DB
    logger *logger.Logger
}

// 创建事务管理器
func NewTransactionManager(db *sql.DB, logger *logger.Logger) *TransactionManager {
    return &TransactionManager{
        db:     db,
        logger: logger,
    }
}

// 事务上下文
type TransactionContext struct {
    Tx     *sql.Tx
    Level  sql.IsolationLevel
    ReadOnly bool
}

// 执行事务
func (tm *TransactionManager) ExecuteInTransaction(ctx context.Context, fn func(ctx context.Context) error) error {
    tx, err := tm.db.BeginTx(ctx, nil)
    if err != nil {
        return fmt.Errorf("failed to begin transaction: %w", err)
    }

    // 将事务注入到上下文中
    txCtx := context.WithValue(ctx, "transaction", tx)

    defer func() {
        if p := recover(); p != nil {
            // 发生panic，回滚事务
            if rbErr := tx.Rollback(); rbErr != nil {
                tm.logger.WithFields(map[string]interface{}{
                    "error":     rbErr,
                    "panic":     p,
                }).Error("Failed to rollback transaction after panic")
            } else {
                tm.logger.WithFields(map[string]interface{}{
                    "panic": p,
                }).Info("Transaction rolled back after panic")
            }
            panic(p) // 重新抛出panic
        }
    }()

    // 执行事务函数
    if err := fn(txCtx); err != nil {
        // 执行失败，回滚事务
        if rbErr := tx.Rollback(); rbErr != nil {
            tm.logger.WithFields(map[string]interface{}{
                "error":     rbErr,
                "func_error": err,
            }).Error("Failed to rollback transaction")
        }
        return fmt.Errorf("transaction failed: %w", err)
    }

    // 提交事务
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("failed to commit transaction: %w", err)
    }

    return nil
}

// 执行只读事务
func (tm *TransactionManager) ExecuteInReadOnlyTransaction(ctx context.Context, fn func(ctx context.Context) error) error {
    opts := &sql.TxOptions{
        Isolation: sql.LevelReadCommitted,
        ReadOnly:  true,
    }

    tx, err := tm.db.BeginTx(ctx, opts)
    if err != nil {
        return fmt.Errorf("failed to begin read-only transaction: %w", err)
    }

    // 将事务注入到上下文中
    txCtx := context.WithValue(ctx, "transaction", tx)

    // 执行事务函数
    if err := fn(txCtx); err != nil {
        // 执行失败，回滚事务
        if rbErr := tx.Rollback(); rbErr != nil {
            tm.logger.WithFields(map[string]interface{}{
                "error":     rbErr,
                "func_error": err,
            }).Error("Failed to rollback read-only transaction")
        }
        return fmt.Errorf("read-only transaction failed: %w", err)
    }

    // 提交事务
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("failed to commit read-only transaction: %w", err)
    }

    return nil
}

// 从上下文中获取事务
func GetTransactionFromContext(ctx context.Context) (*sql.Tx, bool) {
    tx, ok := ctx.Value("transaction").(*sql.Tx)
    return tx, ok
}

// 工作单元模式
type UnitOfWork struct {
    tx     *sql.Tx
    logger *logger.Logger
    committed bool
    rolledBack bool
}

// 创建工作单元
func NewUnitOfWork(tx *sql.Tx, logger *logger.Logger) *UnitOfWork {
    return &UnitOfWork{
        tx:     tx,
        logger: logger,
    }
}

// 提交工作单元
func (uow *UnitOfWork) Commit() error {
    if uow.committed || uow.rolledBack {
        return errors.New("transaction already completed")
    }

    if err := uow.tx.Commit(); err != nil {
        uow.logger.WithFields(map[string]interface{}{
            "error": err,
        }).Error("Failed to commit unit of work")
        return err
    }

    uow.committed = true
    return nil
}

// 回滚工作单元
func (uow *UnitOfWork) Rollback() error {
    if uow.committed || uow.rolledBack {
        return errors.New("transaction already completed")
    }

    if err := uow.tx.Rollback(); err != nil {
        uow.logger.WithFields(map[string]interface{}{
            "error": err,
        }).Error("Failed to rollback unit of work")
        return err
    }

    uow.rolledBack = true
    return nil
}
```

### 分布式事务支持

```go
// internal/pkg/transaction/distributed_transaction.go
package transaction

import (
    "context"
    "errors"
    "fmt"
    "sync"
    "time"

    "github.com/myapp/internal/pkg/logger"
)

// 分布式事务管理器
type DistributedTransactionManager struct {
    participants []*TransactionParticipant
    logger       *logger.Logger
    timeout      time.Duration
}

// 事务参与者
type TransactionParticipant struct {
    ID     string
    Prepare func(ctx context.Context) error
    Commit func(ctx context.Context) error
    Rollback func(ctx context.Context) error
}

// 创建分布式事务管理器
func NewDistributedTransactionManager(timeout time.Duration, logger *logger.Logger) *DistributedTransactionManager {
    return &DistributedTransactionManager{
        participants: make([]*TransactionParticipant, 0),
        logger:       logger,
        timeout:      timeout,
    }
}

// 添加参与者
func (dtm *DistributedTransactionManager) AddParticipant(participant *TransactionParticipant) {
    dtm.participants = append(dtm.participants, participant)
}

// 执行分布式事务（两阶段提交）
func (dtm *DistributedTransactionManager) ExecuteDistributedTransaction(ctx context.Context) error {
    // 创建带超时的上下文
    ctx, cancel := context.WithTimeout(ctx, dtm.timeout)
    defer cancel()

    // 第一阶段：准备阶段
    preparedParticipants := make([]*TransactionParticipant, 0)
    for _, participant := range dtm.participants {
        if err := participant.Prepare(ctx); err != nil {
            // 准备失败，回滚已准备的参与者
            dtm.rollbackPreparedParticipants(ctx, preparedParticipants)
            return fmt.Errorf("participant %s prepare failed: %w", participant.ID, err)
        }
        preparedParticipants = append(preparedParticipants, participant)
    }

    // 第二阶段：提交阶段
    for _, participant := range preparedParticipants {
        if err := participant.Commit(ctx); err != nil {
            dtm.logger.WithFields(map[string]interface{}{
                "error":       err,
                "participant": participant.ID,
            }).Error("Failed to commit participant, manual intervention required")
            return fmt.Errorf("participant %s commit failed: %w", participant.ID, err)
        }
    }

    dtm.logger.Info("Distributed transaction completed successfully")
    return nil
}

// 回滚已准备的参与者
func (dtm *DistributedTransactionManager) rollbackPreparedParticipants(ctx context.Context, participants []*TransactionParticipant) {
    var wg sync.WaitGroup
    errChan := make(chan error, len(participants))

    for _, participant := range participants {
        wg.Add(1)
        go func(p *TransactionParticipant) {
            defer wg.Done()
            if err := p.Rollback(ctx); err != nil {
                dtm.logger.WithFields(map[string]interface{}{
                    "error":       err,
                    "participant": p.ID,
                }).Error("Failed to rollback participant")
                errChan <- err
            }
        }(participant)
    }

    wg.Wait()
    close(errChan)

    // 收集错误
    var errors []error
    for err := range errChan {
        errors = append(errors, err)
    }

    if len(errors) > 0 {
        dtm.logger.WithFields(map[string]interface{}{
            "errors": errors,
        }).Error("Multiple rollback failures occurred")
    }
}

// 补偿事务模式
type CompensatingTransactionManager struct {
    steps       []*TransactionStep
    logger      *logger.Logger
}

// 事务步骤
type TransactionStep struct {
    Name         string
    Execute      func(ctx context.Context) error
    Compensate   func(ctx context.Context) error
}

// 创建补偿事务管理器
func NewCompensatingTransactionManager(logger *logger.Logger) *CompensatingTransactionManager {
    return &CompensatingTransactionManager{
        steps:  make([]*TransactionStep, 0),
        logger: logger,
    }
}

// 添加事务步骤
func (ctm *CompensatingTransactionManager) AddStep(step *TransactionStep) {
    ctm.steps = append(ctm.steps, step)
}

// 执行补偿事务
func (ctm *CompensatingTransactionManager) Execute(ctx context.Context) error {
    executedSteps := make([]*TransactionStep, 0)

    // 执行所有步骤
    for _, step := range ctm.steps {
        if err := step.Execute(ctx); err != nil {
            // 执行失败，启动补偿
            ctm.executeCompensation(ctx, executedSteps)
            return fmt.Errorf("step %s failed: %w", step.Name, err)
        }
        executedSteps = append(executedSteps, step)
    }

    return nil
}

// 执行补偿操作
func (ctm *CompensatingTransactionManager) executeCompensation(ctx context.Context, steps []*TransactionStep) {
    // 按相反顺序执行补偿
    for i := len(steps) - 1; i >= 0; i-- {
        step := steps[i]
        if err := step.Compensate(ctx); err != nil {
            ctm.logger.WithFields(map[string]interface{}{
                "error": err,
                "step":  step.Name,
            }).Error("Failed to compensate transaction step")
        }
    }
}
```

## 最佳实践总结

### 分层架构最佳实践

1. **清晰的层次边界**：每层都有明确的职责和边界
2. **单向依赖**：依赖关系严格单向，避免循环依赖
3. **依赖倒置**：上层依赖下层的抽象，而不是具体实现
4. **接口隔离**：每层都通过接口进行通信
5. **关注点分离**：每层只关注特定的功能领域

### 性能优化最佳实践

1. **缓存策略**：在适当的层实施缓存策略
2. **批量处理**：减少跨层调用次数
3. **异步处理**：对于耗时的操作使用异步处理
4. **连接池**：使用连接池管理数据库连接
5. **监控和调优**：持续监控各层性能并优化

### 测试策略最佳实践

1. **单元测试**：每层都要有完整的单元测试覆盖
2. **集成测试**：测试层与层之间的集成
3. **契约测试**：确保层之间的接口契约
4. **性能测试**：测试各层和整体系统的性能
5. **模拟测试**：使用mock对象隔离被测试的层

### 错误处理最佳实践

1. **统一错误处理**：在每层实施统一的错误处理策略
2. **错误转换**：在各层之间转换错误类型和格式
3. **错误日志**：记录足够的错误信息用于调试
4. **用户友好**：向用户提供友好的错误信息
5. **恢复机制**：实现适当的错误恢复机制

通过遵循这些最佳实践，可以构建高质量、可维护、可扩展的分层架构应用程序。关键是要根据具体的业务需求和团队情况，选择合适的分层模式和实现方式。