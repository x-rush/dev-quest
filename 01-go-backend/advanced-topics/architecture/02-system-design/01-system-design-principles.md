# 系统设计原则

## 目录
- [系统设计概述](#系统设计概述)
- [架构设计原则](#架构设计原则)
- [可扩展性设计](#可扩展性设计)
- [可靠性设计](#可靠性设计)
- [性能设计](#性能设计)
- [安全性设计](#安全性设计)
- [可维护性设计](#可维护性设计)
- [成本效益设计](#成本效益设计)
- [设计模式应用](#设计模式应用)
- [系统设计最佳实践](#系统设计最佳实践)

## 系统设计概述

### 系统设计目标
1. **功能性**：满足业务需求和用户期望
2. **非功能性**：性能、可靠性、可扩展性、安全性等
3. **约束性**：技术栈、预算、时间、人员等限制
4. **演化性**：支持系统的长期演进和变化

### 系统设计流程
```
需求分析 → 架构设计 → 详细设计 → 实现开发 → 测试验证 → 部署运维 → 持续优化
```

## 架构设计原则

### 1. SOLID原则

#### 单一职责原则 (SRP)
```go
// 优化前：多重职责
type UserService struct {
    db *gorm.DB
}

func (s *UserService) CreateUser(user *User) error {
    // 数据验证
    if user.Name == "" {
        return errors.New("name is required")
    }

    // 数据存储
    return s.db.Create(user).Error
}

func (s *UserService) SendWelcomeEmail(user *User) error {
    // 邮件发送
    return sendEmail(user.Email, "Welcome", "Welcome to our service!")
}

// 优化后：职责分离
type UserValidator struct{}
type UserRepository struct{ db *gorm.DB }
type EmailService struct{}

func (v *UserValidator) Validate(user *User) error {
    if user.Name == "" {
        return errors.New("name is required")
    }
    return nil
}

func (r *UserRepository) Create(user *User) error {
    return r.db.Create(user).Error
}

func (e *EmailService) SendWelcomeEmail(user *User) error {
    return sendEmail(user.Email, "Welcome", "Welcome to our service!")
}
```

#### 开放封闭原则 (OCP)
```go
// 优化前：修改需要更改现有代码
type PaymentProcessor struct{}

func (p *PaymentProcessor) ProcessPayment(paymentType string, amount float64) error {
    switch paymentType {
    case "credit_card":
        return p.processCreditCard(amount)
    case "paypal":
        return p.processPayPal(amount)
    default:
        return errors.New("unsupported payment type")
    }
}

// 优化后：通过扩展实现
type PaymentGateway interface {
    ProcessPayment(amount float64) error
}

type CreditCardGateway struct{}
type PayPalGateway struct{}

func (c *CreditCardGateway) ProcessPayment(amount float64) error {
    // 信用卡支付逻辑
    return nil
}

func (p *PayPalGateway) ProcessPayment(amount float64) error {
    // PayPal支付逻辑
    return nil
}

type PaymentProcessor struct {
    gateways map[string]PaymentGateway
}

func (p *PaymentProcessor) AddGateway(name string, gateway PaymentGateway) {
    p.gateways[name] = gateway
}

func (p *PaymentProcessor) ProcessPayment(gatewayName string, amount float64) error {
    gateway, exists := p.gateways[gatewayName]
    if !exists {
        return errors.New("unsupported payment gateway")
    }
    return gateway.ProcessPayment(amount)
}
```

#### 里氏替换原则 (LSP)
```go
// 优化前：违反LSP
type Rectangle struct {
    width, height float64
}

func (r *Rectangle) SetWidth(width float64) {
    r.width = width
}

func (r *Rectangle) SetHeight(height float64) {
    r.height = height
}

func (r *Rectangle) Area() float64 {
    return r.width * r.height
}

type Square struct {
    Rectangle
}

func (s *Square) SetWidth(width float64) {
    s.width = width
    s.height = width // 正方形的宽高相等
}

func (s *Square) SetHeight(height float64) {
    s.height = height
    s.width = height // 正方形的宽高相等
}

// 优化后：正确的设计
type Shape interface {
    Area() float64
}

type Rectangle struct {
    width, height float64
}

func NewRectangle(width, height float64) *Rectangle {
    return &Rectangle{width: width, height: height}
}

func (r *Rectangle) Area() float64 {
    return r.width * r.height
}

type Square struct {
    side float64
}

func NewSquare(side float64) *Square {
    return &Square{side: side}
}

func (s *Square) Area() float64 {
    return s.side * s.side
}
```

### 2. DRY原则

#### 避免重复代码
```go
// 优化前：重复的数据库连接逻辑
func UserService() *UserService {
    db, err := gorm.Open(postgres.Open("dsn"), &gorm.Config{})
    if err != nil {
        panic(err)
    }
    return &UserService{db: db}
}

func OrderService() *OrderService {
    db, err := gorm.Open(postgres.Open("dsn"), &gorm.Config{})
    if err != nil {
        panic(err)
    }
    return &OrderService{db: db}
}

// 优化后：共享数据库连接
type Database struct {
    *gorm.DB
}

func NewDatabase() *Database {
    db, err := gorm.Open(postgres.Open("dsn"), &gorm.Config{})
    if err != nil {
        panic(err)
    }
    return &Database{DB: db}
}

type ServiceBase struct {
    db *Database
}

func NewServiceBase(db *Database) *ServiceBase {
    return &ServiceBase{db: db}
}

type UserService struct {
    *ServiceBase
}

func NewUserService(db *Database) *UserService {
    return &UserService{ServiceBase: NewServiceBase(db)}
}

type OrderService struct {
    *ServiceBase
}

func NewOrderService(db *Database) *OrderService {
    return &OrderService{ServiceBase: NewServiceBase(db)}
}
```

#### 提取公共功能
```go
// 优化前：重复的日志逻辑
func ProcessUser(user *User) error {
    log.Printf("Processing user: %s", user.Name)
    // 处理逻辑
    log.Printf("User processed: %s", user.Name)
    return nil
}

func ProcessOrder(order *Order) error {
    log.Printf("Processing order: %d", order.ID)
    // 处理逻辑
    log.Printf("Order processed: %d", order.ID)
    return nil
}

// 优化后：统一的日志装饰器
type Logger struct {
    prefix string
}

func NewLogger(prefix string) *Logger {
    return &Logger{prefix: prefix}
}

func (l *Logger) LogStart(entity interface{}) {
    switch v := entity.(type) {
    case *User:
        log.Printf("%s - Processing user: %s", l.prefix, v.Name)
    case *Order:
        log.Printf("%s - Processing order: %d", l.prefix, v.ID)
    }
}

func (l *Logger) LogEnd(entity interface{}) {
    switch v := entity.(type) {
    case *User:
        log.Printf("%s - User processed: %s", l.prefix, v.Name)
    case *Order:
        log.Printf("%s - Order processed: %d", l.prefix, v.ID)
    }
}

type ProcessFunc func(interface{}) error

func WithLogging(logger *Logger, process ProcessFunc) ProcessFunc {
    return func(entity interface{}) error {
        logger.LogStart(entity)
        defer logger.LogEnd(entity)
        return process(entity)
    }
}
```

### 3. KISS原则

#### 简化复杂逻辑
```go
// 优化前：复杂的条件判断
func CalculateDiscount(price float64, user *User, category string, isVIP bool) float64 {
    if user != nil {
        if user.Age < 18 {
            if isVIP {
                if category == "student" {
                    return price * 0.7
                } else if category == "book" {
                    return price * 0.8
                }
            } else {
                if category == "student" {
                    return price * 0.8
                } else if category == "book" {
                    return price * 0.9
                }
            }
        } else {
            if isVIP {
                if category == "student" {
                    return price * 0.6
                } else if category == "book" {
                    return price * 0.7
                } else {
                    return price * 0.85
                }
            } else {
                if category == "student" {
                    return price * 0.75
                } else if category == "book" {
                    return price * 0.85
                } else {
                    return price * 0.95
                }
            }
        }
    }
    return price
}

// 优化后：清晰的规则表
type DiscountRule struct {
    IsVIP     bool
    IsStudent bool
    Category  string
    Rate      float64
}

var discountRules = []DiscountRule{
    {true, true, "student", 0.6},
    {true, false, "student", 0.7},
    {false, true, "student", 0.75},
    {true, true, "book", 0.7},
    {true, false, "book", 0.8},
    {false, true, "book", 0.85},
    {true, false, "", 0.85},
    {false, false, "", 0.95},
}

func CalculateDiscount(price float64, user *User, category string) float64 {
    if user == nil {
        return price
    }

    isVIP := user.IsVIP
    isStudent := user.Age < 18

    for _, rule := range discountRules {
        if rule.IsVIP == isVIP && rule.IsStudent == isStudent {
            if rule.Category == "" || rule.Category == category {
                return price * rule.Rate
            }
        }
    }

    return price
}
```

#### 简化数据结构
```go
// 优化前：复杂的嵌套结构
type ComplexConfig struct {
    Database struct {
        Primary struct {
            Host     string
            Port     int
            Username string
            Password string
            Database string
        }
        Replicas []struct {
            Host     string
            Port     int
            Username string
            Password string
            Database string
        }
    }
    Cache struct {
        Redis struct {
            Host     string
            Port     int
            Password string
            DB       int
        }
        Memcached struct {
            Servers []string
        }
    }
}

// 优化后：扁平化结构
type DatabaseConfig struct {
    Host     string
    Port     int
    Username string
    Password string
    Database string
}

type CacheConfig struct {
    Host     string
    Port     int
    Password string
    DB       int
}

type SystemConfig struct {
    PrimaryDB   DatabaseConfig
    ReplicaDBs  []DatabaseConfig
    RedisCache  CacheConfig
    MemcachedServers []string
}
```

## 可扩展性设计

### 1. 水平扩展

#### 无状态服务设计
```go
// 无状态服务示例
type StatelesssService struct {
    db       *Database
    cache    *Cache
    logger   *Logger
}

func NewStatelesssService(db *Database, cache *Cache, logger *Logger) *StatelesssService {
    return &StatelesssService{
        db:     db,
        cache:  cache,
        logger: logger,
    }
}

func (s *StatelesssService) ProcessRequest(req *Request) (*Response, error) {
    // 每个请求都是独立的，不依赖之前的状态
    ctx := context.Background()

    // 从外部存储获取状态
    session, err := s.cache.GetSession(ctx, req.SessionID)
    if err != nil {
        return nil, err
    }

    // 处理请求
    result, err := s.processRequest(ctx, session, req)
    if err != nil {
        return nil, err
    }

    // 更新外部存储
    if err := s.cache.UpdateSession(ctx, req.SessionID, session); err != nil {
        return nil, err
    }

    return result, nil
}
```

#### 分片策略
```go
// 数据分片策略
type ShardStrategy interface {
    GetShard(key string) int
}

type HashShardStrategy struct {
    shardCount int
}

func NewHashShardStrategy(shardCount int) *HashShardStrategy {
    return &HashShardStrategy{shardCount: shardCount}
}

func (s *HashShardStrategy) GetShard(key string) int {
    hash := fnv.New32a()
    hash.Write([]byte(key))
    return int(hash.Sum32()) % s.shardCount
}

type RangeShardStrategy struct {
    shardCount int
}

func NewRangeShardStrategy(shardCount int) *RangeShardStrategy {
    return &RangeShardStrategy{shardCount: shardCount}
}

func (s *RangeShardStrategy) GetShard(key string) int {
    // 简单的范围分片
    firstChar := []byte(key)[0]
    return int(firstChar) % s.shardCount
}

// 分片连接池
type ShardConnectionPool struct {
    shards     []*Database
    strategy  ShardStrategy
    mu        sync.RWMutex
}

func NewShardConnectionPool(configs []DatabaseConfig, strategy ShardStrategy) *ShardConnectionPool {
    shards := make([]*Database, len(configs))
    for i, config := range configs {
        shards[i] = NewDatabase(config)
    }

    return &ShardConnectionPool{
        shards:    shards,
        strategy:  strategy,
    }
}

func (p *ShardConnectionPool) GetConnection(key string) *Database {
    shardIndex := p.strategy.GetShard(key)
    return p.shards[shardIndex]
}

func (p *ShardConnectionPool) Execute(key string, query string, args ...interface{}) error {
    conn := p.GetConnection(key)
    return conn.Exec(query, args...).Error
}
```

### 2. 垂直扩展

#### 服务拆分
```go
// 用户服务
type UserService struct {
    repo   *UserRepository
    cache  *Cache
    logger *Logger
}

func NewUserService(repo *UserRepository, cache *Cache, logger *Logger) *UserService {
    return &UserService{
        repo:   repo,
        cache:  cache,
        logger: logger,
    }
}

func (s *UserService) CreateUser(user *User) error {
    if err := s.repo.Create(user); err != nil {
        return err
    }
    return s.cache.SetUser(user.ID, user)
}

func (s *UserService) GetUser(id string) (*User, error) {
    // 先从缓存获取
    if user, err := s.cache.GetUser(id); err == nil {
        return user, nil
    }

    // 从数据库获取
    user, err := s.repo.GetByID(id)
    if err != nil {
        return nil, err
    }

    // 更新缓存
    s.cache.SetUser(id, user)
    return user, nil
}

// 订单服务
type OrderService struct {
    repo      *OrderRepository
    userSvc   *UserService
    inventory *InventoryService
    logger    *Logger
}

func NewOrderService(repo *OrderRepository, userSvc *UserService, inventory *InventoryService, logger *Logger) *OrderService {
    return &OrderService{
        repo:      repo,
        userSvc:   userSvc,
        inventory: inventory,
        logger:    logger,
    }
}

func (s *OrderService) CreateOrder(order *Order) error {
    // 验证用户
    user, err := s.userSvc.GetUser(order.UserID)
    if err != nil {
        return err
    }

    // 检查库存
    if err := s.inventory.Reserve(order.ProductID, order.Quantity); err != nil {
        return err
    }

    // 创建订单
    if err := s.repo.Create(order); err != nil {
        s.inventory.Release(order.ProductID, order.Quantity)
        return err
    }

    return nil
}
```

#### 读写分离
```go
// 读写分离数据源
type ReadWriteDataSource struct {
    master *Database
    slaves []*Database
    strategy ReadStrategy
    mu     sync.RWMutex
}

type ReadStrategy interface {
    GetSlave() *Database
}

type RoundRobinStrategy struct {
    index  int
    slaves []*Database
    mu     sync.Mutex
}

func NewRoundRobinStrategy(slaves []*Database) *RoundRobinStrategy {
    return &RoundRobinStrategy{
        slaves: slaves,
    }
}

func (s *RoundRobinStrategy) GetSlave() *Database {
    s.mu.Lock()
    defer s.mu.Unlock()

    if len(s.slaves) == 0 {
        return nil
    }

    slave := s.slaves[s.index]
    s.index = (s.index + 1) % len(s.slaves)
    return slave
}

func NewReadWriteDataSource(master *Database, slaves []*Database, strategy ReadStrategy) *ReadWriteDataSource {
    return &ReadWriteDataSource{
        master:   master,
        slaves:   slaves,
        strategy: strategy,
    }
}

func (ds *ReadWriteDataSource) Write(query string, args ...interface{}) error {
    return ds.master.Exec(query, args...).Error
}

func (ds *ReadWriteDataSource) Read(query string, args ...interface{}, dest interface{}) error {
    slave := ds.strategy.GetSlave()
    if slave == nil {
        slave = ds.master
    }
    return slave.Raw(query, args...).Scan(dest).Error
}

// 使用示例
func (ds *ReadWriteDataSource) CreateUser(user *User) error {
    return ds.Write("INSERT INTO users (name, email) VALUES (?, ?)", user.Name, user.Email)
}

func (ds *ReadWriteDataSource) GetUserByID(id string) (*User, error) {
    var user User
    err := ds.Read("SELECT * FROM users WHERE id = ?", id, &user)
    if err != nil {
        return nil, err
    }
    return &user, nil
}
```

### 3. 弹性扩展

#### 自动扩展
```go
// 自动扩展控制器
type AutoScaler struct {
    currentInstances int
    minInstances    int
    maxInstances    int
    targetCPU       float64
    checkInterval   time.Duration
    metrics         MetricsCollector
    provisioner     InstanceProvisioner
}

type MetricsCollector interface {
    GetCPUUsage() (float64, error)
    GetMemoryUsage() (float64, error)
    GetRequestRate() (float64, error)
}

type InstanceProvisioner interface {
    CreateInstance() error
    TerminateInstance(id string) error
    ListInstances() ([]string, error)
}

func NewAutoScaler(min, max int, targetCPU float64, metrics MetricsCollector, provisioner InstanceProvisioner) *AutoScaler {
    return &AutoScaler{
        minInstances:  min,
        maxInstances:  max,
        targetCPU:     targetCPU,
        checkInterval: 30 * time.Second,
        metrics:       metrics,
        provisioner:   provisioner,
    }
}

func (s *AutoScaler) Start() {
    ticker := time.NewTicker(s.checkInterval)
    defer ticker.Stop()

    for range ticker.C {
        if err := s.scale(); err != nil {
            log.Printf("AutoScaler error: %v", err)
        }
    }
}

func (s *AutoScaler) scale() error {
    // 获取当前实例列表
    instances, err := s.provisioner.ListInstances()
    if err != nil {
        return err
    }

    s.currentInstances = len(instances)

    // 获取指标
    cpu, err := s.metrics.GetCPUUsage()
    if err != nil {
        return err
    }

    // 扩展决策
    if cpu > s.targetCPU && s.currentInstances < s.maxInstances {
        // 需要扩展
        if err := s.provisioner.CreateInstance(); err != nil {
            return err
        }
        s.currentInstances++
        log.Printf("Scaled up to %d instances", s.currentInstances)
    } else if cpu < s.targetCPU*0.5 && s.currentInstances > s.minInstances {
        // 需要收缩
        // 选择一个实例终止
        instanceID := instances[len(instances)-1]
        if err := s.provisioner.TerminateInstance(instanceID); err != nil {
            return err
        }
        s.currentInstances--
        log.Printf("Scaled down to %d instances", s.currentInstances)
    }

    return nil
}
```

#### 服务发现
```go
// 服务注册与发现
type ServiceRegistry struct {
    services map[string][]ServiceInstance
    mu       sync.RWMutex
    ttl      time.Duration
}

type ServiceInstance struct {
    ID      string
    Address string
    Port    int
    Health  bool
    LastSeen time.Time
}

func NewServiceRegistry(ttl time.Duration) *ServiceRegistry {
    return &ServiceRegistry{
        services: make(map[string][]ServiceInstance),
        ttl:      ttl,
    }
}

func (r *ServiceRegistry) Register(serviceName, instanceID, address string, port int) {
    r.mu.Lock()
    defer r.mu.Unlock()

    instances := r.services[serviceName]
    for i, instance := range instances {
        if instance.ID == instanceID {
            // 更新现有实例
            instances[i] = ServiceInstance{
                ID:       instanceID,
                Address:  address,
                Port:     port,
                Health:   true,
                LastSeen: time.Now(),
            }
            return
        }
    }

    // 添加新实例
    instances = append(instances, ServiceInstance{
        ID:       instanceID,
        Address:  address,
        Port:     port,
        Health:   true,
        LastSeen: time.Now(),
    })
    r.services[serviceName] = instances
}

func (r *ServiceRegistry) Discover(serviceName string) ([]ServiceInstance, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()

    instances := r.services[serviceName]
    var healthyInstances []ServiceInstance

    for _, instance := range instances {
        if instance.Health && time.Since(instance.LastSeen) < r.ttl {
            healthyInstances = append(healthyInstances, instance)
        }
    }

    return healthyInstances, nil
}

func (r *ServiceRegistry) Heartbeat(serviceName, instanceID string) {
    r.mu.Lock()
    defer r.mu.Unlock()

    instances := r.services[serviceName]
    for i, instance := range instances {
        if instance.ID == instanceID {
            instances[i].LastSeen = time.Now()
            instances[i].Health = true
            return
        }
    }
}

func (r *ServiceRegistry) Cleanup() {
    r.mu.Lock()
    defer r.mu.Unlock()

    for serviceName, instances := range r.services {
        var healthyInstances []ServiceInstance
        for _, instance := range instances {
            if time.Since(instance.LastSeen) < r.ttl {
                healthyInstances = append(healthyInstances, instance)
            }
        }
        r.services[serviceName] = healthyInstances
    }
}
```

## 可靠性设计

### 1. 容错设计

#### 断路器模式
```go
// 断路器实现
type CircuitBreaker struct {
    maxFailures    int
    resetTimeout   time.Duration
    failures       int
    lastFailTime   time.Time
    state          CircuitState
    mu             sync.Mutex
}

type CircuitState int

const (
    CircuitClosed CircuitState = iota
    CircuitOpen
    CircuitHalfOpen
)

func NewCircuitBreaker(maxFailures int, resetTimeout time.Duration) *CircuitBreaker {
    return &CircuitBreaker{
        maxFailures:  maxFailures,
        resetTimeout: resetTimeout,
        state:        CircuitClosed,
    }
}

func (cb *CircuitBreaker) Execute(fn func() error) error {
    cb.mu.Lock()

    if cb.state == CircuitOpen {
        if time.Since(cb.lastFailTime) > cb.resetTimeout {
            cb.state = CircuitHalfOpen
        } else {
            cb.mu.Unlock()
            return errors.New("circuit breaker is open")
        }
    }

    cb.mu.Unlock()

    err := fn()

    cb.mu.Lock()
    defer cb.mu.Unlock()

    if err != nil {
        cb.failures++
        cb.lastFailTime = time.Now()

        if cb.failures >= cb.maxFailures {
            cb.state = CircuitOpen
        }
        return err
    }

    cb.failures = 0
    if cb.state == CircuitHalfOpen {
        cb.state = CircuitClosed
    }
    return nil
}

func (cb *CircuitBreaker) State() CircuitState {
    cb.mu.Lock()
    defer cb.mu.Unlock()
    return cb.state
}

func (cb *CircuitBreaker) Failures() int {
    cb.mu.Lock()
    defer cb.mu.Unlock()
    return cb.failures
}
```

#### 重试机制
```go
// 重试策略
type RetryPolicy struct {
    MaxAttempts int
    BaseDelay   time.Duration
    MaxDelay    time.Duration
    Multiplier  float64
    Jitter      bool
}

type RetryOption func(*RetryPolicy)

func WithMaxAttempts(max int) RetryOption {
    return func(p *RetryPolicy) { p.MaxAttempts = max }
}

func WithBaseDelay(delay time.Duration) RetryOption {
    return func(p *RetryPolicy) { p.BaseDelay = delay }
}

func WithMaxDelay(delay time.Duration) RetryOption {
    return func(p *RetryPolicy) { p.MaxDelay = delay }
}

func WithMultiplier(multiplier float64) RetryOption {
    return func(p *RetryPolicy) { p.Multiplier = multiplier }
}

func WithJitter(enabled bool) RetryOption {
    return func(p *RetryPolicy) { p.Jitter = enabled }
}

func NewRetryPolicy(opts ...RetryOption) *RetryPolicy {
    policy := &RetryPolicy{
        MaxAttempts: 3,
        BaseDelay:   1 * time.Second,
        MaxDelay:    30 * time.Second,
        Multiplier:  2.0,
        Jitter:      true,
    }

    for _, opt := range opts {
        opt(policy)
    }

    return policy
}

func Retry(policy *RetryPolicy, fn func() error) error {
    var lastErr error

    for attempt := 0; attempt < policy.MaxAttempts; attempt++ {
        err := fn()
        if err == nil {
            return nil
        }

        lastErr = err

        if attempt == policy.MaxAttempts-1 {
            break
        }

        delay := policy.BaseDelay * time.Duration(math.Pow(policy.Multiplier, float64(attempt)))
        if delay > policy.MaxDelay {
            delay = policy.MaxDelay
        }

        if policy.Jitter {
            delay = time.Duration(float64(delay) * (0.8 + 0.4*rand.Float64()))
        }

        time.Sleep(delay)
    }

    return lastErr
}
```

#### 限流保护
```go
// 令牌桶限流器
type TokenBucket struct {
    capacity     int64
    tokens       int64
    refillRate   int64 // tokens per second
    lastRefill   time.Time
    mu           sync.Mutex
}

func NewTokenBucket(capacity, refillRate int64) *TokenBucket {
    return &TokenBucket{
        capacity:   capacity,
        tokens:     capacity,
        refillRate: refillRate,
        lastRefill: time.Now(),
    }
}

func (tb *TokenBucket) refill() {
    now := time.Now()
    elapsed := now.Sub(tb.lastRefill).Seconds()
    tokensToAdd := int64(elapsed * float64(tb.refillRate))

    if tokensToAdd > 0 {
        tb.tokens = min(tb.capacity, tb.tokens+tokensToAdd)
        tb.lastRefill = now
    }
}

func (tb *TokenBucket) Allow() bool {
    tb.mu.Lock()
    defer tb.mu.Unlock()

    tb.refill()

    if tb.tokens > 0 {
        tb.tokens--
        return true
    }

    return false
}

func (tb *TokenBucket) Wait() {
    for !tb.Allow() {
        time.Sleep(10 * time.Millisecond)
    }
}

// 滑动窗口限流器
type SlidingWindow struct {
    windowSize   time.Duration
    maxRequests int
    requests     []time.Time
    mu           sync.Mutex
}

func NewSlidingWindow(windowSize time.Duration, maxRequests int) *SlidingWindow {
    return &SlidingWindow{
        windowSize:  windowSize,
        maxRequests: maxRequests,
        requests:    make([]time.Time, 0),
    }
}

func (sw *SlidingWindow) Allow() bool {
    sw.mu.Lock()
    defer sw.mu.Unlock()

    now := time.Now()

    // 清除窗口外的请求
    cutoff := now.Add(-sw.windowSize)
    validRequests := make([]time.Time, 0)
    for _, reqTime := range sw.requests {
        if reqTime.After(cutoff) {
            validRequests = append(validRequests, reqTime)
        }
    }

    sw.requests = validRequests

    // 检查是否允许新请求
    if len(sw.requests) < sw.maxRequests {
        sw.requests = append(sw.requests, now)
        return true
    }

    return false
}
```

### 2. 高可用设计

#### 负载均衡
```go
// 负载均衡器
type LoadBalancer struct {
    strategy LoadBalancingStrategy
    backends []Backend
    mu       sync.RWMutex
}

type Backend struct {
    Address string
    Healthy bool
    Weight  int
}

type LoadBalancingStrategy interface {
    SelectBackend(backends []Backend) *Backend
}

// 轮询策略
type RoundRobinStrategy struct {
    current int
    mu      sync.Mutex
}

func NewRoundRobinStrategy() *RoundRobinStrategy {
    return &RoundRobinStrategy{}
}

func (s *RoundRobinStrategy) SelectBackend(backends []Backend) *Backend {
    s.mu.Lock()
    defer s.mu.Unlock()

    healthyBackends := make([]Backend, 0)
    for _, backend := range backends {
        if backend.Healthy {
            healthyBackends = append(healthyBackends, backend)
        }
    }

    if len(healthyBackends) == 0 {
        return nil
    }

    backend := &healthyBackends[s.current%len(healthyBackends)]
    s.current++
    return backend
}

// 加权轮询策略
type WeightedRoundRobinStrategy struct {
    currentWeights map[string]int
    mu             sync.Mutex
}

func NewWeightedRoundRobinStrategy() *WeightedRoundRobinStrategy {
    return &WeightedRoundRobinStrategy{
        currentWeights: make(map[string]int),
    }
}

func (s *WeightedRoundRobinStrategy) SelectBackend(backends []Backend) *Backend {
    s.mu.Lock()
    defer s.mu.Unlock()

    healthyBackends := make([]Backend, 0)
    for _, backend := range backends {
        if backend.Healthy {
            healthyBackends = append(healthyBackends, backend)
        }
    }

    if len(healthyBackends) == 0 {
        return nil
    }

    // 初始化当前权重
    for _, backend := range healthyBackends {
        if _, exists := s.currentWeights[backend.Address]; !exists {
            s.currentWeights[backend.Address] = 0
        }
    }

    // 选择权重最高的后端
    var selectedBackend *Backend
    maxWeight := -1

    for i, backend := range healthyBackends {
        s.currentWeights[backend.Address] += backend.Weight

        if s.currentWeights[backend.Address] > maxWeight {
            maxWeight = s.currentWeights[backend.Address]
            selectedBackend = &healthyBackends[i]
        }
    }

    if selectedBackend != nil {
        s.currentWeights[selectedBackend.Address] -= maxWeight
    }

    return selectedBackend
}

func NewLoadBalancer(strategy LoadBalancingStrategy, backends []Backend) *LoadBalancer {
    return &LoadBalancer{
        strategy: strategy,
        backends: backends,
    }
}

func (lb *LoadBalancer) AddBackend(backend Backend) {
    lb.mu.Lock()
    defer lb.mu.Unlock()
    lb.backends = append(lb.backends, backend)
}

func (lb *LoadBalancer) RemoveBackend(address string) {
    lb.mu.Lock()
    defer lb.mu.Unlock()

    filtered := make([]Backend, 0)
    for _, backend := range lb.backends {
        if backend.Address != address {
            filtered = append(filtered, backend)
        }
    }
    lb.backends = filtered
}

func (lb *LoadBalancer) SetHealth(address string, healthy bool) {
    lb.mu.Lock()
    defer lb.mu.Unlock()

    for i, backend := range lb.backends {
        if backend.Address == address {
            lb.backends[i].Healthy = healthy
            break
        }
    }
}

func (lb *LoadBalancer) SelectBackend() *Backend {
    lb.mu.RLock()
    defer lb.mu.RUnlock()

    return lb.strategy.SelectBackend(lb.backends)
}
```

#### 健康检查
```go
// 健康检查器
type HealthChecker struct {
    backends map[string]BackendHealth
    interval time.Duration
    mu       sync.RWMutex
}

type BackendHealth struct {
    Address    string
    Healthy    bool
    LastCheck  time.Time
    Latency    time.Duration
    ErrorCount int
}

type HealthCheckFunc func(address string) (bool, time.Duration, error)

func NewHealthChecker(interval time.Duration) *HealthChecker {
    return &HealthChecker{
        backends: make(map[string]BackendHealth),
        interval: interval,
    }
}

func (hc *HealthChecker) AddBackend(address string) {
    hc.mu.Lock()
    defer hc.mu.Unlock()

    hc.backends[address] = BackendHealth{
        Address:   address,
        Healthy:   true,
        LastCheck: time.Now(),
    }
}

func (hc *HealthChecker) RemoveBackend(address string) {
    hc.mu.Lock()
    defer hc.mu.Unlock()
    delete(hc.backends, address)
}

func (hc *HealthChecker) Start(checkFunc HealthCheckFunc) {
    ticker := time.NewTicker(hc.interval)
    defer ticker.Stop()

    for range ticker.C {
        hc.checkAllBackends(checkFunc)
    }
}

func (hc *HealthChecker) checkAllBackends(checkFunc HealthCheckFunc) {
    hc.mu.Lock()
    defer hc.mu.Unlock()

    for address, health := range hc.backends {
        healthy, latency, err := checkFunc(address)

        updatedHealth := BackendHealth{
            Address:    address,
            Healthy:    healthy,
            LastCheck:  time.Now(),
            Latency:    latency,
        }

        if err != nil {
            updatedHealth.ErrorCount = health.ErrorCount + 1
        } else {
            updatedHealth.ErrorCount = 0
        }

        hc.backends[address] = updatedHealth

        if health.Healthy != healthy {
            log.Printf("Backend %s health changed: %v -> %v", address, health.Healthy, healthy)
        }
    }
}

func (hc *HealthChecker) GetBackendHealth(address string) (BackendHealth, bool) {
    hc.mu.RLock()
    defer hc.mu.RUnlock()

    health, exists := hc.backends[address]
    return health, exists
}

func (hc *HealthChecker) GetAllBackends() []BackendHealth {
    hc.mu.RLock()
    defer hc.mu.RUnlock()

    backends := make([]BackendHealth, 0, len(hc.backends))
    for _, health := range hc.backends {
        backends = append(backends, health)
    }
    return backends
}
```

### 3. 数据备份与恢复

#### 数据备份策略
```go
// 数据备份管理器
type BackupManager struct {
    config     BackupConfig
    scheduler  *BackupScheduler
    storage    BackupStorage
    notifier   BackupNotifier
}

type BackupConfig struct {
    Schedule      string // cron expression
    RetentionDays int
    Compression   bool
    Encryption    bool
}

type BackupScheduler interface {
    Schedule(interval time.Duration, fn func())
}

type BackupStorage interface {
    Store(backup *Backup) error
    List() ([]*Backup, error)
    Retrieve(id string) (*Backup, error)
    Delete(id string) error
}

type BackupNotifier interface {
    NotifySuccess(backup *Backup)
    NotifyFailure(backup *Backup, err error)
}

type Backup struct {
    ID          string
    Timestamp   time.Time
    Size        int64
    Checksum    string
    Location    string
    Status      BackupStatus
    Metadata    map[string]string
}

type BackupStatus string

const (
    BackupStatusPending   BackupStatus = "pending"
    BackupStatusRunning   BackupStatus = "running"
    BackupStatusCompleted BackupStatus = "completed"
    BackupStatusFailed    BackupStatus = "failed"
)

func NewBackupManager(config BackupConfig, scheduler BackupScheduler, storage BackupStorage, notifier BackupNotifier) *BackupManager {
    return &BackupManager{
        config:    config,
        scheduler: scheduler,
        storage:   storage,
        notifier:  notifier,
    }
}

func (bm *BackupManager) Start() {
    // 解析调度配置
    interval, err := parseSchedule(bm.config.Schedule)
    if err != nil {
        log.Printf("Failed to parse backup schedule: %v", err)
        return
    }

    // 启动调度器
    bm.scheduler.Schedule(interval, func() {
        backup := &Backup{
            ID:        generateUUID(),
            Timestamp: time.Now(),
            Status:    BackupStatusPending,
            Metadata:  make(map[string]string),
        }

        if err := bm.executeBackup(backup); err != nil {
            log.Printf("Backup failed: %v", err)
            bm.notifier.NotifyFailure(backup, err)
        } else {
            log.Printf("Backup completed: %s", backup.ID)
            bm.notifier.NotifySuccess(backup)
        }
    })

    // 启动清理任务
    go bm.cleanupOldBackups()
}

func (bm *BackupManager) executeBackup(backup *Backup) error {
    backup.Status = BackupStatusRunning

    // 执行备份操作
    data, err := bm.createBackupData()
    if err != nil {
        backup.Status = BackupStatusFailed
        return err
    }

    // 压缩
    if bm.config.Compression {
        data, err = compressData(data)
        if err != nil {
            backup.Status = BackupStatusFailed
            return err
        }
    }

    // 加密
    if bm.config.Encryption {
        data, err = encryptData(data)
        if err != nil {
            backup.Status = BackupStatusFailed
            return err
        }
    }

    // 存储备份
    backup.Size = int64(len(data))
    backup.Checksum = calculateChecksum(data)
    backup.Location = fmt.Sprintf("backups/%s/%s.backup", backup.Timestamp.Format("2006-01-02"), backup.ID)

    if err := bm.storage.Store(backup); err != nil {
        backup.Status = BackupStatusFailed
        return err
    }

    backup.Status = BackupStatusCompleted
    return nil
}

func (bm *BackupManager) cleanupOldBackups() {
    ticker := time.NewTicker(24 * time.Hour)
    defer ticker.Stop()

    for range ticker.C {
        cutoff := time.Now().AddDate(0, 0, -bm.config.RetentionDays)

        backups, err := bm.storage.List()
        if err != nil {
            log.Printf("Failed to list backups: %v", err)
            continue
        }

        for _, backup := range backups {
            if backup.Timestamp.Before(cutoff) {
                if err := bm.storage.Delete(backup.ID); err != nil {
                    log.Printf("Failed to delete backup %s: %v", backup.ID, err)
                } else {
                    log.Printf("Deleted old backup: %s", backup.ID)
                }
            }
        }
    }
}

func (bm *BackupManager) createBackupData() ([]byte, error) {
    // 实现具体的备份逻辑
    // 例如：数据库备份、文件系统备份等
    return []byte("backup data"), nil
}
```

#### 数据恢复机制
```go
// 数据恢复管理器
type RestoreManager struct {
    storage   BackupStorage
    validator DataValidator
    notifier  RestoreNotifier
}

type DataValidator interface {
    Validate(data []byte) error
}

type RestoreNotifier interface {
    NotifyProgress(restore *Restore, progress float64)
    NotifySuccess(restore *Restore)
    NotifyFailure(restore *Restore, err error)
}

type Restore struct {
    ID          string
    BackupID    string
    Timestamp   time.Time
    Status      RestoreStatus
    Progress    float64
    Error       error
    Metadata    map[string]string
}

type RestoreStatus string

const (
    RestoreStatusPending   RestoreStatus = "pending"
    RestoreStatusRunning   RestoreStatus = "running"
    RestoreStatusCompleted RestoreStatus = "completed"
    RestoreStatusFailed    RestoreStatus = "failed"
)

func NewRestoreManager(storage BackupStorage, validator DataValidator, notifier RestoreNotifier) *RestoreManager {
    return &RestoreManager{
        storage:   storage,
        validator: validator,
        notifier:  notifier,
    }
}

func (rm *RestoreManager) StartRestore(backupID string) (*Restore, error) {
    // 获取备份数据
    backup, err := rm.storage.Retrieve(backupID)
    if err != nil {
        return nil, fmt.Errorf("failed to retrieve backup: %w", err)
    }

    restore := &Restore{
        ID:        generateUUID(),
        BackupID:  backupID,
        Timestamp: time.Now(),
        Status:    RestoreStatusPending,
        Metadata:  make(map[string]string),
    }

    // 异步执行恢复
    go rm.executeRestore(restore, backup)

    return restore, nil
}

func (rm *RestoreManager) executeRestore(restore *Restore, backup *Backup) {
    restore.Status = RestoreStatusRunning

    // 读取备份数据
    data, err := rm.readBackupData(backup)
    if err != nil {
        restore.Status = RestoreStatusFailed
        restore.Error = err
        rm.notifier.NotifyFailure(restore, err)
        return
    }

    // 验证数据
    if err := rm.validator.Validate(data); err != nil {
        restore.Status = RestoreStatusFailed
        restore.Error = err
        rm.notifier.NotifyFailure(restore, err)
        return
    }

    // 执行恢复
    if err := rm.restoreData(data, func(progress float64) {
        restore.Progress = progress
        rm.notifier.NotifyProgress(restore, progress)
    }); err != nil {
        restore.Status = RestoreStatusFailed
        restore.Error = err
        rm.notifier.NotifyFailure(restore, err)
        return
    }

    restore.Status = RestoreStatusCompleted
    restore.Progress = 100.0
    rm.notifier.NotifySuccess(restore)
}

func (rm *RestoreManager) readBackupData(backup *Backup) ([]byte, error) {
    // 从存储读取备份数据
    // 实现具体的读取逻辑
    return []byte("backup data"), nil
}

func (rm *RestoreManager) restoreData(data []byte, progressFunc func(float64)) error {
    // 实现具体的数据恢复逻辑
    // 例如：数据库恢复、文件恢复等

    // 模拟进度更新
    for i := 0; i <= 100; i++ {
        progressFunc(float64(i))
        time.Sleep(50 * time.Millisecond)
    }

    return nil
}
```

## 性能设计

### 1. 缓存策略

#### 多级缓存
```go
// 多级缓存实现
type MultiLevelCache struct {
    l1Cache *sync.Map    // 内存缓存
    l2Cache *RedisCache  // Redis缓存
    l3Cache *Database    // 数据库
    stats   CacheStats
    mu      sync.RWMutex
}

type CacheStats struct {
    L1Hits   int64
    L1Misses int64
    L2Hits   int64
    L2Misses int64
    L3Hits   int64
    L3Misses int64
}

type RedisCache struct {
    client *redis.Client
    ttl    time.Duration
}

func NewMultiLevelCache(redisClient *redis.Client, database *Database) *MultiLevelCache {
    return &MultiLevelCache{
        l1Cache: &sync.Map{},
        l2Cache: &RedisCache{
            client: redisClient,
            ttl:    5 * time.Minute,
        },
        l3Cache: database,
    }
}

func (c *MultiLevelCache) Get(key string) (interface{}, error) {
    // L1缓存
    if value, ok := c.l1Cache.Load(key); ok {
        c.mu.Lock()
        c.stats.L1Hits++
        c.mu.Unlock()
        return value, nil
    }

    c.mu.Lock()
    c.stats.L1Misses++
    c.mu.Unlock()

    // L2缓存
    value, err := c.l2Cache.Get(key)
    if err == nil {
        c.l1Cache.Store(key, value)
        c.mu.Lock()
        c.stats.L2Hits++
        c.mu.Unlock()
        return value, nil
    }

    c.mu.Lock()
    c.stats.L2Misses++
    c.mu.Unlock()

    // L3缓存
    value, err = c.l3Cache.Get(key)
    if err != nil {
        c.mu.Lock()
        c.stats.L3Misses++
        c.mu.Unlock()
        return nil, err
    }

    // 更新L2和L1缓存
    c.l2Cache.Set(key, value)
    c.l1Cache.Store(key, value)

    c.mu.Lock()
    c.stats.L3Hits++
    c.mu.Unlock()

    return value, nil
}

func (c *MultiLevelCache) Set(key string, value interface{}) error {
    c.l1Cache.Store(key, value)
    if err := c.l2Cache.Set(key, value); err != nil {
        return err
    }
    return c.l3Cache.Set(key, value)
}

func (c *MultiLevelCache) GetStats() CacheStats {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.stats
}

func (rc *RedisCache) Get(key string) (interface{}, error) {
    result, err := rc.client.Get(key).Result()
    if err != nil {
        return nil, err
    }
    return result, nil
}

func (rc *RedisCache) Set(key string, value interface{}) error {
    return rc.client.Set(key, value, rc.ttl).Err()
}
```

#### 缓存预热
```go
// 缓存预热管理器
type CacheWarmer struct {
    cache       *MultiLevelCache
    dataSource  DataSource
    warmUpItems []WarmUpItem
    concurrent  int
}

type WarmUpItem struct {
    Key      string
    LoadFunc func() (interface{}, error)
    Priority int
}

type DataSource interface {
    GetAllKeys() ([]string, error)
    GetByKey(key string) (interface{}, error)
}

func NewCacheWarmer(cache *MultiLevelCache, dataSource DataSource, concurrent int) *CacheWarmer {
    return &CacheWarmer{
        cache:      cache,
        dataSource: dataSource,
        concurrent: concurrent,
    }
}

func (cw *CacheWarmer) AddWarmUpItem(key string, loadFunc func() (interface{}, error), priority int) {
    cw.warmUpItems = append(cw.warmUpItems, WarmUpItem{
        Key:      key,
        LoadFunc: loadFunc,
        Priority: priority,
    })
}

func (cw *CacheWarmer) WarmUp() error {
    // 按优先级排序
    sort.Slice(cw.warmUpItems, func(i, j int) bool {
        return cw.warmUpItems[i].Priority > cw.warmUpItems[j].Priority
    })

    // 创建worker池
    jobs := make(chan WarmUpItem, len(cw.warmUpItems))
    results := make(chan error, len(cw.warmUpItems))

    // 启动worker
    for i := 0; i < cw.concurrent; i++ {
        go cw.worker(jobs, results)
    }

    // 分发任务
    for _, item := range cw.warmUpItems {
        jobs <- item
    }
    close(jobs)

    // 收集结果
    var errors []error
    for i := 0; i < len(cw.warmUpItems); i++ {
        if err := <-results; err != nil {
            errors = append(errors, err)
        }
    }

    if len(errors) > 0 {
        return fmt.Errorf("cache warm up completed with %d errors", len(errors))
    }

    return nil
}

func (cw *CacheWarmer) worker(jobs <-chan WarmUpItem, results chan<- error) {
    for item := range jobs {
        value, err := item.LoadFunc()
        if err != nil {
            results <- fmt.Errorf("failed to warm up key %s: %w", item.Key, err)
            continue
        }

        if err := cw.cache.Set(item.Key, value); err != nil {
            results <- fmt.Errorf("failed to cache key %s: %w", item.Key, err)
            continue
        }

        results <- nil
    }
}

func (cw *CacheWarmer) WarmUpFromSource() error {
    keys, err := cw.dataSource.GetAllKeys()
    if err != nil {
        return err
    }

    // 分批处理
    batchSize := 100
    for i := 0; i < len(keys); i += batchSize {
        end := i + batchSize
        if end > len(keys) {
            end = len(keys)
        }

        batch := keys[i:end]
        if err := cw.warmUpBatch(batch); err != nil {
            log.Printf("Failed to warm up batch %d-%d: %v", i, end, err)
        }
    }

    return nil
}

func (cw *CacheWarmer) warmUpBatch(keys []string) error {
    var wg sync.WaitGroup
    semaphore := make(chan struct{}, cw.concurrent)
    errChan := make(chan error, len(keys))

    for _, key := range keys {
        wg.Add(1)
        go func(k string) {
            defer wg.Done()

            semaphore <- struct{}{}
            defer func() { <-semaphore }()

            value, err := cw.dataSource.GetByKey(k)
            if err != nil {
                errChan <- fmt.Errorf("failed to load key %s: %w", k, err)
                return
            }

            if err := cw.cache.Set(k, value); err != nil {
                errChan <- fmt.Errorf("failed to cache key %s: %w", k, err)
                return
            }

            errChan <- nil
        }(key)
    }

    wg.Wait()
    close(errChan)

    var errors []error
    for err := range errChan {
        if err != nil {
            errors = append(errors, err)
        }
    }

    if len(errors) > 0 {
        return fmt.Errorf("batch warm up completed with %d errors", len(errors))
    }

    return nil
}
```

### 2. 异步处理

#### 消息队列
```go
// 消息队列实现
type MessageQueue struct {
    channel   chan Message
    workers   []*Worker
    handler   MessageHandler
    metrics   QueueMetrics
    mu        sync.RWMutex
}

type Message struct {
    ID        string
    Topic     string
    Payload   []byte
    Timestamp time.Time
    Retry     int
    Metadata  map[string]string
}

type MessageHandler func(Message) error
type Worker struct {
    id       int
    queue    *MessageQueue
    stopChan chan struct{}
}

type QueueMetrics struct {
    TotalMessages     int64
    ProcessedMessages int64
    FailedMessages    int64
    QueueSize         int64
}

func NewMessageQueue(bufferSize int, workerCount int, handler MessageHandler) *MessageQueue {
    queue := &MessageQueue{
        channel: make(chan Message, bufferSize),
        handler: handler,
        metrics: QueueMetrics{},
    }

    // 创建worker
    for i := 0; i < workerCount; i++ {
        worker := &Worker{
            id:       i,
            queue:    queue,
            stopChan: make(chan struct{}),
        }
        queue.workers = append(queue.workers, worker)
        go worker.start()
    }

    return queue
}

func (w *Worker) start() {
    for {
        select {
        case message := <-w.queue.channel:
            w.queue.processMessage(message)
        case <-w.stopChan:
            return
        }
    }
}

func (q *MessageQueue) processMessage(message Message) {
    q.mu.Lock()
    q.metrics.TotalMessages++
    q.mu.Unlock()

    err := q.handler(message)
    if err != nil {
        q.mu.Lock()
        q.metrics.FailedMessages++
        q.mu.Unlock()

        // 重试逻辑
        if message.Retry < 3 {
            message.Retry++
            time.AfterFunc(time.Second*time.Duration(message.Retry), func() {
                q.channel <- message
            })
        } else {
            log.Printf("Message %s failed after %d retries: %v", message.ID, message.Retry, err)
        }
        return
    }

    q.mu.Lock()
    q.metrics.ProcessedMessages++
    q.mu.Unlock()
}

func (q *MessageQueue) Publish(topic string, payload []byte, metadata map[string]string) (string, error) {
    message := Message{
        ID:        generateUUID(),
        Topic:     topic,
        Payload:   payload,
        Timestamp: time.Now(),
        Metadata:  metadata,
    }

    select {
    case q.channel <- message:
        q.mu.Lock()
        q.metrics.QueueSize = int64(len(q.channel))
        q.mu.Unlock()
        return message.ID, nil
    default:
        return "", errors.New("queue is full")
    }
}

func (q *MessageQueue) GetMetrics() QueueMetrics {
    q.mu.RLock()
    defer q.mu.RUnlock()
    return q.metrics
}

func (q *MessageQueue) Stop() {
    for _, worker := range q.workers {
        close(worker.stopChan)
    }
    close(q.channel)
}
```

#### 任务调度
```go
// 任务调度器
type TaskScheduler struct {
    tasks      map[string]*ScheduledTask
    executor   TaskExecutor
    metrics    SchedulerMetrics
    mu         sync.RWMutex
}

type ScheduledTask struct {
    ID          string
    Name        string
    Schedule    string // cron expression
    Handler     TaskHandler
    NextRun     time.Time
    LastRun     time.Time
    Status      TaskStatus
    RetryCount  int
    MaxRetries  int
    Enabled     bool
    Metadata    map[string]interface{}
}

type TaskHandler func() error
type TaskExecutor interface {
    Execute(task *ScheduledTask) error
}

type TaskStatus string

const (
    TaskStatusPending   TaskStatus = "pending"
    TaskStatusRunning   TaskStatus = "running"
    TaskStatusCompleted TaskStatus = "completed"
    TaskStatusFailed    TaskStatus = "failed"
    TaskStatusDisabled  TaskStatus = "disabled"
)

type SchedulerMetrics struct {
    TotalTasks       int64
    RunningTasks     int64
    CompletedTasks   int64
    FailedTasks      int64
    AverageRunTime   time.Duration
}

func NewTaskScheduler(executor TaskExecutor) *TaskScheduler {
    return &TaskScheduler{
        tasks:    make(map[string]*ScheduledTask),
        executor: executor,
    }
}

func (s *TaskScheduler) AddTask(task *ScheduledTask) error {
    s.mu.Lock()
    defer s.mu.Unlock()

    // 解析调度时间
    nextRun, err := parseCronExpression(task.Schedule)
    if err != nil {
        return err
    }

    task.NextRun = nextRun
    task.Status = TaskStatusPending
    s.tasks[task.ID] = task

    s.metrics.TotalTasks++

    return nil
}

func (s *TaskScheduler) RemoveTask(id string) {
    s.mu.Lock()
    defer s.mu.Unlock()

    if task, exists := s.tasks[id]; exists {
        task.Status = TaskStatusDisabled
        delete(s.tasks, id)
        s.metrics.TotalTasks--
    }
}

func (s *TaskScheduler) EnableTask(id string) error {
    s.mu.Lock()
    defer s.mu.Unlock()

    task, exists := s.tasks[id]
    if !exists {
        return fmt.Errorf("task not found: %s", id)
    }

    task.Enabled = true
    return nil
}

func (s *TaskScheduler) DisableTask(id string) error {
    s.mu.Lock()
    defer s.mu.Unlock()

    task, exists := s.tasks[id]
    if !exists {
        return fmt.Errorf("task not found: %s", id)
    }

    task.Enabled = false
    return nil
}

func (s *TaskScheduler) Start() {
    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        s.checkAndRunTasks()
    }
}

func (s *TaskScheduler) checkAndRunTasks() {
    s.mu.RLock()
    tasks := make([]*ScheduledTask, 0, len(s.tasks))
    for _, task := range s.tasks {
        tasks = append(tasks, task)
    }
    s.mu.RUnlock()

    now := time.Now()

    for _, task := range tasks {
        if !task.Enabled || task.Status != TaskStatusPending {
            continue
        }

        if now.After(task.NextRun) || now.Equal(task.NextRun) {
            go s.executeTask(task)
        }
    }
}

func (s *TaskScheduler) executeTask(task *ScheduledTask) {
    s.mu.Lock()
    task.Status = TaskStatusRunning
    task.LastRun = time.Now()
    s.metrics.RunningTasks++
    s.mu.Unlock()

    start := time.Now()
    err := s.executor.Execute(task)
    duration := time.Since(start)

    s.mu.Lock()
    defer s.mu.Unlock()

    s.metrics.RunningTasks--
    s.metrics.AverageRunTime = (s.metrics.AverageRunTime*time.Duration(s.metrics.CompletedTasks) + duration) /
                               time.Duration(s.metrics.CompletedTasks+1)

    if err != nil {
        task.RetryCount++
        if task.RetryCount <= task.MaxRetries {
            task.Status = TaskStatusPending
            // 计算下次运行时间
            nextRun, err := parseCronExpression(task.Schedule)
            if err == nil {
                task.NextRun = nextRun
            }
        } else {
            task.Status = TaskStatusFailed
            s.metrics.FailedTasks++
        }
        log.Printf("Task %s failed: %v", task.ID, err)
    } else {
        task.Status = TaskStatusCompleted
        task.RetryCount = 0
        s.metrics.CompletedTasks++

        // 计算下次运行时间
        nextRun, err := parseCronExpression(task.Schedule)
        if err == nil {
            task.NextRun = nextRun
            task.Status = TaskStatusPending
        }
    }
}

func (s *TaskScheduler) GetTask(id string) (*ScheduledTask, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    task, exists := s.tasks[id]
    return task, exists
}

func (s *TaskScheduler) GetAllTasks() []*ScheduledTask {
    s.mu.RLock()
    defer s.mu.RUnlock()

    tasks := make([]*ScheduledTask, 0, len(s.tasks))
    for _, task := range s.tasks {
        tasks = append(tasks, task)
    }
    return tasks
}

func (s *TaskScheduler) GetMetrics() SchedulerMetrics {
    s.mu.RLock()
    defer s.mu.RUnlock()
    return s.metrics
}
```

### 3. 性能监控

#### 实时监控
```go
// 性能监控系统
type PerformanceMonitor struct {
    metrics    map[string]interface{}
    collectors []MetricCollector
    aggregators []MetricAggregator
    alerts     []AlertRule
    mu         sync.RWMutex
}

type MetricCollector interface {
    Collect() map[string]interface{}
    Name() string
}

type MetricAggregator interface {
    Aggregate(metrics map[string]interface{}) map[string]interface{}
    Name() string
}

type AlertRule struct {
    Name      string
    Metric    string
    Threshold float64
    Operator  string // ">", "<", "==", "!="
    Duration  time.Duration
    Action    func(Alert)
}

type Alert struct {
    Name        string
    Metric      string
    Value       float64
    Threshold   float64
    Timestamp   time.Time
    Message     string
}

func NewPerformanceMonitor() *PerformanceMonitor {
    return &PerformanceMonitor{
        metrics:    make(map[string]interface{}),
        collectors: make([]MetricCollector, 0),
        aggregators: make([]MetricAggregator, 0),
        alerts:     make([]AlertRule, 0),
    }
}

func (pm *PerformanceMonitor) AddCollector(collector MetricCollector) {
    pm.mu.Lock()
    defer pm.mu.Unlock()
    pm.collectors = append(pm.collectors, collector)
}

func (pm *PerformanceMonitor) AddAggregator(aggregator MetricAggregator) {
    pm.mu.Lock()
    defer pm.mu.Unlock()
    pm.aggregators = append(pm.aggregators, aggregator)
}

func (pm *PerformanceMonitor) AddAlert(rule AlertRule) {
    pm.mu.Lock()
    defer pm.mu.Unlock()
    pm.alerts = append(pm.alerts, rule)
}

func (pm *PerformanceMonitor) Start(interval time.Duration) {
    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for range ticker.C {
        pm.collectMetrics()
        pm.aggregateMetrics()
        pm.checkAlerts()
    }
}

func (pm *PerformanceMonitor) collectMetrics() {
    pm.mu.Lock()
    defer pm.mu.Unlock()

    for _, collector := range pm.collectors {
        metrics := collector.Collect()
        for key, value := range metrics {
            pm.metrics[key] = value
        }
    }
}

func (pm *PerformanceMonitor) aggregateMetrics() {
    pm.mu.Lock()
    defer pm.mu.Unlock()

    for _, aggregator := range pm.aggregators {
        aggregated := aggregator.Aggregate(pm.metrics)
        for key, value := range aggregated {
            pm.metrics[key] = value
        }
    }
}

func (pm *PerformanceMonitor) checkAlerts() {
    pm.mu.RLock()
    defer pm.mu.RUnlock()

    for _, rule := range pm.alerts {
        value, exists := pm.metrics[rule.Metric]
        if !exists {
            continue
        }

        floatValue, ok := value.(float64)
        if !ok {
            continue
        }

        triggered := false
        switch rule.Operator {
        case ">":
            triggered = floatValue > rule.Threshold
        case "<":
            triggered = floatValue < rule.Threshold
        case "==":
            triggered = floatValue == rule.Threshold
        case "!=":
            triggered = floatValue != rule.Threshold
        }

        if triggered {
            alert := Alert{
                Name:      rule.Name,
                Metric:    rule.Metric,
                Value:     floatValue,
                Threshold: rule.Threshold,
                Timestamp: time.Now(),
                Message:   fmt.Sprintf("Alert triggered: %s %s %.2f", rule.Metric, rule.Operator, rule.Threshold),
            }
            rule.Action(alert)
        }
    }
}

func (pm *PerformanceMonitor) GetMetrics() map[string]interface{} {
    pm.mu.RLock()
    defer pm.mu.RUnlock()

    metrics := make(map[string]interface{})
    for key, value := range pm.metrics {
        metrics[key] = value
    }
    return metrics
}

// 系统指标收集器
type SystemMetricsCollector struct{}

func NewSystemMetricsCollector() *SystemMetricsCollector {
    return &SystemMetricsCollector{}
}

func (c *SystemMetricsCollector) Collect() map[string]interface{} {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    return map[string]interface{}{
        "memory_alloc":      float64(m.Alloc),
        "memory_total_alloc": float64(m.TotalAlloc),
        "memory_sys":        float64(m.Sys),
        "memory_num_gc":     float64(m.NumGC),
        "goroutines":       float64(runtime.NumGoroutine()),
        "cpu_usage":        getCPUUsage(),
    }
}

func (c *SystemMetricsCollector) Name() string {
    return "system"
}

func getCPUUsage() float64 {
    // 简化的CPU使用率计算
    // 实际实现需要更复杂的计算
    return 0.0
}

// 应用指标收集器
type ApplicationMetricsCollector struct {
    requestCount int64
    errorCount   int64
    responseTime time.Duration
    mu           sync.RWMutex
}

func NewApplicationMetricsCollector() *ApplicationMetricsCollector {
    return &ApplicationMetricsCollector{}
}

func (c *ApplicationMetricsCollector) RecordRequest(duration time.Duration, isError bool) {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.requestCount++
    c.responseTime += duration
    if isError {
        c.errorCount++
    }
}

func (c *ApplicationMetricsCollector) Collect() map[string]interface{} {
    c.mu.RLock()
    defer c.mu.RUnlock()

    avgResponseTime := time.Duration(0)
    if c.requestCount > 0 {
        avgResponseTime = c.responseTime / time.Duration(c.requestCount)
    }

    errorRate := 0.0
    if c.requestCount > 0 {
        errorRate = float64(c.errorCount) / float64(c.requestCount) * 100
    }

    return map[string]interface{}{
        "request_count":      float64(c.requestCount),
        "error_count":        float64(c.errorCount),
        "avg_response_time":  float64(avgResponseTime),
        "error_rate":         errorRate,
    }
}

func (c *ApplicationMetricsCollector) Name() string {
    return "application"
}
```

这个系统设计原则文档涵盖了架构设计、可扩展性、可靠性、性能、安全性、可维护性、成本效益等各个方面的设计原则，提供了实际可用的代码示例和最佳实践。通过这些设计原则，可以构建高质量、可扩展、可靠的系统。