# Go架构模式实战

## 目录
- [架构模式概述](#架构模式概述)
- [分层架构](#分层架构)
- [微服务架构](#微服务架构)
- [事件驱动架构](#事件驱动架构)
- [CQRS架构](#cqrs架构)
- [六边形架构](#六边形架构)
- [洋葱架构](#洋葱架构)
- [干净架构](#干净架构)
- [Serverless架构](#serverless架构)
- [架构模式选择指南](#架构模式选择指南)

## 架构模式概述

### 什么是架构模式
架构模式是软件系统中高层次的组织结构，它定义了系统的基本结构、组件之间的关系以及组件与环境之间的交互方式。架构模式关注的是系统的整体结构和组织方式。

### 架构模式的重要性
- **系统可维护性**：良好的架构使系统更容易理解和维护
- **可扩展性**：支持系统在需求变化时的平滑扩展
- **可测试性**：便于进行单元测试和集成测试
- **性能优化**：为性能优化提供基础结构
- **团队协作**：清晰的架构边界有助于团队分工协作

### Go语言架构特点
- **简洁性**：Go的简洁语法适合构建清晰的架构
- **并发性**：原生并发支持适合构建高性能系统
- **接口驱动**：基于接口的设计便于解耦和测试
- **模块化**：包管理系统支持模块化开发

## 分层架构

### 架构层次
```
┌─────────────────────────────────────┐
│           表现层 (Presentation)        │
├─────────────────────────────────────┤
│           业务层 (Business)             │
├─────────────────────────────────────┤
│         数据访问层 (Data Access)        │
├─────────────────────────────────────┤
│           基础设施层 (Infrastructure)    │
└─────────────────────────────────────┘
```

### 实现示例

```go
// domain/entity/user.go - 领域实体
package entity

import "time"

type User struct {
    ID        int       `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

func (u *User) Validate() error {
    if u.Username == "" {
        return errors.New("username cannot be empty")
    }
    if u.Email == "" {
        return errors.New("email cannot be empty")
    }
    return nil
}

// domain/repository/user_repository.go - 仓储接口
package repository

import "github.com/yourproject/domain/entity"

type UserRepository interface {
    FindByID(id int) (*entity.User, error)
    FindByEmail(email string) (*entity.User, error)
    Save(user *entity.User) error
    Update(user *entity.User) error
    Delete(id int) error
}

// domain/service/user_service.go - 业务服务
package service

import (
    "github.com/yourproject/domain/entity"
    "github.com/yourproject/domain/repository"
)

type UserService struct {
    userRepo repository.UserRepository
}

func NewUserService(userRepo repository.UserRepository) *UserService {
    return &UserService{userRepo: userRepo}
}

func (s *UserService) CreateUser(username, email string) (*entity.User, error) {
    user := &entity.User{
        Username:  username,
        Email:     email,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }

    if err := user.Validate(); err != nil {
        return nil, err
    }

    existingUser, err := s.userRepo.FindByEmail(email)
    if err == nil && existingUser != nil {
        return nil, errors.New("user already exists")
    }

    if err := s.userRepo.Save(user); err != nil {
        return nil, err
    }

    return user, nil
}

// infrastructure/persistence/mysql_user_repository.go - 数据访问层实现
package persistence

import (
    "database/sql"
    "github.com/yourproject/domain/entity"
    "github.com/yourproject/domain/repository"
)

type MySQLUserRepository struct {
    db *sql.DB
}

func NewMySQLUserRepository(db *sql.DB) repository.UserRepository {
    return &MySQLUserRepository{db: db}
}

func (r *MySQLUserRepository) FindByID(id int) (*entity.User, error) {
    var user entity.User
    err := r.db.QueryRow(
        "SELECT id, username, email, created_at, updated_at FROM users WHERE id = ?",
        id,
    ).Scan(&user.ID, &user.Username, &user.Email, &user.CreatedAt, &user.UpdatedAt)

    if err != nil {
        return nil, err
    }

    return &user, nil
}

// interface/controller/user_controller.go - 表现层
package controller

import (
    "encoding/json"
    "net/http"
    "github.com/yourproject/domain/service"
)

type UserController struct {
    userService *service.UserService
}

func NewUserController(userService *service.UserService) *UserController {
    return &UserController{userService: userService}
}

func (c *UserController) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req struct {
        Username string `json:"username"`
        Email    string `json:"email"`
    }

    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    user, err := c.userService.CreateUser(req.Username, req.Email)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}
```

### 分层架构的优点
- **关注点分离**：每层有明确的职责
- **可维护性**：修改一层不会影响其他层
- **可测试性**：每层都可以独立测试
- **重用性**：业务逻辑可以在不同的表现层重用

## 微服务架构

### 架构特点
- **服务自治**：每个服务独立部署和运行
- **技术异构**：不同服务可以使用不同技术栈
- **弹性伸缩**：根据负载独立扩展服务
- **故障隔离**：单个服务故障不会影响整个系统

### 实现示例

```go
// user-service/main.go - 用户服务入口
package main

import (
    "github.com/yourproject/user-service/internal/handler"
    "github.com/yourproject/user-service/internal/repository"
    "github.com/yourproject/user-service/internal/service"
    "github.com/gin-gonic/gin"
)

func main() {
    // 初始化依赖
    userRepo := repository.NewMySQLUserRepository(getDB())
    userService := service.NewUserService(userRepo)
    userHandler := handler.NewUserHandler(userService)

    // 创建路由
    router := gin.Default()

    // API路由
    api := router.Group("/api/v1")
    {
        users := api.Group("/users")
        {
            users.POST("", userHandler.CreateUser)
            users.GET("/:id", userHandler.GetUser)
            users.PUT("/:id", userHandler.UpdateUser)
            users.DELETE("/:id", userHandler.DeleteUser)
        }
    }

    // 健康检查
    router.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "healthy"})
    })

    // 启动服务
    router.Run(":8081")
}

// order-service/main.go - 订单服务入口
package main

import (
    "github.com/yourproject/order-service/internal/handler"
    "github.com/yourproject/order-service/internal/repository"
    "github.com/yourproject/order-service/internal/service"
    "github.com/gin-gonic/gin"
)

func main() {
    // 初始化依赖
    orderRepo := repository.NewPostgresOrderRepository(getDB())
    userClient := service.NewUserServiceClient("http://user-service:8081")
    orderService := service.NewOrderService(orderRepo, userClient)
    orderHandler := handler.NewOrderHandler(orderService)

    // 创建路由
    router := gin.Default()

    // API路由
    api := router.Group("/api/v1")
    {
        orders := api.Group("/orders")
        {
            orders.POST("", orderHandler.CreateOrder)
            orders.GET("/:id", orderHandler.GetOrder)
            orders.GET("/user/:userId", orderHandler.GetUserOrders)
        }
    }

    // 启动服务
    router.Run(":8082")
}

// api-gateway/main.go - API网关
package main

import (
    "github.com/yourproject/api-gateway/internal/proxy"
    "github.com/yourproject/api-gateway/internal/middleware"
    "github.com/gin-gonic/gin"
)

func main() {
    router := gin.Default()

    // 中间件
    router.Use(middleware.CORS())
    router.Use(middleware.RateLimit())
    router.Use(middleware.Authentication())

    // 服务发现
    serviceRegistry := proxy.NewServiceRegistry()
    serviceRegistry.Register("user-service", "http://user-service:8081")
    serviceRegistry.Register("order-service", "http://order-service:8082")

    // 路由代理
    userProxy := proxy.NewServiceProxy(serviceRegistry, "user-service")
    orderProxy := proxy.NewServiceProxy(serviceRegistry, "order-service")

    // API路由
    api := router.Group("/api/v1")
    {
        api.Any("/users/*path", userProxy.Proxy)
        api.Any("/orders/*path", orderProxy.Proxy)
    }

    // 启动网关
    router.Run(":8080")
}
```

### 服务间通信

```go
// service-discovery/service_registry.go - 服务注册中心
package servicediscovery

import (
    "sync"
    "time"
)

type ServiceInstance struct {
    ID        string    `json:"id"`
    Name      string    `json:"name"`
    Address   string    `json:"address"`
    Port      int       `json:"port"`
    Version   string    `json:"version"`
    Metadata  map[string]string `json:"metadata"`
    LastCheck time.Time `json:"last_check"`
}

type ServiceRegistry struct {
    services map[string][]*ServiceInstance
    mutex    sync.RWMutex
}

func NewServiceRegistry() *ServiceRegistry {
    return &ServiceRegistry{
        services: make(map[string][]*ServiceInstance),
    }
}

func (r *ServiceRegistry) Register(service *ServiceInstance) error {
    r.mutex.Lock()
    defer r.mutex.Unlock()

    service.ID = generateID()
    service.LastCheck = time.Now()

    r.services[service.Name] = append(r.services[service.Name], service)
    return nil
}

func (r *ServiceRegistry) Discover(serviceName string) ([]*ServiceInstance, error) {
    r.mutex.RLock()
    defer r.mutex.RUnlock()

    instances, exists := r.services[serviceName]
    if !exists {
        return nil, errors.New("service not found")
    }

    // 过滤健康的实例
    var healthyInstances []*ServiceInstance
    for _, instance := range instances {
        if time.Since(instance.LastCheck) < 30*time.Second {
            healthyInstances = append(healthyInstances, instance)
        }
    }

    return healthyInstances, nil
}

// service-communication/grpc_client.go - gRPC客户端
package grpcclient

import (
    "google.golang.org/grpc"
    "context"
    "time"
)

type GRPCClientManager struct {
    connections map[string]*grpc.ClientConn
    mutex       sync.RWMutex
}

func NewGRPCClientManager() *GRPCClientManager {
    return &GRPCClientManager{
        connections: make(map[string]*grpc.ClientConn),
    }
}

func (m *GRPCClientManager) GetConnection(serviceName string, registry *ServiceRegistry) (*grpc.ClientConn, error) {
    m.mutex.RLock()
    if conn, exists := m.connections[serviceName]; exists {
        m.mutex.RUnlock()
        return conn, nil
    }
    m.mutex.RUnlock()

    instances, err := registry.Discover(serviceName)
    if err != nil {
        return nil, err
    }

    if len(instances) == 0 {
        return nil, errors.New("no available instances")
    }

    instance := instances[0]
    address := fmt.Sprintf("%s:%d", instance.Address, instance.Port)

    conn, err := grpc.Dial(address, grpc.WithInsecure())
    if err != nil {
        return nil, err
    }

    m.mutex.Lock()
    m.connections[serviceName] = conn
    m.mutex.Unlock()

    return conn, nil
}

// service-communication/http_client.go - HTTP客户端
package httpclient

import (
    "net/http"
    "time"
    "context"
)

type ServiceClient struct {
    baseClient *http.Client
    registry   *ServiceRegistry
    loadBalancer *LoadBalancer
}

func NewServiceClient(registry *ServiceRegistry) *ServiceClient {
    return &ServiceClient{
        baseClient: &http.Client{
            Timeout: 30 * time.Second,
        },
        registry:    registry,
        loadBalancer: NewRoundRobinLoadBalancer(),
    }
}

func (c *ServiceClient) CallService(ctx context.Context, serviceName, path string, method string, body interface{}) (*http.Response, error) {
    instances, err := c.registry.Discover(serviceName)
    if err != nil {
        return nil, err
    }

    instance := c.loadBalancer.Select(instances)
    if instance == nil {
        return nil, errors.New("no available instances")
    }

    url := fmt.Sprintf("http://%s:%d%s", instance.Address, instance.Port, path)

    req, err := http.NewRequestWithContext(ctx, method, url, nil)
    if err != nil {
        return nil, err
    }

    return c.baseClient.Do(req)
}
```

### 配置管理

```go
// config/config.go - 配置管理
package config

import (
    "github.com/spf13/viper"
    "sync"
)

type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Redis    RedisConfig    `mapstructure:"redis"`
    Service  ServiceConfig  `mapstructure:"service"`
}

type ServerConfig struct {
    Port         int    `mapstructure:"port"`
    ReadTimeout  int    `mapstructure:"read_timeout"`
    WriteTimeout int    `mapstructure:"write_timeout"`
    Mode         string `mapstructure:"mode"`
}

type DatabaseConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Database string `mapstructure:"database"`
    Username string `mapstructure:"username"`
    Password string `mapstructure:"password"`
}

type RedisConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Password string `mapstructure:"password"`
    DB       int    `mapstructure:"db"`
}

type ServiceConfig struct {
    Name        string `mapstructure:"name"`
    Version     string `mapstructure:"version"`
    Environment string `mapstructure:"environment"`
}

var (
    instance *Config
    once     sync.Once
)

func Load(configPath string) (*Config, error) {
    var err error
    once.Do(func() {
        instance, err = loadConfig(configPath)
    })
    return instance, err
}

func loadConfig(configPath string) (*Config, error) {
    viper.SetConfigFile(configPath)
    viper.AutomaticEnv()

    if err := viper.ReadInConfig(); err != nil {
        return nil, err
    }

    var config Config
    if err := viper.Unmarshal(&config); err != nil {
        return nil, err
    }

    return &config, nil
}

func Get() *Config {
    if instance == nil {
        panic("Config not loaded. Call Load() first.")
    }
    return instance
}
```

## 事件驱动架构

### 架构组件
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Event Producer │    │   Event Broker  │    │  Event Consumer │
│                 │    │                 │    │                 │
│  1. Produce     │───▶│  2. Store &     │───▶│  3. Process     │
│     Events      │    │     Forward     │    │     Events      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 实现示例

```go
// event/event.go - 事件定义
package event

import "time"

type Event struct {
    ID        string                 `json:"id"`
    Type      string                 `json:"type"`
    Source    string                 `json:"source"`
    Timestamp time.Time              `json:"timestamp"`
    Data      map[string]interface{} `json:"data"`
    Version   string                 `json:"version"`
}

type EventHandler interface {
    Handle(event *Event) error
}

// producer/event_producer.go - 事件生产者
package producer

import (
    "github.com/yourproject/event"
    "github.com/streadway/amqp"
)

type EventProducer struct {
    connection *amqp.Connection
    channel    *amqp.Channel
    exchange   string
}

func NewEventProducer(amqpURL, exchange string) (*EventProducer, error) {
    conn, err := amqp.Dial(amqpURL)
    if err != nil {
        return nil, err
    }

    ch, err := conn.Channel()
    if err != nil {
        conn.Close()
        return nil, err
    }

    err = ch.ExchangeDeclare(
        exchange,
        "topic",
        true,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        ch.Close()
        conn.Close()
        return nil, err
    }

    return &EventProducer{
        connection: conn,
        channel:    ch,
        exchange:   exchange,
    }, nil
}

func (p *EventProducer) Publish(eventType, routingKey string, data map[string]interface{}) error {
    event := &event.Event{
        ID:        generateID(),
        Type:      eventType,
        Source:    "user-service",
        Timestamp: time.Now(),
        Data:      data,
        Version:   "1.0",
    }

    body, err := json.Marshal(event)
    if err != nil {
        return err
    }

    return p.channel.Publish(
        p.exchange,
        routingKey,
        false,
        false,
        amqp.Publishing{
            ContentType: "application/json",
            Body:        body,
        },
    )
}

// consumer/event_consumer.go - 事件消费者
package consumer

import (
    "github.com/yourproject/event"
    "github.com/streadway/amqp"
)

type EventConsumer struct {
    connection *amqp.Connection
    channel    *amqp.Channel
    queue      string
    handlers   map[string]event.EventHandler
}

func NewEventConsumer(amqpURL, queue, exchange string, routingKeys []string) (*EventConsumer, error) {
    conn, err := amqp.Dial(amqpURL)
    if err != nil {
        return nil, err
    }

    ch, err := conn.Channel()
    if err != nil {
        conn.Close()
        return nil, err
    }

    q, err := ch.QueueDeclare(
        queue,
        true,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        ch.Close()
        conn.Close()
        return nil, err
    }

    for _, routingKey := range routingKeys {
        err = ch.QueueBind(
            q.Name,
            routingKey,
            exchange,
            false,
            nil,
        )
        if err != nil {
            ch.Close()
            conn.Close()
            return nil, err
        }
    }

    return &EventConsumer{
        connection: conn,
        channel:    ch,
        queue:      q.Name,
        handlers:   make(map[string]event.EventHandler),
    }, nil
}

func (c *EventConsumer) RegisterHandler(eventType string, handler event.EventHandler) {
    c.handlers[eventType] = handler
}

func (c *EventConsumer) Start() error {
    msgs, err := c.channel.Consume(
        c.queue,
        "",
        true,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        return err
    }

    go func() {
        for msg := range msgs {
            c.handleMessage(msg)
        }
    }()

    return nil
}

func (c *EventConsumer) handleMessage(msg amqp.Delivery) {
    var event event.Event
    if err := json.Unmarshal(msg.Body, &event); err != nil {
        log.Printf("Failed to unmarshal event: %v", err)
        return
    }

    handler, exists := c.handlers[event.Type]
    if !exists {
        log.Printf("No handler for event type: %s", event.Type)
        return
    }

    if err := handler.Handle(&event); err != nil {
        log.Printf("Failed to handle event: %v", err)
    }
}

// event-sourcing/event_store.go - 事件存储
package eventsourcing

import (
    "encoding/json"
    "github.com/yourproject/event"
)

type EventStore interface {
    SaveEvents(aggregateID string, events []*event.Event) error
    GetEvents(aggregateID string) ([]*event.Event, error)
}

type InMemoryEventStore struct {
    events map[string][]*event.Event
    mutex  sync.RWMutex
}

func NewInMemoryEventStore() *InMemoryEventStore {
    return &InMemoryEventStore{
        events: make(map[string][]*event.Event),
    }
}

func (s *InMemoryEventStore) SaveEvents(aggregateID string, events []*event.Event) error {
    s.mutex.Lock()
    defer s.mutex.Unlock()

    s.events[aggregateID] = append(s.events[aggregateID], events...)
    return nil
}

func (s *InMemoryEventStore) GetEvents(aggregateID string) ([]*event.Event, error) {
    s.mutex.RLock()
    defer s.mutex.RUnlock()

    events, exists := s.events[aggregateID]
    if !exists {
        return nil, errors.New("aggregate not found")
    }

    // 返回副本
    result := make([]*event.Event, len(events))
    copy(result, events)
    return result, nil
}

// aggregate/aggregate_root.go - 聚合根
package aggregate

import (
    "github.com/yourproject/event"
    "github.com/yourproject/eventsourcing"
)

type AggregateRoot struct {
    ID      string
    Version int
    Changes []*event.Event
}

func (a *AggregateRoot) ApplyChange(event *event.Event) {
    event.Version = a.Version + 1
    a.Changes = append(a.Changes, event)
    a.Version = event.Version
}

func (a *AggregateRoot) LoadFromHistory(events []*event.Event) {
    for _, event := range events {
        a.ApplyChange(event)
    }
    a.Changes = nil // 清空未提交的变更
}

type UserAggregate struct {
    AggregateRoot
    Username string
    Email    string
    Active   bool
}

func NewUserAggregate(id, username, email string) *UserAggregate {
    user := &UserAggregate{
        AggregateRoot: AggregateRoot{ID: id},
        Username:      username,
        Email:         email,
        Active:        true,
    }

    user.ApplyChange(&event.Event{
        Type: "UserCreated",
        Data: map[string]interface{}{
            "username": username,
            "email":    email,
        },
    })

    return user
}

func (u *UserAggregate) UpdateEmail(newEmail string) error {
    if u.Email == newEmail {
        return errors.New("email already set")
    }

    u.ApplyChange(&event.Event{
        Type: "UserEmailUpdated",
        Data: map[string]interface{}{
            "old_email": u.Email,
            "new_email": newEmail,
        },
    })

    u.Email = newEmail
    return nil
}

func (u *UserAggregate) Deactivate() {
    u.ApplyChange(&event.Event{
        Type: "UserDeactivated",
        Data: map[string]interface{}{
            "reason": "user deactivated",
        },
    })

    u.Active = false
}

func (u *UserAggregate) Save(store eventsourcing.EventStore) error {
    if len(u.Changes) > 0 {
        return store.SaveEvents(u.ID, u.Changes)
    }
    return nil
}
```

## CQRS架构

### 架构原理
CQRS (Command Query Responsibility Segregation) 是一种将命令（写操作）和查询（读操作）分离的架构模式。

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Command Side  │    │   Event Bus     │    │   Query Side    │
│                 │    │                 │    │                 │
│  1. Handle     │    │  2. Publish     │    │  3. Update      │
│    Commands     │───▶│    Events       │───▶│  Read Models    │
│                 │    │                 │    │                 │
│  4. Update     │    │                 │    │  5. Serve       │
│  Write Model   │    │                 │    │    Queries      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 实现示例

```go
// commands/user_commands.go - 命令定义
package commands

type CreateUserCommand struct {
    Username string
    Email    string
}

type UpdateUserEmailCommand struct {
    UserID   string
    NewEmail string
}

type DeactivateUserCommand struct {
    UserID  string
    Reason  string
}

// handlers/user_command_handler.go - 命令处理器
package handlers

import (
    "github.com/yourproject/aggregate"
    "github.com/yourproject/commands"
    "github.com/yourproject/events"
)

type UserCommandHandler struct {
    userRepo     UserRepository
    eventBus     EventBus
    eventStore   EventStore
}

func NewUserCommandHandler(userRepo UserRepository, eventBus EventBus, eventStore EventStore) *UserCommandHandler {
    return &UserCommandHandler{
        userRepo:   userRepo,
        eventBus:   eventBus,
        eventStore: eventStore,
    }
}

func (h *UserCommandHandler) HandleCreateUser(cmd *commands.CreateUserCommand) error {
    // 检查用户是否已存在
    existingUser, err := h.userRepo.FindByEmail(cmd.Email)
    if err == nil && existingUser != nil {
        return errors.New("user already exists")
    }

    // 创建用户聚合
    user := aggregate.NewUserAggregate(generateID(), cmd.Username, cmd.Email)

    // 保存事件
    if err := user.Save(h.eventStore); err != nil {
        return err
    }

    // 发布事件
    for _, change := range user.Changes {
        if err := h.eventBus.Publish(change); err != nil {
            return err
        }
    }

    return nil
}

func (h *UserCommandHandler) HandleUpdateUserEmail(cmd *commands.UpdateUserEmailCommand) error {
    // 获取用户事件历史
    eventHistory, err := h.eventStore.GetEvents(cmd.UserID)
    if err != nil {
        return err
    }

    // 重建用户聚合
    user := &aggregate.UserAggregate{}
    user.LoadFromHistory(eventHistory)

    // 更新邮箱
    if err := user.UpdateEmail(cmd.NewEmail); err != nil {
        return err
    }

    // 保存事件
    if err := user.Save(h.eventStore); err != nil {
        return err
    }

    // 发布事件
    for _, change := range user.Changes {
        if err := h.eventBus.Publish(change); err != nil {
            return err
        }
    }

    return nil
}

// queries/user_queries.go - 查询定义
package queries

type GetUserQuery struct {
    UserID string
}

type GetUserByEmailQuery struct {
    Email string
}

type ListUsersQuery struct {
    Page     int
    PageSize int
    Active   *bool
}

// handlers/user_query_handler.go - 查询处理器
package handlers

import (
    "github.com/yourproject/queries"
    "github.com/yourproject/read_model"
)

type UserQueryHandler struct {
    userReadRepo UserReadRepository
}

func NewUserQueryHandler(userReadRepo UserReadRepository) *UserQueryHandler {
    return &UserQueryHandler{
        userReadRepo: userReadRepo,
    }
}

func (h *UserQueryHandler) HandleGetUser(query *queries.GetUserQuery) (*read_model.UserReadModel, error) {
    return h.userReadRepo.FindByID(query.UserID)
}

func (h *UserQueryHandler) HandleGetUserByEmail(query *queries.GetUserByEmailQuery) (*read_model.UserReadModel, error) {
    return h.userReadRepo.FindByEmail(query.Email)
}

func (h *UserQueryHandler) HandleListUsers(query *queries.ListUsersQuery) ([]*read_model.UserReadModel, int, error) {
    return h.userReadRepo.List(query.Page, query.PageSize, query.Active)
}

// read_model/user_read_model.go - 读模型
package read_model

type UserReadModel struct {
    ID        string    `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    Active    bool      `json:"active"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

// read_model/user_read_repository.go - 读模型仓储
package read_model

type UserReadRepository interface {
    FindByID(id string) (*UserReadModel, error)
    FindByEmail(email string) (*UserReadModel, error)
    List(page, pageSize int, active *bool) ([]*UserReadModel, int, error)
    Save(user *UserReadModel) error
    Update(user *UserReadModel) error
    Delete(id string) error
}

// projections/user_projection.go - 投影
package projections

import (
    "github.com/yourproject/event"
    "github.com/yourproject/read_model"
)

type UserProjection struct {
    readRepo read_model.UserReadRepository
}

func NewUserProjection(readRepo read_model.UserReadRepository) *UserProjection {
    return &UserProjection{readRepo: readRepo}
}

func (p *UserProjection) Handle(evt *event.Event) error {
    switch evt.Type {
    case "UserCreated":
        return p.handleUserCreated(evt)
    case "UserEmailUpdated":
        return p.handleUserEmailUpdated(evt)
    case "UserDeactivated":
        return p.handleUserDeactivated(evt)
    default:
        return nil
    }
}

func (p *UserProjection) handleUserCreated(evt *event.Event) error {
    username := evt.Data["username"].(string)
    email := evt.Data["email"].(string)

    user := &read_model.UserReadModel{
        ID:        evt.ID,
        Username:  username,
        Email:     email,
        Active:    true,
        CreatedAt: evt.Timestamp,
        UpdatedAt: evt.Timestamp,
    }

    return p.readRepo.Save(user)
}

func (p *UserProjection) handleUserEmailUpdated(evt *event.Event) error {
    userID := evt.ID
    newEmail := evt.Data["new_email"].(string)

    user, err := p.readRepo.FindByID(userID)
    if err != nil {
        return err
    }

    user.Email = newEmail
    user.UpdatedAt = evt.Timestamp

    return p.readRepo.Update(user)
}

func (p *UserProjection) handleUserDeactivated(evt *event.Event) error {
    userID := evt.ID

    user, err := p.readRepo.FindByID(userID)
    if err != nil {
        return err
    }

    user.Active = false
    user.UpdatedAt = evt.Timestamp

    return p.readRepo.Update(user)
}
```

## 六边形架构

### 架构结构
```
┌─────────────────────────────────────────┐
│                Application              │
├─────────────────────────────────────────┤
│              Domain Logic              │
│                                       │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │   Ports     │  │  Domain Model   │  │
│  │  (Interfaces)│  │                 │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│            Infrastructure              │
│                                       │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │Adapters     │  │   Frameworks    │  │
│  │ (Primary)   │  │ (Secondary)      │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

### 实现示例

```go
// domain/user.go - 领域模型
package domain

import "errors"

type User struct {
    id       UserID
    username Username
    email    Email
    active   bool
}

func NewUser(username Username, email Email) (*User, error) {
    if username.IsEmpty() {
        return nil, errors.New("username cannot be empty")
    }

    if email.IsEmpty() {
        return nil, errors.New("email cannot be empty")
    }

    return &User{
        id:       NewUserID(),
        username: username,
        email:    email,
        active:   true,
    }, nil
}

func (u *User) ID() UserID {
    return u.id
}

func (u *User) Username() Username {
    return u.username
}

func (u *User) Email() Email {
    return u.email
}

func (u *User) IsActive() bool {
    return u.active
}

func (u *User) UpdateEmail(newEmail Email) error {
    if newEmail.IsEmpty() {
        return errors.New("email cannot be empty")
    }

    if u.email.Equals(newEmail) {
        return errors.New("email already set")
    }

    u.email = newEmail
    return nil
}

func (u *User) Deactivate() {
    u.active = false
}

// domain/value_objects.go - 值对象
package domain

import (
    "errors"
    "regexp"
)

type UserID struct {
    value string
}

func NewUserID() UserID {
    return UserID{value: generateUUID()}
}

func (id UserID) String() string {
    return id.value
}

type Username struct {
    value string
}

func NewUsername(value string) (Username, error) {
    if len(value) < 3 {
        return Username{}, errors.New("username too short")
    }
    if len(value) > 50 {
        return Username{}, errors.New("username too long")
    }

    if !regexp.MustCompile(`^[a-zA-Z0-9_]+$`).MatchString(value) {
        return Username{}, errors.New("username contains invalid characters")
    }

    return Username{value: value}, nil
}

func (u Username) String() string {
    return u.value
}

func (u Username) IsEmpty() bool {
    return u.value == ""
}

type Email struct {
    value string
}

func NewEmail(value string) (Email, error) {
    if !regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`).MatchString(value) {
        return Email{}, errors.New("invalid email format")
    }

    return Email{value: value}, nil
}

func (e Email) String() string {
    return e.value
}

func (e Email) IsEmpty() bool {
    return e.value == ""
}

func (e Email) Equals(other Email) bool {
    return e.value == other.value
}

// domain/ports/user_repository.go - 端口（接口）
package ports

import "github.com/yourproject/domain"

type UserRepository interface {
    FindByID(id domain.UserID) (*domain.User, error)
    FindByEmail(email domain.Email) (*domain.User, error)
    Save(user *domain.User) error
    Update(user *domain.User) error
    Delete(id domain.UserID) error
}

type UserService interface {
    CreateUser(username domain.Username, email domain.Email) (*domain.User, error)
    GetUserByID(id domain.UserID) (*domain.User, error)
    GetUserByEmail(email domain.Email) (*domain.User, error)
    UpdateUserEmail(id domain.UserID, newEmail domain.Email) error
    DeactivateUser(id domain.UserID) error
}

// domain/ports/notification_service.go - 通知服务端口
package ports

type NotificationService interface {
    SendEmail(to, subject, body string) error
    SendSMS(to, message string) error
}

// infrastructure/adapters/mysql_user_repository.go - 适配器
package adapters

import (
    "database/sql"
    "github.com/yourproject/domain"
    "github.com/yourproject/ports"
)

type MySQLUserRepository struct {
    db *sql.DB
}

func NewMySQLUserRepository(db *sql.DB) ports.UserRepository {
    return &MySQLUserRepository{db: db}
}

func (r *MySQLUserRepository) FindByID(id domain.UserID) (*domain.User, error) {
    var user domain.User
    err := r.db.QueryRow(
        "SELECT id, username, email, active FROM users WHERE id = ?",
        id.String(),
    ).Scan(&user.id, &user.username, &user.email, &user.active)

    if err != nil {
        return nil, err
    }

    return &user, nil
}

func (r *MySQLUserRepository) FindByEmail(email domain.Email) (*domain.User, error) {
    var user domain.User
    err := r.db.QueryRow(
        "SELECT id, username, email, active FROM users WHERE email = ?",
        email.String(),
    ).Scan(&user.id, &user.username, &user.email, &user.active)

    if err != nil {
        return nil, err
    }

    return &user, nil
}

func (r *MySQLUserRepository) Save(user *domain.User) error {
    _, err := r.db.Exec(
        "INSERT INTO users (id, username, email, active) VALUES (?, ?, ?, ?)",
        user.ID().String(),
        user.Username().String(),
        user.Email().String(),
        user.IsActive(),
    )
    return err
}

// infrastructure/adapters/email_notification_service.go - 通知适配器
package adapters

import (
    "github.com/yourproject/ports"
)

type EmailNotificationService struct {
    smtpHost     string
    smtpPort     int
    username     string
    password     string
}

func NewEmailNotificationService(smtpHost string, smtpPort int, username, password string) ports.NotificationService {
    return &EmailNotificationService{
        smtpHost: smtpHost,
        smtpPort: smtpPort,
        username: username,
        password: password,
    }
}

func (s *EmailNotificationService) SendEmail(to, subject, body string) error {
    // 实现邮件发送逻辑
    return nil
}

func (s *EmailNotificationService) SendSMS(to, message string) error {
    // 不支持SMS，返回错误
    return errors.New("SMS not supported by email service")
}

// application/user_service_impl.go - 应用服务
package application

import (
    "github.com/yourproject/domain"
    "github.com/yourproject/ports"
)

type UserServiceImpl struct {
    userRepo         ports.UserRepository
    notificationSvc  ports.NotificationService
}

func NewUserServiceImpl(userRepo ports.UserRepository, notificationSvc ports.NotificationService) ports.UserService {
    return &UserServiceImpl{
        userRepo:        userRepo,
        notificationSvc: notificationSvc,
    }
}

func (s *UserServiceImpl) CreateUser(username domain.Username, email domain.Email) (*domain.User, error) {
    // 检查用户是否已存在
    existingUser, err := s.userRepo.FindByEmail(email)
    if err == nil && existingUser != nil {
        return nil, errors.New("user already exists")
    }

    // 创建用户
    user, err := domain.NewUser(username, email)
    if err != nil {
        return nil, err
    }

    // 保存用户
    if err := s.userRepo.Save(user); err != nil {
        return nil, err
    }

    // 发送欢迎邮件
    go func() {
        if err := s.notificationSvc.SendEmail(
            email.String(),
            "Welcome to our platform!",
            "Thank you for registering.",
        ); err != nil {
            log.Printf("Failed to send welcome email: %v", err)
        }
    }()

    return user, nil
}

func (s *UserServiceImpl) UpdateUserEmail(id domain.UserID, newEmail domain.Email) error {
    user, err := s.userRepo.FindByID(id)
    if err != nil {
        return err
    }

    if err := user.UpdateEmail(newEmail); err != nil {
        return err
    }

    return s.userRepo.Update(user)
}

// interfaces/http/user_controller.go - HTTP适配器
package http

import (
    "github.com/yourproject/domain"
    "github.com/yourproject/ports"
    "github.com/gin-gonic/gin"
)

type UserController struct {
    userService ports.UserService
}

func NewUserController(userService ports.UserService) *UserController {
    return &UserController{userService: userService}
}

func (c *UserController) CreateUser(ctx *gin.Context) {
    var req struct {
        Username string `json:"username"`
        Email    string `json:"email"`
    }

    if err := ctx.ShouldBindJSON(&req); err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    username, err := domain.NewUsername(req.Username)
    if err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    email, err := domain.NewEmail(req.Email)
    if err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    user, err := c.userService.CreateUser(username, email)
    if err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    ctx.JSON(201, gin.H{
        "id":       user.ID().String(),
        "username": user.Username().String(),
        "email":    user.Email().String(),
        "active":   user.IsActive(),
    })
}
```

## 洋葱架构

### 架构层次
```
┌─────────────────────────────────────┐
│            Domain Model               │
│           (Core Layer)              │
├─────────────────────────────────────┤
│         Domain Services             │
├─────────────────────────────────────┤
│         Application Services         │
├─────────────────────────────────────┤
│           Infrastructure            │
│         (Outer Layer)              │
└─────────────────────────────────────┘
```

### 实现示例

```go
// domain/model/user.go - 核心领域模型
package model

import (
    "errors"
    "time"
)

type User struct {
    id        ID
    name      Name
    email     Email
    createdAt time.Time
    updatedAt time.Time
}

func NewUser(name Name, email Email) (*User, error) {
    if name.IsEmpty() {
        return nil, errors.New("name cannot be empty")
    }

    if email.IsEmpty() {
        return nil, errors.New("email cannot be empty")
    }

    now := time.Now()
    return &User{
        id:        NewID(),
        name:      name,
        email:     email,
        createdAt: now,
        updatedAt: now,
    }, nil
}

func (u *User) ID() ID {
    return u.id
}

func (u *User) Name() Name {
    return u.name
}

func (u *User) Email() Email {
    return u.email
}

func (u *User) CreatedAt() time.Time {
    return u.createdAt
}

func (u *User) UpdatedAt() time.Time {
    return u.updatedAt
}

func (u *User) Update(name Name, email Email) error {
    if name.IsEmpty() {
        return errors.New("name cannot be empty")
    }

    if email.IsEmpty() {
        return errors.New("email cannot be empty")
    }

    u.name = name
    u.email = email
    u.updatedAt = time.Now()

    return nil
}

// domain/value_objects.go - 值对象
package model

import (
    "errors"
    "regexp"
)

type ID struct {
    value string
}

func NewID() ID {
    return ID{value: generateUUID()}
}

func (id ID) String() string {
    return id.value
}

type Name struct {
    value string
}

func NewName(value string) (Name, error) {
    if len(value) < 2 {
        return Name{}, errors.New("name too short")
    }

    if len(value) > 100 {
        return Name{}, errors.New("name too long")
    }

    return Name{value: value}, nil
}

func (n Name) String() string {
    return n.value
}

func (n Name) IsEmpty() bool {
    return n.value == ""
}

type Email struct {
    value string
}

func NewEmail(value string) (Email, error) {
    if !regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`).MatchString(value) {
        return Email{}, errors.New("invalid email format")
    }

    return Email{value: value}, nil
}

func (e Email) String() string {
    return e.value
}

func (e Email) IsEmpty() bool {
    return e.value == ""
}

// domain/repository/user_repository.go - 仓储接口
package repository

import "github.com/yourproject/domain/model"

type UserRepository interface {
    FindByID(id model.ID) (*model.User, error)
    FindByEmail(email model.Email) (*model.User, error)
    Save(user *model.User) error
    Update(user *model.User) error
    Delete(id model.ID) error
}

// domain/service/user_service.go - 领域服务
package service

import (
    "github.com/yourproject/domain/model"
    "github.com/yourproject/domain/repository"
)

type UserService struct {
    userRepo repository.UserRepository
}

func NewUserService(userRepo repository.UserRepository) *UserService {
    return &UserService{userRepo: userRepo}
}

func (s *UserService) CreateUser(name model.Name, email model.Email) (*model.User, error) {
    // 检查邮箱是否已存在
    existingUser, err := s.userRepo.FindByEmail(email)
    if err == nil && existingUser != nil {
        return nil, errors.New("user with this email already exists")
    }

    // 创建用户
    user, err := model.NewUser(name, email)
    if err != nil {
        return nil, err
    }

    // 保存用户
    if err := s.userRepo.Save(user); err != nil {
        return nil, err
    }

    return user, nil
}

func (s *UserService) GetUserByID(id model.ID) (*model.User, error) {
    user, err := s.userRepo.FindByID(id)
    if err != nil {
        return nil, err
    }

    if user == nil {
        return nil, errors.New("user not found")
    }

    return user, nil
}

func (s *UserService) UpdateUser(id model.ID, name model.Name, email model.Email) error {
    user, err := s.userRepo.FindByID(id)
    if err != nil {
        return err
    }

    if user == nil {
        return errors.New("user not found")
    }

    // 检查邮箱是否已被其他用户使用
    existingUser, err := s.userRepo.FindByEmail(email)
    if err == nil && existingUser != nil && existingUser.ID() != id {
        return errors.New("email already in use")
    }

    // 更新用户
    return user.Update(name, email)
}

// application/usecase/create_user_usecase.go - 应用服务用例
package usecase

import (
    "github.com/yourproject/domain/model"
    "github.com/yourproject/domain/repository"
    "github.com/yourproject/domain/service"
)

type CreateUserUseCase struct {
    userService *service.UserService
}

func NewCreateUserUseCase(userRepo repository.UserRepository) *CreateUserUseCase {
    return &CreateUserUseCase{
        userService: service.NewUserService(userRepo),
    }
}

type CreateUserInput struct {
    Name  string
    Email string
}

type CreateUserOutput struct {
    ID        string
    Name      string
    Email     string
    CreatedAt string
}

func (uc *CreateUserUseCase) Execute(input CreateUserInput) (*CreateUserOutput, error) {
    // 创建值对象
    name, err := model.NewName(input.Name)
    if err != nil {
        return nil, err
    }

    email, err := model.NewEmail(input.Email)
    if err != nil {
        return nil, err
    }

    // 调用领域服务
    user, err := uc.userService.CreateUser(name, email)
    if err != nil {
        return nil, err
    }

    // 返回输出
    return &CreateUserOutput{
        ID:        user.ID().String(),
        Name:      user.Name().String(),
        Email:     user.Email().String(),
        CreatedAt: user.CreatedAt().Format(time.RFC3339),
    }, nil
}

// application/usecase/get_user_usecase.go - 获取用户用例
package usecase

import (
    "github.com/yourproject/domain/model"
    "github.com/yourproject/domain/repository"
    "github.com/yourproject/domain/service"
)

type GetUserUseCase struct {
    userService *service.UserService
}

func NewGetUserUseCase(userRepo repository.UserRepository) *GetUserUseCase {
    return &GetUserUseCase{
        userService: service.NewUserService(userRepo),
    }
}

type GetUserInput struct {
    ID string
}

type GetUserOutput struct {
    ID        string
    Name      string
    Email     string
    CreatedAt string
    UpdatedAt string
}

func (uc *GetUserUseCase) Execute(input GetUserInput) (*GetUserOutput, error) {
    // 创建ID值对象
    id, err := model.ParseID(input.ID)
    if err != nil {
        return nil, err
    }

    // 调用领域服务
    user, err := uc.userService.GetUserByID(id)
    if err != nil {
        return nil, err
    }

    // 返回输出
    return &GetUserOutput{
        ID:        user.ID().String(),
        Name:      user.Name().String(),
        Email:     user.Email().String(),
        CreatedAt: user.CreatedAt().Format(time.RFC3339),
        UpdatedAt: user.UpdatedAt().Format(time.RFC3339),
    }, nil
}

// infrastructure/persistence/mysql_user_repository.go - 持久化适配器
package persistence

import (
    "database/sql"
    "github.com/yourproject/domain/model"
    "github.com/yourproject/domain/repository"
)

type MySQLUserRepository struct {
    db *sql.DB
}

func NewMySQLUserRepository(db *sql.DB) repository.UserRepository {
    return &MySQLUserRepository{db: db}
}

func (r *MySQLUserRepository) FindByID(id model.ID) (*model.User, error) {
    var user model.User
    var name, email string
    var createdAt, updatedAt time.Time

    err := r.db.QueryRow(
        "SELECT name, email, created_at, updated_at FROM users WHERE id = ?",
        id.String(),
    ).Scan(&name, &email, &createdAt, &updatedAt)

    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }

    // 重建领域对象
    userName, err := model.NewName(name)
    if err != nil {
        return nil, err
    }

    userEmail, err := model.NewEmail(email)
    if err != nil {
        return nil, err
    }

    return &model.User{
        id:        id,
        name:      userName,
        email:     userEmail,
        createdAt: createdAt,
        updatedAt: updatedAt,
    }, nil
}

func (r *MySQLUserRepository) FindByEmail(email model.Email) (*model.User, error) {
    var user model.User
    var id, name string
    var createdAt, updatedAt time.Time

    err := r.db.QueryRow(
        "SELECT id, name, created_at, updated_at FROM users WHERE email = ?",
        email.String(),
    ).Scan(&id, &name, &createdAt, &updatedAt)

    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }

    // 重建领域对象
    userID, err := model.ParseID(id)
    if err != nil {
        return nil, err
    }

    userName, err := model.NewName(name)
    if err != nil {
        return nil, err
    }

    return &model.User{
        id:        userID,
        name:      userName,
        email:     email,
        createdAt: createdAt,
        updatedAt: updatedAt,
    }, nil
}

func (r *MySQLUserRepository) Save(user *model.User) error {
    _, err := r.db.Exec(
        "INSERT INTO users (id, name, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        user.ID().String(),
        user.Name().String(),
        user.Email().String(),
        user.CreatedAt(),
        user.UpdatedAt(),
    )
    return err
}

// interfaces/http/user_controller.go - HTTP控制器
package http

import (
    "github.com/yourproject/application/usecase"
    "github.com/gin-gonic/gin"
)

type UserController struct {
    createUserUseCase *usecase.CreateUserUseCase
    getUserUseCase     *usecase.GetUserUseCase
}

func NewUserController(
    createUserUseCase *usecase.CreateUserUseCase,
    getUserUseCase *usecase.GetUserUseCase,
) *UserController {
    return &UserController{
        createUserUseCase: createUserUseCase,
        getUserUseCase:     getUserUseCase,
    }
}

func (c *UserController) CreateUser(ctx *gin.Context) {
    var req usecase.CreateUserInput
    if err := ctx.ShouldBindJSON(&req); err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    output, err := c.createUserUseCase.Execute(req)
    if err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    ctx.JSON(201, output)
}

func (c *UserController) GetUser(ctx *gin.Context) {
    id := ctx.Param("id")
    if id == "" {
        ctx.JSON(400, gin.H{"error": "id is required"})
        return
    }

    output, err := c.getUserUseCase.Execute(usecase.GetUserInput{ID: id})
    if err != nil {
        ctx.JSON(404, gin.H{"error": err.Error()})
        return
    }

    ctx.JSON(200, output)
}
```

## 干净架构

### 架构原则
- **独立于框架**：不依赖于特定的框架
- **可测试性**：业务逻辑可以在没有UI、数据库、服务器的情况下测试
- **独立于UI**：UI可以随时更换，不影响业务逻辑
- **独立于数据库**：可以随时更换数据库
- **独立于外部机构**：业务逻辑不依赖于外部调用

### 架构层次
```
┌─────────────────────────────────────────┐
│                  Entities              │
├─────────────────────────────────────────┤
│               Use Cases               │
├─────────────────────────────────────────┤
│        Interface Adapters             │
├─────────────────────────────────────────┤
│           Frameworks & Drivers        │
└─────────────────────────────────────────┘
```

### 实现示例

```go
// entities/user.go - 实体层（核心业务规则）
package entities

import (
    "errors"
    "time"
)

type User struct {
    ID        UserID
    Name      UserName
    Email     Email
    CreatedAt time.Time
    UpdatedAt time.Time
}

func NewUser(name UserName, email Email) (*User, error) {
    if name.IsEmpty() {
        return nil, errors.New("name cannot be empty")
    }

    if email.IsEmpty() {
        return nil, errors.New("email cannot be empty")
    }

    return &User{
        ID:        NewUserID(),
        Name:      name,
        Email:     email,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }, nil
}

func (u *User) ChangeName(name UserName) error {
    if name.IsEmpty() {
        return errors.New("name cannot be empty")
    }

    u.Name = name
    u.UpdatedAt = time.Now()
    return nil
}

func (u *User) ChangeEmail(email Email) error {
    if email.IsEmpty() {
        return errors.New("email cannot be empty")
    }

    if u.Email == email {
        return errors.New("email already set")
    }

    u.Email = email
    u.UpdatedAt = time.Now()
    return nil
}

// entities/value_objects.go - 值对象
package entities

import (
    "errors"
    "regexp"
    "github.com/google/uuid"
)

type UserID struct {
    value uuid.UUID
}

func NewUserID() UserID {
    return UserID{value: uuid.New()}
}

func (id UserID) String() string {
    return id.value.String()
}

type UserName struct {
    value string
}

func NewUserName(value string) (UserName, error) {
    if len(value) < 2 {
        return UserName{}, errors.New("name too short")
    }

    if len(value) > 100 {
        return UserName{}, errors.New("name too long")
    }

    return UserName{value: value}, nil
}

func (n UserName) String() string {
    return n.value
}

func (n UserName) IsEmpty() bool {
    return n.value == ""
}

type Email struct {
    value string
}

func NewEmail(value string) (Email, error) {
    if !regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`).MatchString(value) {
        return Email{}, errors.New("invalid email format")
    }

    return Email{value: value}, nil
}

func (e Email) String() string {
    return e.value
}

func (e Email) IsEmpty() bool {
    return e.value == ""
}

// usecases/user_repository.go - 用例接口
package usecases

import "github.com/yourproject/entities"

type UserRepository interface {
    FindByID(id entities.UserID) (*entities.User, error)
    FindByEmail(email entities.Email) (*entities.User, error)
    Save(user *entities.User) error
    Update(user *entities.User) error
    Delete(id entities.UserID) error
}

// usecases/create_user_usecase.go - 创建用户用例
package usecases

import (
    "github.com/yourproject/entities"
)

type CreateUserInput struct {
    Name  string
    Email string
}

type CreateUserOutput struct {
    ID        string
    Name      string
    Email     string
    CreatedAt string
}

type CreateUserUseCase struct {
    userRepo UserRepository
}

func NewCreateUserUseCase(userRepo UserRepository) *CreateUserUseCase {
    return &CreateUserUseCase{userRepo: userRepo}
}

func (uc *CreateUserUseCase) Execute(input CreateUserInput) (*CreateUserOutput, error) {
    // 创建值对象
    name, err := entities.NewUserName(input.Name)
    if err != nil {
        return nil, err
    }

    email, err := entities.NewEmail(input.Email)
    if err != nil {
        return nil, err
    }

    // 检查邮箱是否已存在
    existingUser, err := uc.userRepo.FindByEmail(email)
    if err == nil && existingUser != nil {
        return nil, errors.New("user with this email already exists")
    }

    // 创建用户实体
    user, err := entities.NewUser(name, email)
    if err != nil {
        return nil, err
    }

    // 保存用户
    if err := uc.userRepo.Save(user); err != nil {
        return nil, err
    }

    // 返回输出
    return &CreateUserOutput{
        ID:        user.ID.String(),
        Name:      user.Name.String(),
        Email:     user.Email.String(),
        CreatedAt: user.CreatedAt.Format(time.RFC3339),
    }, nil
}

// usecases/update_user_usecase.go - 更新用户用例
package usecases

import (
    "github.com/yourproject/entities"
)

type UpdateUserInput struct {
    ID    string
    Name  string
    Email string
}

type UpdateUserOutput struct {
    ID        string
    Name      string
    Email     string
    UpdatedAt string
}

type UpdateUserUseCase struct {
    userRepo UserRepository
}

func NewUpdateUserUseCase(userRepo UserRepository) *UpdateUserUseCase {
    return &UpdateUserUseCase{userRepo: userRepo}
}

func (uc *UpdateUserUseCase) Execute(input UpdateUserInput) (*UpdateUserOutput, error) {
    // 查找用户
    userID, err := entities.ParseUserID(input.ID)
    if err != nil {
        return nil, err
    }

    user, err := uc.userRepo.FindByID(userID)
    if err != nil {
        return nil, err
    }

    if user == nil {
        return nil, errors.New("user not found")
    }

    // 创建值对象
    name, err := entities.NewUserName(input.Name)
    if err != nil {
        return nil, err
    }

    email, err := entities.NewEmail(input.Email)
    if err != nil {
        return nil, err
    }

    // 检查邮箱是否已被其他用户使用
    existingUser, err := uc.userRepo.FindByEmail(email)
    if err == nil && existingUser != nil && existingUser.ID != userID {
        return nil, errors.New("email already in use")
    }

    // 更新用户
    if err := user.ChangeName(name); err != nil {
        return nil, err
    }

    if err := user.ChangeEmail(email); err != nil {
        return nil, err
    }

    // 保存更新
    if err := uc.userRepo.Update(user); err != nil {
        return nil, err
    }

    // 返回输出
    return &UpdateUserOutput{
        ID:        user.ID.String(),
        Name:      user.Name.String(),
        Email:     user.Email.String(),
        UpdatedAt: user.UpdatedAt.Format(time.RFC3339),
    }, nil
}

// interfaces/persistence/mysql_user_repository.go - 持久化适配器
package persistence

import (
    "database/sql"
    "github.com/yourproject/entities"
    "github.com/yourproject/usecases"
)

type MySQLUserRepository struct {
    db *sql.DB
}

func NewMySQLUserRepository(db *sql.DB) usecases.UserRepository {
    return &MySQLUserRepository{db: db}
}

func (r *MySQLUserRepository) FindByID(id entities.UserID) (*entities.User, error) {
    var user entities.User
    var name, email string
    var createdAt, updatedAt time.Time

    err := r.db.QueryRow(
        "SELECT name, email, created_at, updated_at FROM users WHERE id = ?",
        id.String(),
    ).Scan(&name, &email, &createdAt, &updatedAt)

    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }

    // 重建实体
    userName, err := entities.NewUserName(name)
    if err != nil {
        return nil, err
    }

    userEmail, err := entities.NewEmail(email)
    if err != nil {
        return nil, err
    }

    return &entities.User{
        ID:        id,
        Name:      userName,
        Email:     userEmail,
        CreatedAt: createdAt,
        UpdatedAt: updatedAt,
    }, nil
}

func (r *MySQLUserRepository) FindByEmail(email entities.Email) (*entities.User, error) {
    var user entities.User
    var id, name string
    var createdAt, updatedAt time.Time

    err := r.db.QueryRow(
        "SELECT id, name, created_at, updated_at FROM users WHERE email = ?",
        email.String(),
    ).Scan(&id, &name, &createdAt, &updatedAt)

    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }

    // 重建实体
    userID, err := entities.ParseUserID(id)
    if err != nil {
        return nil, err
    }

    userName, err := entities.NewUserName(name)
    if err != nil {
        return nil, err
    }

    return &entities.User{
        ID:        userID,
        Name:      userName,
        Email:     email,
        CreatedAt: createdAt,
        UpdatedAt: updatedAt,
    }, nil
}

func (r *MySQLUserRepository) Save(user *entities.User) error {
    _, err := r.db.Exec(
        "INSERT INTO users (id, name, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        user.ID.String(),
        user.Name.String(),
        user.Email.String(),
        user.CreatedAt,
        user.UpdatedAt,
    )
    return err
}

// interfaces/http/user_controller.go - HTTP适配器
package http

import (
    "github.com/yourproject/usecases"
    "github.com/gin-gonic/gin"
)

type UserController struct {
    createUserUseCase *usecases.CreateUserUseCase
    updateUserUseCase *usecases.UpdateUserUseCase
}

func NewUserController(
    createUserUseCase *usecases.CreateUserUseCase,
    updateUserUseCase *usecases.UpdateUserUseCase,
) *UserController {
    return &UserController{
        createUserUseCase: createUserUseCase,
        updateUserUseCase: updateUserUseCase,
    }
}

func (c *UserController) CreateUser(ctx *gin.Context) {
    var req usecases.CreateUserInput
    if err := ctx.ShouldBindJSON(&req); err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    output, err := c.createUserUseCase.Execute(req)
    if err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    ctx.JSON(201, output)
}

func (c *UserController) UpdateUser(ctx *gin.Context) {
    var req usecases.UpdateUserInput
    if err := ctx.ShouldBindJSON(&req); err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    req.ID = ctx.Param("id")
    if req.ID == "" {
        ctx.JSON(400, gin.H{"error": "id is required"})
        return
    }

    output, err := c.updateUserUseCase.Execute(req)
    if err != nil {
        ctx.JSON(400, gin.H{"error": err.Error()})
        return
    }

    ctx.JSON(200, output)
}

// interfaces/grpc/user_service.go - gRPC适配器
package grpc

import (
    "context"
    "github.com/yourproject/usecases"
    pb "github.com/yourproject/proto"
)

type UserService struct {
    createUserUseCase *usecases.CreateUserUseCase
    updateUserUseCase *usecases.UpdateUserUseCase
}

func NewUserService(
    createUserUseCase *usecases.CreateUserUseCase,
    updateUserUseCase *usecases.UpdateUserUseCase,
) *UserService {
    return &UserService{
        createUserUseCase: createUserUseCase,
        updateUserUseCase: updateUserUseCase,
    }
}

func (s *UserService) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
    input := usecases.CreateUserInput{
        Name:  req.Name,
        Email: req.Email,
    }

    output, err := s.createUserUseCase.Execute(input)
    if err != nil {
        return nil, err
    }

    return &pb.CreateUserResponse{
        User: &pb.User{
            Id:        output.ID,
            Name:      output.Name,
            Email:     output.Email,
            CreatedAt: output.CreatedAt,
        },
    }, nil
}

func (s *UserService) UpdateUser(ctx context.Context, req *pb.UpdateUserRequest) (*pb.UpdateUserResponse, error) {
    input := usecases.UpdateUserInput{
        ID:    req.Id,
        Name:  req.Name,
        Email: req.Email,
    }

    output, err := s.updateUserUseCase.Execute(input)
    if err != nil {
        return nil, err
    }

    return &pb.UpdateUserResponse{
        User: &pb.User{
            Id:        output.ID,
            Name:      output.Name,
            Email:     output.Email,
            UpdatedAt: output.UpdatedAt,
        },
    }, nil
}
```

## Serverless架构

### 架构特点
- **无服务器管理**：无需管理服务器基础设施
- **按需扩展**：根据请求量自动扩展
- **事件驱动**：响应各种事件触发
- **微服务友好**：适合构建微服务架构

### 实现示例

```go
// functions/user_create.go - 用户创建函数
package functions

import (
    "context"
    "github.com/yourproject/entities"
    "github.com/yourproject/usecases"
    "github.com/aws/aws-lambda-go/events"
    "github.com/aws/aws-lambda-go/lambda"
)

type CreateUserHandler struct {
    createUserUseCase *usecases.CreateUserUseCase
}

func NewCreateUserHandler(createUserUseCase *usecases.CreateUserUseCase) *CreateUserHandler {
    return &CreateUserHandler{createUserUseCase: createUserUseCase}
}

func (h *CreateUserHandler) Handle(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
    var input usecases.CreateUserInput
    if err := json.Unmarshal([]byte(request.Body), &input); err != nil {
        return events.APIGatewayProxyResponse{
            StatusCode: 400,
            Body:       `{"error": "invalid request body"}`,
        }, nil
    }

    output, err := h.createUserUseCase.Execute(input)
    if err != nil {
        return events.APIGatewayProxyResponse{
            StatusCode: 400,
            Body:       `{"error": "` + err.Error() + `"}`,
        }, nil
    }

    response, _ := json.Marshal(output)
    return events.APIGatewayProxyResponse{
        StatusCode: 201,
        Body:       string(response),
    }, nil
}

// functions/user_get.go - 获取用户函数
package functions

import (
    "context"
    "github.com/yourproject/usecases"
    "github.com/aws/aws-lambda-go/events"
)

type GetUserHandler struct {
    getUserUseCase *usecases.GetUserUseCase
}

func NewGetUserHandler(getUserUseCase *usecases.GetUserUseCase) *GetUserHandler {
    return &GetUserHandler{getUserUseCase: getUserUseCase}
}

func (h *GetUserHandler) Handle(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
    userID := request.PathParameters["id"]
    if userID == "" {
        return events.APIGatewayProxyResponse{
            StatusCode: 400,
            Body:       `{"error": "user id is required"}`,
        }, nil
    }

    input := usecases.GetUserInput{ID: userID}
    output, err := h.getUserUseCase.Execute(input)
    if err != nil {
        return events.APIGatewayProxyResponse{
            StatusCode: 404,
            Body:       `{"error": "user not found"}`,
        }, nil
    }

    response, _ := json.Marshal(output)
    return events.APIGatewayProxyResponse{
        StatusCode: 200,
        Body:       string(response),
    }, nil
}

// main.go - 函数入口
package main

import (
    "github.com/yourproject/functions"
    "github.com/yourproject/usecases"
    "github.com/yourproject/interfaces/persistence"
)

func main() {
    // 初始化依赖
    db := getDatabaseConnection()
    userRepo := persistence.NewMySQLUserRepository(db)

    // 创建用例
    createUserUseCase := usecases.NewCreateUserUseCase(userRepo)
    getUserUseCase := usecases.NewGetUserUseCase(userRepo)

    // 创建处理器
    createUserHandler := functions.NewCreateUserHandler(createUserUseCase)
    getUserHandler := functions.NewGetUserHandler(getUserUseCase)

    // 根据环境变量选择函数
    switch os.Getenv("FUNCTION_NAME") {
    case "createUser":
        lambda.Start(createUserHandler.Handle)
    case "getUser":
        lambda.Start(getUserHandler.Handle)
    default:
        panic("unknown function name")
    }
}

// infrastructure/aws/dynamodb_user_repository.go - DynamoDB适配器
package aws

import (
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/service/dynamodb"
    "github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
    "github.com/yourproject/entities"
    "github.com/yourproject/usecases"
)

type DynamoDBUserRepository struct {
    client *dynamodb.DynamoDB
    table  string
}

func NewDynamoDBUserRepository(client *dynamodb.DynamoDB, table string) usecases.UserRepository {
    return &DynamoDBUserRepository{
        client: client,
        table:  table,
    }
}

func (r *DynamoDBUserRepository) FindByID(id entities.UserID) (*entities.User, error) {
    result, err := r.client.GetItem(&dynamodb.GetItemInput{
        TableName: aws.String(r.table),
        Key: map[string]*dynamodb.AttributeValue{
            "id": {
                S: aws.String(id.String()),
            },
        },
    })

    if err != nil {
        return nil, err
    }

    if result.Item == nil {
        return nil, nil
    }

    var user entities.User
    err = dynamodbattribute.UnmarshalMap(result.Item, &user)
    if err != nil {
        return nil, err
    }

    return &user, nil
}

func (r *DynamoDBUserRepository) Save(user *entities.User) error {
    item, err := dynamodbattribute.MarshalMap(user)
    if err != nil {
        return err
    }

    _, err = r.client.PutItem(&dynamodb.PutItemInput{
        TableName: aws.String(r.table),
        Item:      item,
    })

    return err
}

// infrastructure/events/s3_event_handler.go - S3事件处理
package events

import (
    "context"
    "github.com/aws/aws-lambda-go/events"
    "github.com/aws/aws-lambda-go/lambda"
)

type S3EventHandler struct {
    processor FileProcessor
}

func NewS3EventHandler(processor FileProcessor) *S3EventHandler {
    return &S3EventHandler{processor: processor}
}

func (h *S3EventHandler) Handle(ctx context.Context, event events.S3Event) error {
    for _, record := range event.Records {
        bucket := record.S3.Bucket.Name
        key := record.S3.Object.Key

        if err := h.processor.ProcessFile(bucket, key); err != nil {
            log.Printf("Failed to process file %s/%s: %v", bucket, key, err)
            continue
        }

        log.Printf("Successfully processed file %s/%s", bucket, key)
    }

    return nil
}

type FileProcessor interface {
    ProcessFile(bucket, key string) error
}
```

## 架构模式选择指南

### 选择因素

#### 1. 项目规模
- **小型项目**：分层架构、干净架构
- **中型项目**：六边形架构、洋葱架构
- **大型项目**：微服务架构、CQRS架构
- **超大型项目**：混合架构模式

#### 2. 团队规模
- **小团队**：分层架构、干净架构
- **中团队**：六边形架构、洋葱架构
- **大团队**：微服务架构、事件驱动架构

#### 3. 业务复杂度
- **简单业务**：分层架构
- **中等复杂度**：六边形架构、洋葱架构
- **复杂业务**：CQRS架构、事件驱动架构

#### 4. 性能要求
- **一般性能**：分层架构、六边形架构
- **高性能**：微服务架构、CQRS架构
- **极高性能**：事件驱动架构、Serverless架构

#### 5. 可扩展性需求
- **垂直扩展**：分层架构、干净架构
- **水平扩展**：微服务架构、事件驱动架构
- **自动扩展**：Serverless架构

### 决策矩阵

```go
// architecture_decision.go - 架构决策辅助
package architecture

import (
    "fmt"
)

type ProjectContext struct {
    TeamSize       int
    ProjectSize    string // "small", "medium", "large"
    BusinessComplexity string // "simple", "medium", "complex"
    PerformanceRequirement string // "low", "medium", "high"
    ScalabilityNeed string // "vertical", "horizontal", "auto"
    TimeToMarket   string // "fast", "normal", "slow"
}

type ArchitectureRecommendation struct {
    PrimaryPattern   string
    SecondaryPattern string
    Reason          string
    Pros           []string
    Cons           []string
}

func RecommendArchitecture(ctx ProjectContext) ArchitectureRecommendation {
    // 小型项目 + 小团队
    if ctx.ProjectSize == "small" && ctx.TeamSize <= 5 {
        if ctx.TimeToMarket == "fast" {
            return ArchitectureRecommendation{
                PrimaryPattern: "Layered Architecture",
                SecondaryPattern: "Clean Architecture",
                Reason: "Simple and quick to implement for small teams",
                Pros: []string{
                    "Easy to understand",
                    "Quick development",
                    "Low complexity",
                },
                Cons: []string{
                    "Limited scalability",
                    "Tight coupling risk",
                },
            }
        } else {
            return ArchitectureRecommendation{
                PrimaryPattern: "Clean Architecture",
                SecondaryPattern: "Layered Architecture",
                Reason: "Better maintainability for small to medium projects",
                Pros: []string{
                    "Good separation of concerns",
                    "Testable",
                    "Maintainable",
                },
                Cons: []string{
                    "Slightly more complex",
                    "Learning curve",
                },
            }
        }
    }

    // 中型项目 + 中等团队
    if ctx.ProjectSize == "medium" && ctx.TeamSize <= 20 {
        if ctx.BusinessComplexity == "complex" {
            return ArchitectureRecommendation{
                PrimaryPattern: "Hexagonal Architecture",
                SecondaryPattern: "Onion Architecture",
                Reason: "Good balance between flexibility and structure for complex business logic",
                Pros: []string{
                    "Flexible technology choices",
                    "Testable business logic",
                    "Good for complex domains",
                },
                Cons: []string{
                    "More complex to implement",
                    "Requires discipline",
                },
            }
        } else {
            return ArchitectureRecommendation{
                PrimaryPattern: "Onion Architecture",
                SecondaryPattern: "Clean Architecture",
                Reason: "Good maintainability and testability for medium projects",
                Pros: []string{
                    "Clear dependency direction",
                    "Good testability",
                    "Maintainable",
                },
                Cons: []string{
                    "More layers to manage",
                    "Initial setup complexity",
                },
            }
        }
    }

    // 大型项目 + 大团队
    if ctx.ProjectSize == "large" || ctx.TeamSize > 20 {
        if ctx.BusinessComplexity == "complex" && ctx.PerformanceRequirement == "high" {
            return ArchitectureRecommendation{
                PrimaryPattern: "CQRS Architecture",
                SecondaryPattern: "Event-Driven Architecture",
                Reason: "High performance and scalability for complex business domains",
                Pros: []string{
                    "High performance",
                    "Scalable read/write models",
                    "Good for complex domains",
                },
                Cons: []string{
                    "Very complex",
                    "Eventual consistency",
                    "Higher development cost",
                },
            }
        } else {
            return ArchitectureRecommendation{
                PrimaryPattern: "Microservices Architecture",
                SecondaryPattern: "Event-Driven Architecture",
                Reason: "Good scalability and team autonomy for large projects",
                Pros: []string{
                    "Independent deployment",
                    "Technology diversity",
                    "Team autonomy",
                },
                Cons: []string{
                    "Distributed complexity",
                    "Network latency",
                    "Operational overhead",
                },
            }
        }
    }

    // 默认推荐
    return ArchitectureRecommendation{
        PrimaryPattern: "Layered Architecture",
        SecondaryPattern: "Clean Architecture",
        Reason: "Good starting point for most projects",
        Pros: []string{
            "Simple to understand",
            "Widely used",
            "Good documentation",
        },
        Cons: []string{
            "Can lead to tight coupling",
            "Limited flexibility",
        },
    }
}

// architecture_patterns.go - 架构模式特征
package architecture

type ArchitecturePattern struct {
    Name           string
    Description    string
    UseCases       []string
    Pros           []string
    Cons           []string
    Complexity     int // 1-5
    Scalability    int // 1-5
    Maintainability int // 1-5
}

var ArchitecturePatterns = map[string]ArchitecturePattern{
    "Layered Architecture": {
        Name:        "Layered Architecture",
        Description: "Traditional n-tier architecture with clear separation of concerns",
        UseCases:    []string{"Simple CRUD applications", "Internal tools", "Proof of concepts"},
        Pros:        []string{"Simple to understand", "Easy to implement", "Good for small teams"},
        Cons:        []string{"Can lead to tight coupling", "Limited flexibility", "Performance overhead"},
        Complexity:     2,
        Scalability:    2,
        Maintainability: 3,
    },
    "Clean Architecture": {
        Name:        "Clean Architecture",
        Description: "Architecture that emphasizes independence of frameworks, UI, and databases",
        UseCases:    []string{"Domain-driven applications", "Long-lived applications", "Test-critical applications"},
        Pros:        []string{"Framework independent", "Highly testable", "Database independent"},
        Cons:        []string{"More complex", "Learning curve", "More boilerplate"},
        Complexity:     4,
        Scalability:    3,
        Maintainability: 5,
    },
    "Hexagonal Architecture": {
        Name:        "Hexagonal Architecture",
        Description: "Architecture that isolates the core business logic from outside concerns",
        UseCases:    []string{"Applications with multiple interfaces", "Plugin-based systems", "Complex business domains"},
        Pros:        []string{"Technology flexibility", "Testable core", "Multiple interfaces"},
        Cons:        []string{"Complex to implement", "Requires discipline", "More abstractions"},
        Complexity:     4,
        Scalability:    4,
        Maintainability: 4,
    },
    "Onion Architecture": {
        Name:        "Onion Architecture",
        Description: "Architecture with dependency inversion and clear layer boundaries",
        UseCases:    []string{"Enterprise applications", "Domain-driven design", "Long-term projects"},
        Pros:        []string{"Clear dependency direction", "Good testability", "Maintainable"},
        Cons:        []string{"More layers", "Complex setup", "Steep learning curve"},
        Complexity:     4,
        Scalability:    3,
        Maintainability: 5,
    },
    "Microservices Architecture": {
        Name:        "Microservices Architecture",
        Description: "Architecture that structures an application as a collection of loosely coupled services",
        UseCases:    []string{"Large-scale applications", "Multi-team projects", "Cloud-native applications"},
        Pros:        []string{"Independent deployment", "Technology diversity", "Team autonomy"},
        Cons:        []string{"Distributed complexity", "Network latency", "Operational overhead"},
        Complexity:     5,
        Scalability:    5,
        Maintainability: 3,
    },
    "Event-Driven Architecture": {
        Name:        "Event-Driven Architecture",
        Description: "Architecture that uses events to communicate between decoupled components",
        UseCases:    []string{"Real-time applications", "IoT systems", "Workflow-based applications"},
        Pros:        []string{"Loose coupling", "Scalable", "Real-time processing"},
        Cons:        []string{"Eventual consistency", "Debugging complexity", "Event schema management"},
        Complexity:     4,
        Scalability:    5,
        Maintainability: 3,
    },
    "CQRS Architecture": {
        Name:        "CQRS Architecture",
        Description: "Architecture that separates read operations from write operations",
        UseCases:    []string{"High-performance applications", "Complex read models", "Real-time analytics"},
        Pros:        []string{"Optimized read/write models", "Scalable", "Performance"},
        Cons:        []string{"Eventual consistency", "Complex implementation", "Data synchronization"},
        Complexity:     5,
        Scalability:    5,
        Maintainability: 3,
    },
    "Serverless Architecture": {
        Name:        "Serverless Architecture",
        Description: "Architecture that uses cloud functions without managing servers",
        UseCases:    []string{"Event-driven applications", "API gateways", "Data processing pipelines"},
        Pros:        []string{"No server management", "Auto-scaling", "Cost-effective"},
        Cons:        []string{"Vendor lock-in", "Cold starts", "Limited execution time"},
        Complexity:     3,
        Scalability:    5,
        Maintainability: 4,
    },
}

// architecture_evolution.go - 架构演进建议
package architecture

type EvolutionPath struct {
    From     string
    To       string
    Trigger   string
    Steps     []string
    Challenges []string
    Benefits  []string
}

var EvolutionPaths = []EvolutionPath{
    {
        From:   "Layered Architecture",
        To:     "Clean Architecture",
        Trigger: "Increasing complexity and testability requirements",
        Steps: []string{
            "Identify core business logic",
            "Create domain models",
            "Implement dependency inversion",
            "Add interface adapters",
        },
        Challenges: []string{
            "Refactoring existing code",
            "Team training",
            "Temporary complexity increase",
        },
        Benefits: []string{
            "Better testability",
            "Framework independence",
            "Long-term maintainability",
        },
    },
    {
        From:   "Clean Architecture",
        To:     "Microservices Architecture",
        Trigger: "Team growth and deployment frequency requirements",
        Steps: []string{
            "Identify bounded contexts",
            "Create service boundaries",
            "Implement service communication",
            "Add monitoring and logging",
        },
        Challenges: []string{
            "Distributed systems complexity",
            "Data consistency",
            "Operational overhead",
        },
        Benefits: []string{
            "Independent deployment",
            "Team autonomy",
            "Technology diversity",
        },
    },
    {
        From:   "Monolithic Application",
        To:     "Event-Driven Architecture",
        Trigger: "Real-time requirements and scalability needs",
        Steps: []string{
            "Identify events",
            "Implement event bus",
            "Create event handlers",
            "Add event sourcing if needed",
        },
        Challenges: []string{
            "Eventual consistency",
            "Event schema management",
            "Debugging complexity",
        },
        Benefits: []string{
            "Loose coupling",
            "Real-time processing",
            "Scalability",
        },
    },
}
```

这个Go架构模式实战文档涵盖了多种现代软件架构模式在Go语言中的实现，包括分层架构、微服务架构、事件驱动架构、CQRS架构、六边形架构、洋葱架构、干净架构和Serverless架构。每种架构模式都提供了详细的代码示例、使用场景和优缺点分析，以及架构模式选择指南。这些内容可以帮助开发者根据项目需求选择合适的架构模式，并在Go项目中实现这些架构。