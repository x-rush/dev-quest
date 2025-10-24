# Go微服务实战项目

## 项目概述
本项目将构建一个完整的微服务系统，包含用户服务、产品服务、订单服务和API网关。通过这个项目，您将学习如何使用Go语言构建可扩展的微服务架构，包括服务间通信、数据一致性、服务发现和监控等关键技术。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `projects/practical-projects` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#微服务` `#grpc` `#实战项目` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 技术栈
- **Go 1.21+**: 主要开发语言
- **Gin/Echo**: Web框架
- **gRPC**: 服务间通信
- **Redis**: 缓存和消息队列
- **PostgreSQL**: 主数据库
- **MongoDB**: 文档存储
- **Docker & Kubernetes**: 容器化部署
- **Jaeger**: 分布式追踪
- **Prometheus & Grafana**: 监控和可视化
- **Envoy**: API网关

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (Envoy)                      │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌────────▼────────┐   ┌───────▼──────┐
│ User Service │   │ Product Service │   │ Order Service │
└───────┬──────┘   └────────┬────────┘   └───────┬──────┘
        │                    │                    │
┌───────▼──────┐   ┌────────▼────────┐   ┌───────▼──────┐
│  PostgreSQL  │   │    MongoDB     │   │  PostgreSQL  │
└──────────────┘   └─────────────────┘   └──────────────┘
        │                    │                    │
┌───────▼──────┐   ┌────────▼────────┐   ┌───────▼──────┐
│     Redis    │   │     Redis       │   │     Redis     │
└──────────────┘   └─────────────────┘   └──────────────┘
```

## 服务设计

### 1. 用户服务 (User Service)
负责用户管理、认证和授权。

**功能特性:**
- 用户注册、登录、注销
- JWT令牌生成和验证
- 用户信息管理
- 权限控制
- 用户活动日志

**技术实现:**
- 使用Gin框架构建REST API
- PostgreSQL存储用户数据
- Redis缓存会话和权限信息
- gRPC提供服务间通信接口

**主要API:**
```
POST /api/v1/users/register      # 用户注册
POST /api/v1/users/login         # 用户登录
GET  /api/v1/users/profile       # 获取用户信息
PUT  /api/v1/users/profile       # 更新用户信息
DELETE /api/v1/users/logout       # 用户注销
```

### 2. 产品服务 (Product Service)
负责产品信息管理和库存控制。

**功能特性:**
- 产品CRUD操作
- 库存管理
- 产品分类管理
- 产品搜索和过滤
- 产品图片管理

**技术实现:**
- 使用Echo框架构建REST API
- MongoDB存储产品信息
- Redis缓存热门产品
- 全文搜索支持

**主要API:**
```
GET    /api/v1/products            # 获取产品列表
POST   /api/v1/products            # 创建产品
GET    /api/v1/products/:id        # 获取产品详情
PUT    /api/v1/products/:id        # 更新产品
DELETE /api/v1/products/:id        # 删除产品
GET    /api/v1/products/search     # 搜索产品
```

### 3. 订单服务 (Order Service)
负责订单处理和支付集成。

**功能特性:**
- 订单创建和管理
- 支付处理
- 订单状态跟踪
- 库存扣减
- 订单报表

**技术实现:**
- 使用Gin框架构建REST API
- PostgreSQL存储订单数据
- Redis缓存订单状态
- 事件驱动架构

**主要API:**
```
POST   /api/v1/orders              # 创建订单
GET    /api/v1/orders/:id          # 获取订单详情
PUT    /api/v1/orders/:id          # 更新订单
DELETE /api/v1/orders/:id          # 取消订单
GET    /api/v1/orders/user/:userId # 获取用户订单
POST   /api/v1/orders/:id/pay      # 支付订单
```

### 4. API网关
统一的入口点，负责路由、认证和负载均衡。

**功能特性:**
- 请求路由和转发
- 认证和授权
- 限流和熔断
- 请求/响应转换
- 监控和日志

**技术实现:**
- 使用Envoy作为API网关
- 配置路由规则
- 集成认证服务
- 设置限流策略

## 数据模型设计

### 用户模型
```go
// models/user.go
package models

import "time"

type User struct {
    ID        string    `json:"id" gorm:"primary_key"`
    Username  string    `json:"username" gorm:"unique;not null"`
    Email     string    `json:"email" gorm:"unique;not null"`
    Password  string    `json:"-" gorm:"not null"`
    FirstName string    `json:"first_name"`
    LastName  string    `json:"last_name"`
    Phone     string    `json:"phone"`
    Address   string    `json:"address"`
    Role      string    `json:"role" gorm:"default:'user'"`
    Active    bool      `json:"active" gorm:"default:true"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

type UserSession struct {
    ID        string    `json:"id" gorm:"primary_key"`
    UserID    string    `json:"user_id" gorm:"not null"`
    Token     string    `json:"token" gorm:"unique;not null"`
    ExpiresAt time.Time `json:"expires_at"`
    CreatedAt time.Time `json:"created_at"`
}
```

### 产品模型
```go
// models/product.go
package models

import "time"

type Product struct {
    ID          string  `json:"id" bson:"_id,omitempty"`
    Name        string  `json:"name" bson:"name" validate:"required"`
    Description string  `json:"description" bson:"description"`
    Price       float64 `json:"price" bson:"price" validate:"required,min=0"`
    Category    string  `json:"category" bson:"category"`
    Stock       int     `json:"stock" bson:"stock" validate:"min=0"`
    SKU         string  `json:"sku" bson:"sku" validate:"required"`
    Images      []string `json:"images" bson:"images"`
    Tags        []string `json:"tags" bson:"tags"`
    Active      bool    `json:"active" bson:"active" default:"true"`
    CreatedAt   time.Time `json:"created_at" bson:"created_at"`
    UpdatedAt   time.Time `json:"updated_at" bson:"updated_at"`
}

type ProductCategory struct {
    ID          string    `json:"id" bson:"_id,omitempty"`
    Name        string    `json:"name" bson:"name" validate:"required"`
    Description string    `json:"description" bson:"description"`
    ParentID    string    `json:"parent_id" bson:"parent_id"`
    CreatedAt   time.Time `json:"created_at" bson:"created_at"`
    UpdatedAt   time.Time `json:"updated_at" bson:"updated_at"`
}
```

### 订单模型
```go
// models/order.go
package models

import "time"

type Order struct {
    ID         string      `json:"id" gorm:"primary_key"`
    UserID     string      `json:"user_id" gorm:"not null"`
    Status     string      `json:"status" gorm:"not null"`
    Total      float64     `json:"total" gorm:"not null"`
    Currency   string      `json:"currency" gorm:"default:'USD'"`
    Items      []OrderItem `json:"items" gorm:"foreignKey:OrderID"`
    Shipping   Shipping    `json:"shipping" gorm:"embedded"`
    Payment    Payment     `json:"payment" gorm:"embedded"`
    CreatedAt  time.Time   `json:"created_at"`
    UpdatedAt  time.Time   `json:"updated_at"`
}

type OrderItem struct {
    ID          string  `json:"id" gorm:"primary_key"`
    OrderID     string  `json:"order_id" gorm:"not null"`
    ProductID   string  `json:"product_id" gorm:"not null"`
    ProductName string  `json:"product_name"`
    Quantity    int     `json:"quantity" gorm:"not null"`
    Price       float64 `json:"price" gorm:"not null"`
    Total       float64 `json:"total" gorm:"not null"`
}

type Shipping struct {
    Address   string `json:"address"`
    City      string `json:"city"`
    State     string `json:"state"`
    Country   string `json:"country"`
    ZipCode   string `json:"zip_code"`
    Method    string `json:"method"`
    Cost      float64 `json:"cost"`
    Status    string `json:"status"`
}

type Payment struct {
    Method    string    `json:"method"`
    Amount    float64   `json:"amount"`
    Status    string    `json:"status"`
    TransactionID string `json:"transaction_id"`
    PaidAt    time.Time `json:"paid_at"`
}
```

## 服务间通信

### gRPC服务定义
```protobuf
// proto/user.proto
syntax = "proto3";

package user;
option go_package = "./pb";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc GetUserByEmail(GetUserByEmailRequest) returns (GetUserResponse);
  rpc ValidateToken(ValidateTokenRequest) returns (ValidateTokenResponse);
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  string id = 1;
  string username = 2;
  string email = 3;
  string first_name = 4;
  string last_name = 5;
  string role = 6;
  bool active = 7;
}

message GetUserByEmailRequest {
  string email = 1;
}

message ValidateTokenRequest {
  string token = 1;
}

message ValidateTokenResponse {
  bool valid = 1;
  string user_id = 2;
  string role = 3;
}
```

### 服务间调用示例
```go
// services/user_service.go
package services

import (
    "context"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
)

type UserServiceClient struct {
    client pb.UserServiceClient
}

func NewUserServiceClient(addr string) (*UserServiceClient, error) {
    conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
    if err != nil {
        return nil, err
    }

    return &UserServiceClient{
        client: pb.NewUserServiceClient(conn),
    }, nil
}

func (s *UserServiceClient) GetUser(ctx context.Context, id string) (*pb.GetUserResponse, error) {
    ctx, cancel := context.WithTimeout(ctx, time.Second*3)
    defer cancel()

    return s.client.GetUser(ctx, &pb.GetUserRequest{Id: id})
}

func (s *UserServiceClient) ValidateToken(ctx context.Context, token string) (*pb.ValidateTokenResponse, error) {
    ctx, cancel := context.WithTimeout(ctx, time.Second*3)
    defer cancel()

    return s.client.ValidateToken(ctx, &pb.ValidateTokenRequest{Token: token})
}
```

## 事件驱动架构

### 事件定义
```go
// events/events.go
package events

import (
    "encoding/json"
    "time"
)

type Event struct {
    ID        string      `json:"id"`
    Type      string      `json:"type"`
    Source    string      `json:"source"`
    Data      interface{} `json:"data"`
    Timestamp time.Time   `json:"timestamp"`
}

type UserRegisteredEvent struct {
    UserID    string `json:"user_id"`
    Username  string `json:"username"`
    Email     string `json:"email"`
    Timestamp time.Time `json:"timestamp"`
}

type OrderCreatedEvent struct {
    OrderID    string      `json:"order_id"`
    UserID     string      `json:"user_id"`
    Total      float64     `json:"total"`
    Items      []OrderItem `json:"items"`
    Timestamp  time.Time   `json:"timestamp"`
}

type ProductUpdatedEvent struct {
    ProductID string    `json:"product_id"`
    Name      string    `json:"name"`
    Price     float64   `json:"price"`
    Stock     int       `json:"stock"`
    Timestamp time.Time `json:"timestamp"`
}

type EventHandler interface {
    Handle(event *Event) error
}
```

### 事件发布和订阅
```go
// events/publisher.go
package events

import (
   "context"
   "encoding/json"
	"time"

	"github.com/go-redis/redis/v8"
)

type EventPublisher struct {
	redis *redis.Client
}

func NewEventPublisher(redisAddr string) *EventPublisher {
	return &EventPublisher{
		redis: redis.NewClient(&redis.Options{
			Addr: redisAddr,
		}),
	}
}

func (p *EventPublisher) Publish(ctx context.Context, eventType string, data interface{}) error {
	event := &Event{
		ID:        generateEventID(),
		Type:      eventType,
		Source:    getHostName(),
		Data:      data,
		Timestamp: time.Now(),
	}

	eventData, err := json.Marshal(event)
	if err != nil {
		return err
	}

	return p.redis.Publish(ctx, "events", eventData).Err()
}

// events/subscriber.go
package events

import (
	"context"
	"encoding/json"
	"log"

	"github.com/go-redis/redis/v8"
)

type EventSubscriber struct {
	redis   *redis.Client
	handlers map[string]EventHandler
}

func NewEventSubscriber(redisAddr string) *EventSubscriber {
	return &EventSubscriber{
		redis: redis.NewClient(&redis.Options{
			Addr: redisAddr,
		}),
		handlers: make(map[string]EventHandler),
	}
}

func (s *EventSubscriber) Subscribe(eventType string, handler EventHandler) {
	s.handlers[eventType] = handler
}

func (s *EventSubscriber) Start(ctx context.Context) error {
	pubsub := s.redis.Subscribe(ctx, "events")
	defer pubsub.Close()

	ch := pubsub.Channel()
	for {
		select {
		case <-ctx.Done():
			return nil
		case msg := <-ch:
			var event Event
			if err := json.Unmarshal([]byte(msg.Payload), &event); err != nil {
				log.Printf("Failed to unmarshal event: %v", err)
				continue
			}

			handler, ok := s.handlers[event.Type]
			if !ok {
				log.Printf("No handler for event type: %s", event.Type)
				continue
			}

			if err := handler.Handle(&event); err != nil {
				log.Printf("Failed to handle event: %v", err)
			}
		}
	}
}
```

## 分布式追踪

### Jaeger集成
```go
// tracing/tracing.go
package tracing

import (
	"io"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.4.0"
	"go.opentelemetry.io/otel/trace"
)

func InitTracer(serviceName, jaegerURL string) (func(), error) {
	// 创建Jaeger导出器
	exp, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint(jaegerURL)))
	if err != nil {
		return nil, err
	}

	// 创建资源
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceNameKey.String(serviceName),
			semconv.DeploymentEnvironmentKey.String("production"),
		),
	)
	if err != nil {
		return nil, err
	}

	// 创建追踪器提供者
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exp),
		sdktrace.WithResource(res),
	)

	// 注册全局追踪器
	otel.SetTracerProvider(tp)

	// 返回清理函数
	return func() {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := tp.Shutdown(ctx); err != nil {
			log.Printf("Failed to shutdown tracer provider: %v", err)
		}
	}, nil
}

func StartSpan(ctx context.Context, tracer trace.Tracer, name string) (context.Context, trace.Span) {
	return tracer.Start(ctx, name)
}
```

### 中间件集成
```go
// middleware/tracing.go
package middleware

import (
	"net/http"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"

	"github.com/gin-gonic/gin"
)

func TracingMiddleware(serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 创建追踪上下文
		tracer := otel.Tracer(serviceName)
		ctx, span := tracer.Start(c.Request.Context(), c.Request.URL.Path)
		defer span.End()

		// 设置属性
		span.SetAttributes(
			attribute.String("http.method", c.Request.Method),
			attribute.String("http.url", c.Request.URL.String()),
			attribute.String("http.host", c.Request.Host),
			attribute.String("http.scheme", c.Request.URL.Scheme),
		)

		// 更新上下文
		c.Request = c.Request.WithContext(ctx)

		// 继续处理请求
		c.Next()

		// 设置状态码属性
		span.SetAttributes(
			attribute.Int("http.status_code", c.Writer.Status()),
		)
	}
}
```

## 配置管理

### 配置结构
```go
// config/config.go
package config

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Server      ServerConfig      `mapstructure:"server"`
	Database    DatabaseConfig    `mapstructure:"database"`
	Redis       RedisConfig       `mapstructure:"redis"`
	JWT         JWTConfig         `mapstructure:"jwt"`
	Tracing     TracingConfig     `mapstructure:"tracing"`
	Services    ServicesConfig    `mapstructure:"services"`
}

type ServerConfig struct {
	Host         string        `mapstructure:"host"`
	Port         int           `mapstructure:"port"`
	ReadTimeout  time.Duration `mapstructure:"read_timeout"`
	WriteTimeout time.Duration `mapstructure:"write_timeout"`
	IdleTimeout  time.Duration `mapstructure:"idle_timeout"`
}

type DatabaseConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	User     string `mapstructure:"user"`
	Password string `mapstructure:"password"`
	DBName   string `mapstructure:"dbname"`
	SSLMode  string `mapstructure:"sslmode"`
}

type RedisConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	Password string `mapstructure:"password"`
	DB       int    `mapstructure:"db"`
}

type JWTConfig struct {
	Secret     string        `mapstructure:"secret"`
	ExpiresIn  time.Duration `mapstructure:"expires_in"`
	RefreshIn  time.Duration `mapstructure:"refresh_in"`
}

type TracingConfig struct {
	Enabled    bool   `mapstructure:"enabled"`
	JaegerURL  string `mapstructure:"jaeger_url"`
	ServiceName string `mapstructure:"service_name"`
}

type ServicesConfig struct {
	UserServiceURL    string `mapstructure:"user_service_url"`
	ProductServiceURL string `mapstructure:"product_service_url"`
	OrderServiceURL   string `mapstructure:"order_service_url"`
}

func LoadConfig(configPath string) (*Config, error) {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(configPath)
	viper.AddConfigPath(".")
	viper.AddConfigPath("./config")

	// 设置默认值
	setDefaults()

	// 环境变量覆盖
	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("failed to read config: %w", err)
	}

	var config Config
	if err := viper.Unmarshal(&config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return &config, nil
}

func setDefaults() {
	viper.SetDefault("server.host", "0.0.0.0")
	viper.SetDefault("server.port", 8080)
	viper.SetDefault("server.read_timeout", "15s")
	viper.SetDefault("server.write_timeout", "15s")
	viper.SetDefault("server.idle_timeout", "60s")

	viper.SetDefault("database.host", "localhost")
	viper.SetDefault("database.port", 5432)
	viper.SetDefault("database.sslmode", "disable")

	viper.SetDefault("redis.host", "localhost")
	viper.SetDefault("redis.port", 6379)
	viper.SetDefault("redis.db", 0)

	viper.SetDefault("jwt.expires_in", "24h")
	viper.SetDefault("jwt.refresh_in", "168h")

	viper.SetDefault("tracing.enabled", true)
	viper.SetDefault("tracing.jaeger_url", "http://localhost:14268/api/traces")
}

func GetEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func GetEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
```

## 部署配置

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Gateway
  api-gateway:
    image: envoyproxy/envoy:v1.25-latest
    ports:
      - "8080:8080"
      - "8081:8081"
    volumes:
      - ./api-gateway/envoy.yaml:/etc/envoy/envoy.yaml
    depends_on:
      - user-service
      - product-service
      - order-service
    networks:
      - microservices

  # User Service
  user-service:
    build: ./user-service
    ports:
      - "8082:8080"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_NAME=user_service
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET=your-secret-key
      - JAEGER_URL=http://jaeger:14268/api/traces
    depends_on:
      - postgres
      - redis
      - jaeger
    networks:
      - microservices

  # Product Service
  product-service:
    build: ./product-service
    ports:
      - "8083:8080"
    environment:
      - DB_HOST=mongo
      - DB_PORT=27017
      - DB_NAME=product_service
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JAEGER_URL=http://jaeger:14268/api/traces
    depends_on:
      - mongo
      - redis
      - jaeger
    networks:
      - microservices

  # Order Service
  order-service:
    build: ./order-service
    ports:
      - "8084:8080"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_NAME=order_service
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - USER_SERVICE_URL=http://user-service:8080
      - PRODUCT_SERVICE_URL=http://product-service:8080
      - JAEGER_URL=http://jaeger:14268/api/traces
    depends_on:
      - postgres
      - redis
      - jaeger
    networks:
      - microservices

  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_MULTIPLE_DATABASES=user_service,order_service
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - microservices

  mongo:
    image: mongo:6
    environment:
      - MONGO_INITDB_DATABASE=product_service
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    networks:
      - microservices

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - microservices

  # Monitoring
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - microservices

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - microservices

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - microservices

volumes:
  postgres_data:
  mongo_data:
  redis_data:
  grafana_data:

networks:
  microservices:
    driver: bridge
```

### Kubernetes部署
```yaml
# k8s/user-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: database-config
              key: host
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: password
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

## 监控和日志

### Prometheus指标
```go
// monitoring/metrics.go
package monitoring

import (
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// HTTP请求指标
	httpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status"},
	)

	httpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "Duration of HTTP requests",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)

	// 业务指标
	userRegistrationsTotal = promauto.NewCounter(
		prometheus.CounterOpts{
			Name: "user_registrations_total",
			Help: "Total number of user registrations",
		},
	)

	ordersTotal = promauto.NewCounter(
		prometheus.CounterOpts{
			Name: "orders_total",
			Help: "Total number of orders created",
		},
	)

	// 数据库指标
	dbConnectionsActive = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "db_connections_active",
			Help: "Number of active database connections",
		},
	)

	// Redis指标
	redisCommandsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "redis_commands_total",
			Help: "Total number of Redis commands",
		},
		[]string{"command"},
	)
)

func RecordHTTPRequest(method, endpoint string, status int, duration time.Duration) {
	httpRequestsTotal.WithLabelValues(method, endpoint, strconv.Itoa(status)).Inc()
	httpRequestDuration.WithLabelValues(method, endpoint).Observe(duration.Seconds())
}

func RecordUserRegistration() {
	userRegistrationsTotal.Inc()
}

func RecordOrder() {
	ordersTotal.Inc()
}

func UpdateDBConnections(count int) {
	dbConnectionsActive.Set(float64(count))
}

func RecordRedisCommand(command string) {
	redisCommandsTotal.WithLabelValues(command).Inc()
}
```

### 结构化日志
```go
// logging/logger.go
package logging

import (
	"log/slog"
	"os"
	"time"

	"github.com/lmittmann/tint"
)

type Logger struct {
	*slog.Logger
}

type LogFields map[string]interface{}

func NewLogger(serviceName string) *Logger {
	handler := tint.NewHandler(os.Stdout, &tint.Options{
		Level:      slog.LevelDebug,
		TimeFormat: time.RFC3339,
		AddSource:  true,
	})

	logger := slog.New(handler)
	logger = logger.With("service", serviceName)

	return &Logger{Logger: logger}
}

func (l *Logger) WithFields(fields LogFields) *Logger {
	var args []interface{}
	for key, value := range fields {
		args = append(args, key, value)
	}
	return &Logger{Logger: l.Logger.With(args...)}
}

func (l *Logger) Info(msg string, fields LogFields) {
	if len(fields) > 0 {
		l.Logger.Info(msg, l.slogFields(fields)...)
	} else {
		l.Logger.Info(msg)
	}
}

func (l *Logger) Error(msg string, fields LogFields) {
	if len(fields) > 0 {
		l.Logger.Error(msg, l.slogFields(fields)...)
	} else {
		l.Logger.Error(msg)
	}
}

func (l *Logger) Debug(msg string, fields LogFields) {
	if len(fields) > 0 {
		l.Logger.Debug(msg, l.slogFields(fields)...)
	} else {
		l.Logger.Debug(msg)
	}
}

func (l *Logger) slogFields(fields LogFields) []interface{} {
	var args []interface{}
	for key, value := range fields {
		args = append(args, key, value)
	}
	return args
}
```

## 测试策略

### 单元测试
```go
// services/user_service_test.go
package services

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockUserRepository
type MockUserRepository struct {
	mock.Mock
}

func (m *MockUserRepository) Create(ctx context.Context, user *User) (*User, error) {
	args := m.Called(ctx, user)
	return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) GetByID(ctx context.Context, id string) (*User, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) GetByEmail(ctx context.Context, email string) (*User, error) {
	args := m.Called(ctx, email)
	return args.Get(0).(*User), args.Error(1)
}

func TestUserService_CreateUser(t *testing.T) {
	// 准备测试数据
	ctx := context.Background()
	user := &User{
		Username: "testuser",
		Email:    "test@example.com",
		Password: "hashedpassword",
	}

	// 创建mock
	mockRepo := new(MockUserRepository)
	mockRepo.On("Create", ctx, user).Return(user, nil)
	mockRepo.On("GetByEmail", ctx, user.Email).Return((*User)(nil), nil)

	// 创建服务
	service := NewUserService(mockRepo)

	// 执行测试
	result, err := service.CreateUser(ctx, user)

	// 验证结果
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, user.Username, result.Username)
	assert.Equal(t, user.Email, result.Email)

	// 验证mock调用
	mockRepo.AssertExpectations(t)
}

func TestUserService_GetUser(t *testing.T) {
	// 准备测试数据
	ctx := context.Background()
	userID := "123"
	expectedUser := &User{
		ID:       userID,
		Username: "testuser",
		Email:    "test@example.com",
	}

	// 创建mock
	mockRepo := new(MockUserRepository)
	mockRepo.On("GetByID", ctx, userID).Return(expectedUser, nil)

	// 创建服务
	service := NewUserService(mockRepo)

	// 执行测试
	result, err := service.GetUser(ctx, userID)

	// 验证结果
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, expectedUser.ID, result.ID)
	assert.Equal(t, expectedUser.Username, result.Username)

	// 验证mock调用
	mockRepo.AssertExpectations(t)
}
```

### 集成测试
```go
// integration/user_service_integration_test.go
package integration

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
)

type UserServiceIntegrationSuite struct {
	suite.Suite
	server *httptest.Server
}

func (suite *UserServiceIntegrationSuite) SetupSuite() {
	// 初始化测试数据库
	suite.SetupTestDatabase()

	// 创建测试服务器
	suite.server = httptest.NewServer(CreateUserRouter())
}

func (suite *UserServiceIntegrationSuite) TearDownSuite() {
	suite.server.Close()
	suite.CleanupTestDatabase()
}

func (suite *UserServiceIntegrationSuite) TestCreateUser() {
	// 准备测试数据
	user := map[string]interface{}{
		"username":  "testuser",
		"email":     "test@example.com",
		"password":  "password123",
		"first_name": "Test",
		"last_name":  "User",
	}

	// 发送请求
	jsonData, _ := json.Marshal(user)
	resp, err := http.Post(suite.server.URL+"/api/v1/users", "application/json", bytes.NewBuffer(jsonData))

	// 验证响应
	assert.NoError(suite.T(), err)
	assert.Equal(suite.T(), http.StatusCreated, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	assert.NoError(suite.T(), err)

	// 验证返回数据
	assert.Contains(suite.T(), response, "id")
	assert.Contains(suite.T(), response, "username")
	assert.Contains(suite.T(), response, "email")
	assert.Equal(suite.T(), "testuser", response["username"])
	assert.Equal(suite.T(), "test@example.com", response["email"])
}

func (suite *UserServiceIntegrationSuite) TestGetUser() {
	// 首先创建用户
	user := map[string]interface{}{
		"username":  "testuser2",
		"email":     "test2@example.com",
		"password":  "password123",
		"first_name": "Test",
		"last_name":  "User2",
	}

	jsonData, _ := json.Marshal(user)
	resp, err := http.Post(suite.server.URL+"/api/v1/users", "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(suite.T(), err)

	var createdUser map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&createdUser)
	assert.NoError(suite.T(), err)

	// 获取用户信息
	resp, err = http.Get(suite.server.URL + "/api/v1/users/" + createdUser["id"].(string))
	assert.NoError(suite.T(), err)
	assert.Equal(suite.T(), http.StatusOK, resp.StatusCode)

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	assert.NoError(suite.T(), err)

	// 验证返回数据
	assert.Equal(suite.T(), createdUser["id"], response["id"])
	assert.Equal(suite.T(), "testuser2", response["username"])
	assert.Equal(suite.T(), "test2@example.com", response["email"])
}

func TestUserServiceIntegrationSuite(t *testing.T) {
	suite.Run(t, new(UserServiceIntegrationSuite))
}
```

## 项目启动指南

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/your-username/go-microservices-demo.git
cd go-microservices-demo

# 安装依赖
go mod download

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等配置
```

### 2. 启动服务
```bash
# 使用Docker Compose启动所有服务
docker-compose up -d

# 或者手动启动各个服务
# 启动用户服务
cd user-service
go run main.go

# 启动产品服务
cd product-service
go run main.go

# 启动订单服务
cd order-service
go run main.go
```

### 3. 测试API
```bash
# 用户注册
curl -X POST http://localhost:8080/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 用户登录
curl -X POST http://localhost:8080/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 创建产品
curl -X POST http://localhost:8080/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"Test Product","price":99.99,"stock":100,"category":"Electronics"}'

# 创建订单
curl -X POST http://localhost:8080/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"items":[{"product_id":"PRODUCT_ID","quantity":1}]}'
```

## 扩展功能

### 1. 消息队列集成
```go
// messaging/rabbitmq.go
package messaging

import (
	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitMQClient struct {
	conn    *amqp.Connection
	channel *amqp.Channel
}

func NewRabbitMQClient(url string) (*RabbitMQClient, error) {
	conn, err := amqp.Dial(url)
	if err != nil {
		return nil, err
	}

	channel, err := conn.Channel()
	if err != nil {
		return nil, err
	}

	return &RabbitMQClient{
		conn:    conn,
		channel: channel,
	}, nil
}

func (r *RabbitMQClient) Publish(exchange, key string, message []byte) error {
	return r.channel.Publish(
		exchange,
		key,
		false,
		false,
		amqp.Publishing{
			ContentType: "application/json",
			Body:        message,
		},
	)
}

func (r *RabbitMQClient) Consume(queue, consumer string) (<-chan amqp.Delivery, error) {
	return r.channel.Consume(
		queue,
		consumer,
		true,
		false,
		false,
		false,
		nil,
	)
}

func (r *RabbitMQClient) Close() error {
	if r.channel != nil {
		r.channel.Close()
	}
	if r.conn != nil {
		r.conn.Close()
	}
	return nil
}
```

### 2. 缓存策略
```go
// cache/cache.go
package cache

import (
	"context"
	"encoding/json"
	"time"

	"github.com/go-redis/redis/v8"
)

type Cache struct {
	client *redis.Client
}

func NewCache(addr string) *Cache {
	return &Cache{
		client: redis.NewClient(&redis.Options{
			Addr: addr,
		}),
	}
}

func (c *Cache) Set(ctx context.Context, key string, value interface{}, expiration time.Duration) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}

	return c.client.Set(ctx, key, data, expiration).Err()
}

func (c *Cache) Get(ctx context.Context, key string, dest interface{}) error {
	data, err := c.client.Get(ctx, key).Result()
	if err != nil {
		return err
	}

	return json.Unmarshal([]byte(data), dest)
}

func (c *Cache) Delete(ctx context.Context, key string) error {
	return c.client.Del(ctx, key).Err()
}

func (c *Cache) Exists(ctx context.Context, key string) (bool, error) {
	count, err := c.client.Exists(ctx, key).Result()
	return count > 0, err
}
```

### 3. 限流和熔断
```go
// middleware/rate_limiter.go
package middleware

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"golang.org/x/time/rate"
)

func RateLimiter(r rate.Limit, b int) gin.HandlerFunc {
	limiter := rate.NewLimiter(r, b)

	return func(c *gin.Context) {
		if !limiter.Allow() {
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error": "Too many requests",
			})
			c.Abort()
			return
		}
		c.Next()
	}
}

// middleware/circuit_breaker.go
package middleware

import (
	"net/http"
	"sync/atomic"

	"github.com/gin-gonic/gin"
	"github.com/sony/gobreaker"
)

type CircuitBreaker struct {
	cb *gobreaker.CircuitBreaker
}

func NewCircuitBreaker() *CircuitBreaker {
	settings := gobreaker.Settings{
		Name:        "HTTP Circuit Breaker",
		MaxRequests: 5,
		Interval:    10 * time.Second,
		Timeout:     5 * time.Second,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			return counts.ConsecutiveFailures > 3
		},
		OnStateChange: func(name string, from, to gobreaker.State) {
			// 记录状态变化
		},
	}

	return &CircuitBreaker{
		cb: gobreaker.NewCircuitBreaker(settings),
	}
}

func (cb *CircuitBreaker) Middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		_, err := cb.cb.Execute(func() (interface{}, error) {
			c.Next()
			return nil, c.Errors.Last()
		})

		if err != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"error": "Service unavailable",
			})
			c.Abort()
			return
		}
	}
}
```

## 总结
通过这个微服务实战项目，您将学习到如何使用Go语言构建完整的微服务架构，包括：

1. **服务拆分**: 如何将应用拆分为多个独立的服务
2. **服务间通信**: 使用gRPC进行服务间高效通信
3. **事件驱动**: 实现松耦合的事件驱动架构
4. **分布式追踪**: 使用Jaeger进行分布式追踪
5. **监控和日志**: 完整的监控和日志系统
6. **容器化部署**: 使用Docker和Kubernetes进行部署
7. **测试策略**: 单元测试、集成测试和端到端测试

这个项目展示了Go语言在微服务开发中的强大能力，通过合理的设计模式和最佳实践，可以构建出高性能、可扩展的微服务系统。

*最后更新: 2025年9月*